#!/usr/bin/env python3
"""
trs_to_sensex_eaf.py

Convert ESLO / Transcriber .trs files to ELAN .eaf files following the
Sens-Ex speaker-tier convention:

    ESLO speaker spk1 -> SP1_trs
    ESLO speaker spk2 -> SP2_trs
    ...

Features
--------
- preserves Turn / Sync time alignment;
- handles multi-speaker Turns using <Who nb="...">;
- creates one alignable tier per speaker;
- writes a speaker mapping CSV alongside each EAF;
- optionally keeps Transcriber <Event> information in the transcription text;
- processes one .trs file or a whole directory;
- interactive file selection from a directory;
- per-file choice between whole-file conversion and excerpt conversion;
- excerpt boundaries can be entered as HH:MM:SS(.mmm), MM:SS(.mmm), or seconds;
- excerpted EAFs are rebased to 00:00:00 for later alignment with extracted media.

Dependency
----------
    pip install pympi-ling

Examples
--------
Interactive selection + optional excerpts:
    python3 trs_to_sensex_eaf.py input_trs/ -o eaf/ --interactive

Non-interactive batch conversion (all TRS files):
    python3 trs_to_sensex_eaf.py input_trs/ -o eaf/

Single file:
    python3 trs_to_sensex_eaf.py ESLO2_ENT_1001.trs

Whole-file conversion with media linking:
    python3 trs_to_sensex_eaf.py input_trs/ -o eaf/ --media-dir audio/

NOTE ON EXCERPTS
----------------
For excerpt conversion, annotations are clipped to the requested interval and
timestamps are shifted so that the excerpt begins at 0 ms. The original full
media file is deliberately NOT linked to the excerpted EAF, because that would
be temporally misleading. A separate media-extraction script can later create
the matching audio/video excerpt using the same start/end boundaries.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

try:
    from pympi.Elan import Eaf
except ImportError:
    raise SystemExit(
        "Missing dependency 'pympi-ling'. Install it with:\n"
        "    pip install pympi-ling"
    )


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Speaker:
    trs_id: str
    trs_name: str
    sensex_id: str
    tier_id: str


@dataclass
class Segment:
    trs_speaker_id: str
    start_ms: int
    end_ms: int
    text: str


@dataclass
class ConversionRequest:
    trs_path: Path
    excerpt_start_ms: Optional[int] = None
    excerpt_end_ms: Optional[int] = None

    @property
    def is_excerpt(self) -> bool:
        return self.excerpt_start_ms is not None and self.excerpt_end_ms is not None


# ---------------------------------------------------------------------------
# Time utilities
# ---------------------------------------------------------------------------

def sec_to_ms(value: str | float | int) -> int:
    """Convert Transcriber seconds to ELAN integer milliseconds."""
    return int(round(float(value) * 1000))


def parse_time_to_ms(value: str) -> int:
    """
    Parse a user-entered time.

    Accepted:
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
            f"Invalid time '{value}'. Use HH:MM:SS(.mmm), MM:SS(.mmm), or seconds."
        )

    if seconds < 0:
        raise ValueError("Time cannot be negative.")

    return int(round(seconds * 1000))


def ms_to_clock(ms: int) -> str:
    """Human-readable HH:MM:SS.mmm."""
    total_seconds = ms / 1000
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"


def ms_to_filename_token(ms: int) -> str:
    """Filesystem-safe compact time token: HHMMSSmmm."""
    total_seconds, milli = divmod(ms, 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}{minutes:02d}{seconds:02d}{milli:03d}"


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """Collapse XML/newline whitespace while preserving transcript content."""
    return re.sub(r"\s+", " ", text or "").strip()


def event_to_text(elem: ET.Element) -> str:
    """
    Represent a Transcriber <Event> inline.

    Example:
        <Event desc="rire" type="noise".../> -> [rire]
    """
    desc = (elem.attrib.get("desc") or elem.attrib.get("type") or "event").strip()
    return f"[{desc}]"


def append_piece(
    buffers: Dict[str, List[str]],
    speaker_id: Optional[str],
    piece: str
) -> None:
    if not speaker_id:
        return
    piece = normalize_text(piece)
    if piece:
        buffers.setdefault(speaker_id, []).append(piece)


# ---------------------------------------------------------------------------
# TRS parsing
# ---------------------------------------------------------------------------

def parse_speakers(root: ET.Element) -> List[Speaker]:
    """Read speakers in declaration order, assigning SP1, SP2, ..."""
    speakers: List[Speaker] = []
    seen = set()

    speakers_node = root.find(".//Speakers")
    if speakers_node is not None:
        for i, elem in enumerate(speakers_node.findall("Speaker"), start=1):
            trs_id = (elem.attrib.get("id") or f"spk{i}").strip()
            if trs_id in seen:
                continue
            trs_name = (elem.attrib.get("name") or trs_id).strip()
            sensex_id = f"SP{i}"
            speakers.append(
                Speaker(
                    trs_id=trs_id,
                    trs_name=trs_name,
                    sensex_id=sensex_id,
                    tier_id=f"{sensex_id}_trs",
                )
            )
            seen.add(trs_id)

    # Add undeclared IDs encountered in Turns.
    turn_speaker_ids: List[str] = []
    for turn in root.findall(".//Turn"):
        for spk in (turn.attrib.get("speaker") or "").split():
            if spk and spk not in turn_speaker_ids:
                turn_speaker_ids.append(spk)

    next_n = len(speakers) + 1
    for trs_id in turn_speaker_ids:
        if trs_id not in seen:
            sensex_id = f"SP{next_n}"
            speakers.append(
                Speaker(
                    trs_id=trs_id,
                    trs_name=trs_id,
                    sensex_id=sensex_id,
                    tier_id=f"{sensex_id}_trs",
                )
            )
            seen.add(trs_id)
            next_n += 1

    return speakers


def parse_turn(turn: ET.Element, keep_events: bool = True) -> List[Segment]:
    """
    Convert one Transcriber <Turn> into time-aligned speaker segments.

    - Turn provides startTime / endTime.
    - Sync starts a new time interval.
    - Who nb="1", Who nb="2", ... selects the speaker listed in Turn@speaker.
    """
    start_s = turn.attrib.get("startTime")
    end_s = turn.attrib.get("endTime")

    if start_s is None or end_s is None:
        return []

    turn_start = sec_to_ms(start_s)
    turn_end = sec_to_ms(end_s)
    speaker_ids = (turn.attrib.get("speaker") or "").split()

    if not speaker_ids:
        return []

    current_start = turn_start
    current_speaker: Optional[str] = speaker_ids[0]
    buffers: Dict[str, List[str]] = {}
    out: List[Segment] = []

    def flush(interval_end: int) -> None:
        nonlocal buffers
        if interval_end <= current_start:
            buffers = {}
            return

        for spk_id, pieces in buffers.items():
            text = normalize_text(" ".join(pieces))
            if text:
                out.append(
                    Segment(
                        trs_speaker_id=spk_id,
                        start_ms=current_start,
                        end_ms=interval_end,
                        text=text,
                    )
                )
        buffers = {}

    append_piece(buffers, current_speaker, turn.text or "")

    for child in list(turn):
        tag = child.tag.split("}")[-1]

        if tag == "Sync":
            sync_time = sec_to_ms(child.attrib.get("time", current_start / 1000))
            flush(sync_time)
            current_start = sync_time

        elif tag == "Who":
            try:
                nb = int(child.attrib.get("nb", "1"))
                current_speaker = speaker_ids[nb - 1]
            except (ValueError, IndexError):
                pass

        elif tag == "Event":
            if keep_events:
                append_piece(buffers, current_speaker, event_to_text(child))

        else:
            append_piece(buffers, current_speaker, child.text or "")

        append_piece(buffers, current_speaker, child.tail or "")

    flush(turn_end)
    return out


def parse_trs(
    trs_path: Path,
    keep_events: bool = True
) -> Tuple[List[Speaker], List[Segment], ET.Element]:
    tree = ET.parse(trs_path)
    root = tree.getroot()

    speakers = parse_speakers(root)

    segments: List[Segment] = []
    for turn in root.findall(".//Turn"):
        segments.extend(parse_turn(turn, keep_events=keep_events))

    segments.sort(key=lambda x: (x.start_ms, x.end_ms, x.trs_speaker_id))
    return speakers, segments, root


def get_recording_bounds(root: ET.Element, segments: List[Segment]) -> Tuple[int, int]:
    """Return best-known recording/transcription bounds."""
    start_ms = min((s.start_ms for s in segments), default=0)
    end_ms = max((s.end_ms for s in segments), default=0)

    # Transcriber sometimes provides section/episode bounds even beyond actual text.
    candidates = []
    for elem in root.findall(".//*[@endTime]"):
        try:
            candidates.append(sec_to_ms(elem.attrib["endTime"]))
        except (ValueError, TypeError):
            pass

    if candidates:
        end_ms = max(end_ms, max(candidates))

    return start_ms, end_ms


# ---------------------------------------------------------------------------
# Excerpt handling
# ---------------------------------------------------------------------------

def excerpt_segments(
    segments: List[Segment],
    start_ms: int,
    end_ms: int,
) -> List[Segment]:
    """
    Keep intervals intersecting [start_ms, end_ms], clip them at the boundaries,
    and rebase the excerpt so start_ms becomes 0.
    """
    out: List[Segment] = []

    for seg in segments:
        # No overlap.
        if seg.end_ms <= start_ms or seg.start_ms >= end_ms:
            continue

        clipped_start = max(seg.start_ms, start_ms)
        clipped_end = min(seg.end_ms, end_ms)

        if clipped_end <= clipped_start:
            continue

        out.append(
            Segment(
                trs_speaker_id=seg.trs_speaker_id,
                start_ms=clipped_start - start_ms,
                end_ms=clipped_end - start_ms,
                text=seg.text,
            )
        )

    return out


def speakers_used_in_segments(
    speakers: List[Speaker],
    segments: List[Segment]
) -> List[Speaker]:
    """For excerpts, omit completely empty speaker tiers."""
    used = {s.trs_speaker_id for s in segments}
    return [s for s in speakers if s.trs_id in used]


# ---------------------------------------------------------------------------
# Interactive selection
# ---------------------------------------------------------------------------

def parse_selection(selection: str, n_files: int) -> List[int]:
    """
    Parse:
        all
        1
        1,3,5
        2-5
        1,3-6,9
    Return zero-based unique indices.
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
                    raise ValueError(f"File number out of range: {i}")
                chosen.add(i - 1)
        else:
            try:
                i = int(chunk)
            except ValueError:
                raise ValueError(f"Invalid selection part: {chunk}")

            if not 1 <= i <= n_files:
                raise ValueError(f"File number out of range: {i}")
            chosen.add(i - 1)

    if not chosen:
        raise ValueError("No files selected.")

    return sorted(chosen)


def choose_files_interactively(files: List[Path]) -> List[Path]:
    print("\nAvailable TRS files:")
    print("-" * 72)
    for i, path in enumerate(files, start=1):
        print(f"{i:>3}. {path.name}")
    print("-" * 72)
    print("Choose files using e.g. 1,3,5-7 or 'all'.")

    while True:
        raw = input("Files to convert: ").strip()
        if raw.lower() in {"q", "quit", "exit"}:
            raise SystemExit("Cancelled.")
        try:
            indices = parse_selection(raw, len(files))
            return [files[i] for i in indices]
        except ValueError as e:
            print(f"Invalid selection: {e}")


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


def ask_time(prompt: str, default_ms: Optional[int] = None) -> int:
    while True:
        default_txt = f" [{ms_to_clock(default_ms)}]" if default_ms is not None else ""
        raw = input(f"{prompt}{default_txt}: ").strip()

        if not raw and default_ms is not None:
            return default_ms

        try:
            return parse_time_to_ms(raw)
        except ValueError as e:
            print(e)


def build_interactive_requests(
    selected_files: List[Path],
    keep_events: bool,
) -> List[ConversionRequest]:
    requests: List[ConversionRequest] = []

    print("\nExcerpt configuration")
    print("=" * 72)
    print("Times accepted: HH:MM:SS(.mmm), MM:SS(.mmm), or seconds.")
    print("Excerpted EAFs will begin at 00:00:00.")
    print("=" * 72)

    for path in selected_files:
        print(f"\nFile: {path.name}")

        if not ask_yes_no("Convert only an excerpt?", default=False):
            requests.append(ConversionRequest(path))
            continue

        try:
            _, segments, root = parse_trs(path, keep_events=keep_events)
        except Exception as e:
            print(f"Could not inspect {path.name}: {e}")
            print("This file will be skipped.")
            continue

        rec_start, rec_end = get_recording_bounds(root, segments)
        print(
            f"Available transcription span: "
            f"{ms_to_clock(rec_start)} -> {ms_to_clock(rec_end)}"
        )

        while True:
            start_ms = ask_time("Excerpt start", default_ms=rec_start)
            end_ms = ask_time("Excerpt end", default_ms=rec_end)

            if end_ms <= start_ms:
                print("End time must be later than start time.")
                continue

            if start_ms < rec_start:
                print(
                    f"Start is before the first known transcription time "
                    f"({ms_to_clock(rec_start)})."
                )
                if not ask_yes_no("Use it anyway?", default=False):
                    continue

            if end_ms > rec_end:
                print(
                    f"End is after the last known transcription time "
                    f"({ms_to_clock(rec_end)})."
                )
                if not ask_yes_no("Use it anyway?", default=False):
                    continue

            print(
                f"Selected excerpt: {ms_to_clock(start_ms)} -> "
                f"{ms_to_clock(end_ms)} "
                f"(duration {ms_to_clock(end_ms - start_ms)})"
            )

            if ask_yes_no("Confirm this excerpt?", default=True):
                requests.append(
                    ConversionRequest(
                        trs_path=path,
                        excerpt_start_ms=start_ms,
                        excerpt_end_ms=end_ms,
                    )
                )
                break

    return requests


# ---------------------------------------------------------------------------
# ELAN output
# ---------------------------------------------------------------------------

def find_media_for_trs(
    trs_path: Path,
    media_dir: Optional[Path],
    root: ET.Element
) -> Optional[Path]:
    """Try to locate the corresponding WAV/MP3/MP4 media file."""
    candidates: List[Path] = []

    trans_audio = root.attrib.get("audio_filename")
    if trans_audio:
        audio_name = Path(trans_audio).name
        if media_dir:
            candidates.append(media_dir / audio_name)
        candidates.append(trs_path.parent / audio_name)

    search_dir = media_dir or trs_path.parent
    stem = trs_path.stem
    for ext in (".wav", ".mp3", ".mp4", ".m4a", ".flac"):
        candidates.append(search_dir / f"{stem}{ext}")

    for p in candidates:
        if p.exists():
            return p.resolve()

    return None


def create_eaf(
    trs_path: Path,
    eaf_path: Path,
    speakers: List[Speaker],
    segments: List[Segment],
    root: ET.Element,
    media_dir: Optional[Path] = None,
    excerpt_start_ms: Optional[int] = None,
    excerpt_end_ms: Optional[int] = None,
) -> Dict[str, int]:
    eaf = Eaf(author="Sens-Ex TRS→EAF converter")

    try:
        eaf.add_property("source_format", "Transcriber TRS")
        eaf.add_property("source_file", trs_path.name)
        eaf.add_property("conversion_protocol", "Sens-Ex")

        if excerpt_start_ms is not None and excerpt_end_ms is not None:
            eaf.add_property("excerpt_source_start", ms_to_clock(excerpt_start_ms))
            eaf.add_property("excerpt_source_end", ms_to_clock(excerpt_end_ms))
            eaf.add_property(
                "excerpt_source_start_ms",
                str(excerpt_start_ms)
            )
            eaf.add_property(
                "excerpt_source_end_ms",
                str(excerpt_end_ms)
            )
            eaf.add_property("timestamps_rebased_to_zero", "true")
    except Exception:
        pass

    is_excerpt = excerpt_start_ms is not None and excerpt_end_ms is not None

    # Whole-file EAFs may safely link the original media. Excerpts should later
    # link the extracted media excerpt, not the original full recording.
    if not is_excerpt:
        media = find_media_for_trs(trs_path, media_dir, root)
        if media:
            try:
                eaf.add_linked_file(str(media), mimetype=None, time_origin=0)
            except TypeError:
                try:
                    eaf.add_linked_file(str(media))
                except Exception:
                    pass
            except Exception:
                pass

    speaker_by_trs = {s.trs_id: s for s in speakers}

    for spk in speakers:
        try:
            eaf.add_tier(spk.tier_id, part=spk.trs_name)
        except TypeError:
            eaf.add_tier(spk.tier_id)

    last_end_by_tier: Dict[str, int] = {}
    stats = {
        "segments_total": 0,
        "segments_written": 0,
        "segments_skipped_empty": 0,
        "same_tier_overlap_adjustments": 0,
    }

    for seg in segments:
        stats["segments_total"] += 1

        spk = speaker_by_trs.get(seg.trs_speaker_id)
        if spk is None:
            continue

        text = normalize_text(seg.text)
        if not text:
            stats["segments_skipped_empty"] += 1
            continue

        start = seg.start_ms
        end = seg.end_ms

        previous_end = last_end_by_tier.get(spk.tier_id)
        if previous_end is not None and start < previous_end:
            adjusted_start = previous_end
            if adjusted_start < end:
                start = adjusted_start
                stats["same_tier_overlap_adjustments"] += 1
            else:
                start = max(seg.start_ms, end - 1)
                stats["same_tier_overlap_adjustments"] += 1

        if end <= start:
            end = start + 1

        eaf.add_annotation(spk.tier_id, start, end, text)
        last_end_by_tier[spk.tier_id] = end
        stats["segments_written"] += 1

    eaf_path.parent.mkdir(parents=True, exist_ok=True)
    eaf.to_file(str(eaf_path))
    return stats


def write_speaker_map(csv_path: Path, speakers: List[Speaker]) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["trs_speaker_id", "trs_speaker_name", "sensex_speaker_id", "eaf_tier"]
        )
        for spk in speakers:
            writer.writerow([spk.trs_id, spk.trs_name, spk.sensex_id, spk.tier_id])


# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------

def iter_trs_files(input_path: Path) -> Iterable[Path]:
    if input_path.is_file():
        if input_path.suffix.lower() != ".trs":
            raise ValueError(f"Input file is not .trs: {input_path}")
        yield input_path
    elif input_path.is_dir():
        yield from sorted(input_path.glob("*.trs"))
    else:
        raise FileNotFoundError(input_path)


def output_paths(
    request: ConversionRequest,
    output_dir: Optional[Path]
) -> Tuple[Path, Path]:
    trs_path = request.trs_path

    if request.is_excerpt:
        start_token = ms_to_filename_token(request.excerpt_start_ms)
        end_token = ms_to_filename_token(request.excerpt_end_ms)
        stem = f"{trs_path.stem}__excerpt_{start_token}-{end_token}"
    else:
        stem = trs_path.stem

    base_dir = output_dir if output_dir is not None else trs_path.parent
    return (
        base_dir / f"{stem}.eaf",
        base_dir / f"{stem}_speaker_map.csv",
    )


def convert_one(
    request: ConversionRequest,
    output_dir: Optional[Path],
    media_dir: Optional[Path],
    keep_events: bool,
) -> None:
    trs_path = request.trs_path
    speakers, segments, root = parse_trs(trs_path, keep_events=keep_events)

    if request.is_excerpt:
        segments = excerpt_segments(
            segments,
            request.excerpt_start_ms,
            request.excerpt_end_ms,
        )
        speakers = speakers_used_in_segments(speakers, segments)

        if not segments:
            raise ValueError(
                "No transcription annotations intersect the requested excerpt."
            )

    eaf_path, map_path = output_paths(request, output_dir)

    stats = create_eaf(
        trs_path=trs_path,
        eaf_path=eaf_path,
        speakers=speakers,
        segments=segments,
        root=root,
        media_dir=media_dir,
        excerpt_start_ms=request.excerpt_start_ms,
        excerpt_end_ms=request.excerpt_end_ms,
    )
    write_speaker_map(map_path, speakers)

    print(f"\n[OK] {trs_path.name}")
    if request.is_excerpt:
        print(
            f"     excerpt: {ms_to_clock(request.excerpt_start_ms)} -> "
            f"{ms_to_clock(request.excerpt_end_ms)}"
        )
        print(
            f"     EAF timeline: 00:00:00.000 -> "
            f"{ms_to_clock(request.excerpt_end_ms - request.excerpt_start_ms)}"
        )
    else:
        print("     mode: whole file")

    print(f"     EAF: {eaf_path}")
    print(f"     speaker map: {map_path}")
    print(f"     speakers: {len(speakers)}")
    print(f"     annotations: {stats['segments_written']}")

    if stats["same_tier_overlap_adjustments"]:
        print(
            "     WARNING: "
            f"{stats['same_tier_overlap_adjustments']} same-speaker overlap(s) "
            "required boundary adjustment."
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Convert ESLO/Transcriber TRS files to Sens-Ex-style ELAN EAF."
    )
    p.add_argument(
        "input",
        type=Path,
        help="A .trs file or a directory containing .trs files.",
    )
    p.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory. Default: beside each input TRS.",
    )
    p.add_argument(
        "--media-dir",
        type=Path,
        default=None,
        help=(
            "Optional directory containing corresponding media. "
            "Only whole-file EAFs are linked automatically."
        ),
    )
    p.add_argument(
        "--drop-events",
        action="store_true",
        help="Do not preserve Transcriber <Event> elements as [event] text.",
    )
    p.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help=(
            "Interactively choose which TRS files to convert and whether each "
            "selected file should be excerpted."
        ),
    )
    return p


def main() -> None:
    args = build_arg_parser().parse_args()

    try:
        files = list(iter_trs_files(args.input))
    except (ValueError, FileNotFoundError) as e:
        raise SystemExit(str(e))

    if not files:
        raise SystemExit(f"No .trs files found in: {args.input}")

    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    keep_events = not args.drop_events

    if args.interactive:
        selected = choose_files_interactively(files)
        requests = build_interactive_requests(
            selected_files=selected,
            keep_events=keep_events,
        )
    else:
        requests = [ConversionRequest(path) for path in files]

    if not requests:
        raise SystemExit("No files scheduled for conversion.")

    print("\nConversion plan")
    print("=" * 72)
    for req in requests:
        if req.is_excerpt:
            print(
                f"- {req.trs_path.name}: excerpt "
                f"{ms_to_clock(req.excerpt_start_ms)} -> "
                f"{ms_to_clock(req.excerpt_end_ms)}"
            )
        else:
            print(f"- {req.trs_path.name}: whole file")
    print("=" * 72)

    if args.interactive and not ask_yes_no("Start conversion?", default=True):
        raise SystemExit("Cancelled.")

    failed = 0
    for request in requests:
        try:
            convert_one(
                request=request,
                output_dir=args.output_dir,
                media_dir=args.media_dir,
                keep_events=keep_events,
            )
        except Exception as e:
            failed += 1
            print(f"[ERROR] {request.trs_path}: {e}", file=sys.stderr)

    if failed:
        raise SystemExit(f"{failed} file(s) failed.")


if __name__ == "__main__":
    main()
