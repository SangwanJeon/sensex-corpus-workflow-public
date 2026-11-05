# TXT to CoNLL-U

[`txt_to_conllu.py`](txt_to_conllu.py) converts tier-prefixed TXT transcripts into automatic French CoNLL-U drafts using spaCy, Stanza, or both. The script searches input subdirectories recursively.

## Requirements

Use a Python environment compatible with spaCy and Stanza:

```sh
python3 -m pip install spacy stanza
```

Both packages must be installed because both are imported at startup. For spaCy, install the French model:

```sh
python3 -m spacy download fr_core_news_md
```

For Stanza, pre-download French models if needed:

```sh
python3 -c "import stanza; stanza.download('fr', processors='tokenize,mwt,pos,lemma,depparse')"
```

Model downloads require network access. See the official [spaCy model setup](https://spacy.io/usage/models) and [Stanza model download instructions](https://stanfordnlp.github.io/stanza/download_models.html). Versions are not pinned; record the package/model versions used. The script is fixed to French and has no language option.

## Input format

Use UTF-8 files with the lowercase `.txt` extension. Each nonempty line must contain a whitespace-free tier identifier, whitespace, and the text to parse:

```text
SP1_trs bonjour tout le monde // comment allez-vous
SP2_trs très bien merci
```

A tab may separate the tier from the text. There is no header row. `//` splits the text into separate units; it does not detect illocutionary boundaries automatically.

The parser treats everything after the first field as transcript text. Do not provide extra timestamp columns or ordinary plain text without a tier prefix: timestamps would be parsed as words, and a plain sentence's first word would be consumed as its tier. A one-field line is skipped. ELAN tabular exports and stage 03 ASR TXT output require preparation into this schema first.

Keep basenames unique across all input subdirectories and choose a separate output directory to avoid overwriting previous results.

## Run

Run from this directory with your input and output paths:

```sh
python3 txt_to_conllu.py /path/to/txt /path/to/output --tools spacy
```

To use Stanza:

```sh
python3 txt_to_conllu.py /path/to/txt /path/to/output --tools stanza
```

Stanza is the default when `--tools` is omitted. Use `--tools spacy stanza` to produce both sets. Use `--help` to display arguments.

The advertised `--encoding` option is currently ineffective: input is always opened as UTF-8. Convert other encodings before using the current script.

## Outputs

Each input creates `<output>/spacy/SOURCE.conllu` and/or `<output>/stanza/SOURCE.conllu`. Each line's `//`-separated units are written as individual blocks. Comments record sentence ID, source basename, tool, line number, tier, and text. Source timing is not retained as dedicated metadata.

Rows contain FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, and DEPREL. DEPS and MISC are `_`, so enhanced dependencies and token-spacing metadata are not preserved.

## Known issues and review

- **Conditional Stanza head error:** when a model document contains several sentences, token IDs continue across them but dependency heads remain sentence-local. Later dependencies can point into an earlier sentence. The configured `tokenize_no_ssplit=True` reduces exposure but does not repair this helper-function defect.
- Both engines can put multiple model sentences into one block, leaving multiple roots.
- Stanza multiword-token surface range rows are omitted, and spacing information is discarded.
- Files with identical basenames overwrite the same output, and failures can leave partial files. A missing input directory can be reported as no TXT files found rather than an error.
- There is no automatic structural-validation gate or full model/configuration provenance record.

These are automatic drafts. Validate against the [CoNLL-U format](https://universaldependencies.org/format.html), verify source coverage and tree structure, and review linguistic annotations before the [manual UD revision stage](../../../05_manual_ud_revision/).
