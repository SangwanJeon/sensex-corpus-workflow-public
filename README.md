# Sens-Ex Corpus Workflow

Sens-Ex Corpus Workflow preserves, organizes, documents, and shares the
scripts and methodological resources developed for the construction and processing
of the Sens-Ex multimodal computer-mediated communication (CMC) corpus.

Its primary purpose is to document the actual corpus construction workflow, including
the technical procedures that reflect the underlying methodological framework, and manual 
interventions involved.

## Situating the Corpus Construction Workflow within the Overall Sens-Ex Research Project

**[Sens-Ex – Sensationalism and Discursive Excess in the Post-Digital Era](https://olindinum.huma-num.fr/en/research/research-projects/)** (a structuring
research project supported by the Maison Européenne des Sciences de l'Homme et de la Société 
Lille Nord de France, 2025–2027) aims to identify the formal features that characterize 
sensationalist discourse across a wide range of discursive genres.

The methodological framework combines two complementary approaches: 
**community-based corpus construction** and **perception-based investigation**.

The **community-based approach** involves university students enrolled in sociolinguistics courses 
at the University of Lille, their instructor, and members of the research team. 
By involving participants with diverse digital practices and experiences, this approach seeks to 
mitigate the influence of personalized recommendation algorithms and platform-specific information 
environments on data selection. It thereby contributes to broadening the range of CMC platforms, 
communicative situations, and discursive genres represented in the corpus.

The **perception-based approach** builds on the understanding of discursive excess as a perception-dependent 
and folk-linguistic notion (Preston, 1993, 2001, 2018). 
Rather than relying exclusively on predefined linguistic criteria, this approach incorporates sociolinguistic 
perception surveys addressed to a broader public. These surveys constitute a central component of the research 
framework, allowing researchers to investigate how discursive excess is perceived and evaluated by language users.

## Repository Architecture

See the [public repository architecture and complete file inventory](docs/repository_architecture.md) for the directory structure, included document names, script and sample inventories, and full GitHub URLs.

## Principal stages

Following the participatory identification, evaluation, and selection of excerpts within the broader Sens-Ex 
research framework, the technical corpus construction workflow is organized into five principal stages:

| Directory                                                                      | Intended scope                                                                                                                                                                                                                      |
|--------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [01_data_collection](01_data_collection/README.md)                             | Collection of audiovisual and interactional data from CMC platforms (YouTube, TikTok, Twitch, and X), including the retrieval of source media and associated interactional content.                                                 |
| [02_corpus_metadata_construction](02_corpus_metadata_construction/README.md)   | Construction and documentation of corpus metadata, including platform-specific information, content production and dissemination metrics, communicative contexts, and semiotic modalities.                                          |
| [03_data_preparation](03_data_preparation/README.md)                           | Media preparation (including WAV extraction), manual and/or automatic transcription, ELAN annotation, transcription standardization, segmentation into illocutionary units, and integration and temporal alignment of Twitch chats. |
| [04_automatic_morphosyntactic_nlp](04_automatic_morphosyntactic_nlp/README.md) | Conversion of ELAN (EAF) files into CoNLL-U, followed by automatic tokenization, lemmatization, morphosyntactic tagging (UPOS), and dependency parsing according to the Universal Dependencies (UD) framework.                      |
| [05_manual_ud_revision](05_manual_ud_revision/README.md)                       | Manual revision and validation of automatically generated morphosyntactic and dependency annotations using ArboratorGrew, including documentation of annotation procedures and revised CoNLL-U data.                                 |

These five stages constitute the organizational framework of the **Sens-Ex Corpus Workflow** repository. 

They document the technical and methodological operations involved in transforming selected CMC materials into 
structured, annotated corpus data.

The workflow documented here begins with data collection, while the preceding activities—identification of 
potential excerpts, collaborative evaluation, perception-based investigation, and collective selection—belong 
to the broader participatory Sens-Ex research framework.

The repository documents both automated procedures and manual methodological interventions. Although the five 
directories reflect the principal stages of corpus construction, they should not be interpreted as a fully 
automated, end-to-end pipeline. Certain operations require human intervention, and the historical use, execution 
order, and applicability of individual scripts must be established through the available documentation and 
supporting evidence. 

## Tutorials for Open-Source Softwares, Annotation Tools, and Existing Pipelines

The construction of the Sens-Ex corpus required the use of several existing open-source software applications, annotation tools, and processing pipelines, as no single tool could meet all the methodological and technical requirements of data collection, preparation, corpus construction, and linguistic annotation.

To document how these tools were used within the Sens-Ex workflow and share the practical knowledge acquired through their application, members of the research team developed a series of tutorials.

These tutorials aim to provide guidance ranging from an initial introduction to each tool to its application to specific research tasks. They document:

- The basic functionalities of the tools and how to get started.
- Their practical applications to specific stages of Sens-Ex corpus construction.
- Their technical and methodological limitations, where appropriate.
- The procedures, adaptations, or complementary tools used to bridge the gap between researchers' needs and the functionalities available.

The tutorials reflect the team's practical experience and methodological decisions. They are intended to help colleagues understand, reproduce where feasible, or adapt the procedures to their own research contexts.

## Scripts and Their Limitations

The Python scripts developed for Sens-Ex are **task-specific resources**, created or adapted to address particular requirements encountered during corpus construction.

They may rely on specific file structures, metadata schemas, languages, local paths, software dependencies, model versions, or manual operations. Some scripts have overlapping functionalities or represent successive stages of development.

Each script should therefore be considered in relation to its original purpose, documented usage, dependencies, and known limitations. Its inclusion in this repository does not imply that it has been independently validated or is directly reusable in other research contexts without adaptation.

## Public Repository Snapshot

This repository starts from a reviewed snapshot of the current workflow resources with a new Git history. Earlier audio recordings and internal audit documents are excluded. Public pilot metadata omit student contributor names, institutional sharing fields, and historical filenames containing student names. Original working records and historical commits remain in a separate private repository.
