# Automatic Speech Recognition

[`asr_batch.py`](asr_batch.py) creates draft speech transcripts from a media file or recursively from a directory. It offers faster-whisper (`--engine whisper`) and an optional WhisperX alignment branch (`--engine whisperx`). Review transcripts and timings manually before using them for Sens-Ex annotation.

## Requirements

Use a Python environment with the chosen engine installed. For the faster-whisper branch:

```sh
python3 -m pip install faster-whisper
```

The WhisperX branch additionally requires `whisperx` and its compatible dependencies. Model and alignment weights may need downloading. Package versions are not pinned in this directory.

## Instructions

Run from this directory with your input file or folder and a separate output directory:

```sh
python3 asr_batch.py /path/to/audio /path/to/transcripts --engine whisper --model medium --language fr --formats txt,json
```

Use `--language it` for Italian, or omit `--language` for automatic detection. The defaults are CPU and `int8`; `--device cuda` is also available. Add `--vad_filter` to request voice activity filtering in the faster-whisper branch. Use `--help` for the full argument list.

## Outputs

- `.txt`: joined transcript text, without timecodes.
- `.json`: segments with start/end times in seconds, text, and selected engine/model information.
- `.words.json`: word timestamps only when returned by the WhisperX branch. Requesting `words` in faster-whisper mode does not produce this file.

Times are relative to the input media. An extracted recording therefore has excerpt-relative times, not the original recording's absolute times.

## Known issues

- **Output collisions:** outputs are flattened into one directory. Identical stems and filenames containing additional dots can resolve to the same output path. For example, `clip.a.wav` and `clip.b.wav` both produce `clip.json`. Use distinct dot-free stems and separate output directories until naming is corrected.
- **WhisperX compatibility:** the code passes `vad_filter` to `transcribe`, but the locally installed WhisperX signature does not accept it. This branch needs repair and validation before use; it is not a verified word-alignment route.
- A model is loaded separately for every input file. A failure interrupts the batch; successful earlier outputs may already exist.
- This script's JSON is not directly the `time,text` transcription CSV required by the Twitch HTML preparation script.
