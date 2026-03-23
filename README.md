# yt-whisper

> Transcribe any YouTube video to text in one command.

[![PyPI](https://img.shields.io/pypi/v/yt-whisper)](https://pypi.org/project/yt-whisper/)
[![Python](https://img.shields.io/pypi/pyversions/yt-whisper)](https://pypi.org/project/yt-whisper/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

`yt-whisper` downloads the audio from a YouTube URL and runs it through [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (CTranslate2 backend — comparable speed to [whisper.cpp](https://github.com/ggml-org/whisper.cpp)) or [Moonshine](https://github.com/usefulsensors/moonshine) for English-only content. Output can be plain text, SRT/VTT subtitles, or JSON with timestamps.

---

## Features

- **One command** — paste a URL, get a transcript
- **Multiple models** — tiny to large-v3-turbo (Whisper) or Moonshine for ultra-fast English transcription
- **Multiple formats** — `.txt`, `.srt`, `.vtt`, `.json`, or all at once
- **Auto language detection** — or force a specific language
- **Translation** — translate any language to English via Whisper
- **GPU support** — CUDA auto-detected, or force `cpu`/`cuda`/`auto`
- **Rich terminal UI** — progress spinners, video metadata panel, transcription stats

---

## Requirements

- Python 3.9+
- [ffmpeg](https://ffmpeg.org/) — required for audio extraction

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg

# Windows
winget install ffmpeg
```

---

## Installation

```bash
pip install yt-whisper
```

With [Moonshine](https://github.com/usefulsensors/moonshine) support (English-only, faster on short clips):

```bash
pip install 'yt-whisper[moonshine]'
```

Install from source:

```bash
git clone https://github.com/V0latix/YT-Whisper
cd YT-Whisper
pip install -e .
```

---

## Quick Start

```bash
yt-whisper "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

The transcript is printed to the terminal and saved as `<video-title>.txt` in the current directory.

---

## Usage

```
yt-whisper [OPTIONS] URL
```

### Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--model` | `-m` | `base` | Model name (see [Models](#models)) |
| `--language` | `-l` | auto | Force language code, e.g. `fr`, `en` |
| `--task` | `-t` | `transcribe` | `transcribe` or `translate` (→ English) |
| `--output-dir` | `-o` | `.` | Directory to save output files |
| `--format` | `-f` | `txt` | `txt`, `srt`, `vtt`, `json`, or `all` |
| `--device` | `-d` | `auto` | `cpu`, `cuda`, or `auto` |
| `--print/--no-print` | `-p` | print | Print transcript to stdout |
| `--version` | `-v` | — | Show version and exit |

### Examples

```bash
# Basic transcription → saves <title>.txt
yt-whisper "https://youtube.com/watch?v=..."

# Higher accuracy with a larger model
yt-whisper "https://youtube.com/watch?v=..." --model large-v3

# Generate SRT subtitles
yt-whisper "https://youtube.com/watch?v=..." --format srt

# Generate every format at once
yt-whisper "https://youtube.com/watch?v=..." --format all

# Force French, then translate to English
yt-whisper "https://youtube.com/watch?v=..." --language fr --task translate

# Save files to a specific folder
yt-whisper "https://youtube.com/watch?v=..." --output-dir ./transcripts

# Run on GPU
yt-whisper "https://youtube.com/watch?v=..." --device cuda

# Silent — save file only, no stdout
yt-whisper "https://youtube.com/watch?v=..." --no-print

# Use Moonshine for fast English-only transcription
yt-whisper "https://youtube.com/watch?v=..." --model moonshine-base
```

---

## Models

### Whisper — multilingual

| Model | Params | Languages | Relative speed |
|---|---|---|---|
| `tiny` | 39 M | multilingual | ~32× |
| `tiny.en` | 39 M | English only | ~32× |
| `base` | 74 M | multilingual | ~16× |
| `base.en` | 74 M | English only | ~16× |
| `small` | 244 M | multilingual | ~6× |
| `small.en` | 244 M | English only | ~6× |
| `medium` | 769 M | multilingual | ~2× |
| `medium.en` | 769 M | English only | ~2× |
| `large-v1` | 1 550 M | multilingual | 1× |
| `large-v2` | 1 550 M | multilingual | 1× |
| `large-v3` | 1 550 M | multilingual | 1× |
| `large-v3-turbo` | 809 M | multilingual | ~2× |

### Moonshine — English-only (`[moonshine]` extra required)

Moonshine scales compute with audio length (unlike Whisper's fixed 30 s chunks), making it significantly faster for short clips.

| Model | Params | WER |
|---|---|---|
| `moonshine-tiny` | 26 M | 12.7 % |
| `moonshine-base` | 61 M | 10.1 % |

Models are downloaded automatically on first use and cached at `~/.cache/huggingface/`.

---

## Output Formats

| Format | Description |
|--------|-------------|
| `txt` | Plain text transcript |
| `srt` | SubRip subtitles — for video players (VLC, mpv, …) |
| `vtt` | WebVTT subtitles — for web players and YouTube |
| `json` | Full data with per-segment timestamps |
| `all` | All four formats at once |

Output files are named after the video title and saved to the current directory (or `--output-dir`).

---

## License

[MIT](LICENSE)
