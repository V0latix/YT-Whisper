# yt-whisper

Extract text from YouTube videos using [Whisper](https://github.com/openai/whisper) via [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (CTranslate2 backend — same speed as [whisper.cpp](https://github.com/ggml-org/whisper.cpp)).

## Requirements

- Python 3.9+
- [ffmpeg](https://ffmpeg.org/) — required for audio extraction

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
winget install ffmpeg
```

## Installation

```bash
# Whisper only (default)
pip install yt-whisper

# With Moonshine support
pip install 'yt-whisper[moonshine]'
```

Or install from source:

```bash
git clone https://github.com/V0latix/YT-Whisper
cd yt-whisper
pip install -e .
```

## Usage

```bash
yt-whisper "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Options

```
Arguments:
  URL                    YouTube video URL [required]

Options:
  -m, --model TEXT       Model to use [default: base]
                         Whisper : tiny | tiny.en | base | base.en | small | small.en |
                                   medium | medium.en | large-v1 | large-v2 | large-v3 | large-v3-turbo
                         Moonshine: moonshine-tiny | moonshine-base  (English-only, requires [moonshine] extra)
  -l, --language TEXT    Force language (e.g. 'fr', 'en'). Auto-detect if not set. Ignored for Moonshine.
  -t, --task [transcribe|translate]
                         transcribe = keep original language
                         translate  = translate to English [default: transcribe]
                         (ignored for Moonshine)
  -o, --output-dir PATH  Directory to save output files [default: current directory]
  -f, --format [txt|srt|vtt|json|all]
                         Output format [default: txt]
  -d, --device TEXT      Inference device: cpu, cuda, or auto [default: auto]
  -p, --print / --no-print
                         Print transcription to stdout [default: print]
  -v, --version          Show version and exit.
  --help                 Show this message and exit.
```

### Examples

```bash
# Basic transcription (outputs .txt)
yt-whisper "https://youtube.com/watch?v=..."

# Use a larger model for better accuracy
yt-whisper "https://youtube.com/watch?v=..." --model large-v3

# Generate SRT subtitles
yt-whisper "https://youtube.com/watch?v=..." --format srt

# Generate all formats at once
yt-whisper "https://youtube.com/watch?v=..." --format all

# Force French language
yt-whisper "https://youtube.com/watch?v=..." --language fr

# Translate to English
yt-whisper "https://youtube.com/watch?v=..." --task translate

# Save to a specific directory
yt-whisper "https://youtube.com/watch?v=..." --output-dir ./transcripts

# Use GPU if available
yt-whisper "https://youtube.com/watch?v=..." --device cuda

# Don't print to stdout (just save files)
yt-whisper "https://youtube.com/watch?v=..." --no-print
```

## Models

### Whisper (multilingual, default)

| Model          | Parameters | Languages    | Speed   |
|----------------|-----------|--------------|---------|
| tiny           | 39M       | multilingual | ~32x    |
| base           | 74M       | multilingual | ~16x    |
| small          | 244M      | multilingual | ~6x     |
| medium         | 769M      | multilingual | ~2x     |
| large-v3       | 1550M     | multilingual | 1x      |
| large-v3-turbo | 809M      | multilingual | ~2x     |

### Moonshine (English-only, faster for short content)

Requires `pip install 'yt-whisper[moonshine]'`. Moonshine scales compute with audio length (unlike Whisper's fixed 30s chunks), making it faster for short clips.

| Model           | Parameters | WER   |
|-----------------|-----------|-------|
| moonshine-tiny  | 26M       | 12.7% |
| moonshine-base  | 61M       | 10.1% |

Models are downloaded automatically on first use and cached at `~/.cache/huggingface/`.

## Output Formats

| Format | Description                          |
|--------|--------------------------------------|
| `txt`  | Plain text transcript                |
| `srt`  | SubRip subtitles (for video players) |
| `vtt`  | WebVTT subtitles (for web players)   |
| `json` | Full data with timestamps            |
| `all`  | All formats at once                  |

## License

MIT
