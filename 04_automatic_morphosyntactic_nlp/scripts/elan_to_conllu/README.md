# ELAN EAF to CoNLL-U

[`elan_to_conllu_all.py`](elan_to_conllu_all.py) converts annotations from a directory of EAF files into automatic French CoNLL-U drafts. It supports spaCy, Stanza, or both. The script searches input subdirectories recursively.

## Requirements

Use a Python environment compatible with spaCy, Stanza, and `pympi-ling`:

```sh
python3 -m pip install spacy stanza pympi-ling
```

Both NLP packages must be installed because the script imports both at startup, even when only one engine is selected. Package/model versions are not pinned; record your environment for reproducibility.

For spaCy, install the French model used by the script:

```sh
python3 -m spacy download fr_core_news_md
```

For Stanza, pre-download French models if needed:

```sh
python3 -c "import stanza; stanza.download('fr', processors='tokenize,mwt,pos,lemma,depparse')"
```

Model downloads require network access. See the official [spaCy model setup](https://spacy.io/usage/models) and [Stanza model download instructions](https://stanfordnlp.github.io/stanza/download_models.html). The script's language is fixed to French; there is no language option.

## Prepare the inputs

1. Place the EAF files in an input directory. Matching uses the lowercase `.eaf` extension.
2. Choose the transcription tiers intended for parsing, such as `SP1_trs` and `SP2_trs`. List the actual tier names in your files.
3. Check manual segmentation and transcription. Each annotation is treated as one unit unless its text contains `//`, which creates additional units. Literal `//` in URLs is also split.
4. Ensure input files have unique basenames, including across nested directories. Outputs are flattened by basename and existing files can be overwritten.

## Run

Run from this directory, replacing paths and tier names:

```sh
python3 elan_to_conllu_all.py /path/to/eaf /path/to/output --tiers SP1_trs SP2_trs --tools spacy
```

To use Stanza instead:

```sh
python3 elan_to_conllu_all.py /path/to/eaf /path/to/output --tiers SP1_trs SP2_trs --tools stanza
```

Use `--tools spacy stanza` for both engines; this is also the default when `--tools` is omitted. Use `--help` to display arguments.

If `--tiers` is omitted, all tiers except names ending in `_nonverbal` are included. This may include metadata, chat, screen text, and duplicate `_verbal`/`_trs` transcriptions. Supplying `--tiers` with no names also selects all eligible tiers. A requested tier that is absent produces no corresponding segments.

## Outputs

Each input creates `<output>/spacy/SOURCE.conllu` and/or `<output>/stanza/SOURCE.conllu`. Comments record source basename, tool, tier, annotation ordinal, IU index/count, and parent start/end times. When an annotation is split on `//`, every subunit inherits the entire parent interval; these are not separately aligned IU times.

Token rows contain FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, and DEPREL. DEPS and MISC are `_`; enhanced dependencies and original token-spacing information are not preserved.

## Review before manual revision

- Multiple model sentences can be combined into one output block with multiple roots. The EAF Stanza branch offsets heads across sentences, but this does not create a single valid UD tree.
- Stanza multiword-token surface range rows are omitted.
- Internal newlines/tabs and spaCy whitespace tokens can break serialization. Review and normalize source text before processing, preserving the source version.
- Files sharing a basename overwrite the same output. A failed batch is not recovered per file.
- Model versions and stable corpus identifiers are not recorded automatically.

Validate the serialized files against the [CoNLL-U format](https://universaldependencies.org/format.html), check their trees and source coverage, and review linguistic annotations before handing them to [stage 05](../../../05_manual_ud_revision/). A successful run does not establish annotation accuracy or UD validity.
