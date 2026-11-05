# Media Excerpt Extraction

[`extract_excerpts.py`](extract_excerpts.py) copies whole recordings or extracts selected intervals using FFmpeg.

## Requirements

Python 3, FFmpeg, and preferably FFprobe on `PATH`. Only the Python standard library is used. FFprobe provides duration information for checking excerpt boundaries.

Only `extract_excerpts.py` and this README are versioned in this directory. Source recordings, generated excerpts, manifests, and supplementary documents are kept locally and ignored by Git.

## Instructions

Run these commands from this directory, replacing input and output paths with your own.

Select recordings and excerpt boundaries interactively:

```sh
python3 extract_excerpts.py /path/to/media -o /path/to/excerpts --interactive --reencode
```

Choose files, choose whole-file copying or excerpt extraction, and enter start/end times as seconds, `MM:SS`, or `HH:MM:SS`, optionally with milliseconds. Match these boundaries to those used for TRS-to-EAF conversion.

Copy whole files without prompts:

```sh
python3 extract_excerpts.py /path/to/media -o /path/to/copies
```

Without `--interactive`, the script copies whole files; `--reencode` alone does not select an excerpt. Use `--help` for the available options.

## Outputs

- Whole-file copies retain their filenames.
- Excerpts use `SOURCE__excerpt_HHMMSSmmm-HHMMSSmmm.ext`.
- `multimedia_extraction_manifest.csv` records source/output paths, source boundaries, requested duration, and re-encoding choice. Rows are appended on subsequent runs.

## Limits

Stream-copy cuts may depend on source packet/keyframe boundaries. Re-encoding is intended for more precise cuts, but the current FLAC branch incorrectly requests PCM in a FLAC container and fails; do not use it for FLAC re-encoding until corrected. Output paths can be reused and overwritten. The manifest records requested duration rather than a measurement of the result. This utility does not impose the mono settings used by the separate audio converter.
