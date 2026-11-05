#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pip install beautifulsoup4 lxml
#python3 build_emote_dict.py /path/to/html_folder emotes_global.json

import os, re, json, argparse
from bs4 import BeautifulSoup

TWITCH_ID_RE = re.compile(r"/emoticons/v2/(\d+)/")

def parse_emote_id_from_src(src: str) -> str:
    if not src:
        return ""
    m = TWITCH_ID_RE.search(src)
    return m.group(1) if m else ""

def pick_better(existing: dict, candidate: dict) -> dict:
    """
    Heuristic to keep the 'best' entry when the same emote id is seen multiple times.
    Prefer:
    - having alt/title
    - width/height present
    - src containing '/dark/' over others (customize if you want)
    """
    if not existing:
        return candidate

    score = 0
    def s(meta):
        sc = 0
        if meta.get("alt"): sc += 2
        if meta.get("title"): sc += 1
        if meta.get("width") and meta.get("height"): sc += 1
        if "/dark/" in (meta.get("src") or ""): sc += 1
        if "/2.0" in (meta.get("src") or ""): sc += 1  # prefer higher res if present
        return sc

    return candidate if s(candidate) > s(existing) else existing

def extract_emotes_from_html(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    out = {}
    for img in soup.find_all("img"):
        src = img.get("src", "") or ""
        emote_id = parse_emote_id_from_src(src)
        if not emote_id:
            continue

        meta = {
            "src": src,
            "alt": img.get("alt", "") or "",
            "title": img.get("title", "") or "",
            "width": str(img.get("width", "") or ""),
            "height": str(img.get("height", "") or ""),
        }
        out[emote_id] = pick_better(out.get(emote_id), meta)

    return out

def iter_html_files(root: str):
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith((".html", ".htm")):
                yield os.path.join(dirpath, fn)

def main(root: str, out_json: str):
    global_dict = {}
    n_files = 0
    n_imgs = 0

    for path in iter_html_files(root):
        n_files += 1
        local = extract_emotes_from_html(path)
        n_imgs += len(local)

        for emote_id, meta in local.items():
            global_dict[emote_id] = pick_better(global_dict.get(emote_id), meta)

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(global_dict, f, ensure_ascii=False, indent=2)

    print(f"Scanned {n_files} HTML files.")
    print(f"Found {len(global_dict)} unique emote IDs (from {n_imgs} file-level unique IDs).")
    print(f"Wrote: {out_json}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Build a global Twitch emote dictionary from a folder of HTML files.")
    ap.add_argument("root", help="Root folder containing HTML files")
    ap.add_argument("out_json", help="Output JSON path (e.g., emotes_global.json)")
    args = ap.parse_args()
    main(args.root, args.out_json)
