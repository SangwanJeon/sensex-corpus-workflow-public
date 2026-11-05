from pathlib import Path
import argparse
import re
import spacy
import stanza


def split_utterances(text):
    parts = [p.strip() for p in text.split("//")]
    return [p for p in parts if p]

def parse_txt_line(line):
    """
    First column = metadata to include in sent_id and # tier.
    Everything after the first whitespace block = text to parse.
    """

    line = line.strip()

    if not line:
        return None, None

    parts = line.split(maxsplit=1)

    if len(parts) == 1:
        return parts[0], ""

    first_column = parts[0].strip()
    text = parts[1].strip()

    return first_column, text

def enrich_with_spacy(text, nlp):
    doc = nlp(text)
    rows = []

    for i, tok in enumerate(doc, start=1):
        head = 0 if tok.head == tok else tok.head.i + 1
        deprel = "root" if tok.head == tok else tok.dep_

        rows.append([
            i,
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

    return rows


def enrich_with_stanza(text, nlp):
    doc = nlp(text)
    rows = []

    token_id = 1

    for sent in doc.sentences:
        for word in sent.words:
            rows.append([
                token_id,
                word.text,
                word.lemma or "_",
                word.upos or "_",
                word.xpos or "_",
                word.feats or "_",
                word.head,
                word.deprel or "_",
                "_",
                "_",
            ])
            token_id += 1

    return rows


def write_sentence(out, sent_id, source, line_id, tier, text, rows, tool_name):
    out.write(f"# sent_id = {sent_id}\n")
    out.write(f"# source = {source}\n")
    out.write(f"# tool = {tool_name}\n")
    out.write(f"# line_id = {line_id}\n")
    out.write(f"# tier = {tier}\n")
    out.write(f"# text = {text}\n")

    for row in rows:
        out.write("\t".join(map(str, row)) + "\n")

    out.write("\n")


def convert_txt_file(txt_path, out_path, tool_name, nlp):
    sent_counter = 1

    with open(txt_path, "r", encoding="utf-8") as f, open(out_path, "w", encoding="utf-8") as out:
        for line_id, line in enumerate(f, start=1):
            tier, text = parse_txt_line(line)

            if not text:
                continue

            utterances = split_utterances(text)

            for utt in utterances:
                sent_id = f"{txt_path.stem}_{tier}_{sent_counter:04d}"

                if tool_name == "spaCy":
                    rows = enrich_with_spacy(utt, nlp)
                elif tool_name == "Stanza":
                    rows = enrich_with_stanza(utt, nlp)
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")

                write_sentence(
                    out=out,
                    sent_id=sent_id,
                    source=txt_path.name,
                    line_id=line_id,
                    tier=tier,
                    text=utt,
                    rows=rows,
                    tool_name=tool_name,
                )

                sent_counter += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="Directory containing TXT files")
    parser.add_argument("output_dir", help="Directory where CoNLL-U files will be written")
    parser.add_argument(
        "--tools",
        nargs="+",
        default=["stanza"],
        choices=["spacy", "stanza"],
        help="NLP tools to use"
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Input TXT encoding, default: utf-8"
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    txt_files = sorted(input_dir.rglob("*.txt"))

    if not txt_files:
        print("No .txt files found.")
        return

    models = {}

    if "spacy" in args.tools:
        print("Loading spaCy...")
        models["spacy"] = spacy.load("fr_core_news_md")
        (output_dir / "spacy").mkdir(parents=True, exist_ok=True)

    if "stanza" in args.tools:
        print("Loading Stanza...")
        models["stanza"] = stanza.Pipeline(
            lang="fr",
            processors="tokenize,mwt,pos,lemma,depparse",
            tokenize_no_ssplit=True
        )
        (output_dir / "stanza").mkdir(parents=True, exist_ok=True)

    for txt_path in txt_files:
        print(f"Processing: {txt_path}")

        if "spacy" in args.tools:
            out_path = output_dir / "spacy" / txt_path.with_suffix(".conllu").name
            convert_txt_file(txt_path, out_path, "spaCy", models["spacy"])

        if "stanza" in args.tools:
            out_path = output_dir / "stanza" / txt_path.with_suffix(".conllu").name
            convert_txt_file(txt_path, out_path, "Stanza", models["stanza"])

    print("Done.")


if __name__ == "__main__":
    main()
