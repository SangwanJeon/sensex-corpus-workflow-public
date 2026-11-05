# TRS-to-EAF Conversion

[`trs_to_sensex_eaf_v2.py`](trs_to_sensex_eaf_v2.py) converts Transcriber `.trs` files into ELAN `.eaf` annotations. Speakers are assigned `SP1_trs`, `SP2_trs`, etc., in declaration order; a speaker mapping CSV preserves the source IDs and names.

## Requirements

Python 3.10 or newer and `pympi-ling`:

```sh
python3 -m pip install pympi-ling
```

## Instructions

Run from this directory, replacing the example paths.

Convert a file or directory, optionally linking corresponding full recordings:

```sh
python3 trs_to_sensex_eaf_v2.py /path/to/trs -o /path/to/eaf --media-dir /path/to/media
```

Select files and choose whole recordings or excerpts interactively:

```sh
python3 trs_to_sensex_eaf_v2.py /path/to/trs -o /path/to/eaf --interactive
```

Enter excerpt boundaries as seconds, `MM:SS`, or `HH:MM:SS`, optionally with milliseconds. There are no noninteractive excerpt start/end flags. `--drop-events` omits Transcriber Event markers; otherwise these are retained as bracketed text.

## Outputs and alignment

Each conversion writes an EAF and `SOURCE_speaker_map.csv`. Excerpt filenames include `__excerpt_HHMMSSmmm-HHMMSSmmm`, matching the media extraction naming convention.

Whole-file conversion can link matching media. Excerpt annotations are clipped and rebased to zero, and source-boundary properties are added when supported. Full recordings are deliberately not linked to excerpt EAFs: extract matching media with [`extract_excerpts.py`](../extract_excerpts/extract_excerpts.py), using the same boundaries, then link that excerpt in ELAN.

## Review in ELAN

Check speaker assignments, linked media, and annotation boundaries. This is a TRS conversion, not automatic illocutionary segmentation or a completed Sens-Ex annotation. It does not create the complete `_verbal`/`_nonverbal` tier structure described in the tutorial.

If an excerpt cuts through an annotation, its full text is retained even though its time interval is shortened. Same-speaker overlaps can trigger automatic boundary adjustments. Review these cases manually. Speaker maps retain original names, and existing output files can be replaced.
