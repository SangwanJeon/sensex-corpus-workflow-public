# 04 — Automatic Morphosyntactic Annotation and Dependency Parsing

## Overview

This stage covers the automatic morphosyntactic annotation and dependency parsing of the Sens-Ex corpus.

Python scripts developed for Sens-Ex convert annotated linguistic data from **ELAN (`.eaf`) or text (`.txt`) files into CoNLL-U format**, using NLP libraries to enrich the data with linguistic annotations.

The processing includes:

1. **Tokenization:** identification of tokens in the input text.
2. **Multiword-token analysis:** identification and expansion of multiword tokens, particularly relevant to French contractions such as *au* (*à + le*) and *du* (*de + le*).
3. **Lemmatization:** identification of the canonical form of each word.
4. **Morphosyntactic annotation:** assignment of Universal Part-of-Speech (UPOS) tags and morphological features.
5. **Dependency parsing:** automatic identification of syntactic dependency relations following the Universal Dependencies (UD) framework.

These operations are performed using two NLP libraries:

- [Stanza](https://stanfordnlp.github.io/stanza/) — Stanford NLP library providing tokenization, multiword-token expansion, lemmatization, morphosyntactic tagging, and dependency parsing.
- [spaCy](https://spacy.io/) — NLP library providing tokenization, lemmatization, part-of-speech tagging, morphological analysis, and dependency parsing.

The scripts generate **CoNLL-U files containing the resulting annotations**, rather than separate files for each processing operation.

For detailed script descriptions, usage instructions, and a comparison of the EAF and TXT conversion procedures, see the [EAF converter instructions](elan_to_conllu/README.md) and [TXT converter instructions](txt_to_conllu/README.md).

## Methodological Considerations

The scripts do not perform automatic linguistic segmentation into illocutionary units (IUs). In Sens-Ex, IU boundaries were established and manually verified in ELAN before automatic processing.

The scripts process these pre-established units, including subdivisions explicitly marked using `//` where applicable.

The generated CoNLL-U files contain **preliminary automatic annotations** that require verification and manual revision.

See [05 — Manual UD Revision](../../05_manual_ud_revision/) for the subsequent annotation revision stage.

## EAF/TXT to CoNLL-U Conversion Scripts

### Available Scripts

| Feature                         | [`elan_to_conllu_all.py`](elan_to_conllu/elan_to_conllu_all.py) | [`txt_to_conllu.py`](txt_to_conllu/txt_to_conllu.py) |
|---------------------------------|--------------------------------------------------|----------------------------------------|
| Input format                    | ELAN (`.eaf`)                                    | Text (`.txt`)                          |
| Output format                   | CoNLL-U (`.conllu`)                              | CoNLL-U (`.conllu`)                    |
| NLP libraries                   | Stanza / spaCy                                   | Stanza / spaCy                         |
| Default NLP processing          | Both libraries                                   | Stanza                                 |
| Language                        | French                                           | French                                 |
| Tokenization                    | Yes                                              | Yes                                    |
| Multiword-token processing      | Stanza: enabled; export incomplete               | Stanza: enabled; export incomplete     |
| Lemmatization                   | Yes                                              | Yes                                    |
| UPOS tagging                    | Yes                                              | Yes                                    |
| Morphological features          | Yes                                              | Yes                                    |
| Basic UD dependency parsing     | Yes                                              | Yes                                    |
| Illocutionary-unit segmentation | Uses existing annotations and `//` delimiters    | Uses existing `//` delimiters          |
| Annotation tiers                | Selectable                                       | Read from the first field of each line |
| Timing information              | EAF parent-annotation timestamps                 | Not retained as dedicated metadata     |

## Important Notes

Both scripts generate automatically annotated CoNLL-U files that combine tokenization, lemmatization, morphosyntactic annotation, and basic dependency parsing.

**Multiword-token processing:** Stanza's multiword-token expansion is enabled, but the current exporters omit CoNLL-U range lines representing the original surface tokens.

**Input requirements:** The TXT converter expects a specific tier-prefixed text format. It should not be used directly with arbitrary plain-text transcriptions without checking the input structure.

**Segmentation:** Neither script automatically identifies illocutionary units. Segmentation must be established beforehand.

**Validation:** The generated annotations require verification before being treated as valid UD data or imported for manual revision.

## Limitations

The scripts were developed for the specific requirements of Sens-Ex and are configured for French-language processing.

Although Stanza's multiword-token processor is enabled, the current CoNLL-U exporters do not preserve all multiword-token surface representations. Consequently, the exported files should not be considered complete or validated UD annotations without further verification.

Additional implementation-specific limitations are documented in the [EAF converter README](elan_to_conllu/README.md) and [TXT converter README](txt_to_conllu/README.md).
