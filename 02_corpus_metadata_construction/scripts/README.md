# Metadata Scripts

## CSV Exports

CSV files preserve workbook values, including known inconsistencies. Dates and times use readable ISO dates and 24-hour times; spreadsheet formatting is omitted. The XLSX files remain the editable sources.

Regenerate both sets of exports with [`export_workbooks_to_csv.py`](export_workbooks_to_csv.py), which requires `openpyxl`:

```sh
python3 02_corpus_metadata_construction/scripts/export_workbooks_to_csv.py
```

Run the command from the repository root. The empty worksheet is skipped.

## Python Scripts

This directory contains Python scripts supporting metadata retrieval.

**[`twitch_clip_to_vod.py`](twitch_clip_to_vod.py)**

This script uses the Twitch API to retrieve information about Twitch clips and their corresponding video-on-demand (VOD) recordings.

It supports the identification of VOD-relative excerpt boundaries using the clip offset and duration provided by the API.

The script requires Twitch API credentials and appropriate Python dependencies.

Its outputs should be verified before being incorporated into the metadata workbooks, particularly when VOD information or temporal offsets are unavailable.
