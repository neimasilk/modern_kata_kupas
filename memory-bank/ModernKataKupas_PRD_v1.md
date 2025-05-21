# **Product Requirement Document: ModernKataKupas**

Version: 1.0  
Creation Date: May 21, 2025  
Author: Gemini (based on requirements from Mukhlis Amien)  
Project Goal: To develop a robust, rule-based Indonesian sub-word morphological separator and reconstructor ("ModernKataKupas") that can be used as a standalone tool or a pre-processing library for NLP research and applications, particularly for enhancing the performance of LLMs and NMT systems with Indonesian language.

## **1\. Introduction**

### **1.1 Purpose**

This document outlines the product requirements for "ModernKataKupas," an advanced rule-based morphological separator for Bahasa Indonesia. The tool aims to decompose Indonesian words into their constituent morphemes (root word, prefixes, suffixes, and markers for processes like reduplication) and accurately reconstruct the original word from these components.

### **1.2 Problem Statement**

Standard sub-word tokenization methods (e.g., BPE, SentencePiece) used in modern NLP, especially with Large Language Models (LLMs), often produce segments that do not align with linguistic morpheme boundaries in morphologically rich languages like Indonesian. This can lead to:

* Reduced semantic interpretability of tokens.  
* Challenges in handling the vast number of inflected word forms, contributing to vocabulary sparseness.  
* Difficulties for models in learning systematic morphological patterns.  
* Suboptimal performance in low-resource scenarios where data-driven tokenizers cannot be effectively trained.

ModernKataKupas aims to address these issues by providing a linguistically informed segmentation that preserves morphological information.

### **1.3 Target Users**

1. **NLP Researchers:** Investigating Indonesian linguistics, morphology, and its impact on NLP models.  
2. **Machine Learning Engineers/Practitioners:** Developing or fine-tuning models (LLMs, NMT systems) for Indonesian language tasks.  
3. **Linguists and Language Educators:** Exploring Indonesian word structure or creating educational tools.  
4. **Software Developers:** Integrating Indonesian morphological analysis into applications.

### **1.4 Scope**

* **In Scope:**  
  * Development of a Python library for morphological separation and reconstruction.  
  * Handling of common Indonesian prefixes, suffixes, confixes, and possessive/particle clitics.  
  * Systematic handling of various types of reduplication (dwilingga, dwipurwa, dwilingga salin suara, affixed reduplication).  
  * Implementation of rules for common morphophonemic changes (e.g., nasal assimilation/elision).  
  * Maintenance of an extensible root word dictionary and affix rule set.  
  * Ability to process individual words and lists of words.  
* **Out of Scope (for V1.0, but potential future work):**  
  * Full syntactic parsing or deep semantic analysis.  
  * Real-time, context-dependent disambiguation of highly ambiguous segmentations (beyond rule-based heuristics).  
  * A graphical user interface (GUI).  
  * Direct training of neural models (the tool is a pre-processor/library).

## **2\. Goals and Objectives**

* **Primary Goal:** To create a highly accurate and reliable rule-based Indonesian morphological separator and reconstructor.  
* **Objectives:**  
  1. **Accuracy:** Achieve high precision and recall in identifying correct morpheme boundaries and canonical affix forms.  
  2. **Coverage:** Handle a wide range of common Indonesian morphological phenomena.  
  3. **Reconstructibility:** Ensure that segmented words can be perfectly reconstructed to their original form.  
  4. **Vocabulary Reduction:** Demonstrate significant reduction in effective vocabulary size when applied to Indonesian text corpora.  
  5. **Usability:** Provide a simple and intuitive API for use as a Python library.  
  6. **Maintainability & Extensibility:** Design the system with clear, modular code and easily updatable rule sets and dictionaries.  
  7. **Performance:** While accuracy is paramount, the tool should be reasonably efficient for processing moderately sized text datasets.

## **3\. User Stories (Illustrative)**

* **As an NLP researcher,** I want to segment Indonesian text into meaningful morphemes so that I can analyze morphological patterns and use these segments as input for my models.  
* **As an ML engineer,** I want to pre-process my Indonesian training data using ModernKataKupas to potentially improve my LLM's performance on downstream tasks like sentiment analysis or text classification.  
* **As a linguist,** I want to use ModernKataKupas to quickly analyze the structure of complex Indonesian words and verify morphological rules.  
* **As a developer,** I want to integrate ModernKataKupas into my application to normalize Indonesian words for better search or indexing.

## **4\. Functional Requirements**

### **4.1 Core Segmentation Functionality**

* **FR1.1 Input:** The system shall accept a single Indonesian word (string) or a list of Indonesian words as input.  
* **FR1.2 Output Format:** For each input word, the system shall output a string representing the segmented morphemes, separated by a tilde (\~). Canonical forms of affixes should be used. Special markers for reduplication must be included.  
  * Example: mempermainkan \-\> meN\~per\~main\~kan  
  * Example: buku-bukunya \-\> buku\~ulg\~nya  
  * Example: lelaki \-\> laki\~rp (or ul\_purwa\~laki)  
* **FR1.3 Normalization:** The system shall perform initial text normalization (lowercase, basic punctuation handling) on input words before processing.  
* **FR1.4 Root Word Identification:** The system shall utilize an underlying Indonesian stemmer (e.g., PySastrawi) and an up-to-date root word dictionary to identify the base form of a word.  
* **FR1.5 Affix Identification:**  
  * **FR1.5.1 Prefixes:** The system must identify and separate standard Indonesian prefixes (e.g., meN-, ber-, di-, ter-, peN-, per-, se-, ke-) including their allomorphs and associated morphophonemic changes (nasal assimilation, elision). Layered prefixes (e.g., memper-, keber-) must be handled.  
  * **FR1.5.2 Suffixes:** The system must identify and separate standard Indonesian derivational suffixes (e.g., \-kan, \-i, \-an).  
  * **FR1.5.3 Clitics:** The system must identify and separate inflectional particles (-lah, \-kah, \-tah, \-pun) and possessive pronouns (-ku, \-mu, \-nya), respecting their typical order of appearance after derivational suffixes.  
  * **FR1.5.4 Confixes:** Confixes (e.g., ke-an, per-an, peN-an, ber-an) shall be segmented into their constituent prefix and suffix parts relative to the root word.  
* **FR1.6 Reduplication Handling:**  
  * **FR1.6.1 Dwilingga (Full Reduplication):** E.g., rumah-rumah. Output: rumah\~ulg.  
  * **FR1.6.2 Dwilingga with Affixes:** E.g., bermain-main. Output: ber\~main\~ulg. E.g., rumah-rumahan. Output: rumah\~ulg\~an.  
  * **FR1.6.3 Dwilingga Salin Suara (Full Reduplication with Phonetic Change):** E.g., bolak-balik. Output: bolak\~rs(\~balik).  
  * **FR1.6.4 Dwipurwa (Partial Reduplication \- Initial Syllable):** E.g., lelaki. Output: laki\~rp.  
* **FR1.7 Loanword Affixation:** The system should attempt to segment common Indonesian affixes from recognizable loanword bases (e.g., di-update \-\> di\~update). This may require an auxiliary list of common loanwords.  
* **FR1.8 Ambiguity Handling (Basic):** For words with multiple valid rule-based segmentations, the system should (for V1.0) prioritize based on:  
  1. Longest valid root match from the dictionary.  
  2. Predefined rule precedence.  
     If still ambiguous, it may output the most probable one or a list (TBD based on complexity).

### **4.2 Reconstruction Functionality**

* **FR2.1 Input:** A segmented Indonesian word string (as produced by FR1.2).  
* **FR2.2 Output:** The original, unsegmented Indonesian word string.  
* **FR2.3 Morphophonemic Application:** The reconstruction process must correctly re-apply morphophonemic rules when combining affixes and roots (e.g., meN\~ \+ pukul \-\> memukul).  
* **FR2.4 Reduplication Reconstruction:** Correctly reconstruct all supported types of reduplication from their markers.

### **4.3 Configuration and Data Management**

* **FR3.1 Root Word Dictionary:** The system shall use an external, easily updatable root word dictionary file (e.g., text file).  
* **FR3.2 Affix Rule Repository:** Morphological rules (affix definitions, allomorphs, conditions, morphophonemic changes) shall be stored in an external, structured, human-readable format (e.g., JSON or YAML) for maintainability and extensibility.  
* **FR3.3 String Alignment:** The system will use an implementation of the Needleman-Wunsch algorithm for aligning word forms with their roots to guide affix identification.

## **5\. Non-Functional Requirements**

* **NFR1. Accuracy:** The primary goal is high accuracy in segmentation and reconstruction, benchmarked against a manually annotated gold standard dataset. Target \>95% accuracy on common word structures.  
* **NFR2. Performance:**  
  * **NFR2.1 Segmentation Speed:** Should be efficient enough for batch processing of large text files (e.g., target X words/second on standard hardware).  
  * **NFR2.2 Memory Usage:** Should have reasonable memory footprint, especially when loading dictionaries and rules.  
* **NFR3. Maintainability:** Code should be well-documented, modular, and follow Python best practices. Rules and dictionaries should be externalized for easy updates.  
* **NFR4. Extensibility:** The system architecture should allow for the addition of new morphological rules, affix patterns, and dictionary entries with relative ease.  
* **NFR5. Testability:** Comprehensive unit tests and integration tests must cover all core functionalities and morphological rules.  
* **NFR6. Usability (as a library):**  
  * Simple and intuitive Python API.  
  * Clear documentation for installation and usage.  
  * Packaged for easy installation (e.g., via pip).  
* **NFR7. Reliability:** The tool should consistently produce the same output for the same input and handle edge cases gracefully (e.g., empty input, non-Indonesian words).

## **6\. Success Metrics (for the Tool)**

* **SM1. Segmentation Accuracy:** Percentage of words correctly segmented into morphemes compared to a gold-standard annotated dataset.  
* **SM2. Reconstruction Accuracy:** Percentage of segmented words correctly reconstructed to their original form.  
* **SM3. Vocabulary Reduction Rate:** Achieved percentage reduction in unique token types when applied to benchmark Indonesian corpora, compared to word-level and standard sub-word tokenizers.  
* **SM4. OOV Rate Reduction:** Reduction in OOV rates on test sets when using the segmented vocabulary.  
* **SM5. Performance on Downstream NLP Tasks (as part of the research paper):** Improvement in metrics (BLEU, F1, Accuracy, etc.) when ModernKataKupas is used as a pre-processor for LLMs/NMT systems compared to baselines.  
* **SM6. Processing Speed:** Words processed per second.

## **7\. Future Considerations (Post V1.0)**

* Integration of statistical models for disambiguating highly ambiguous segmentations.  
* Support for more granular morphological features/tags as output.  
* Handling of a wider range of informal language and neologisms.  
* Development of a GUI or web-based demo.  
* Interactive rule editor/tester.

This PRD will guide the development of the "ModernKataKupas" tool. It will be a living document and may be updated as the project progresses and new insights are gained.