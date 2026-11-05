# 04 — Automatic Morphosyntactic Annotation and Dependency Parsing

This directory contains two converters for generating automatic CoNLL-U drafts from Sens-Ex transcripts. Both use French spaCy and/or Stanza models for tokenization, lemmatization, part-of-speech tagging, morphological analysis, and basic dependency parsing.

| Directory                                     | Input and purpose                                                                               |
|-----------------------------------------------|-------------------------------------------------------------------------------------------------|
| [`scripts/elan_to_conllu/`](scripts/elan_to_conllu/README.md) | Convert selected ELAN EAF annotations, retaining tier and parent-annotation timing information. |
| [`scripts/txt_to_conllu/`](scripts/txt_to_conllu/README.md)   | Convert TXT transcripts whose lines begin with a tier identifier followed by the text to parse. |

Each directory contains its script and instructions for dependencies, input preparation, execution, outputs, and known limitations. The scripts split existing `//` markers; they do not perform automatic illocutionary segmentation. Their model language is currently fixed to French.

Outputs require structural validation and linguistic review before the [manual UD revision stage](../05_manual_ud_revision/). The local report `docs/AUDIT_04.md` (relative to the repository root) records the audit findings.
