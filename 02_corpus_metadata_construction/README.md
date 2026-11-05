# 02 — Corpus Metadata Construction

## Overview

This directory contains the metadata documentation.

The metadata were collected, documented, and manually verified by student interns and the technical coordinator, under the supervision of the Sens-Ex coordinating research team.

Three principal categories of metadata are distinguished:

1. **Production and platform-related metadata**
2. **Preliminary judgments of discursive excess documented during the identification of potential excerpts**
3. **Semiotic and communicative metadata documented by research participants (student interns and technical coordinator)**

The metadata workbooks and their CSV exports are listed below.

### 1. Production and Platform-Related Metadata

These metadata document the original audiovisual materials, their sources, and their publication contexts.

They include information such as:

- Original video title.
- Content creator or channel name.
- Source URL and platform.
- Publication and collection dates.
- Duration of the original audiovisual material.
- Start and end times of the selected excerpt.
- Platform-specific engagement metrics, where available (views, likes, shares, subscribers, etc.).

These metadata were manually checked against the available source information.

Some platform-specific information, particularly for Twitch, can also be retrieved using Python scripts and platform APIs.

### 2. Preliminary Judgments of Discursive Excess

This category documents preliminary assessments concerning the presence or absence of discursive excess in the selected materials.

These assessments are recorded separately from the results of sociolinguistic perception surveys conducted within the Sens-Ex research framework.

The results of the first sociolinguistic perception survey, conducted in 2025, are included in the historical Sens-Ex corpus 1.0 workbook described below.

### 3. Semiotic and Communicative Metadata

These metadata describe the semiotic modalities and communicative characteristics of the selected excerpts.

They include information concerning:

- The presence and characteristics of oral and written communication.
- Other semiotic modalities represented in the audiovisual materials.
- The communicative situation and interactional context.
- Relevant contextual characteristics of the discourse.

These metadata were documented under the supervision of the Sens-Ex coordinating research team.

## Available Resources

### Metadata Documentation and Workbooks

| Resource                                                                                              | Description                                                                                                                                                                                                                                                                                                          |
|-------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`sensex_metadata_ver_20260830.xlsx`](metadata_workbooks/sensex_metadata_ver_20260830.xlsx)           | Metadata workbook containing 93 records across six populated sheets corresponding to different versions of the French Sens-Ex corpus (SEFR2.0, SEFR1.0, SEFR0.0, SEFR0.1, SEFR0.2, and SEFR0.3). <br/>Six worksheet exports for viewing directly on GitHub: [Metadata CSV exports](metadata_workbooks/csv/README.md) |
| [`sociolinguistic_pilot_survey_results.xlsx`](pilot_survey/sociolinguistic_pilot_survey_results.xlsx) | Historical workbook containing French and Italian corpus inventories, pilot data, results from the first sociolinguistic perception survey conducted in 2025, and filename mappings. <br/>Five worksheet exports for viewing directly on GitHub: [Pilot survey CSV exports](pilot_survey/csv/README.md)              |
| [`sensex_metadata_set.pdf`](metadata_dictionary/sensex_metadata_set.pdf)                              | Metadata dictionary defining 34 fields used to describe the corpus materials.                                                                                                                                                                                                                                        |

**Note:** The workbooks document different stages and scopes of corpus construction. Their relationships, identifier mappings, and version histories require further documentation.

Instructions for CSV export and Twitch metadata retrieval are available in the [scripts documentation](scripts/README.md).

## Usage

1. Consult the metadata dictionary to identify the relevant metadata fields and their definitions.
2. Select the appropriate Excel workbook according to the corpus version or research dataset.
3. Verify production-related information against the original sources whenever possible.
4. Document preliminary judgments of discursive excess separately from sociolinguistic survey results.
5. Record semiotic and communicative characteristics according to the adopted metadata conventions.
6. Where necessary, use the available scripts to retrieve platform-specific information.

## Limitations

The metadata resources reflect successive stages of the Sens-Ex corpus construction process and may contain differences in coverage, field definitions, and annotation conventions.

The current audit identifies several issues requiring verification, including:

- A duplicated corpus item identifier.
- Inconsistencies between excerpt boundaries and recorded durations.
- Differences between the metadata dictionary and spreadsheet field values.
- Inconsistent representations of platform metrics and missing values.
- Incomplete documentation of relationships between corpus versions.
- Insufficient documentation of the aggregation and interpretation of the 2025 survey results.

These issues should be resolved through verification against the original materials and methodological documentation rather than through automatic normalization alone.

The Twitch metadata retrieval script also has known limitations concerning API responses, timestamp precision, and error handling.

Before public distribution, the metadata workbooks and scripts must be reviewed for personal information, API credentials, and applicable sharing permissions.
