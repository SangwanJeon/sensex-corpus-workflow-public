#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pip install pympi-ling beautifulsoup4 lxml rapidfuzz num2words
#
# HTML (time,text,author,message)  ->  enrich an EAF extract
# - estimates OFFSET by matching EAF speech segments to HTML 'text' column (fuzzy)
# - rebases HTML timestamps into the EAF extract timeline
# - adds:
#     STREAMER_HTML (alignable)  : normalized minimal-ortho streamer speech from HTML
#     CHAT_MESSAGE (alignable)   : chat with emotes replaced by readable tokens ⟦emote:<id>⟧
#     CHAT_AUTHOR (ref)          : author id
#     CHAT_EMOTE_MAP (ref)       : JSON list with token/src/id/etc. for reconstruction
#     CHAT_MESSAGE_RAW (ref)     : optional raw chat (as plain text, safe-escaped)
#
# Notes:
# - Emote "names" are not required; ID+src is enough.
# - ELAN does not support rendering <img>; we store safe tokens in CHAT_MESSAGE.
# - advance chat 4 seconds: python3 html2eaf.py input.html input.eaf output.eaf --shift 4
# - move chat earlier by 2.5 seconds: python3 html2eaf.py input.html input.eaf output.eaf --shift -2.5

import re
import string
import unicodedata
import statistics
import json
import html as htmllib
from dataclasses import dataclass
from typing import List, Tuple

from bs4 import BeautifulSoup
from num2words import num2words
from rapidfuzz import fuzz
import pympi

import xml.etree.ElementTree as ET
import os

def reorder_tiers_in_eaf(eaf_path_in: str, eaf_path_out: str, ordered_tier_ids: List[str]):
    tree = ET.parse(eaf_path_in)
    root = tree.getroot()

    tiers = root.findall("TIER")
    by_id = {t.get("TIER_ID"): t for t in tiers}

    # remove all tier nodes
    for t in tiers:
        root.remove(t)

    # reinsert tiers in desired order (only existing ones)
    for tid in ordered_tier_ids:
        node = by_id.get(tid)
        if node is not None:
            root.append(node)

    # append any tiers not mentioned (just in case)
    remaining = [tid for tid in by_id.keys() if tid not in ordered_tier_ids]
    for tid in remaining:
        root.append(by_id[tid])

    tree.write(eaf_path_out, encoding="UTF-8", xml_declaration=True)

# ----------------------------
# Config (generic defaults)
# ----------------------------
ANCHOR_TIER_CANDIDATES = ["SP1_verbal", "SP2_verbal", "SP3_verbal", "SPEECH", "SPEECH_STREAMER"]
DEFAULT_EXTRACT_TIER = "default"

MIN_ANCHOR_SCORE = 85          # fuzzy match threshold (lower to 80 if needed)
MAX_ANCHORS_USED = 30          # keep median stable
EDGE_MARGIN_MS = 1500          # allow slight spillover at edges
CHAT_FALLBACK_DUR_MS = 2000    # end time if last chat event
STREAMER_FALLBACK_DUR_MS = 2000


# ----------------------------
# Emotes (HTML -> safe tokens + JSON map)
# ----------------------------
TWITCH_ID_RE = re.compile(r"/emoticons/v2/(\d+)/")

def parse_emote_id_from_src(src: str) -> str:
    if not src:
        return ""
    m = TWITCH_ID_RE.search(src)
    return m.group(1) if m else ""

def encode_emotes(message: str) -> Tuple[str, List[dict]]:
    """
    Replace <img ...> emotes by tokens safe for ELAN, and return:
      (text_with_tokens, emote_metadata_list)
    """
    msg = htmllib.unescape(message)
    soup = BeautifulSoup(msg, "lxml")

    emotes: List[dict] = []
    idx = 1

    for img in soup.find_all("img"):
        src = img.get("src", "")
        emote_id = parse_emote_id_from_src(src)
        label = emote_id if emote_id else f"u{idx:03d}"
        token = f"{{emote:{label}}}"

        emotes.append({
            "token": token,
            "provider": "twitch" if emote_id else "",
            "id": emote_id,
            "src": src,
            "width": img.get("width", ""),
            "height": img.get("height", ""),
            "alt": img.get("alt", ""),
            "title": img.get("title", "")
        })

        img.replace_with(token)
        idx += 1

    clean_text = soup.get_text(" ", strip=False)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()
    return clean_text, emotes


# ----------------------------
# Data
# ----------------------------
@dataclass
class HtmlRow:
    t_ms_abs: int
    speech_raw: str
    speech_norm: str
    author: str
    chat_html: str
    chat_with_emotes: str
    chat_text: str


@dataclass
class EafAnchor:
    start_ms: int
    text_norm: str
    tier: str


# ----------------------------
# Text normalization (minimal ortho for streamer speech + anchor matching)
# ----------------------------
# ----------------------------
# Text normalization (minimal ortho for streamer speech + anchor matching)
# Keep apostrophes and hyphens, remove the rest of punctuation (.,;:?! etc.)
# ----------------------------
DIGIT_RE = re.compile(r"\d+")

# Build a punctuation set that EXCLUDES apostrophe and hyphen
# - keep: '  ’  -
# - remove: everything else in string.punctuation + French quotes/dashes/ellipsis
PUNCT_TO_REMOVE = (string.punctuation.replace("'", "").replace("-", "") + "«»…–—")
PUNCT_RE = re.compile(r"[{}]".format(re.escape(PUNCT_TO_REMOVE)))

def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def digits_to_fr_words(s: str) -> str:
    def repl(m):
        return num2words(int(m.group(0)), lang="fr")
    return DIGIT_RE.sub(repl, s)

def normalize_min_ortho(s: str, strip_diacritics: bool = False) -> str:
    """
    Minimal orthographic transcription:
    - lowercase
    - digits -> words (French)
    - remove punctuation EXCEPT apostrophes and hyphens
    """
    s = s.strip().lower()

    # normalize curly apostrophe to straight apostrophe
    s = s.replace("’", "'")

    s = digits_to_fr_words(s)

    # remove unwanted punctuation (but keep ' and -)
    s = PUNCT_RE.sub(" ", s)

    if strip_diacritics:
        s = strip_accents(s)

    # normalize spaces (keep hyphen/apostrophe untouched)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ----------------------------
# Time parsing (HTML)
# ----------------------------
def parse_time_to_ms(t: str) -> int:
    t = t.strip()
    # numeric seconds
    if re.fullmatch(r"\d+(\.\d+)?", t):
        return int(float(t) * 1000)

    # hh:mm:ss(.ms) optional
    m = re.fullmatch(r"(?:(\d+):)?(\d{1,2}):(\d{2})(?:\.(\d{1,3}))?", t)
    if not m:
        raise ValueError(f"Unrecognized time format: {t!r}")
    hh = int(m.group(1) or 0)
    mm = int(m.group(2))
    ss = int(m.group(3))
    ms = int((m.group(4) or "0").ljust(3, "0"))
    return ((hh * 3600 + mm * 60 + ss) * 1000) + ms


# ----------------------------
# Parse HTML (4 columns)
# ----------------------------
def parse_html_4col(path: str) -> List[HtmlRow]:
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    rows: List[HtmlRow] = []

    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) != 4:
            continue

        time_s = htmllib.unescape(tds[0].get_text(" ", strip=True))
        speech = htmllib.unescape(tds[1].get_text(" ", strip=True))
        author = htmllib.unescape(tds[2].get_text(" ", strip=True))

        # keep inner HTML so <img> survives
        chat_html = "".join(str(x) for x in tds[3].contents).strip()
        chat_html = htmllib.unescape(chat_html)

        if not time_s:
            continue
        t_ms = parse_time_to_ms(time_s)

        speech_norm = normalize_min_ortho(speech) if speech.strip() else ""

        if chat_html.strip():
            chat_with_emotes, _emote_data = encode_emotes(chat_html)  # tokens included
            chat_text = BeautifulSoup(chat_html, "lxml").get_text(" ", strip=True)
        else:
            chat_with_emotes, chat_text = "", ""

        rows.append(HtmlRow(
            t_ms_abs=t_ms,
            speech_raw=speech,
            speech_norm=speech_norm,
            author=author.strip(),
            chat_html=chat_html,
            chat_with_emotes=chat_with_emotes,
            chat_text=chat_text
        ))

    rows.sort(key=lambda r: r.t_ms_abs)
    return rows


# ----------------------------
# Parse EAF anchors + extract window
# ----------------------------
def get_extract_window(eaf: pympi.Elan.Eaf) -> Tuple[int, int]:
    """
    Prefer DEFAULT_EXTRACT_TIER if present; else use global min/max times.
    """
    if DEFAULT_EXTRACT_TIER in eaf.get_tier_names():
        anns = eaf.get_annotation_data_for_tier(DEFAULT_EXTRACT_TIER)
        starts = [a[0] for a in anns]
        ends   = [a[1] for a in anns]
        return (min(starts), max(ends))

    min_t, max_t = None, None
    for tier in eaf.get_tier_names():
        for (s, e, _) in eaf.get_annotation_data_for_tier(tier):
            min_t = s if min_t is None else min(min_t, s)
            max_t = e if max_t is None else max(max_t, e)
    if min_t is None or max_t is None:
        raise ValueError("Cannot determine extract window (no annotations found).")
    return (min_t, max_t)

def collect_eaf_anchors(eaf: pympi.Elan.Eaf) -> List[EafAnchor]:
    tier_names = eaf.get_tier_names()
    candidates = [t for t in ANCHOR_TIER_CANDIDATES if t in tier_names]
    if not candidates:
        candidates = [t for t in tier_names if "verbal" in t.lower()]

    anchors: List[EafAnchor] = []
    for tier in candidates:
        for (start, _end, value) in eaf.get_annotation_data_for_tier(tier):
            if not value or not value.strip():
                continue
            anchors.append(EafAnchor(
                start_ms=start,
                text_norm=normalize_min_ortho(value),
                tier=tier
            ))

    anchors.sort(key=lambda a: len(a.text_norm), reverse=True)
    return anchors[:MAX_ANCHORS_USED]


# ----------------------------
# Offset estimation (anchors -> median offset)
# ----------------------------
def estimate_offset_ms(anchors: List[EafAnchor], html_rows: List[HtmlRow]) -> int:
    streamer_rows = [r for r in html_rows if r.speech_norm]
    offsets: List[int] = []

    for a in anchors:
        best_time = None
        best_score = 0

        for r in streamer_rows:
            score = fuzz.partial_ratio(a.text_norm, r.speech_norm)
            if score > best_score:
                best_score = score
                best_time = r.t_ms_abs

        if best_time is not None and best_score >= MIN_ANCHOR_SCORE:
            offsets.append(best_time - a.start_ms)

    if not offsets:
        raise ValueError(
            "No reliable anchors found to estimate OFFSET.\n"
            "- Check that the EAF speech text occurs in the HTML 'text' column.\n"
            "- Or lower MIN_ANCHOR_SCORE (e.g., 80).\n"
        )

    return int(statistics.median(offsets))


# ----------------------------
# Add tiers + annotations
# ----------------------------


def ensure_tiers(eaf: pympi.Elan.Eaf):
    if "STREAMER_HTML" not in eaf.get_tier_names():
        eaf.add_tier("STREAMER_HTML")


def make_intervals(times: List[int], values: List[str], fallback_dur: int) -> List[Tuple[int, int, str]]:
    out: List[Tuple[int, int, str]] = []
    for i, (t, v) in enumerate(zip(times, values)):
        if not v or not v.strip():
            continue
        if i < len(times) - 1:
            end = max(t + 1, times[i + 1] - 1)
        else:
            end = t + fallback_dur
        out.append((t, end, v))
    return out

def add_interval_annotations(eaf: pympi.Elan.Eaf, tier: str, items: List[Tuple[int, int, str]]) -> List[str]:
    ann_ids: List[str] = []
    for s, e, v in items:
        if e <= s:
            continue
        ann_ids.append(eaf.add_annotation(tier, s, e, v))
    return ann_ids

def clip_intervals(items: List[Tuple[int, int, str]], lo: int, hi: int) -> List[Tuple[int, int, str]]:
    """
    Clip (start,end) to [lo, hi]. Drop intervals that become empty.
    """
    out: List[Tuple[int, int, str]] = []
    for s, e, v in items:
        s2 = max(lo, s)
        e2 = min(hi, e)
        if e2 > s2:
            out.append((s2, e2, v))
    return out

def safe_tier_id(s: str) -> str:
    """
    ELAN tier IDs should avoid spaces; keep it simple & stable.
    Your authors already look like 'User155', so this is mostly for safety.
    """
    s = (s or "").strip()
    if not s:
        return "User_"
    # replace spaces/tabs with underscore, remove weird chars
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^0-9A-Za-z_\-]", "_", s)
    return s

# ----------------------------
# Main
# ----------------------------
def main(html_path: str, eaf_in: str, eaf_out: str, manual_shift_sec: float = 0.0):
    html_rows = parse_html_4col(html_path)

    manual_shift_ms = int(manual_shift_sec * 1000)

    eaf = pympi.Elan.Eaf(eaf_in)
    extract_start, extract_end = get_extract_window(eaf)

    anchors = collect_eaf_anchors(eaf)
    offset = estimate_offset_ms(anchors, html_rows)

    ensure_tiers(eaf)

    safe_lo = max(0, extract_start - EDGE_MARGIN_MS)
    safe_hi = extract_end + EDGE_MARGIN_MS

    streamer_times: List[int] = []
    streamer_vals: List[str] = []

    user_events: dict = {}

    for r in html_rows:
        t_rel = r.t_ms_abs - offset
        if t_rel < safe_lo or t_rel > safe_hi:
            continue

        if r.speech_norm:
            streamer_times.append(t_rel)
            streamer_vals.append(r.speech_norm)

        if r.chat_html.strip() and (r.author or "").strip():
            user = safe_tier_id(r.author)

            # apply shift ONLY to chat
            t_chat = max(0, t_rel + manual_shift_ms)

            user_events.setdefault(user, []).append((t_chat, r.chat_with_emotes.strip()))

    # streamer tier
    streamer_intervals = make_intervals(streamer_times, streamer_vals, STREAMER_FALLBACK_DUR_MS)
    streamer_intervals = clip_intervals(streamer_intervals, safe_lo, safe_hi)
    add_interval_annotations(eaf, "STREAMER_HTML", streamer_intervals)

    # user tiers
    for user, evts in user_events.items():
        evts.sort(key=lambda x: x[0])

        if user not in eaf.get_tier_names():
            eaf.add_tier(user)

        times = [t for (t, _msg) in evts]
        msgs  = [m for (_t, m) in evts]

        intervals = make_intervals(times, msgs, CHAT_FALLBACK_DUR_MS)
        intervals = clip_intervals(intervals, safe_lo, safe_hi)
        add_interval_annotations(eaf, user, intervals)

    # 1) write to a temporary file first
    tmp_out = eaf_out + ".tmp.eaf"
    eaf.to_file(tmp_out)

    # 2) build the tier order
    base_order = []
    for t in eaf.get_tier_names():
        if t in user_events:
            continue
        base_order.append(t)

    user_order = list(user_events.keys())  # insertion order = first appearance
    final_order = base_order + user_order

    # keep only tiers that truly exist
    existing_tiers = set(eaf.get_tier_names())
    final_order = [t for t in final_order if t in existing_tiers]

    # 3) reorder tiers in XML and write final output
    reorder_tiers_in_eaf(tmp_out, eaf_out, final_order)

    # 4) cleanup temp
    try:
        os.remove(tmp_out)
    except OSError:
        pass

    print(f"CHAT_SHIFT(ms)={manual_shift_ms}")
    print(f"OFFSET(ms)={offset} | Extract=[{extract_start},{extract_end}] | Written: {eaf_out}")
    print(f"Manual chat shift applied: {manual_shift_sec} sec")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(
        description="Rebase 4-col HTML transcript/chat into an EAF extract and add tiers with emote-safe representation."
    )
    ap.add_argument("html_path", help="Input HTML file (4 columns: time,text,author,message)")
    ap.add_argument("eaf_in", help="Input EAF extract to enrich")
    ap.add_argument("eaf_out", help="Output EAF path")
    ap.add_argument(
        "--shift",
        type=float,
        default=0.0,
        help="Manual chat shift in seconds (e.g. --shift 4 or --shift -2.5)"
    )
    args = ap.parse_args()
    main(args.html_path, args.eaf_in, args.eaf_out, args.shift)
