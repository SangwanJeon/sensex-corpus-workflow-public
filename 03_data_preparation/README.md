# 03 — Data Preparation

## Overview

This stage covers the preparation of the audiovisual and interactional data collected for the Sens-Ex corpus, from audio extraction and transcription to ELAN annotation, discourse segmentation, and the integration of Twitch live chats.

The procedures combine automated processing using Python scripts and external tools with manual transcription, annotation, and revision according to the methodological conventions adopted for Sens-Ex.

## Directory Contents

| Directory                       | Contents                                                                                                                                                                                                                                                                                    |
|---------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`tutorials/`](tutorials/)      | The Sens-Ex ELAN tutorial, available in [PDF](tutorials/Short%20ELAN%20tutorial_v3.pdf) and [DOCX](tutorials/Short%20ELAN%20tutorial_v3.docx) formats. It provides instructions for using ELAN preparing corpus data, including the minimal orthographic transcription protocol adopted for oral transcription tiers (SPx_trs).<br/>A complementary [15-minute video tutorial](https://www.youtube.com/watch?v=k05hQ4xpRL4&t=2s) demonstrates how to create EAF files and add or edit annotation tiers in ELAN. |
| [`scripts/`](scripts/README.md) | Subdirectories for: <br/>**audio conversion**, <br/>**media excerpt extraction**, <br/>**automatic speech recognition**, <br/>**TRS-to-EAF conversion**, and <br/>**Twitch preparation**.                                                                                                   |

## Data Preparation Workflow

The preparation tasks described below should not be understood as a mandatory sequence of operations for every collected sample. Depending on the source platform, the characteristics of the collected data, the processing pipelines employed, and the available file formats, different combinations of preparation procedures may be required, while others may be unnecessary.

These complementary procedures aim to produce **standardized, consistently structured, and usable data** for subsequent transcription, annotation, and linguistic analysis.

### 1. Audio Extraction from Video Files

Audio tracks are extracted from collected MP4 video excerpts and converted into WAV files using FFmpeg.

The WAV files serve as audio references for transcription and annotation in ELAN, helping ensure accurate synchronization between the audio signal, video recordings, and time-aligned annotations.

**Resources:**

- [Audio extraction script and instructions](scripts/extract_audio_from_video/README.md).
- [Media excerpt extraction script and instructions](scripts/extract_excerpts/README.md), for cases where an excerpt must first be extracted from a longer recording.
- [FFmpeg](https://ffmpeg.org/) — an open-source multimedia framework for processing audio and video files, including format conversion, compression, filtering, and streaming. The Python scripts developed for Sens-Ex use FFmpeg to perform the underlying media-processing operations.

### 2. Manual and Automatic Speech Transcription

The speech contained in the audiovisual excerpts is transcribed manually and/or automatically.

Automatic speech recognition (ASR) is performed using Python scripts integrating speech recognition tools, particularly [Whisper](https://github.com/openai/whisper).

The automatically generated transcriptions serve as preliminary materials and require manual verification and correction before further annotation.

**Resources:**

- [`asr_batch.py`](scripts/automatic_speech_recognition/asr_batch.py) for batch automatic speech recognition; see the [ASR instructions and known limitations](scripts/automatic_speech_recognition/README.md).

### 3. Creation of ELAN Annotation Files

ELAN annotation files (`.eaf`) are created to organize and synchronize linguistic annotations with the audiovisual recordings.

The EAF files provide the annotation structure used in the subsequent stages of corpus preparation.

**Resources:**

- [ELAN annotation software](https://archive.mpi.nl/tla/elan/download): open-source annotation tool for audio and video recordings.
- Written tutorial: [Sens-Ex ELAN tutorial](tutorials/Short%20ELAN%20tutorial_v3.pdf) in the `tutorials/` directory.
- Video tutorial: [creating new annotations in ELAN | Sens-Ex project](https://www.youtube.com/watch?v=k05hQ4xpRL4&t=2s) – a complementary 15-minute tutorial demonstraing how to create EAF files and add or edit annotation tiers in ELAN.
- TRS-to_EAF conversion: [Conversion instructions](scripts/convert_trs2eaf/README.md) for generating EAF files from Transcriber (.trs) files.

### 4. Standardization and Manual Revision of Oral Transcription Tiers (SP_trs)

The verbal annotation tiers are standardized according to the transcription protocol adopted for Sens-Ex.

This procedure includes manual revision of the transcriptions to ensure a consistent representation of the spoken signal, particularly through a minimal orthographic transcription convention. 

For further details on this convention and it's application in ELAN, consult the [Sens-Ex ELAN tutorial](tutorials/Short%20ELAN%20tutorial_v3.pdf) in the `tutorials/` directory (p.8).

The aim is to obtain consistent verbal transcriptions across the corpus to facilitate subsequent morphosyntactic and prosodic annotations and analyses.


### 5. Discourse Segmentation into Illocutionary Units

The transcribed discourse represented in the verbal annotation tiers is manually segmented into **illocutionary units**.

This segmentation follows the methodological conventions adopted for Sens-Ex and is performed through manual annotation and revision in ELAN.

The resulting units provide the basis for subsequent automatic morphosyntactic annotation and dependency parsing.

### 6. Integration of Twitch Live Chats

For audiovisual excerpts collected from Twitch, the corresponding live-chat messages are integrated into the ELAN annotation files.

Python scripts support the extraction, preparation, and temporal alignment of chat messages with the audiovisual recordings.

This procedure makes it possible to represent interactions between streamers and chat participants within a shared, time-aligned annotation environment.

**Resources:**

- [Twitch preparation scripts and instructions](scripts/prepare_twitch_data/README.md)

## Output

The main outputs of this stage are ELAN annotation files (`.eaf`) containing standardized verbal transcriptions, manually segmented illocutionary units, and, where applicable, temporally aligned Twitch chat messages.

These EAF files constitute the principal input for the next stage: [04 — Automatic Morphosyntactic NLP](../04_automatic_morphosyntactic_nlp/).
