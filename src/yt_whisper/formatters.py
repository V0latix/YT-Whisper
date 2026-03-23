"""Output formatters for transcription results."""

from pathlib import Path

from .transcriber import TranscriptionResult


def _format_timestamp(seconds: float, fmt: str = "srt") -> str:
    """Format seconds into SRT or VTT timestamp."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)

    if fmt == "vtt":
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def to_txt(result: TranscriptionResult) -> str:
    """Plain text output."""
    return "\n".join(seg.text for seg in result.segments)


def to_srt(result: TranscriptionResult) -> str:
    """SubRip subtitle format."""
    lines = []
    for i, seg in enumerate(result.segments, start=1):
        start = _format_timestamp(seg.start, "srt")
        end = _format_timestamp(seg.end, "srt")
        lines.append(f"{i}\n{start} --> {end}\n{seg.text}\n")
    return "\n".join(lines)


def to_vtt(result: TranscriptionResult) -> str:
    """WebVTT subtitle format."""
    lines = ["WEBVTT\n"]
    for i, seg in enumerate(result.segments, start=1):
        start = _format_timestamp(seg.start, "vtt")
        end = _format_timestamp(seg.end, "vtt")
        lines.append(f"{i}\n{start} --> {end}\n{seg.text}\n")
    return "\n".join(lines)


def to_json(result: TranscriptionResult) -> str:
    """JSON output with full metadata."""
    import json

    data = {
        "language": result.language,
        "language_probability": result.language_probability,
        "duration": result.duration,
        "segments": [
            {"start": seg.start, "end": seg.end, "text": seg.text}
            for seg in result.segments
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


FORMATTERS = {
    "txt": to_txt,
    "srt": to_srt,
    "vtt": to_vtt,
    "json": to_json,
}


def write_output(
    result: TranscriptionResult,
    output_path: Path,
    fmt: str,
) -> None:
    """Write transcription to a file."""
    formatter = FORMATTERS[fmt]
    content = formatter(result)
    output_path.write_text(content, encoding="utf-8")
