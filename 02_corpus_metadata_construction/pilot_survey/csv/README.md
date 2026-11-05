# CSV exports

Source workbook: `sociolinguistic_pilot_survey_results.xlsx` in the parent directory.

These UTF-8 CSV files contain one populated worksheet each and can be viewed on GitHub. The XLSX workbook remains the editable source. Empty worksheets and trailing empty rows/columns are omitted; interior blank cells and rows are preserved.

Dates use ISO format (`YYYY-MM-DD`); times use 24-hour `HH:MM:SS` with fractional seconds when present. Blank cells stay empty, and literal values such as `na`, category spellings, abbreviated metrics, and identifiers are preserved. Workbook formatting and annotations are not included. These exports do not correct the data-quality issues identified in the audit.

| Worksheet | Records | Columns |
| --- | --- | --- |
| [PilotSurveyColumns](PilotSurveyColumns.csv) | 32 | 27 |
| [corpus1.0_fr](corpus1.0_fr.csv) | 28 | 14 |
| [corpus1.0_it](corpus1.0_it.csv) | 24 | 9 |
| [corpus0.0](corpus0.0.csv) | 32 | 12 |
| [Sheet1](Sheet1.csv) | 30 | 2 |

To regenerate both workbooks' exports, install `openpyxl` and run:

```sh
python3 02_corpus_metadata_construction/scripts/export_workbooks_to_csv.py
```

Run the command from the repository root.
