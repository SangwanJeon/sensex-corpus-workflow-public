# CSV exports

Source workbook: `sensex_metadata_ver_20260830.xlsx` in the parent directory.

These UTF-8 CSV files contain one populated worksheet each and can be viewed on GitHub. The XLSX workbook remains the editable source. Empty worksheets and trailing empty rows/columns are omitted; interior blank cells and rows are preserved.

Dates use ISO format (`YYYY-MM-DD`); times use 24-hour `HH:MM:SS` with fractional seconds when present. Blank cells stay empty, and literal values such as `na`, category spellings, abbreviated metrics, and identifiers are preserved. Workbook formatting and annotations are not included. These exports do not correct the data-quality issues identified in the audit.

| Worksheet | Records | Columns |
| --- | --- | --- |
| [SEFR2.0](SEFR2.0.csv) | 34 | 36 |
| [SEFR1.0](SEFR1.0.csv) | 25 | 35 |
| [SEFR0.0](SEFR0.0.csv) | 10 | 35 |
| [SEFR0.1](SEFR0.1.csv) | 9 | 35 |
| [SEFR0.2](SEFR0.2.csv) | 11 | 35 |
| [SEFR0.3](SEFR0.3.csv) | 4 | 35 |

To regenerate both workbooks' exports, install `openpyxl` and run:

```sh
python3 02_corpus_metadata_construction/scripts/export_workbooks_to_csv.py
```

Run the command from the repository root.
