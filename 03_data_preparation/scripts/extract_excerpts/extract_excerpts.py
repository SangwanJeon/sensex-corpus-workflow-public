#!/usr/bin/env python3
"""
extract_multimedia_interactive.py

Interactive multimedia extractor for the Sens-Ex / ESLO workflow.

Features
--------
- choose one or several media files interactively;
- supports common audio and video formats;
- choose whole-file copy or excerpt extraction per selected file;
- define excerpt boundaries as HH:MM:SS(.mmm), MM:SS(.mmm), or seconds;
- uses ffmpeg for robust audio/video cutting;
- optional stream-copy mode for fast lossless extraction;
- optional re-encoding mode for frame/sample-accurate cuts;
- predictable filenames compatible with the TRS→EAF excerpt convention:
      FILE__excerpt_HHMMSSmmm-HHMMSSmmm.ext
- can process one file or a whole directory;
- writes a CSV manifest with source/excerpt provenance.

Requirements
------------
Install ffmpeg and make sure it is available on PATH.

macOS with Homebrew:
    brew install ffmpeg

Examples
--------
Interactive directory mode:
    python3 extract_multimedia_interactive.py media/ -o excerpts/ -i

Single file:
    python3 extract_multimedia_interactive.py recording.mp4 -o excerpts/ -i

Non-interactive full-file copy:
    python3 extract_multimedia_interactive.py media/ -o copied_media/
"""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


SUPPORTED_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".flac",
    ".m4a",
    ".aac",
    ".ogg",
    ".opus",
    ".mp4",
    ".mov",
    ".mkv",
    ".webm",
    ".avi",
    ".m4v",
}


@dataclass
class ExtractionRequest:
    source_path: Path
    excerpt_start_ms: Optional[int] = None
    excerpt_end_ms: Optional[int] = None
    reencode: bool = False

    @property
    def is_excerpt(self) -> bool:
        return (
            self.excerpt_start_ms is not None
            and self.excerpt_end_ms is not None
        )


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------

def parse_time_to_ms(value: str) -> int:
    """
    Accept:
        75
        75.5
        01:15
        01:15.500
        00:01:15
        00:01:15.500
    """
    value = value.strip()
    if not value:
        raise ValueError("empty time value")

    parts = value.split(":")

    try:
        if len(parts) == 1:
            seconds = float(parts[0])

        elif len(parts) == 2:
            minutes = int(parts[0])
            seconds = minutes * 60 + float(parts[1])

        elif len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = hours * 3600 + minutes * 60 + float(parts[2])

        else:
            raise ValueError

    except ValueError:
        raise ValueError(
            f"Invalid time '{value}'. "
            "Use HH:MM:SS(.mmm), MM:SS(.mmm), or seconds."
        )

    if seconds < 0:
        raise ValueError("Time cannot be negative.")

    return int(round(seconds * 1000))


def ms_to_clock(ms: int) -> str:
    total_seconds = ms / 1000
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"


def ms_to_filename_token(ms: int) -> str:
    total_seconds, milli = divmod(ms, 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}{minutes:02d}{seconds:02d}{milli:03d}"


# ---------------------------------------------------------------------------
# ffmpeg helpers
# ---------------------------------------------------------------------------

def check_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise SystemExit(
            "ffmpeg was not found on PATH.\n"
            "On macOS with Homebrew, install it with:\n"
            "    brew install ffmpeg"
        )


def get_duration_ms(path: Path) -> Optional[int]:
    """
    Use ffprobe if available. Return None if duration cannot be read.
    """
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        return None

    cmd = [
        ffprobe,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        seconds = float(result.stdout.strip())
        return int(round(seconds * 1000))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# File selection
# ---------------------------------------------------------------------------

def iter_media_files(input_path: Path) -> Iterable[Path]:
    if input_path.is_file():
        if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported media extension: {input_path.suffix}"
            )
        yield input_path

    elif input_path.is_dir():
        for path in sorted(input_path.iterdir()):
            if (
                path.is_file()
                and path.suffix.lower() in SUPPORTED_EXTENSIONS
            ):
                yield path

    else:
        raise FileNotFoundError(input_path)


def parse_selection(selection: str, n_files: int) -> List[int]:
    """
    Parse:
        all
        1
        1,3,5
        2-5
        1,3-6,9
    """
    selection = selection.strip().lower()

    if selection in {"all", "a", "*"}:
        return list(range(n_files))

    chosen = set()

    for chunk in selection.split(","):
        chunk = chunk.strip()

        if not chunk:
            continue

        if "-" in chunk:
            left, right = chunk.split("-", 1)

            try:
                start = int(left)
                end = int(right)
            except ValueError:
                raise ValueError(f"Invalid selection part: {chunk}")

            if start > end:
                start, end = end, start

            for i in range(start, end + 1):
                if not 1 <= i <= n_files:
                    raise ValueError(
                        f"File number out of range: {i}"
                    )
                chosen.add(i - 1)

        else:
            try:
                i = int(chunk)
            except ValueError:
                raise ValueError(
                    f"Invalid selection part: {chunk}"
                )

            if not 1 <= i <= n_files:
                raise ValueError(
                    f"File number out of range: {i}"
                )

            chosen.add(i - 1)

    if not chosen:
        raise ValueError("No files selected.")

    return sorted(chosen)


def choose_files_interactively(files: List[Path]) -> List[Path]:
    print("\nAvailable multimedia files:")
    print("-" * 72)

    for i, path in enumerate(files, start=1):
        duration = get_duration_ms(path)
        duration_txt = (
            f" [{ms_to_clock(duration)}]"
            if duration is not None
            else ""
        )
        print(f"{i:>3}. {path.name}{duration_txt}")

    print("-" * 72)
    print("Choose files using e.g. 1,3,5-7 or 'all'.")

    while True:
        raw = input("Files to process: ").strip()

        if raw.lower() in {"q", "quit", "exit"}:
            raise SystemExit("Cancelled.")

        try:
            indices = parse_selection(raw, len(files))
            return [files[i] for i in indices]
        except ValueError as e:
            print(f"Invalid selection: {e}")


# ---------------------------------------------------------------------------
# Interactive prompts
# ---------------------------------------------------------------------------

def ask_yes_no(prompt: str, default: bool = False) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "

    while True:
        raw = input(prompt + suffix).strip().lower()

        if not raw:
            return default

        if raw in {"y", "yes", "o", "oui"}:
            return True

        if raw in {"n", "no", "non"}:
            return False

        print("Please answer y/yes or n/no.")


def ask_time(
    prompt: str,
    default_ms: Optional[int] = None
) -> int:
    while True:
        default_txt = (
            f" [{ms_to_clock(default_ms)}]"
            if default_ms is not None
            else ""
        )

        raw = input(
            f"{prompt}{default_txt}: "
        ).strip()

        if not raw and default_ms is not None:
            return default_ms

        try:
            return parse_time_to_ms(raw)
        except ValueError as e:
            print(e)


def build_interactive_requests(
    selected_files: List[Path],
    default_reencode: bool,
) -> List[ExtractionRequest]:

    requests: List[ExtractionRequest] = []

    print("\nExtraction configuration")
    print("=" * 72)
    print("Times accepted: HH:MM:SS(.mmm), MM:SS(.mmm), or seconds.")
    print("=" * 72)

    for path in selected_files:
        print(f"\nFile: {path.name}")

        duration_ms = get_duration_ms(path)

        if duration_ms is not None:
            print(f"Duration: {ms_to_clock(duration_ms)}")

        if not ask_yes_no(
            "Extract only an excerpt?",
            default=False,
        ):
            requests.append(
                ExtractionRequest(
                    source_path=path,
                    reencode=False,
                )
            )
            continue

        while True:
            start_ms = ask_time(
                "Excerpt start",
                default_ms=0,
            )

            end_ms = ask_time(
                "Excerpt end",
                default_ms=duration_ms,
            )

            if end_ms <= start_ms:
                print(
                    "End time must be later than start time."
                )
                continue

            if (
                duration_ms is not None
                and end_ms > duration_ms
            ):
                print(
                    f"End exceeds media duration "
                    f"({ms_to_clock(duration_ms)})."
                )

                if not ask_yes_no(
                    "Use it anyway?",
                    default=False,
                ):
                    continue

            print(
                f"Selected excerpt: "
                f"{ms_to_clock(start_ms)} -> "
                f"{ms_to_clock(end_ms)} "
                f"(duration "
                f"{ms_to_clock(end_ms - start_ms)})"
            )

            if not ask_yes_no(
                "Confirm this excerpt?",
                default=True,
            ):
                continue

            reencode = ask_yes_no(
                "Use frame/sample-accurate re-encoding?",
                default=default_reencode,
            )

            requests.append(
                ExtractionRequest(
                    source_path=path,
                    excerpt_start_ms=start_ms,
                    excerpt_end_ms=end_ms,
                    reencode=reencode,
                )
            )

            break

    return requests


# ---------------------------------------------------------------------------
# Output naming
# ---------------------------------------------------------------------------

def build_output_path(
    request: ExtractionRequest,
    output_dir: Path,
) -> Path:

    source = request.source_path

    if request.is_excerpt:
        start_token = ms_to_filename_token(
            request.excerpt_start_ms
        )
        end_token = ms_to_filename_token(
            request.excerpt_end_ms
        )

        filename = (
            f"{source.stem}"
            f"__excerpt_"
            f"{start_token}-{end_token}"
            f"{source.suffix.lower()}"
        )

    else:
        filename = source.name

    return output_dir / filename


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def copy_whole_file(
    source: Path,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(source, output_path)


def extract_excerpt(
    request: ExtractionRequest,
    output_path: Path,
) -> None:

    source = request.source_path

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    start_seconds = request.excerpt_start_ms / 1000
    duration_seconds = (
        request.excerpt_end_ms
        - request.excerpt_start_ms
    ) / 1000

    cmd = [
        "ffmpeg",
        "-y",
        "-ss", f"{start_seconds:.3f}",
        "-i", str(source),
        "-t", f"{duration_seconds:.3f}",
    ]

    if request.reencode:
        ext = source.suffix.lower()

        if ext in {
            ".wav",
            ".flac",
        }:
            cmd += ["-c:a", "pcm_s16le"]

        elif ext in {
            ".mp3",
        }:
            cmd += ["-c:a", "libmp3lame"]

        elif ext in {
            ".m4a",
            ".aac",
        }:
            cmd += ["-c:a", "aac"]

        elif ext in {
            ".ogg",
            ".opus",
        }:
            cmd += ["-c:a", "libopus"]

        else:
            # General video re-encoding.
            cmd += [
                "-c:v", "libx264",
                "-c:a", "aac",
            ]

    else:
        # Fast stream copy.
        cmd += ["-c", "copy"]

    cmd.append(str(output_path))

    subprocess.run(
        cmd,
        check=True,
    )


def process_request(
    request: ExtractionRequest,
    output_dir: Path,
) -> Path:

    output_path = build_output_path(
        request,
        output_dir,
    )

    if request.is_excerpt:
        extract_excerpt(
            request,
            output_path,
        )
    else:
        copy_whole_file(
            request.source_path,
            output_path,
        )

    return output_path


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

def write_manifest(
    rows: List[dict],
    output_dir: Path,
) -> None:

    manifest_path = (
        output_dir
        / "multimedia_extraction_manifest.csv"
    )

    fieldnames = [
        "source_file",
        "output_file",
        "mode",
        "source_start",
        "source_end",
        "source_start_ms",
        "source_end_ms",
        "duration",
        "reencoded",
    ]

    write_header = not manifest_path.exists()

    with manifest_path.open(
        "a",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )

        if write_header:
            writer.writeheader()

        writer.writerows(rows)

    print(
        f"\nManifest: {manifest_path}"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Interactively extract/copy "
            "audio and video files."
        )
    )

    p.add_argument(
        "input",
        type=Path,
        help=(
            "A media file or directory "
            "containing media files."
        ),
    )

    p.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        required=True,
        help="Output directory.",
    )

    p.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help=(
            "Interactively select files "
            "and excerpt boundaries."
        ),
    )

    p.add_argument(
        "--reencode",
        action="store_true",
        help=(
            "Default to accurate re-encoding "
            "for excerpts."
        ),
    )

    return p


def main() -> None:
    args = build_arg_parser().parse_args()

    check_ffmpeg()

    try:
        files = list(
            iter_media_files(args.input)
        )
    except (
        ValueError,
        FileNotFoundError,
    ) as e:
        raise SystemExit(str(e))

    if not files:
        raise SystemExit(
            f"No supported media files "
            f"found in: {args.input}"
        )

    args.output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    if args.interactive:
        selected = choose_files_interactively(
            files
        )

        requests = build_interactive_requests(
            selected_files=selected,
            default_reencode=args.reencode,
        )

    else:
        requests = [
            ExtractionRequest(
                source_path=path
            )
            for path in files
        ]

    if not requests:
        raise SystemExit(
            "No files scheduled for processing."
        )

    print("\nProcessing plan")
    print("=" * 72)

    for req in requests:
        if req.is_excerpt:
            print(
                f"- {req.source_path.name}: "
                f"{ms_to_clock(req.excerpt_start_ms)} "
                f"-> "
                f"{ms_to_clock(req.excerpt_end_ms)} "
                f"({'re-encode' if req.reencode else 'stream copy'})"
            )
        else:
            print(
                f"- {req.source_path.name}: "
                f"whole-file copy"
            )

    print("=" * 72)

    if (
        args.interactive
        and not ask_yes_no(
            "Start processing?",
            default=True,
        )
    ):
        raise SystemExit("Cancelled.")

    rows = []
    failed = 0

    for request in requests:
        try:
            output_path = process_request(
                request,
                args.output_dir,
            )

            if request.is_excerpt:
                duration_ms = (
                    request.excerpt_end_ms
                    - request.excerpt_start_ms
                )

                mode = "excerpt"

                start_clock = ms_to_clock(
                    request.excerpt_start_ms
                )

                end_clock = ms_to_clock(
                    request.excerpt_end_ms
                )

                duration_clock = ms_to_clock(
                    duration_ms
                )

            else:
                mode = "whole_file"
                start_clock = ""
                end_clock = ""
                duration_clock = ""
                duration_ms = None

            rows.append(
                {
                    "source_file": str(
                        request.source_path
                    ),
                    "output_file": str(
                        output_path
                    ),
                    "mode": mode,
                    "source_start": (
                        start_clock
                        if request.is_excerpt
                        else ""
                    ),
                    "source_end": (
                        end_clock
                        if request.is_excerpt
                        else ""
                    ),
                    "source_start_ms": (
                        request.excerpt_start_ms
                        if request.is_excerpt
                        else ""
                    ),
                    "source_end_ms": (
                        request.excerpt_end_ms
                        if request.is_excerpt
                        else ""
                    ),
                    "duration": (
                        duration_clock
                        if request.is_excerpt
                        else ""
                    ),
                    "reencoded": (
                        request.reencode
                        if request.is_excerpt
                        else False
                    ),
                }
            )

            print(
                f"\n[OK] "
                f"{request.source_path.name}"
            )

            print(
                f"     output: "
                f"{output_path}"
            )

        except subprocess.CalledProcessError as e:
            failed += 1

            print(
                f"\n[ERROR] ffmpeg failed "
                f"for {request.source_path}: "
                f"{e}",
                file=sys.stderr,
            )

        except Exception as e:
            failed += 1

            print(
                f"\n[ERROR] "
                f"{request.source_path}: "
                f"{e}",
                file=sys.stderr,
            )

    if rows:
        write_manifest(
            rows,
            args.output_dir,
        )

    if failed:
        raise SystemExit(
            f"{failed} file(s) failed."
        )


if __name__ == "__main__":
    main()
