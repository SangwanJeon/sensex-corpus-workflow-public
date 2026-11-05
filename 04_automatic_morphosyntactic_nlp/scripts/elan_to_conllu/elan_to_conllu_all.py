#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## python3 elan_to_conllu_all.py \
##  "/path/to/eaf_directory" \
##  "/path/to/output_directory"
### python3 elan_to_conllu_all.py \
###  "/path/to/eaf_directory" \
###  "/path/to/output_directory" \
###  --tools stanza
####python3 elan_to_conllu_all.py \
####  "/path/to/eaf_directory" \
####  "/path/to/output_directory" \
####  --tiers SP1_trs SP2_trs User1 User2 \
####  --tools stanza

from pathlib import Path
from pympi.Elan import Eaf
import argparse
import re
import spacy
import stanza


NONVERBAL_SUFFIX = "_nonverbal"
IU_BOUNDARY_RE = re.compile(r"\s*//\s*")


def ms_to_time(ms):
    s = ms / 1000
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h:02d}:{m:02d}:{sec:06.3f}"


def split_into_illocutionary_units(text):
    return [
        unit.strip()
        for unit in IU_BOUNDARY_RE.split(text)
        if unit.strip()
    ]


def extract_elan_segments(eaf_path, tiers=None):
    eaf = Eaf(str(eaf_path))
    segments = []

    for tier in eaf.get_tier_names():
        if tiers and tier not in tiers:
            continue

        if tier.lower().endswith(NONVERBAL_SUFFIX):
            continue

        for annotation_index, (start, end, text) in enumerate(
            eaf.get_annotation_data_for_tier(tier),
            start=1,
        ):
            text = (text or "").strip()
            if not text:
                continue

            iu_units = split_into_illocutionary_units(text)
            iu_count = len(iu_units)

            for iu_index, iu_text in enumerate(iu_units, start=1):
                segments.append({
                    "tier": tier,
                    "start": start,
                    "end": end,
                    "text": iu_text,
                    "original_text": text,
                    "annotation_index": annotation_index,
                    "iu_index": iu_index,
                    "iu_count": iu_count,
                })

    segments.sort(
        key=lambda seg: (
            seg["start"],
            seg["end"],
            seg["tier"],
            seg["annotation_index"],
            seg["iu_index"],
        )
    )

    return segments


def enrich_with_spacy(segments, nlp):
    enriched = []

    for i, seg in enumerate(segments, start=1):
        doc = nlp(seg["text"])
        rows = []

        for j, tok in enumerate(doc, start=1):
            head = 0 if tok.head == tok else tok.head.i + 1
            deprel = "root" if tok.head == tok else (tok.dep_ or "_")

            rows.append([
                j,
                tok.text,
                tok.lemma_ or "_",
                tok.pos_ or "_",
                tok.tag_ or "_",
                str(tok.morph) if tok.morph else "_",
                head,
                deprel,
                "_",
                "_",
            ])

        enriched.append((i, seg, rows))

    return enriched


def enrich_with_stanza(segments, nlp):
    enriched = []

    for i, seg in enumerate(segments, start=1):
        doc = nlp(seg["text"])
        rows = []
        token_offset = 0

        for sent in doc.sentences:
            for word in sent.words:
                token_id = token_offset + word.id
                head = 0 if word.head == 0 else token_offset + word.head

                rows.append([
                    token_id,
                    word.text,
                    word.lemma or "_",
                    word.upos or "_",
                    word.xpos or "_",
                    word.feats or "_",
                    head,
                    word.deprel or "_",
                    "_",
                    "_",
                ])

            token_offset += len(sent.words)

        enriched.append((i, seg, rows))

    return enriched


def sanitize_id_component(value):
    value = str(value).strip()
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"[^0-9A-Za-z_.-]", "_", value)
    return value or "tier"


def write_conllu(enriched, eaf_path, out_path, tool_name):
    stem = sanitize_id_component(eaf_path.stem)

    with open(out_path, "w", encoding="utf-8") as out:
        for i, seg, rows in enriched:
            tier_id = sanitize_id_component(seg["tier"])
            sent_id = (
                f"{stem}_{i:04d}_{tier_id}"
                f"_ann{seg['annotation_index']:04d}"
                f"_iu{seg['iu_index']:02d}"
            )

            out.write(f"# sent_id = {sent_id}\n")
            out.write(f"# source = {eaf_path.name}\n")
            out.write(f"# tool = {tool_name}\n")
            out.write(f"# tier = {seg['tier']}\n")
            out.write(f"# annotation_index = {seg['annotation_index']}\n")
            out.write(f"# iu_index = {seg['iu_index']}\n")
            out.write(f"# iu_count = {seg['iu_count']}\n")
            out.write(f"# start = {ms_to_time(seg['start'])}\n")
            out.write(f"# end = {ms_to_time(seg['end'])}\n")
            out.write(f"# text = {seg['text']}\n")

            if seg["iu_count"] > 1:
                out.write(f"# original_annotation = {seg['original_text']}\n")

            for row in rows:
                out.write("\t".join(map(str, row)) + "\n")

            out.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Convert all ELAN tiers except *_nonverbal tiers to CoNLL-U. "
            "Annotations containing // are split into separate illocutionary units."
        )
    )
    parser.add_argument(
        "input_dir",
        help="Directory containing EAF files"
    )
    parser.add_argument(
        "output_dir",
        help="Directory where CoNLL-U outputs will be written"
    )
    parser.add_argument(
        "--tiers",
        nargs="*",
        default=None,
        help=(
            "Optional specific ELAN tiers to process. "
            "Tiers ending in _nonverbal remain excluded."
        )
    )
    parser.add_argument(
        "--tools",
        nargs="+",
        default=["spacy", "stanza"],
        choices=["spacy", "stanza"],
        help="NLP tools to use"
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    eaf_files = sorted(input_dir.rglob("*.eaf"))

    if not eaf_files:
        print("No .eaf files found.")
        return

    models = {}

    if "spacy" in args.tools:
        print("Loading spaCy...")
        models["spacy"] = spacy.load("fr_core_news_md")

    if "stanza" in args.tools:
        print("Loading Stanza...")
        models["stanza"] = stanza.Pipeline(
            lang="fr",
            processors="tokenize,mwt,pos,lemma,depparse",
            tokenize_no_ssplit=True
        )

    for tool in args.tools:
        (output_dir / tool).mkdir(parents=True, exist_ok=True)

    for eaf_path in eaf_files:
        print(f"Processing: {eaf_path}")

        segments = extract_elan_segments(
            eaf_path,
            tiers=args.tiers
        )

        if not segments:
            print(f"  No matching segments found in {eaf_path.name}")
            continue

        split_annotation_count = len({
            (seg["tier"], seg["annotation_index"])
            for seg in segments
            if seg["iu_count"] > 1
        })

        print(
            f"  Extracted {len(segments)} IU(s); "
            f"{split_annotation_count} annotation(s) contained //"
        )

        if "spacy" in args.tools:
            enriched = enrich_with_spacy(segments, models["spacy"])
            out_path = output_dir / "spacy" / f"{eaf_path.stem}.conllu"
            write_conllu(enriched, eaf_path, out_path, "spaCy")
            print(f"  Written: {out_path}")

        if "stanza" in args.tools:
            enriched = enrich_with_stanza(segments, models["stanza"])
            out_path = output_dir / "stanza" / f"{eaf_path.stem}.conllu"
            write_conllu(enriched, eaf_path, out_path, "Stanza")
            print(f"  Written: {out_path}")

    print("Done.")


if __name__ == "__main__":
    main()
