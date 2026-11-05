#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
twitch_clip_to_vod.py

Goal
-----
Given Twitch clip URLs or clip IDs, retrieve:
- clip_id
- clip_url
- parent video_id
- VOD URL
- exact VOD-relative start time
- exact VOD-relative end time
- start/end in seconds
- clip duration

Input
-----
A text file with one clip URL or clip ID per line, for example:
https://clips.twitch.tv/FamousClipSlug
https://www.twitch.tv/somechannel/clip/FamousClipSlug
FamousClipSlug

Usage
-----
1) Create a Twitch developer application and get:
   - CLIENT_ID
   - CLIENT_SECRET

2) Export them in your shell:
   export TWITCH_CLIENT_ID="your_client_id"
   export TWITCH_CLIENT_SECRET="your_client_secret"

3) Run:
   python3 twitch_clip_to_vod.py clips.txt output.csv

Notes
-----
- The script uses an app access token via Twitch OAuth.
- If a clip has no available parent VOD, the script leaves the VOD fields empty.
- "Exact start/end timestamps" here means exact timestamps relative to the VOD timeline.
"""

import csv
import os
import re
import sys
import math
import requests
from typing import List, Dict, Optional

TOKEN_URL = "https://id.twitch.tv/oauth2/token"
CLIPS_URL = "https://api.twitch.tv/helix/clips"
VIDEOS_URL = "https://api.twitch.tv/helix/videos"


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def load_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def get_app_access_token(client_id: str, client_secret: str) -> str:
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }
    r = requests.post(TOKEN_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    token = data.get("access_token")
    if not token:
        raise RuntimeError("Could not retrieve Twitch app access token.")
    return token


def build_headers(client_id: str, access_token: str) -> Dict[str, str]:
    return {
        "Client-Id": client_id,
        "Authorization": f"Bearer {access_token}",
    }


def parse_clip_id(raw: str) -> Optional[str]:
    """
    Accept:
    - clip slug alone
    - https://clips.twitch.tv/<slug>
    - https://www.twitch.tv/<channel>/clip/<slug>
    """
    raw = raw.strip()
    if not raw:
        return None

    # clips.twitch.tv/<slug>
    m = re.search(r"clips\.twitch\.tv/([A-Za-z0-9_-]+)", raw)
    if m:
        return m.group(1)

    # twitch.tv/<channel>/clip/<slug>
    m = re.search(r"twitch\.tv/[^/]+/clip/([A-Za-z0-9_-]+)", raw)
    if m:
        return m.group(1)

    # bare slug
    if re.fullmatch(r"[A-Za-z0-9_-]+", raw):
        return raw

    return None


def chunked(seq: List[str], size: int):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def get_clips_metadata(clip_ids: List[str], headers: Dict[str, str]) -> Dict[str, dict]:
    """
    Twitch Get Clips accepts up to 100 ids per request.
    Returns dict keyed by clip_id.
    """
    results = {}

    for batch in chunked(clip_ids, 100):
        params = [("id", clip_id) for clip_id in batch]
        r = requests.get(CLIPS_URL, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        payload = r.json()

        for item in payload.get("data", []):
            results[item["id"]] = item

    return results


def get_videos_metadata(video_ids: List[str], headers: Dict[str, str]) -> Dict[str, dict]:
    """
    Twitch Get Videos accepts up to 100 ids per request.
    Returns dict keyed by video_id.
    """
    results = {}
    clean_ids = [vid for vid in video_ids if vid]

    for batch in chunked(clean_ids, 100):
        params = [("id", vid) for vid in batch]
        r = requests.get(VIDEOS_URL, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        payload = r.json()

        for item in payload.get("data", []):
            results[item["id"]] = item

    return results


def seconds_to_hms(total_seconds: Optional[float]) -> str:
    if total_seconds is None:
        return ""
    total_seconds = int(math.floor(total_seconds))
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def seconds_to_twitch_t(total_seconds: Optional[float]) -> str:
    if total_seconds is None:
        return ""
    total_seconds = int(math.floor(total_seconds))
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h}h{m}m{s}s"


def make_vod_url(video_url: str, start_seconds: Optional[float] = None) -> str:
    if not video_url:
        return ""
    if start_seconds is None:
        return video_url
    return f"{video_url}?t={seconds_to_twitch_t(start_seconds)}"


def read_input_file(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 twitch_clip_to_vod.py <input.txt> <output.csv>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    client_id = load_env("TWITCH_CLIENT_ID")
    client_secret = load_env("TWITCH_CLIENT_SECRET")
    raw_items = read_input_file(input_path)
    parsed = []
    invalid = []

    for raw in raw_items:
        clip_id = parse_clip_id(raw)
        if clip_id:
            parsed.append((raw, clip_id))
        else:
            invalid.append(raw)

    if not parsed:
        raise RuntimeError("No valid clip IDs or clip URLs found in input file.")

    access_token = get_app_access_token(client_id, client_secret)
    headers = build_headers(client_id, access_token)

    clip_ids = [clip_id for _, clip_id in parsed]
    clips_by_id = get_clips_metadata(clip_ids, headers)

    video_ids = []
    for clip_id in clip_ids:
        clip = clips_by_id.get(clip_id)
        if clip:
            vid = clip.get("video_id", "")
            if vid:
                video_ids.append(vid)

    videos_by_id = get_videos_metadata(sorted(set(video_ids)), headers)

    rows = []
    for original_input, clip_id in parsed:
        clip = clips_by_id.get(clip_id)

        if not clip:
            rows.append({
                "input": original_input,
                "clip_id": clip_id,
                "clip_url": "",
                "clip_title": "",
                "broadcaster_name": "",
                "created_at": "",
                "video_id": "",
                "vod_url": "",
                "vod_url_with_start": "",
                "vod_start_seconds": "",
                "vod_end_seconds": "",
                "vod_start_hms": "",
                "vod_end_hms": "",
                "clip_duration_seconds": "",
                "status": "clip_not_found",
            })
            continue

        video_id = clip.get("video_id") or ""
        vod_offset = clip.get("vod_offset")
        clip_duration = clip.get("duration")

        video = videos_by_id.get(video_id, {}) if video_id else {}
        base_vod_url = video.get("url", f"https://www.twitch.tv/videos/{video_id}" if video_id else "")

        # Exact VOD-relative times
        start_seconds = vod_offset if vod_offset is not None else None
        end_seconds = None
        if vod_offset is not None and clip_duration is not None:
            end_seconds = vod_offset + clip_duration

        status = "ok"
        if not video_id or vod_offset is None:
            status = "vod_unavailable_or_offset_missing"

        rows.append({
            "input": original_input,
            "clip_id": clip_id,
            "clip_url": clip.get("url", ""),
            "clip_title": clip.get("title", ""),
            "broadcaster_name": clip.get("broadcaster_name", ""),
            "created_at": clip.get("created_at", ""),
            "video_id": video_id,
            "vod_url": base_vod_url,
            "vod_url_with_start": make_vod_url(base_vod_url, start_seconds),
            "vod_start_seconds": start_seconds if start_seconds is not None else "",
            "vod_end_seconds": end_seconds if end_seconds is not None else "",
            "vod_start_hms": seconds_to_hms(start_seconds),
            "vod_end_hms": seconds_to_hms(end_seconds),
            "clip_duration_seconds": clip_duration if clip_duration is not None else "",
            "status": status,
        })

    fieldnames = [
        "input",
        "clip_id",
        "clip_url",
        "clip_title",
        "broadcaster_name",
        "created_at",
        "video_id",
        "vod_url",
        "vod_url_with_start",
        "vod_start_seconds",
        "vod_end_seconds",
        "vod_start_hms",
        "vod_end_hms",
        "clip_duration_seconds",
        "status",
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    eprint(f"Wrote {len(rows)} rows to: {output_path}")

    if invalid:
        eprint("\nIgnored invalid lines:")
        for x in invalid:
            eprint(f"  - {x}")


if __name__ == "__main__":
    main()
