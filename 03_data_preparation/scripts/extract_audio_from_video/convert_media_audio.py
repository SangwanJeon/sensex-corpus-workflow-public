#!/usr/bin/env python3
"""
convert_media_audio.py
Convert .mp4/.mov to .mp3 or .wav (default settings: 44100 Hz, mono, 16-bit) using ffmpeg.

"""

import shutil
import subprocess
import sys
from pathlib import Path


SUPPORTED_EXTS = {
    ".mp4", ".mov", ".m4v", ".mpeg", ".mpg", ".webm", ".mkv", ".avi",
    ".m4a", ".aac", ".flac", ".wav", ".ogg", ".mp3", ".amr"
}


def ensure_ffmpeg():
    if shutil.which("ffmpeg") is None:
        print("ERROR: ffmpeg is not installed or not in PATH.\n")
        print("Mac: brew install ffmpeg")
        print("Linux: sudo apt install ffmpeg")
        print("Windows: install ffmpeg and add it to PATH")
        sys.exit(1)


def list_media_files():
    files = [f for f in Path.cwd().iterdir()
             if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS]
    return sorted(files)


def convert_file(input_path: Path, output_format: str):
    output_path = input_path.with_suffix(f".{output_format}")

    cmd = ["ffmpeg", "-y", "-i", str(input_path), "-vn"]

    if output_format == "mp3":
        cmd += ["-acodec", "libmp3lame", "-b:a", "192k"]

    elif output_format == "wav":
        cmd += [
            "-acodec", "pcm_s16le",
            "-ar", "44100",
            "-ac", "1"
        ]

    else:
        # Generic conversion
        pass

    cmd.append(str(output_path))
    subprocess.run(cmd, check=True)

    print(f"\n✅ Conversion completed: {output_path.name}")


def main():
    ensure_ffmpeg()

    print("\n=== MEDIA AUDIO CONVERTER ===\n")

    media_files = list_media_files()

    if not media_files:
        print("No compatible media files found in this folder.")
        sys.exit(1)

    print("Available media files:\n")
    for idx, file in enumerate(media_files, start=1):
        print(f"{idx}) {file.name}")

    choice = input("\nSelect the file number to convert: ").strip()

    try:
        input_path = media_files[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        sys.exit(1)

    print("\nWhich output format do you want?")
    print("1) mp3 (compressed)")
    print("2) wav (Praat-friendly)")
    print("Or type another format manually (e.g., flac, ogg)")

    format_choice = input("Press 1, 2, or type format name: ").strip().lower()

    if format_choice == "1":
        output_format = "mp3"
    elif format_choice == "2":
        output_format = "wav"
    else:
        output_format = format_choice

    print("\nConverting...\n")
    convert_file(input_path, output_format)
    
    

if __name__ == "__main__":
    main()
