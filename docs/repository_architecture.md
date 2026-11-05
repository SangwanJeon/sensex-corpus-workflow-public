# Sens-Ex Corpus Workflow Public — Repository Architecture

Architecture snapshot: 2026-11-05, checked against public repository commit `377eee3b5e71b84ed7985a5e1d622c672041d7b5` plus this architecture document and its README entry. GitHub links below follow `main` and therefore show its latest contents once changes are published. File counts describe the checked snapshot; links use the public origin URL and URL-encoded filenames.

Repository: **Sens-Ex Corpus Workflow — <https://github.com/SangwanJeon/sensex-corpus-workflow-public>**. Start with the Project Overview and Research Context — <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/README.md>. The repository is public; these links can be opened without access to the private archive.

## Purpose and Workflow

The repository preserves and documents the technical and methodological resources used to construct the Sens-Ex multimodal computer-mediated communication corpus. Its five stages organize collection, metadata construction, preparation, automatic NLP, and manual annotation revision.

Participatory identification, evaluation, perception-based investigation, and selection of materials belong to the broader research framework. The technical workflow documented here starts with collection. Metadata construction supports later stages, and preparation tasks vary by source and available formats; this is not a single mandatory, fully automated pipeline.

| Stage — GitHub directory | Main role | Principal resources or artifacts |
| --- | --- | --- |
| 01 — Data Collection<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/01_data_collection> | Collect source materials | Collection tutorials and demonstration video |
| 02 — Corpus Metadata Construction<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/02_corpus_metadata_construction> | Describe corpus items and survey context | Metadata dictionary, XLSX inventories, CSV views, retrieval/export scripts |
| 03 — Data Preparation<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/03_data_preparation> | Prepare media and linguistic representations | Media utilities, transcripts, ELAN EAF preparation and annotation guidance |
| 04 — Automatic Morphosyntactic Annotation and Dependency Parsing<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/04_automatic_morphosyntactic_nlp> | Generate automatic annotation drafts | EAF/TXT converters producing CoNLL-U with spaCy and/or Stanza |
| 05 — Manual Morphosyntactic and UD Syntactic Revision<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/05_manual_ud_revision> | Revise annotations and retain versions | ArboratorGrew guidance, automatic baseline, and exported annotator revisions |

## Directory Tree

The tree includes all 27 stage directories/subdirectories and the architecture documentation added here. The complete file inventory below lists exact filenames and full GitHub URLs.

```text
sensex-corpus-workflow-public/
├── README.md
├── .gitignore
├── docs/
│   └── repository_architecture.md
├── 01_data_collection/
│   └── tutorials/
├── 02_corpus_metadata_construction/
│   ├── metadata_dictionary/
│   ├── metadata_workbooks/
│   │   └── csv/
│   ├── pilot_survey/
│   │   └── csv/
│   └── scripts/
├── 03_data_preparation/
│   ├── tutorials/
│   └── scripts/
│       ├── automatic_speech_recognition/
│       ├── convert_trs2eaf/
│       ├── extract_audio_from_video/
│       ├── extract_excerpts/
│       └── prepare_twitch_data/
├── 04_automatic_morphosyntactic_nlp/
│   └── scripts/
│       ├── elan_to_conllu/
│       └── txt_to_conllu/
└── 05_manual_ud_revision/
    ├── tutorials/
    └── samples/
        ├── auto/
        ├── annotator_revision_1/
        └── annotator_revision_2/
```

Local Git metadata, virtual environments, and IDE settings are outside the corpus workflow architecture. Ignored media directories are described separately below rather than presented as published resources.

## Complete Stage Directory Guide

Each entry pairs a descriptive title with the full, clickable GitHub URL. Its README, where present, contains detailed instructions.

### 01 — Data Collection

GitHub URL: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/01_data_collection>

Path: `01_data_collection/`. Tutorials for collecting and processing audiovisual and interactional materials from CMC platforms.

| Subdirectory title — GitHub link | Relative path within this stage | Contents and role |
| --- | --- | --- |
| CMC Multimedia Collection Tutorials<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/01_data_collection/tutorials> | `tutorials/` | English and French PDF tutorials and the VideoProc Vlogger demonstration video. |

Key resources: English CMC Multimedia Processing Tutorial — <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/01_data_collection/tutorials/Tutorial%20for%20processing%20CMC%20multimedia%20data.pdf>; French CMC Multimedia Processing Tutorial — <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/01_data_collection/tutorials/Tutorial%20for%20processing%20CMC%20multimedia%20data_FR.pdf>; VideoProc Vlogger Demonstration — <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/01_data_collection/tutorials/clip_vid_tutorial_videoprocvlogger.mp4>.

### 02 — Corpus Metadata Construction

GitHub URL: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/02_corpus_metadata_construction>

Path: `02_corpus_metadata_construction/`. Metadata definitions, corpus inventories, production/platform information, semiotic descriptions, and pilot perception-survey results.

| Subdirectory title — GitHub link | Relative path within this stage | Contents and role |
| --- | --- | --- |
| Metadata Dictionary<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/02_corpus_metadata_construction/metadata_dictionary> | `metadata_dictionary/` | PDF defining 34 metadata fields and describing annotation conventions. |
| Corpus Metadata Workbooks<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/02_corpus_metadata_construction/metadata_workbooks> | `metadata_workbooks/` | The dated French metadata workbook, containing 93 records across six populated worksheets. |
| Corpus Metadata CSV Exports<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/02_corpus_metadata_construction/metadata_workbooks/csv> | `metadata_workbooks/csv/` | Six worksheet exports: SEFR0.0, SEFR0.1, SEFR0.2, SEFR0.3, SEFR1.0, and SEFR2.0. |
| Pilot Sociolinguistic Survey<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/02_corpus_metadata_construction/pilot_survey> | `pilot_survey/` | Historical French/Italian inventories, pilot records, 2025 survey aggregates, and filename mappings. |
| Pilot Survey CSV Exports<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/02_corpus_metadata_construction/pilot_survey/csv> | `pilot_survey/csv/` | Five worksheet exports: PilotSurveyColumns, corpus1.0_fr, corpus1.0_it, corpus0.0, and Sheet1. |
| Metadata Retrieval and Export Scripts<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/02_corpus_metadata_construction/scripts> | `scripts/` | Twitch clip-to-VOD metadata retrieval and reproducible workbook-to-CSV export. |

Key resources: Sens-Ex Metadata Dictionary — <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/metadata_dictionary/sensex_metadata_set.pdf>; Metadata Workbook — 2026-08-30 — <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/metadata_workbooks/sensex_metadata_ver_20260830.xlsx>; Pilot Sociolinguistic Survey Workbook — <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/pilot_survey/sociolinguistic_pilot_survey_results.xlsx>.

Scripts: Workbook-to-CSV Export — <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/scripts/export_workbooks_to_csv.py> and Twitch Clip-to-VOD Metadata Retrieval — <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/scripts/twitch_clip_to_vod.py>. XLSX files remain editable sources; CSV files provide GitHub-readable worksheet views. Preliminary excessiveness judgments and survey results are distinct metadata.

### 03 — Data Preparation

GitHub URL: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/03_data_preparation>

Path: `03_data_preparation/`. Media preparation, draft/manual transcription, ELAN annotation, transcription standardization, manual illocutionary segmentation, and Twitch chat integration.

| Subdirectory title — GitHub link | Relative path within this stage | Contents and role |
| --- | --- | --- |
| Sens-Ex ELAN Tutorial<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/03_data_preparation/tutorials> | `tutorials/` | The ELAN tutorial in PDF and DOCX, covering media linking, tiers, transcription, annotation, and export. |
| Data Preparation Script Index<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/03_data_preparation/scripts> | `scripts/` | Instructions linking the five separate preparation utilities; these do not form a mandatory automatic sequence. |
| Automatic Speech Recognition<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/03_data_preparation/scripts/automatic_speech_recognition> | `scripts/automatic_speech_recognition/` | Batch draft transcription with faster-whisper and an optional WhisperX branch, with documented compatibility limits. |
| Transcriber TRS to ELAN EAF<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/03_data_preparation/scripts/convert_trs2eaf> | `scripts/convert_trs2eaf/` | TRS conversion, speaker-tier mappings, and optional excerpt conversion with times rebased to zero. |
| Audio Extraction and Conversion<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/03_data_preparation/scripts/extract_audio_from_video> | `scripts/extract_audio_from_video/` | FFmpeg-based audio conversion and its demonstration video; WAV output uses 44.1 kHz, mono, 16-bit PCM. |
| Media Excerpt Extraction<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/03_data_preparation/scripts/extract_excerpts> | `scripts/extract_excerpts/` | The extraction script and README only. Other local recordings, excerpts, manifests, and supplementary documents are ignored. |
| Twitch Data Preparation<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/03_data_preparation/scripts/prepare_twitch_data> | `scripts/prepare_twitch_data/` | VOD/chat acquisition, transcription, four-column HTML preparation, EAF enrichment, and emote inventory. Emote textualization remains work in progress. |

Key tutorial: ELAN for Sens-Ex Corpus Preparation — PDF — <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/tutorials/Short%20ELAN%20tutorial_v3.pdf> and ELAN for Sens-Ex Corpus Preparation — DOCX — <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/tutorials/Short%20ELAN%20tutorial_v3.docx>.

Preparation scripts support distinct operations. Manual transcription revision, minimal orthographic standardization, and illocutionary-unit segmentation remain methodological interventions. Excerpt-relative and original-recording timestamps must be distinguished when linking media, transcripts, and EAF annotations.

### 04 — Automatic Morphosyntactic Annotation and Dependency Parsing

GitHub URL: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/04_automatic_morphosyntactic_nlp>

Path: `04_automatic_morphosyntactic_nlp/`. French automatic NLP and basic dependency annotation exported as CoNLL-U drafts from EAF or tier-prefixed TXT inputs.

| Subdirectory title — GitHub link | Relative path within this stage | Contents and role |
| --- | --- | --- |
| Automatic NLP Script Documentation<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/04_automatic_morphosyntactic_nlp/scripts> | `scripts/` | Overview and comparison of the two converters, libraries, input conventions, and output limitations. |
| ELAN EAF to CoNLL-U<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/04_automatic_morphosyntactic_nlp/scripts/elan_to_conllu> | `scripts/elan_to_conllu/` | EAF converter and instructions; retains source tier and parent-annotation timing metadata. |
| Tier-Prefixed TXT to CoNLL-U<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/04_automatic_morphosyntactic_nlp/scripts/txt_to_conllu> | `scripts/txt_to_conllu/` | TXT converter and instructions; expects a tier identifier followed by transcript text on each line. |

Scripts: EAF Annotation Converter — <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/04_automatic_morphosyntactic_nlp/scripts/elan_to_conllu/elan_to_conllu_all.py> and Tier-Prefixed TXT Converter — <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/04_automatic_morphosyntactic_nlp/scripts/txt_to_conllu/txt_to_conllu.py>.

These scripts process existing segmentation, including explicit `//` subdivisions, and generate preliminary annotations. Model language is currently fixed to French. Tokenization, CoNLL-U structure, dependency graphs, and linguistic analyses require verification before manual-revision handoff.

### 05 — Manual Morphosyntactic and UD Syntactic Revision

GitHub URL: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/05_manual_ud_revision>

Path: `05_manual_ud_revision/`. ArboratorGrew-based manual revision of automatic annotations and exported annotation sets; includes an experimental SUD coconstruction proposal.

| Subdirectory title — GitHub link | Relative path within this stage | Contents and role |
| --- | --- | --- |
| Manual Annotation Tutorial Overview<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/05_manual_ud_revision/tutorials> | `tutorials/` | Scope and resources for the French tutorial: automatic NLP, CoNLL-U import, manual annotation, and the SUD trial. The tutorial file itself is not yet present. |
| Automatic and Revised Annotation Samples<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/05_manual_ud_revision/samples> | `samples/` | Organization of automatic baselines and the two annotators’ exported revision sets. |
| Automatic Annotation Baseline<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/05_manual_ud_revision/samples/auto> | `samples/auto/` | 34 standard-named CoNLL-U files, SEFR2001 through SEFR2034, before manual revision. |
| Annotation Revision — Annotator 1<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/05_manual_ud_revision/samples/annotator_revision_1> | `samples/annotator_revision_1/` | 36 CoNLL-U exports: 34 standard SEFR files plus two supplementary exports named for SEFR2001 and SEFR2034. |
| Annotation Revision — Annotator 2<br><https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/05_manual_ud_revision/samples/annotator_revision_2> | `samples/annotator_revision_2/` | 11 CoNLL-U exports: nine standard SEFR files (SEFR2026–SEFR2034) plus two supplementary exports named for SEFR2001 and SEFR2034. Its README describes coverage of 10 samples. |

The three sample directories retain separate annotation versions. Counts refer to exported files, not necessarily distinct source samples: the two `merci-de-dupliquer-vos-annotations-dans-...` exports in each revision set are separately named artifacts and are not silently merged with the standard SEFR files.

The tutorial overview describes experimental SUD coconstruction encoding; this does not establish corpus-wide adoption of that proposal. The annotation framework and review status should accompany each exported set.

## Public Scope and Missing Resources

The public snapshot has its own Git history. As documented in the root README, earlier audio recordings and internal audit documents are excluded. Public pilot metadata omit student contributor names, institutional sharing fields, and historical filenames containing student names. Original working records and historical commits remain private.

The stage 05 tutorial directory contains only its README; the tutorial file has not yet been added. Stage 04's README mentions `docs/AUDIT_04.md`, but that audit is absent from this public repository. This architecture document does not imply that those missing files are publicly available.

The tracked `.gitignore` excludes macOS `.DS_Store` files, DOCX files under stage 02, and everything in `03_data_preparation/scripts/extract_excerpts/` except its Python script and README. Generated media, EAF annotations, transcripts, HTML timelines, and manifests described in usage instructions are processing artifacts, not included files unless explicitly listed in the inventory below.

## Architecture Documentation

[repository_architecture.md](https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/docs/repository_architecture.md) is this public repository's architecture guide. The root README links to it. Internal audit documents from the private archive are outside its inventory.

## Connections Between Stages

| Connection | Artifacts and interpretation |
| --- | --- |
| Collection → metadata construction and preparation | Source media, platform URLs, source identifiers, and collection context support metadata records and subsequent media/transcript work. |
| Metadata ↔ later stages | Item identifiers, language, source locations, time boundaries, and annotation context support traceability; historical filename mappings and inconsistent identifiers need review. |
| Preparation → automatic NLP | Reviewed and manually segmented EAF annotations, or explicitly prepared tier-prefixed TXT, supply linguistic input. Generic ASR TXT is not automatically compatible with the TXT converter schema. |
| Automatic NLP → manual revision | Automatic `.conllu` drafts form the baseline; the selected samples are retained under `05_manual_ud_revision/samples/auto/`. |
| Manual revision → retained annotation exports | ArboratorGrew exports are retained separately in the two annotator revision directories, allowing comparison with the baseline. File presence does not itself establish validation. |

This document describes repository organization and intended artifact relationships. It does not establish that every available script was run on every sample, resolve known audit findings, or certify the linguistic correctness of exported annotations.

## Complete File Inventory

This inventory contains **141 files**: 1 `(no extension)`, 81 `.conllu`, 11 `.csv`, 1 `.docx`, 27 `.md`, 2 `.mp4`, 4 `.pdf`, 12 `.py`, 2 `.xlsx`. Every tracked file is listed, together with this newly added document. Directory headings link to GitHub directory views; file links open GitHub file views. Descriptive README titles are taken from their first heading. Other entries use exact filenames.

### Repository root

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `.gitignore` | Git exclusion rules | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/.gitignore> |
| `README.md` | Sens-Ex Corpus Workflow | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/README.md> |

### 01_data_collection/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/01_data_collection>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | 01 — Data Collection | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/01_data_collection/README.md> |

### 01_data_collection/tutorials/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/01_data_collection/tutorials>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `Tutorial for processing CMC multimedia data.pdf` | PDF document | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/01_data_collection/tutorials/Tutorial%20for%20processing%20CMC%20multimedia%20data.pdf> |
| `Tutorial for processing CMC multimedia data_FR.pdf` | PDF document | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/01_data_collection/tutorials/Tutorial%20for%20processing%20CMC%20multimedia%20data_FR.pdf> |
| `clip_vid_tutorial_videoprocvlogger.mp4` | Video tutorial | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/01_data_collection/tutorials/clip_vid_tutorial_videoprocvlogger.mp4> |

### 02_corpus_metadata_construction/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/02_corpus_metadata_construction>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | 02 — Corpus Metadata Construction | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/README.md> |

### 02_corpus_metadata_construction/metadata_dictionary/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/02_corpus_metadata_construction/metadata_dictionary>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | Metadata Dictionary | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/metadata_dictionary/README.md> |
| `sensex_metadata_set.pdf` | PDF document | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/metadata_dictionary/sensex_metadata_set.pdf> |

### 02_corpus_metadata_construction/metadata_workbooks/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/02_corpus_metadata_construction/metadata_workbooks>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | Metadata Workbooks | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/metadata_workbooks/README.md> |
| `sensex_metadata_ver_20260830.xlsx` | Excel workbook | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/metadata_workbooks/sensex_metadata_ver_20260830.xlsx> |

### 02_corpus_metadata_construction/metadata_workbooks/csv/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/02_corpus_metadata_construction/metadata_workbooks/csv>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | CSV exports | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/metadata_workbooks/csv/README.md> |
| `SEFR0.0.csv` | Worksheet CSV export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/metadata_workbooks/csv/SEFR0.0.csv> |
| `SEFR0.1.csv` | Worksheet CSV export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/metadata_workbooks/csv/SEFR0.1.csv> |
| `SEFR0.2.csv` | Worksheet CSV export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/metadata_workbooks/csv/SEFR0.2.csv> |
| `SEFR0.3.csv` | Worksheet CSV export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/metadata_workbooks/csv/SEFR0.3.csv> |
| `SEFR1.0.csv` | Worksheet CSV export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/metadata_workbooks/csv/SEFR1.0.csv> |
| `SEFR2.0.csv` | Worksheet CSV export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/metadata_workbooks/csv/SEFR2.0.csv> |

### 02_corpus_metadata_construction/pilot_survey/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/02_corpus_metadata_construction/pilot_survey>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | Pilot Sociolinguistic Survey Results | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/pilot_survey/README.md> |
| `sociolinguistic_pilot_survey_results.xlsx` | Excel workbook | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/pilot_survey/sociolinguistic_pilot_survey_results.xlsx> |

### 02_corpus_metadata_construction/pilot_survey/csv/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/02_corpus_metadata_construction/pilot_survey/csv>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `PilotSurveyColumns.csv` | Worksheet CSV export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/pilot_survey/csv/PilotSurveyColumns.csv> |
| `README.md` | CSV exports | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/pilot_survey/csv/README.md> |
| `Sheet1.csv` | Worksheet CSV export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/pilot_survey/csv/Sheet1.csv> |
| `corpus0.0.csv` | Worksheet CSV export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/pilot_survey/csv/corpus0.0.csv> |
| `corpus1.0_fr.csv` | Worksheet CSV export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/pilot_survey/csv/corpus1.0_fr.csv> |
| `corpus1.0_it.csv` | Worksheet CSV export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/pilot_survey/csv/corpus1.0_it.csv> |

### 02_corpus_metadata_construction/scripts/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/02_corpus_metadata_construction/scripts>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | Metadata Scripts | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/scripts/README.md> |
| `export_workbooks_to_csv.py` | Python script | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/scripts/export_workbooks_to_csv.py> |
| `twitch_clip_to_vod.py` | Python script | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/02_corpus_metadata_construction/scripts/twitch_clip_to_vod.py> |

### 03_data_preparation/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/03_data_preparation>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | 03 — Data Preparation | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/README.md> |

### 03_data_preparation/scripts/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/03_data_preparation/scripts>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | Data Preparation Scripts | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/scripts/README.md> |

### 03_data_preparation/scripts/automatic_speech_recognition/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/03_data_preparation/scripts/automatic_speech_recognition>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | Automatic Speech Recognition | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/scripts/automatic_speech_recognition/README.md> |
| `asr_batch.py` | Python script | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/scripts/automatic_speech_recognition/asr_batch.py> |

### 03_data_preparation/scripts/convert_trs2eaf/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/03_data_preparation/scripts/convert_trs2eaf>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | TRS-to-EAF Conversion | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/scripts/convert_trs2eaf/README.md> |
| `trs_to_sensex_eaf_v2.py` | Python script | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/scripts/convert_trs2eaf/trs_to_sensex_eaf_v2.py> |

### 03_data_preparation/scripts/extract_audio_from_video/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/03_data_preparation/scripts/extract_audio_from_video>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | Audio Extraction and Conversion | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/scripts/extract_audio_from_video/README.md> |
| `clip_vid_tutorial__extract_audio_from_video.mp4` | Video tutorial | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/scripts/extract_audio_from_video/clip_vid_tutorial__extract_audio_from_video.mp4> |
| `convert_media_audio.py` | Python script | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/scripts/extract_audio_from_video/convert_media_audio.py> |

### 03_data_preparation/scripts/extract_excerpts/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/03_data_preparation/scripts/extract_excerpts>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | Media Excerpt Extraction | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/scripts/extract_excerpts/README.md> |
| `extract_excerpts.py` | Python script | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/scripts/extract_excerpts/extract_excerpts.py> |

### 03_data_preparation/scripts/prepare_twitch_data/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/03_data_preparation/scripts/prepare_twitch_data>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | Twitch Data Preparation | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/scripts/prepare_twitch_data/README.md> |
| `build_emote_dict.py` | Python script | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/scripts/prepare_twitch_data/build_emote_dict.py> |
| `extract_twitch.py` | Python script | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/scripts/prepare_twitch_data/extract_twitch.py> |
| `html2eaf.py` | Python script | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/scripts/prepare_twitch_data/html2eaf.py> |
| `prepare_twitch_html_for_eaf.py` | Python script | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/scripts/prepare_twitch_data/prepare_twitch_html_for_eaf.py> |

### 03_data_preparation/tutorials/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/03_data_preparation/tutorials>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `Short ELAN tutorial_v3.docx` | Word document | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/tutorials/Short%20ELAN%20tutorial_v3.docx> |
| `Short ELAN tutorial_v3.pdf` | PDF document | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/03_data_preparation/tutorials/Short%20ELAN%20tutorial_v3.pdf> |

### 04_automatic_morphosyntactic_nlp/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/04_automatic_morphosyntactic_nlp>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | 04 — Automatic Morphosyntactic Annotation and Dependency Parsing | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/04_automatic_morphosyntactic_nlp/README.md> |

### 04_automatic_morphosyntactic_nlp/scripts/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/04_automatic_morphosyntactic_nlp/scripts>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | 04 — Automatic Morphosyntactic Annotation and Dependency Parsing | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/04_automatic_morphosyntactic_nlp/scripts/README.md> |

### 04_automatic_morphosyntactic_nlp/scripts/elan_to_conllu/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/04_automatic_morphosyntactic_nlp/scripts/elan_to_conllu>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | ELAN EAF to CoNLL-U | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/04_automatic_morphosyntactic_nlp/scripts/elan_to_conllu/README.md> |
| `elan_to_conllu_all.py` | Python script | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/04_automatic_morphosyntactic_nlp/scripts/elan_to_conllu/elan_to_conllu_all.py> |

### 04_automatic_morphosyntactic_nlp/scripts/txt_to_conllu/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/04_automatic_morphosyntactic_nlp/scripts/txt_to_conllu>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | TXT to CoNLL-U | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/04_automatic_morphosyntactic_nlp/scripts/txt_to_conllu/README.md> |
| `txt_to_conllu.py` | Python script | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/04_automatic_morphosyntactic_nlp/scripts/txt_to_conllu/txt_to_conllu.py> |

### 05_manual_ud_revision/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/05_manual_ud_revision>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | 05 — Manual Morphosyntactic and UD Syntactic Revision | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/README.md> |

### 05_manual_ud_revision/samples/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/05_manual_ud_revision/samples>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | Automatic and Revised Annotation Samples | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/README.md> |

### 05_manual_ud_revision/samples/annotator_revision_1/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/05_manual_ud_revision/samples/annotator_revision_1>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | Annotation Revision — Annotator 1 | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/README.md> |
| `SEFR2001.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2001.conllu> |
| `SEFR2002.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2002.conllu> |
| `SEFR2003.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2003.conllu> |
| `SEFR2004.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2004.conllu> |
| `SEFR2005.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2005.conllu> |
| `SEFR2006.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2006.conllu> |
| `SEFR2007.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2007.conllu> |
| `SEFR2008.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2008.conllu> |
| `SEFR2009.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2009.conllu> |
| `SEFR2010.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2010.conllu> |
| `SEFR2011.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2011.conllu> |
| `SEFR2012.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2012.conllu> |
| `SEFR2013.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2013.conllu> |
| `SEFR2014.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2014.conllu> |
| `SEFR2015.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2015.conllu> |
| `SEFR2016.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2016.conllu> |
| `SEFR2017.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2017.conllu> |
| `SEFR2018.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2018.conllu> |
| `SEFR2019.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2019.conllu> |
| `SEFR2020.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2020.conllu> |
| `SEFR2021.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2021.conllu> |
| `SEFR2022.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2022.conllu> |
| `SEFR2023.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2023.conllu> |
| `SEFR2024.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2024.conllu> |
| `SEFR2025.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2025.conllu> |
| `SEFR2026.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2026.conllu> |
| `SEFR2027.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2027.conllu> |
| `SEFR2028.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2028.conllu> |
| `SEFR2029.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2029.conllu> |
| `SEFR2030.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2030.conllu> |
| `SEFR2031.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2031.conllu> |
| `SEFR2032.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2032.conllu> |
| `SEFR2033.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2033.conllu> |
| `SEFR2034.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/SEFR2034.conllu> |
| `merci-de-dupliquer-vos-annotations-dans-SEFR2001.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/merci-de-dupliquer-vos-annotations-dans-SEFR2001.conllu> |
| `merci-de-dupliquer-vos-annotations-dans-SEFR2034.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_1/merci-de-dupliquer-vos-annotations-dans-SEFR2034.conllu> |

### 05_manual_ud_revision/samples/annotator_revision_2/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/05_manual_ud_revision/samples/annotator_revision_2>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | Annotation Revision — Annotator 2 | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_2/README.md> |
| `SEFR2026.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_2/SEFR2026.conllu> |
| `SEFR2027.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_2/SEFR2027.conllu> |
| `SEFR2028.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_2/SEFR2028.conllu> |
| `SEFR2029.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_2/SEFR2029.conllu> |
| `SEFR2030.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_2/SEFR2030.conllu> |
| `SEFR2031.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_2/SEFR2031.conllu> |
| `SEFR2032.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_2/SEFR2032.conllu> |
| `SEFR2033.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_2/SEFR2033.conllu> |
| `SEFR2034.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_2/SEFR2034.conllu> |
| `merci-de-dupliquer-vos-annotations-dans-SEFR2001.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_2/merci-de-dupliquer-vos-annotations-dans-SEFR2001.conllu> |
| `merci-de-dupliquer-vos-annotations-dans-SEFR2034.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/annotator_revision_2/merci-de-dupliquer-vos-annotations-dans-SEFR2034.conllu> |

### 05_manual_ud_revision/samples/auto/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/05_manual_ud_revision/samples/auto>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | Automatic Baseline | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/README.md> |
| `SEFR2001.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2001.conllu> |
| `SEFR2002.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2002.conllu> |
| `SEFR2003.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2003.conllu> |
| `SEFR2004.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2004.conllu> |
| `SEFR2005.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2005.conllu> |
| `SEFR2006.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2006.conllu> |
| `SEFR2007.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2007.conllu> |
| `SEFR2008.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2008.conllu> |
| `SEFR2009.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2009.conllu> |
| `SEFR2010.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2010.conllu> |
| `SEFR2011.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2011.conllu> |
| `SEFR2012.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2012.conllu> |
| `SEFR2013.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2013.conllu> |
| `SEFR2014.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2014.conllu> |
| `SEFR2015.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2015.conllu> |
| `SEFR2016.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2016.conllu> |
| `SEFR2017.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2017.conllu> |
| `SEFR2018.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2018.conllu> |
| `SEFR2019.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2019.conllu> |
| `SEFR2020.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2020.conllu> |
| `SEFR2021.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2021.conllu> |
| `SEFR2022.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2022.conllu> |
| `SEFR2023.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2023.conllu> |
| `SEFR2024.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2024.conllu> |
| `SEFR2025.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2025.conllu> |
| `SEFR2026.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2026.conllu> |
| `SEFR2027.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2027.conllu> |
| `SEFR2028.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2028.conllu> |
| `SEFR2029.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2029.conllu> |
| `SEFR2030.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2030.conllu> |
| `SEFR2031.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2031.conllu> |
| `SEFR2032.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2032.conllu> |
| `SEFR2033.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2033.conllu> |
| `SEFR2034.conllu` | CoNLL-U annotation export | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/samples/auto/SEFR2034.conllu> |

### 05_manual_ud_revision/tutorials/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/05_manual_ud_revision/tutorials>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `README.md` | Tutorials | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/05_manual_ud_revision/tutorials/README.md> |

### docs/

Directory: <https://github.com/SangwanJeon/sensex-corpus-workflow-public/tree/main/docs>

| Exact filename | Document title or file type | GitHub URL |
| --- | --- | --- |
| `repository_architecture.md` | Public repository architecture and complete file inventory | <https://github.com/SangwanJeon/sensex-corpus-workflow-public/blob/main/docs/repository_architecture.md> |
