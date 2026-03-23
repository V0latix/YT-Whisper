"""Transcription backends: faster-whisper (Whisper) and Moonshine."""

import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np


# ── Model registries ──────────────────────────────────────────────────────────

WHISPER_MODELS = [
    "tiny", "tiny.en", "base", "base.en",
    "small", "small.en", "medium", "medium.en",
    "large-v1", "large-v2", "large-v3", "large-v3-turbo",
]

MOONSHINE_MODELS = ["moonshine-tiny", "moonshine-base"]

MODELS = WHISPER_MODELS + MOONSHINE_MODELS


# ── Shared data classes ───────────────────────────────────────────────────────

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


# ── Audio helpers (no extra deps — uses stdlib wave + numpy) ──────────────────

def _read_wav(path: Path) -> tuple[np.ndarray, int]:
    """Read a WAV file into a float32 mono numpy array."""
    with wave.open(str(path), "rb") as f:
        sr = f.getframerate()
        n_channels = f.getnchannels()
        sampwidth = f.getsampwidth()
        raw = f.readframes(f.getnframes())

    dtype_map = {1: np.int8, 2: np.int16, 4: np.int32}
    dtype = dtype_map[sampwidth]
    audio = np.frombuffer(raw, dtype=dtype).astype(np.float32)
    audio /= float(np.iinfo(dtype).max)

    if n_channels > 1:
        audio = audio.reshape(-1, n_channels).mean(axis=1)

    return audio, sr


def _resample(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """Linear resample to target sample rate."""
    if orig_sr == target_sr:
        return audio
    new_len = int(len(audio) * target_sr / orig_sr)
    return np.interp(
        np.linspace(0, len(audio) - 1, new_len),
        np.arange(len(audio)),
        audio,
    ).astype(np.float32)


# ── Whisper backend (faster-whisper / CTranslate2) ────────────────────────────

def _transcribe_whisper(
    audio_path: Path,
    model_size: str,
    language: str | None,
    task: str,
    device: str,
    compute_type: str,
) -> TranscriptionResult:
    from faster_whisper import WhisperModel

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

    segments = [
        TranscriptionSegment(start=seg.start, end=seg.end, text=seg.text.strip())
        for seg in segments_gen
    ]

    return TranscriptionResult(
        segments=segments,
        language=info.language,
        language_probability=info.language_probability,
        duration=info.duration,
    )


# ── Moonshine backend (useful-moonshine) ──────────────────────────────────────

_MOONSHINE_SR = 16_000
_MOONSHINE_MAX_SECONDS = 60


def _transcribe_moonshine(
    audio_path: Path,
    model_size: str,  # "tiny" or "base"
) -> TranscriptionResult:
    try:
        import moonshine as ms
    except ImportError:
        raise ImportError(
            "Moonshine is not installed. Run: pip install 'yt-whisper[moonshine]'"
        )

    audio, sr = _read_wav(audio_path)
    audio = _resample(audio, sr, _MOONSHINE_SR)
    duration = len(audio) / _MOONSHINE_SR

    chunk_samples = _MOONSHINE_MAX_SECONDS * _MOONSHINE_SR
    model_id = f"moonshine/{model_size}"

    segments = []
    for chunk_start in range(0, len(audio), chunk_samples):
        chunk = audio[chunk_start : chunk_start + chunk_samples]
        start_time = chunk_start / _MOONSHINE_SR
        end_time = min(start_time + _MOONSHINE_MAX_SECONDS, duration)

        texts = ms.transcribe(chunk, model_id)
        text = " ".join(texts).strip()
        if text:
            segments.append(TranscriptionSegment(start=start_time, end=end_time, text=text))

    return TranscriptionResult(
        segments=segments,
        language="en",
        language_probability=1.0,
        duration=duration,
    )


# ── Public dispatcher ─────────────────────────────────────────────────────────

def transcribe(
    audio_path: Path,
    model_size: str = "base",
    language: str | None = None,
    task: str = "transcribe",
    device: str = "auto",
    compute_type: str = "auto",
) -> TranscriptionResult:
    """
    Transcribe audio. Dispatches to the right backend based on model name.

    Whisper models : tiny, base, small, medium, large-v3, ...
    Moonshine models: moonshine-tiny, moonshine-base  (English-only)
    """
    if model_size in MOONSHINE_MODELS:
        size = model_size.removeprefix("moonshine-")
        return _transcribe_moonshine(audio_path, size)

    return _transcribe_whisper(audio_path, model_size, language, task, device, compute_type)
