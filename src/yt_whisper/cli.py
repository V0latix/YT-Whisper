"""CLI entry point for yt-whisper."""

import tempfile
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from . import __version__
from .downloader import download_audio, get_video_info
from .formatters import FORMATTERS, write_output
from .transcriber import MODELS, transcribe

app = typer.Typer(
    name="yt-whisper",
    help="Extract text from YouTube videos using Whisper.",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()
err_console = Console(stderr=True)


class OutputFormat(str, Enum):
    txt = "txt"
    srt = "srt"
    vtt = "vtt"
    json = "json"
    all = "all"


class Task(str, Enum):
    transcribe = "transcribe"
    translate = "translate"


def version_callback(value: bool) -> None:
    if value:
        console.print(f"yt-whisper [bold green]v{__version__}[/bold green]")
        raise typer.Exit()


@app.command()
def main(
    url: Annotated[str, typer.Argument(help="YouTube video URL")],
    model: Annotated[
        str,
        typer.Option("--model", "-m", help=f"Whisper model size. Options: {', '.join(MODELS)}"),
    ] = "base",
    language: Annotated[
        Optional[str],
        typer.Option("--language", "-l", help="Force language (e.g. 'fr', 'en'). Auto-detect if not set."),
    ] = None,
    task: Annotated[
        Task,
        typer.Option("--task", "-t", help="'transcribe' to keep original language, 'translate' to translate to English."),
    ] = Task.transcribe,
    output_dir: Annotated[
        Optional[Path],
        typer.Option("--output-dir", "-o", help="Directory to save output files. Defaults to current directory."),
    ] = None,
    output_format: Annotated[
        OutputFormat,
        typer.Option("--format", "-f", help="Output format."),
    ] = OutputFormat.txt,
    device: Annotated[
        str,
        typer.Option("--device", "-d", help="Device to run inference on: 'cpu', 'cuda', or 'auto'."),
    ] = "auto",
    print_text: Annotated[
        bool,
        typer.Option("--print/--no-print", "-p", help="Print transcription to stdout."),
    ] = True,
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    """
    Transcribe a YouTube video to text using Whisper.

    Examples:

    \b
      yt-whisper "https://youtube.com/watch?v=..."
      yt-whisper "https://youtube.com/watch?v=..." --model large-v3 --format srt
      yt-whisper "https://youtube.com/watch?v=..." --language fr --task translate
    """
    if model not in MODELS:
        err_console.print(f"[red]Unknown model '{model}'. Choose from: {', '.join(MODELS)}[/red]")
        raise typer.Exit(1)

    out_dir = output_dir or Path.cwd()
    out_dir.mkdir(parents=True, exist_ok=True)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        # Fetch metadata
        task_id = progress.add_task("[cyan]Fetching video info...", total=None)
        try:
            info = get_video_info(url)
        except Exception as e:
            err_console.print(f"[red]Failed to fetch video info: {e}[/red]")
            raise typer.Exit(1)

        title = info.get("title", "Unknown")
        duration = info.get("duration", 0)
        channel = info.get("channel", info.get("uploader", "Unknown"))

        progress.update(task_id, description=f"[cyan]Found:[/cyan] [bold]{title}[/bold]")

        # Show video metadata
        progress.stop()

    console.print(
        Panel.fit(
            f"[bold]{title}[/bold]\n"
            f"[dim]Channel:[/dim] {channel}  "
            f"[dim]Duration:[/dim] {duration // 60}m {duration % 60}s",
            title="[green]YouTube Video[/green]",
            border_style="green",
        )
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        ) as progress:
            # Download audio
            dl_task = progress.add_task("[yellow]Downloading audio...", total=None)
            try:
                audio_path, _ = download_audio(url, tmp_path)
            except Exception as e:
                err_console.print(f"[red]Failed to download audio: {e}[/red]")
                raise typer.Exit(1)
            progress.update(dl_task, description="[green]Audio downloaded[/green]")

            # Transcribe
            tr_task = progress.add_task(
                f"[yellow]Transcribing with [bold]{model}[/bold] model...", total=None
            )
            try:
                result = transcribe(
                    audio_path,
                    model_size=model,
                    language=language,
                    task=task.value,
                    device=device,
                )
            except Exception as e:
                err_console.print(f"[red]Transcription failed: {e}[/red]")
                raise typer.Exit(1)
            progress.update(tr_task, description="[green]Transcription complete[/green]")

    # Display stats
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_row("[dim]Language[/dim]", f"[bold]{result.language}[/bold] ({result.language_probability:.0%})")
    table.add_row("[dim]Segments[/dim]", str(len(result.segments)))
    table.add_row("[dim]Duration[/dim]", f"{result.duration:.1f}s")
    table.add_row("[dim]Model[/dim]", model)
    console.print(table)
    console.print()

    # Safe filename from video title
    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title).strip()[:80]

    # Write output(s)
    formats_to_write = list(FORMATTERS.keys()) if output_format == OutputFormat.all else [output_format.value]
    written_files = []

    for fmt in formats_to_write:
        out_file = out_dir / f"{safe_title}.{fmt}"
        write_output(result, out_file, fmt)
        written_files.append(out_file)
        console.print(f"[green]Saved[/green] {out_file}")

    # Print to stdout if requested
    if print_text:
        from .formatters import to_txt
        console.print()
        console.rule("[dim]Transcription[/dim]")
        console.print(to_txt(result))


if __name__ == "__main__":
    app()
