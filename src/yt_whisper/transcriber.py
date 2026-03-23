"""Whisper transcription using faster-whisper (CTranslate2 backend)."""

from dataclasses import dataclass
from pathlib import Path
from typing import Generator

from faster_whisper import WhisperModel
from faster_whisper.transcribe import Segment


MODELS = ["tiny", "tiny.en", "base", "base.en", "small", "small.en", "medium", "medium.en", "large-v1", "large-v2", "large-v3", "large-v3-turbo"]


@dataclass
class TranscriptionSegment:
    start: float
    end: float
    text: str


@dataclass
class TranscriptionResult:
    segments: list[TranscriptionSegment]
    language: str
    language_probability: float
    duration: float


def transcribe(
    audio_path: Path,
    model_size: str = "base",
    language: str | None = None,
    task: str = "transcribe",
    device: str = "auto",
    compute_type: str = "auto",
) -> tuple[TranscriptionResult, Generator]:
    """
    Transcribe audio using faster-whisper.

    Args:
        audio_path: Path to the audio file.
        model_size: Whisper model size (tiny, base, small, medium, large-v3, ...).
        language: Force a specific language (e.g. "fr", "en"). Auto-detect if None.
        task: "transcribe" or "translate" (translate to English).
        device: "cpu", "cuda", or "auto".
        compute_type: Quantization type ("auto", "float16", "int8", ...).

    Returns:
        A tuple of (TranscriptionResult, segment generator).
    """
    if device == "auto":
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            device = "cpu"

    if compute_type == "auto":
        compute_type = "float16" if device == "cuda" else "int8"

    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    segments_gen, info = model.transcribe(
        str(audio_path),
        language=language,
        task=task,
        beam_size=5,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
    )

    segments = []
    for seg in segments_gen:
        segments.append(
            TranscriptionSegment(
                start=seg.start,
                end=seg.end,
                text=seg.text.strip(),
            )
        )

    return TranscriptionResult(
        segments=segments,
        language=info.language,
        language_probability=info.language_probability,
        duration=info.duration,
    )
