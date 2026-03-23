"""YouTube audio downloader using yt-dlp."""

import tempfile
from pathlib import Path

import yt_dlp


def get_video_info(url: str) -> dict:
    """Fetch video metadata without downloading."""
    opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False)


def download_audio(url: str, output_dir: Path) -> tuple[Path, dict]:
    """
    Download audio from a YouTube URL.

    Returns the path to the downloaded audio file and video metadata.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(output_dir / "%(id)s.%(ext)s")

    opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "0",
            }
        ],
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)

    video_id = info["id"]
    audio_path = output_dir / f"{video_id}.wav"
    return audio_path, info
