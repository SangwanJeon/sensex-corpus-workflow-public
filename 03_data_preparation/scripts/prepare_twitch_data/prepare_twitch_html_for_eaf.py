#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prepare a four-column Twitch HTML file for html2eaf.py.

Inputs:
  1. TwitchDownloaderCLI full chat HTML
  2. WhisperX full transcription CSV (columns: time,text)
  3. Either:
       - a merged excerpt CSV whose filename contains:
         HH-MM-SS_HH-MM-SS
       - or explicit --start and --end values

Output columns:
  time | text | author | message

Main properties:
  - speech and chat remain separate chronological rows;
  - timestamps are absolute VOD timestamps;
  - users are anonymized consistently from the whole full-chat file;
  - @mentions are anonymized consistently;
  - Twitch emotes remain real <img src="..."> elements;
  - CSS/base64 emotes from TwitchDownloaderCLI are resolved into src attributes;
  - an anonymization map is saved as CSV and JSON.

Installation:
  pip install pandas beautifulsoup4 lxml
"""

import argparse
import csv
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd
from bs4 import BeautifulSoup, NavigableString, Tag


TIME_IN_HREF_RE = re.compile(
    r"[?&]t=(?:(\d+)h)?(?:(\d+)m)?(?:(\d+(?:\.\d+)?)s)?",
    re.IGNORECASE,
)

WINDOW_IN_FILENAME_RE = re.compile(
    r"(?P<sh>\d{2})-(?P<sm>\d{2})-(?P<ss>\d{2}(?:\.\d+)?)_"
    r"(?P<eh>\d{2})-(?P<em>\d{2})-(?P<es>\d{2}(?:\.\d+)?)"
)

CSS_CONTENT_URL_RE = re.compile(
    r"\.([A-Za-z0-9_-]+)\s*\{[^{}]*?"
    r"content\s*:\s*url\(\s*([\"'])(.*?)\2\s*\)\s*;?[^{}]*?\}",
    re.IGNORECASE | re.DOTALL,
)

MENTION_RE = re.compile(r"@([A-Za-z0-9_]+)")


@dataclass
class ChatRecord:
    time: float
    original_author: str
    author: str
    message_html: str


@dataclass
class OutputRow:
    time: float
    text: str
    author: str
    message_html: str
    kind_order: int
    source_order: int


def parse_time_value(value: str) -> float:
    """Parse seconds, MM:SS, or HH:MM:SS into seconds."""
    value = str(value).strip()

    if re.fullmatch(r"\d+(?:\.\d+)?", value):
        return float(value)

    parts = value.split(":")
    if len(parts) not in (2, 3):
        raise ValueError(f"Unsupported time value: {value!r}")

    try:
        numbers = [float(part) for part in parts]
    except ValueError as exc:
        raise ValueError(f"Unsupported time value: {value!r}") from exc

    if len(numbers) == 2:
        minutes, seconds = numbers
        return minutes * 60 + seconds

    hours, minutes, seconds = numbers
    return hours * 3600 + minutes * 60 + seconds


def parse_window_from_filename(path: Path) -> Tuple[float, float]:
    match = WINDOW_IN_FILENAME_RE.search(path.name)
    if not match:
        raise ValueError(
            "Could not infer the excerpt window from the merged CSV filename. "
            "Use --start and --end explicitly."
        )

    start = (
        int(match.group("sh")) * 3600
        + int(match.group("sm")) * 60
        + float(match.group("ss"))
    )
    end = (
        int(match.group("eh")) * 3600
        + int(match.group("em")) * 60
        + float(match.group("es"))
    )

    if end < start:
        raise ValueError("The inferred excerpt end precedes its start.")

    return start, end


def extract_comment_time(comment: Tag) -> Optional[float]:
    """Read the absolute VOD time from the TwitchDownloader comment link."""
    link = comment.find("a", href=TIME_IN_HREF_RE)

    if link and link.get("href"):
        match = TIME_IN_HREF_RE.search(link["href"])
        if match:
            hours = float(match.group(1) or 0)
            minutes = float(match.group(2) or 0)
            seconds = float(match.group(3) or 0)
            return hours * 3600 + minutes * 60 + seconds

    # Fallback: read displayed [H:MM:SS]
    raw = comment.get_text(" ", strip=True)
    match = re.search(r"\[\s*(\d+:\d{2}:\d{2}(?:\.\d+)?)\s*\]", raw)
    if match:
        return parse_time_value(match.group(1))

    return None


def extract_css_image_map(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Map TwitchDownloader CSS classes to their content:url(...) value.
    This supports embedded base64 images and ordinary URLs.
    """
    mapping: Dict[str, str] = {}

    for style in soup.find_all("style"):
        css = style.string or style.get_text()
        for class_name, _quote, url in CSS_CONTENT_URL_RE.findall(css):
            mapping[class_name] = html.unescape(url.strip())

    return mapping


def author_role(comment: Tag) -> str:
    """
    Return broadcaster, moderator, or user based on badge titles.
    """
    titles = {
        str(img.get("title", "")).strip().lower()
        for img in comment.find_all("img", class_=lambda c: c and "badge-image" in c)
    }

    if "broadcaster" in titles:
        return "broadcaster"
    if "moderator" in titles:
        return "moderator"
    return "user"


def collect_author_information(
    comments: Sequence[Tag],
    broadcaster_names: Iterable[str],
) -> Tuple[List[str], Dict[str, str], Dict[str, str]]:
    """
    Return:
      first appearance order,
      canonical display spelling,
      strongest role found for each username.
    """
    first_order: List[str] = []
    display_name: Dict[str, str] = {}
    roles: Dict[str, str] = {}

    broadcaster_keys = {
        name.strip().lower()
        for name in broadcaster_names
        if name and name.strip()
    }

    role_priority = {"user": 0, "moderator": 1, "broadcaster": 2}

    for comment in comments:
        author_tag = comment.find("span", class_="comment-author")
        if not author_tag:
            continue

        original = author_tag.get_text(" ", strip=True)
        if not original:
            continue

        key = original.lower()

        if key not in display_name:
            display_name[key] = original
            first_order.append(key)

        role = author_role(comment)
        if key in broadcaster_keys:
            role = "broadcaster"

        previous = roles.get(key, "user")
        if role_priority[role] > role_priority[previous]:
            roles[key] = role
        elif key not in roles:
            roles[key] = previous

    # Add explicitly supplied broadcaster names even if they never write in chat.
    for broadcaster in broadcaster_names:
        broadcaster = broadcaster.strip()
        if not broadcaster:
            continue
        key = broadcaster.lower()
        if key not in display_name:
            display_name[key] = broadcaster
            first_order.append(key)
        roles[key] = "broadcaster"

    return first_order, display_name, roles


def build_anonymization_map(
    comments: Sequence[Tag],
    broadcaster_names: Iterable[str],
) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str]]:
    """
    Build one stable map from the whole chat.

    All broadcaster usernames map to Broadcaster.
    Moderators map to Moderator1, Moderator2, ...
    Other users map to User1, User2, ...
    """
    order, display_names, roles = collect_author_information(
        comments,
        broadcaster_names,
    )

    mapping: Dict[str, str] = {}
    moderator_counter = 1
    user_counter = 1

    for key in order:
        role = roles.get(key, "user")

        if role == "broadcaster":
            mapping[key] = "Broadcaster"
        elif role == "moderator":
            mapping[key] = f"Moderator{moderator_counter}"
            moderator_counter += 1
        else:
            mapping[key] = f"User{user_counter}"
            user_counter += 1

    return mapping, display_names, roles


def replace_mentions_in_fragment(
    fragment: BeautifulSoup,
    mapping: Dict[str, str],
) -> None:
    """Replace @username only in text nodes, never inside HTML attributes."""

    def replacement(match: re.Match) -> str:
        original = match.group(1)
        pseudonym = mapping.get(original.lower())
        return f"@{pseudonym}" if pseudonym else match.group(0)

    for text_node in list(fragment.find_all(string=True)):
        if text_node.parent and text_node.parent.name in {"style", "script"}:
            continue

        updated = MENTION_RE.sub(replacement, str(text_node))
        if updated != str(text_node):
            text_node.replace_with(updated)


def resolve_emotes_in_message(
    message_tag: Tag,
    css_image_map: Dict[str, str],
    mapping: Dict[str, str],
    image_width: int = 20,
) -> str:
    """
    Preserve message markup while converting CSS-only Twitch emotes
    to ordinary <img src="..."> elements.
    """
    fragment = BeautifulSoup(
        "".join(str(node) for node in message_tag.contents),
        "lxml",
    )

    container = fragment.body or fragment

    for img in container.find_all("img"):
        classes = list(img.get("class", []))

        src = img.get("src", "").strip()
        if not src:
            for class_name in classes:
                candidate = css_image_map.get(class_name)
                if candidate:
                    src = candidate
                    break

        if src:
            img["src"] = src

        img["width"] = str(image_width)
        img.attrs.pop("height", None)

        title = str(img.get("title", "")).strip()
        if title and not img.get("alt"):
            img["alt"] = title

        # Output does not need TwitchDownloader's generated CSS classes.
        img.attrs.pop("class", None)

        # Remove the hidden duplicate emote label immediately following the img.
        sibling = img.find_next_sibling()
        if (
            isinstance(sibling, Tag)
            and sibling.name == "span"
            and "text-hide" in sibling.get("class", [])
        ):
            sibling.decompose()

    replace_mentions_in_fragment(container, mapping)

    return "".join(str(node) for node in container.contents).strip()


def parse_full_chat(
    chat_html_path: Path,
    start: float,
    end: float,
    broadcaster_names: Iterable[str],
) -> Tuple[List[ChatRecord], Dict[str, str], Dict[str, str], Dict[str, str]]:
    with chat_html_path.open("r", encoding="utf-8") as file:
        soup = BeautifulSoup(file.read(), "lxml")

    comments = soup.find_all("pre", class_="comment-root")
    if not comments:
        raise ValueError(
            "No <pre class='comment-root'> messages were found in the chat HTML."
        )

    css_image_map = extract_css_image_map(soup)
    mapping, display_names, roles = build_anonymization_map(
        comments,
        broadcaster_names,
    )

    records: List[ChatRecord] = []

    for comment in comments:
        time = extract_comment_time(comment)
        if time is None or time < start or time > end:
            continue

        author_tag = comment.find("span", class_="comment-author")
        message_tag = comment.find("span", class_="comment-message")

        if not author_tag or not message_tag:
            continue

        original_author = author_tag.get_text(" ", strip=True)
        author_key = original_author.lower()
        pseudonym = mapping.get(author_key)

        if not pseudonym:
            # Defensive fallback; normally every author has already been mapped.
            pseudonym = f"User{len(mapping) + 1}"
            mapping[author_key] = pseudonym
            display_names[author_key] = original_author
            roles[author_key] = "user"

        message_html = resolve_emotes_in_message(
            message_tag,
            css_image_map,
            mapping,
        )

        # TwitchDownloader message cells often begin with ": "
        message_html = re.sub(r"^\s*:\s*", "", message_html)

        records.append(
            ChatRecord(
                time=float(time),
                original_author=original_author,
                author=pseudonym,
                message_html=message_html,
            )
        )

    return records, mapping, display_names, roles


def load_transcription_rows(
    transcription_csv: Path,
    start: float,
    end: float,
) -> List[OutputRow]:
    df = pd.read_csv(transcription_csv, encoding="utf-8-sig")

    required = {"time", "text"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(
            f"Transcription CSV is missing columns: {sorted(missing)}"
        )

    df = df.copy()
    df["time"] = pd.to_numeric(df["time"], errors="coerce")
    df["text"] = df["text"].fillna("").astype(str)
    df = df.dropna(subset=["time"])
    df = df[(df["time"] >= start) & (df["time"] <= end)]

    rows: List[OutputRow] = []

    for source_order, row in enumerate(df.itertuples(index=False)):
        text = str(row.text).strip()
        if not text:
            continue

        rows.append(
            OutputRow(
                time=float(row.time),
                text=text,
                author="",
                message_html="",
                kind_order=1,
                source_order=source_order,
            )
        )

    return rows


def combine_rows(
    chat_records: Sequence[ChatRecord],
    speech_rows: Sequence[OutputRow],
) -> List[OutputRow]:
    rows = list(speech_rows)

    for source_order, record in enumerate(chat_records):
        rows.append(
            OutputRow(
                time=record.time,
                text="",
                author=record.author,
                message_html=record.message_html,
                kind_order=0,
                source_order=source_order,
            )
        )

    rows.sort(
        key=lambda row: (
            row.time,
            row.kind_order,
            row.source_order,
        )
    )

    return rows


def format_seconds(value: float) -> str:
    return f"{value:.3f}"


def write_output_html(rows: Sequence[OutputRow], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    prefix = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Twitch speech and anonymized chat</title>
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet"/>
<style>
  body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
  }
  .table-wrapper {
    padding: 20px;
    max-width: 100%;
    overflow-x: auto;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    border: 1px solid #ddd;
    table-layout: fixed;
  }
  th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
    word-wrap: break-word;
    white-space: normal;
    overflow: hidden;
  }
  th:first-child, td:first-child {
    width: 100px;
  }
  th {
    position: sticky;
    top: 0;
    background-color: #343a40;
    color: white;
  }
  tr:nth-child(even) {
    background-color: #f2f2f2;
  }
  img {
    vertical-align: middle;
  }
</style>
</head>
<body>
<div class="table-wrapper">
<table border="1" class="dataframe table table-striped">
<thead class="thead-dark">
<tr style="text-align: left;">
<th>time</th>
<th>text</th>
<th>author</th>
<th>message</th>
</tr>
</thead>
<tbody>
"""

    suffix = """</tbody>
</table>
</div>
</body>
</html>
"""

    with output_path.open("w", encoding="utf-8") as file:
        file.write(prefix)

        for row in rows:
            file.write("<tr>\n")
            file.write(f"<td>{format_seconds(row.time)}</td>\n")
            file.write(f"<td>{html.escape(row.text)}</td>\n")
            file.write(f"<td>{html.escape(row.author)}</td>\n")
            file.write(f"<td>{row.message_html}</td>\n")
            file.write("</tr>\n")

        file.write(suffix)


def write_mapping_files(
    mapping: Dict[str, str],
    display_names: Dict[str, str],
    roles: Dict[str, str],
    csv_path: Path,
    json_path: Path,
) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    records = [
        {
            "original_author": display_names.get(key, key),
            "anonymized_author": pseudonym,
            "role": roles.get(key, "user"),
        }
        for key, pseudonym in mapping.items()
    ]

    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "original_author",
                "anonymized_author",
                "role",
            ],
        )
        writer.writeheader()
        writer.writerows(records)

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)


def validate_output(
    output_path: Path,
    start: float,
    end: float,
) -> Dict[str, int]:
    with output_path.open("r", encoding="utf-8") as file:
        soup = BeautifulSoup(file.read(), "lxml")

    table = soup.find("table")
    if table is None:
        raise ValueError("Validation failed: no table found.")

    headers = [
        th.get_text(" ", strip=True)
        for th in table.find_all("th")
    ]
    if headers != ["time", "text", "author", "message"]:
        raise ValueError(
            f"Validation failed: unexpected headers {headers!r}"
        )

    body_rows = table.find("tbody").find_all("tr")
    speech_count = 0
    chat_count = 0
    emote_count = 0

    previous_time: Optional[float] = None

    for row in body_rows:
        cells = row.find_all("td")
        if len(cells) != 4:
            raise ValueError(
                "Validation failed: a row does not contain four cells."
            )

        current_time = float(cells[0].get_text(strip=True))
        if current_time < start or current_time > end:
            raise ValueError(
                f"Validation failed: timestamp {current_time} is outside the window."
            )

        if previous_time is not None and current_time < previous_time:
            raise ValueError(
                "Validation failed: rows are not chronologically ordered."
            )
        previous_time = current_time

        text = cells[1].get_text(" ", strip=True)
        author = cells[2].get_text(" ", strip=True)
        message = cells[3].get_text(" ", strip=True)

        if text:
            speech_count += 1
        if author or message or cells[3].find("img"):
            chat_count += 1

        for img in cells[3].find_all("img"):
            if not img.get("src"):
                raise ValueError(
                    "Validation failed: an emote image has no src attribute."
                )
            emote_count += 1

    return {
        "rows": len(body_rows),
        "speech_rows": speech_count,
        "chat_rows": chat_count,
        "emotes": emote_count,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Create a four-column HTML timeline from full Twitch chat "
            "and a full WhisperX transcription."
        )
    )

    parser.add_argument(
        "chat_html",
        type=Path,
        help="Full TwitchDownloaderCLI chat_full.html",
    )
    parser.add_argument(
        "transcription_csv",
        type=Path,
        help="Full WhisperX CSV with columns time,text",
    )
    parser.add_argument(
        "output_html",
        type=Path,
        help="Four-column HTML file to create",
    )

    parser.add_argument(
        "--merged-csv",
        type=Path,
        help=(
            "Optional excerpt merged CSV. Its filename is used to infer "
            "the HH-MM-SS_HH-MM-SS window."
        ),
    )
    parser.add_argument(
        "--start",
        help="Excerpt start: seconds, MM:SS, or HH:MM:SS",
    )
    parser.add_argument(
        "--end",
        help="Excerpt end: seconds, MM:SS, or HH:MM:SS",
    )
    parser.add_argument(
        "--broadcaster",
        action="append",
        default=[],
        help=(
            "Original streamer username. May be repeated. "
            "This username is mapped to Broadcaster, including @mentions."
        ),
    )
    parser.add_argument(
        "--mapping-csv",
        type=Path,
        help="Optional anonymization mapping CSV path",
    )
    parser.add_argument(
        "--mapping-json",
        type=Path,
        help="Optional anonymization mapping JSON path",
    )

    args = parser.parse_args()

    if args.start is not None or args.end is not None:
        if args.start is None or args.end is None:
            parser.error("--start and --end must be supplied together.")
        start = parse_time_value(args.start)
        end = parse_time_value(args.end)
    elif args.merged_csv:
        start, end = parse_window_from_filename(args.merged_csv)
    else:
        parser.error(
            "Supply either --merged-csv or both --start and --end."
        )

    if end < start:
        parser.error("The excerpt end must not precede the start.")

    mapping_csv = args.mapping_csv or args.output_html.with_name(
        args.output_html.stem + "_anonymization_map.csv"
    )
    mapping_json = args.mapping_json or args.output_html.with_name(
        args.output_html.stem + "_anonymization_map.json"
    )

    chat_records, mapping, display_names, roles = parse_full_chat(
        args.chat_html,
        start,
        end,
        args.broadcaster,
    )

    speech_rows = load_transcription_rows(
        args.transcription_csv,
        start,
        end,
    )

    rows = combine_rows(chat_records, speech_rows)
    write_output_html(rows, args.output_html)

    write_mapping_files(
        mapping,
        display_names,
        roles,
        mapping_csv,
        mapping_json,
    )

    report = validate_output(
        args.output_html,
        start,
        end,
    )

    print(f"Window: {start:.3f}–{end:.3f} seconds")
    print(f"Full-chat identities mapped: {len(mapping)}")
    print(f"Excerpt chat rows: {len(chat_records)}")
    print(f"Excerpt speech rows: {len(speech_rows)}")
    print(f"Total output rows: {report['rows']}")
    print(f"Preserved emote images: {report['emotes']}")
    print(f"HTML written: {args.output_html}")
    print(f"Mapping CSV written: {mapping_csv}")
    print(f"Mapping JSON written: {mapping_json}")


if __name__ == "__main__":
    main()
