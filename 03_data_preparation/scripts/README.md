# Data Preparation Scripts

Choose the operation needed for your source material. These tools are separate utilities rather than a single automatic pipeline.

| Directory | Operation |
| --- | --- |
| [`extract_audio_from_video/`](extract_audio_from_video/README.md) | Convert a selected media file to WAV, MP3, or another audio format. Includes the audio extraction video tutorial. |
| [`extract_excerpts/`](extract_excerpts/README.md) | Copy whole recordings or extract time-bounded media excerpts and write a provenance manifest. |
| [`automatic_speech_recognition/`](automatic_speech_recognition/README.md) | Generate draft transcripts with faster-whisper or the optional WhisperX branch. |
| [`convert_trs2eaf/`](convert_trs2eaf/README.md) | Convert Transcriber/ESLO TRS files into speaker-based ELAN EAF annotations. |
| [`prepare_twitch_data/`](prepare_twitch_data/README.md) | Retrieve Twitch media/chat, prepare HTML timelines, and enrich EAF files. Emote textualization remains under development. |

Follow the README in the selected directory for dependencies, commands, outputs, and limitations. Preserve source timestamps when coordinating media excerpts with EAF annotations.
