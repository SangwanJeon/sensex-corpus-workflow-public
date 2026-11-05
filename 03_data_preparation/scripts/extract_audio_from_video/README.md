# Audio Extraction and Conversion

[`convert_media_audio.py`](convert_media_audio.py) converts one selected media file using FFmpeg. The [video tutorial](clip_vid_tutorial__extract_audio_from_video.mp4) demonstrates audio extraction.

## Requirements

Python 3 and FFmpeg available on `PATH`. No additional Python packages are required.

## Instructions

1. Open a terminal in the directory containing the media to convert. The script lists files in the **current working directory**, not automatically the script directory, and does not search subdirectories.
2. Run the script using its full path, or run the following from this script directory after placing a working copy of your media here:

```sh
python3 convert_media_audio.py
```

3. Enter a positive file number from the displayed list.
4. Select `1` for MP3, `2` for WAV, or type another FFmpeg-supported output format.

The output is written beside the input with the same stem and a different extension. WAV output is PCM, 16-bit, 44.1 kHz, mono. MP3 output uses 192 kb/s; the WAV sample-rate and channel settings are not applied to MP3 or custom formats.

## Limits

Existing output files can be overwritten without confirmation. Selecting the same output extension as the input produces the same input/output path and fails in FFmpeg. Use a working copy and check the output before linking it to an EAF. The script does not record a conversion manifest.
