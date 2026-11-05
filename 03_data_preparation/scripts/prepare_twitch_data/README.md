# Twitch Data Preparation

**Work in progress:** Twitch emote textualization currently has unresolved issues, and work is ongoing. Check emote order, identity, labels, and preservation in the original HTML, prepared HTML, and EAF before treating outputs as validated corpus annotations.

## Scripts

| Script | Purpose |
| --- | --- |
| [`extract_twitch.py`](extract_twitch.py) | Retrieve a VOD and full chat, extract audio, transcribe with WhisperX, and export full/sample CSVs and HTML. |
| [`prepare_twitch_html_for_eaf.py`](prepare_twitch_html_for_eaf.py) | Build a four-column `time,text,author,message` HTML timeline from full chat HTML and a full transcription CSV; preserve independent speech/chat rows and write pseudonym mappings. |
| [`html2eaf.py`](html2eaf.py) | Estimate an offset from matching speech annotations, then add speech and per-user chat tiers to an existing EAF. |
| [`build_emote_dict.py`](build_emote_dict.py) | Build a JSON inventory of recognized numeric Twitch emote IDs found in HTML images. This inventory is not automatically consumed by `html2eaf.py`. |

## Requirements

For HTML preparation, the emote dictionary, and EAF enrichment:

```sh
python3 -m pip install pandas beautifulsoup4 lxml pympi-ling rapidfuzz num2words
```

The extraction script additionally imports `matplotlib`, `torch`, and `whisperx`, and invokes FFmpeg, FFprobe, yt-dlp, and TwitchDownloaderCLI. Use an environment compatible with those packages; versions are not pinned. Downloads and model inference were not exercised in the audit.

## 1. Retrieve media, chat, and transcription

Edit the configuration at the top of `extract_twitch.py` before running it:

- Set `VIDEO_URL`, `LANGUAGE`, and `SAMPLE_START`/`SAMPLE_END`; set both sample bounds to `None` for a full-only run.
- Set `TWITCHDOWNLOADER_CLI` to your executable. Its default points to `tools/TwitchDownloaderCLI`, which is not supplied here.
- Review `TWITCH_COOKIES_FROM_BROWSER` (currently `chrome`), authentication settings, model settings, and reuse switches for your environment. Keep actual credentials outside versioned files.

```sh
python3 extract_twitch.py
```

Outputs are organized under `twitch_archive/<title>__<vod_id>/`, with `downloads/`, `chat/`, `results/`, and `vod_metadata.json`. Full chat is named `chat_full.html`; the full transcription is `twitch_full_transcription.csv` with `time,text` columns. Select the actual generated paths for the next command.

The older merged HTML uses `time,author,message,text`, may lose speech not near chat, and uses excerpt-relative times for samples. **Do not pass it directly to `html2eaf.py`.** Its pseudonymization and emote handling also have known limitations.

## 2. Prepare the four-column HTML

Use the original **full** chat HTML and **full** transcription CSV, whose times refer to the same VOD:

```sh
python3 prepare_twitch_html_for_eaf.py /path/to/chat_full.html /path/to/twitch_full_transcription.csv /path/to/prepared.html --start 00:27:46 --end 00:28:58 --broadcaster STREAMER_USERNAME
```

Replace all paths and the username. `--broadcaster` can be repeated. Alternatively, `--merged-csv /path/to/twitch_HH-MM-SS_HH-MM-SS_merged_output.csv` infers the window from the **filename**, not its data; explicit `--start` and `--end` take precedence.

Prepared HTML retains **absolute VOD timestamps**, separate speech/chat rows, and image markup. It writes `_anonymization_map.csv` and `_anonymization_map.json` beside the output unless overridden with `--mapping-csv` and `--mapping-json`. These maps contain original identities: the operation is reversible pseudonymization, despite the option names.

## 3. Enrich an existing EAF

Use an EAF containing matching speech and a populated extraction-window tier (`default`) or other timed annotations. Recognized speech anchors include `SP1_verbal`, `SP2_verbal`, `SP3_verbal`, `SPEECH`, and `SPEECH_STREAMER`; the fallback selects tier names containing `verbal`. `_trs` tiers alone are not selected automatically.

```sh
python3 html2eaf.py /path/to/prepared.html /path/to/excerpt.eaf /path/to/enriched.eaf
```

The script estimates the offset by fuzzy matching speech, rebases the HTML times onto the EAF timeline, and adds `STREAMER_HTML` plus a tier per chat author. Inspect the reported offset and all alignments in ELAN. This is heuristic synchronization, not validated turn alignment.

`--shift 4` moves chat **later** by four seconds; `--shift -2.5` moves it earlier by 2.5 seconds. Speech is not shifted. The source comment describing a positive shift as “advance” is misleading.

## 4. Inspect emotes (optional)

```sh
python3 build_emote_dict.py /path/to/html_directory /path/to/emotes_global.json
```

## Known issues to review

- The older extractor moves emote images to the end of a message and may lose CSS-only image sources.
- Numeric-ID matching does not cover all emote source formats. Generic `{emote:u001}` labels can be reused across messages.
- `html2eaf.py` writes `{emote:ID}` tokens but currently does **not** write the emote metadata/reference tiers advertised in its header; the reconstruction metadata is discarded.
- Chat intervals are inferred from the next message by the same author, with a two-second fallback for the last message. These are not measured message-display durations. Simultaneous messages can overlap.
- New HTML preparation and the older extractor have different timestamp and column conventions. Always use the explicit preparation step above.
- Reused transcription files are not checked against changed model/language settings. Inspect cached inputs when changing configuration.
