#!/usr/bin/env python3
"""Export the metadata workbooks for GitHub viewing.

Requires openpyxl (python3 -m pip install openpyxl).
Run from any directory: python3 path/to/export_workbooks_to_csv.py
The XLSX files remain the editable source; CSV files contain values only.
"""

import csv
from datetime import date, datetime, time, timedelta
from pathlib import Path

from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    ROOT / "metadata_workbooks/sensex_metadata_ver_20260830.xlsx",
    ROOT / "pilot_survey/sociolinguistic_pilot_survey_results.xlsx",
)


def serialize(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        if value.time() == time.min:
            return value.date().isoformat()
        return value.isoformat(sep=" ")
    if isinstance(value, (date, time)):
        return value.isoformat()
    if isinstance(value, timedelta):
        micros = round(value.total_seconds() * 1_000_000)
        sign = "-" if micros < 0 else ""
        seconds, fractional = divmod(abs(micros), 1_000_000)
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        suffix = f".{fractional:06d}".rstrip("0") if fractional else ""
        return f"{sign}{hours:02d}:{minutes:02d}:{seconds:02d}{suffix}"
    return str(value)


def export_workbook(source):
    workbook = load_workbook(source, data_only=False)
    output_dir = source.parent / "csv"
    exported = []
    try:
        for sheet in workbook:
            rows = list(sheet.iter_rows())
            if any(cell.data_type == "f" for row in rows for cell in row):
                raise ValueError(f"Formula cells require review: {source.name}/{sheet.title}")
            populated = [
                (r, c)
                for r, row in enumerate(rows)
                for c, cell in enumerate(row)
                if cell.value is not None
            ]
            if not populated:
                print(f"Skipped empty sheet: {source.name}/{sheet.title}")
                continue
            last_row = max(r for r, _ in populated)
            last_col = max(c for _, c in populated)
            values = [
                [serialize(cell.value) for cell in row[:last_col + 1]]
                for row in rows[:last_row + 1]
            ]
            output_dir.mkdir(exist_ok=True)
            target = output_dir / f"{sheet.title}.csv"
            with target.open("w", encoding="utf-8", newline="") as handle:
                csv.writer(handle, lineterminator="\n").writerows(values)
            with target.open(encoding="utf-8", newline="") as handle:
                if list(csv.reader(handle)) != values:
                    raise ValueError(f"CSV verification failed: {target}")
            exported.append((target.name, len(values) - 1, last_col + 1))
            print(f"Exported {target.relative_to(ROOT)}: {len(values) - 1} records")
    finally:
        workbook.close()

    lines = [
        "# CSV exports", "",
        f"Source workbook: `{source.name}` in the parent directory.", "",
        "These UTF-8 CSV files contain one populated worksheet each and can be viewed on GitHub. "
        "The XLSX workbook remains the editable source. Empty worksheets and trailing empty "
        "rows/columns are omitted; interior blank cells and rows are preserved.", "",
        "Dates use ISO format (`YYYY-MM-DD`); times use 24-hour `HH:MM:SS` "
        "with fractional seconds when present. Blank cells stay empty, and literal values "
        "such as `na`, category spellings, abbreviated metrics, and identifiers are preserved. "
        "Workbook formatting and annotations are not included. These exports do not correct "
        "the data-quality issues identified in the audit.", "",
        "| Worksheet | Records | Columns |",
        "| --- | --- | --- |",
        *[f"| [{name[:-4]}]({name}) | {count} | {width} |" for name, count, width in exported],
        "", "To regenerate both workbooks' exports, install `openpyxl` and run:", "",
        "```sh", "python3 02_corpus_metadata_construction/scripts/export_workbooks_to_csv.py",
        "```", "", "Run the command from the repository root.", "",
    ]
    (output_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    for source in SOURCES:
        export_workbook(source)
