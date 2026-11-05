# 05 — Manual Morphosyntactic and UD Syntactic Revision

## Overview

This stage follows the [automatic morphosyntactic annotation and dependency parsing stage](../04_automatic_morphosyntactic_nlp/). It covers the manual verification and correction of automatically generated annotations for the Sens-Ex corpus.

CoNLL-U files produced in stage 04 provide preliminary annotations. They are imported into [ArboratorGrew](https://arborator.grew.fr/), a collaborative tool for dependency annotation, where tokenization, lemmas, part-of-speech tags, morphological features, and syntactic dependency relations can be inspected and revised. See the [official ArboratorGrew documentation](https://arborator.github.io/arborator-documentation/) for tool instructions.

## Directory Contents

| Directory                           | Contents                                                                                                                                                                                                                                        |
|-------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`tutorials/`](tutorials/README.md) | Documentation of the tutorial, currently available in French, covering automatic morphosyntactic and syntactic processing, CoNLL-U import into ArboratorGrew, manual annotation, and an experimental SUD proposal for encoding coconstructions. |
| [`samples/`](samples/README.md)     | Automatic CoNLL-U baselines in `auto/` and ArboratorGrew exports in `annotator_revision_1/` and `annotator_revision_2/`.                                                                                                                        |

## Revision Workflow

1. Prepare the automatic CoNLL-U output from stage 04 and check its structure before import.
2. Import the file into ArboratorGrew and inspect the annotations alongside the source transcript and, when needed, the audiovisual material.
3. Manually revise tokenization, lemmas, UPOS tags, morphological features, dependency heads, and dependency relations according to the selected annotation conventions.
4. Review the corrected annotations, document unresolved cases and annotation decisions, and export the revised CoNLL-U files. Keep the automatic baseline in `samples/auto/` and place exported corrections in the appropriate revision directory. Record the annotation and review status separately.

## Experimental Encoding of Coconstructions

The tutorial also explores a proposal for encoding coconstructions using [Surface Syntactic Universal Dependencies (SUD)](https://surfacesyntacticud.org/). This is an experimental annotation proposal being tried for Sens-Ex.
