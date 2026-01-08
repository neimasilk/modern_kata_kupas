# ModernKataKupas: A Rule-Based Morphological Segmenter for Indonesian
## Paper Draft

---

## Abstract

Indonesian, an Austronesian language spoken by over 270 million people, features rich derivational morphology with productive affixation and reduplication patterns. However, open-source morphological analysis tools for Indonesian remain limited, with most focusing solely on stemming rather than full morpheme segmentation. This paper presents ModernKataKupas, a rule-based morphological segmenter that decomposes Indonesian words into their constituent morphemes while preserving reconstructibility. Our system employs a two-strategy segmentation approach—prefix-first and suffix-first—combined with comprehensive morphophonemic rules and a 29,932-word root dictionary. Evaluation on a 191-word gold standard test set covering 14 morphological categories yields 76.96% word accuracy and 84.33% morpheme F1 score, significantly outperforming the baseline Sastrawi stemmer (2.09% accuracy). An ablation study reveals dictionary size as the most critical factor, contributing +69.63% accuracy improvement from minimal to full lexicon. ModernKataKupas achieves 100% accuracy on possessive markers and passive voice prefixes, while reduplication with phonetic change remains challenging (44.44% accuracy). The system is released as open-source software, providing a foundation for Indonesian NLP applications.

**Keywords:** Morphological segmentation, Indonesian language processing, Rule-based NLP, Computational linguistics

---

## 1. Introduction

### 1.1 Background

Indonesian (Bahasa Indonesia) is the official language of Indonesia, spoken by over 270 million people as a first or second language. As an Austronesian language, Indonesian exhibits highly productive morphology with four types of affixes: prefixes (awalan), suffixes (akhiran), circumfixes (konfiks), and infixes (sisipan). Words are formed through systematic affixation to root words (kata dasar), with complex morphophonemic changes at morpheme boundaries.

Consider the word *mempertanggungjawabkan* "to hold accountable," which decomposes into:
- *meN-* (actor focus prefix, allomorph *menge-* before *t*)
- *per-* (causative prefix)
- *tanggung* (root: "responsible")
- *-jawab* (root compound: "answer")
- *-kan* (benefactive suffix)

This morphological complexity poses challenges for natural language processing (NLP) tasks. Proper morphological analysis enables:
- More efficient tokenization for language models
- Improved stemming and lemmatization
- Better feature extraction for text classification
- Enhanced machine translation between Indonesian and other languages

### 1.2 The Problem

Existing open-source tools for Indonesian morphology focus primarily on **stemming**—removing affixes to extract root words—rather than **morphological segmentation**—identifying all constituent morphemes. The most widely used tool, PySastrawi, implements a stemming algorithm but does not provide full morpheme breakdown or reconstructibility.

This gap is significant because:
1. **Loss of linguistic information:** Stemming discards affixes that carry grammatical and semantic meaning
2. **No reconstructibility:** Original words cannot be reconstructed from stemmed forms
3. **Limited application scope:** Stemming alone is insufficient for advanced NLP tasks requiring morpheme-level analysis

### 1.3 Our Contribution

We present **ModernKataKupas**, a rule-based morphological segmenter for Indonesian that:

1. **Decomposes words into morphemes** with full linguistic annotation (prefixes, suffixes, reduplication markers)
2. **Maintains reconstructibility**—original words can be reconstructed from segmented forms
3. **Handles complex phenomena** including morphophonemic allomorphy, reduplication (dwilingga, dwipurwa, salin suara), and loanword affixation
4. **Achieves strong performance**—76.96% word accuracy on a comprehensive gold standard
5. **Is open-source** and extensible for research and production use

Additionally, we contribute:
- A **gold standard test set** of 191 words covering 14 morphological categories, generated with assistance from DeepSeek API
- An **ablation study** demonstrating dictionary size as the dominant factor (+69.63% impact)
- **Per-category analysis** identifying strengths (100% on possessives) and weaknesses (44% on phonetic reduplication)

### 1.4 Paper Organization

The remainder of this paper is organized as follows: Section 2 reviews related work on Indonesian morphological analysis. Section 3 describes Indonesian morphology and the challenges it presents. Section 4 presents the ModernKataKupas system architecture and algorithms. Section 5 describes our experimental setup, including gold standard generation and evaluation metrics. Section 6 presents results and analysis. Section 7 discusses limitations and future work. Section 8 concludes.

---

## 2. Related Work

### 2.1 Indonesian Morphological Analysis

**Sastrawi** (Artiwi, 2013) is the most widely used open-source Indonesian stemmer. It implements a stemming algorithm based on the "Bahasa" stemming algorithm (Asian, 2007) but does not provide full morphological segmentation. Sastrawi only returns root words, discarding information about which affixes were removed.

**MorphInd** (Larasati, 2012) is a joint morphological analyzer and part-of-speech tagger for Indonesian. It uses a conditional random field (CRF) approach with morphological features. However, MorphInd is not publicly available as a library and requires significant computational resources.

**Indonesian NLP Library** (William, 2020) provides basic text preprocessing but lacks comprehensive morphological analysis.

### 2.2 Morphological Segmentation for Other Languages

Morphological segmentation has been extensively studied for languages with rich morphology:

- **Arabic:** Habash (2010), multiple systems using morphological databases and statistical models
- **Turkish:** Çetinoğlu (2012), statistical and rule-based approaches
- **Finnish:** Koskenniemi (1983), two-level morphology formalism
- **Malay:** A hybrid approach combining rules and machine learning (Rani, 2018)

Indonesian presents unique challenges due to its extensive prefix circumfix combinations and reduplication patterns that differ from other Austronesian languages like Malay.

### 2.3 Our Approach

ModernKataKupas differs from prior work in:
1. **Full segmentation** rather than just stemming
2. **Reconstructibility** via canonical morpheme representation
3. **Explicit reduplication handling** with three types recognized
4. **Two-strategy disambiguation** for prefix/suffix ordering
5. **Open-source availability** with extensible rule system

---

## 3. Indonesian Morphology

### 3.1 Affix Types

Indonesian has four types of affixes:

| Type | Indonesian | Example | Gloss |
|------|-----------|---------|-------|
| Prefixes | *awalan* | *ber*-jalan | *ber*-walk |
| Suffixes | *akhiran* | jalan-*kan* | walk-*APPL* |
| Circumfixes | *konfiks* | *ke*-jalan-*an* | *ke*-walk-*STAT* |
| Infixes | *sisipan* | g*el*ap (from *gap* "dark") | dark |

### 3.2 Morphophonemic Allomorphy

Many prefixes undergo phonological changes based on the following root:

| Prefix | Allomorphs | Example |
|--------|-----------|---------|
| *meN-* | *me-*, *men-*, *meng-*, *meny-* | *me*masak, *men*ulis, *meng*ambil, *meny*anyi |
| *peN-* | *pe-*, *pen-*, *peng-*, *peny-* | *pe*masak, *pen*ulis, *peng*ambil |
| *ber-* | *ber-*, *be-*, *bel-* | *ber*jalan, *be*kerja, *bel*ajar |
| *ter-* | *ter-*, *te-*, *tel-* | *ter*lihat, *te*rima, *tel*usu |

### 3.3 Reduplication

Indonesian uses reduplication for pluralization, emphasis, and variety:

1. **Dwilingga (full reduplication):** *buku* "book" → *buku-buku* "books"
2. **Dwipurwa (partial reduplication):** *laki* "male" → *lelaki* "man"
3. **Dwilingga Salin Suara (phonetic change):** *bolak* → *bolak-balik* "back-and-forth"

### 3.4 Challenges for Computational Analysis

1. **Prefix layering:** *meN-* + *per-* + root (e.g., *mempertanyakan*)
2. **Ambiguous affix boundaries:** *-an* can be suffix or part of circumfix
3. **Reduplication with affixes:** *bermain-main* "playing around"
4. **Loanword affixation:** *di-scan* "scanned", *mem-backup* "backing up"

---

## 4. System Design

### 4.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    ModernKataKupas                      │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐   │
│  │ Normalizer  │→│  Separator  │→│ Reconstructor │   │
│  └─────────────┘  └─────────────┘  └──────────────┘   │
│         │                │                  │          │
│         ▼                ▼                  ▼          │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐   │
│  │   Rules     │  │ Dictionary  │  │    Rules     │   │
│  └─────────────┘  └─────────────┘  └──────────────┘   │
│                                                          │
│  Data: kata_dasar.txt (29,932 words)                   │
│        loanwords.txt (5,804 words)                     │
│        affix_rules.json (morphophonemic rules)        │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Segmentation Algorithm

#### Input: Word *w*

1. **Normalize:** Lowercase, strip punctuation
2. **Check dictionary:** If *w* in kata_dasar, return *w*
3. **Handle reduplication:** Detect dwilingga, dwipurwa, or salin suara
4. **Two-strategy segmentation:**
   - **S1:** Strip prefixes, then suffixes
   - **S2:** Strip suffixes, then prefixes
5. **Select best result:** Longest valid stem, prefer S1 if tie
6. **Format output:** Tilde-separated morphemes

#### Output Format

| Input | Output | Morphemes |
|-------|--------|-----------|
| *mempermainkan* | `meN~per~main~kan` | meN- + per- + main + -kan |
| *buku-buku* | `buku~ulg` | buku + full reduplication |
| *sayur-mayur* | `sayur~rs(~mayur)` | sayur + phonetic reduplication |

### 4.3 Ambiguity Resolution

When multiple segmentations are possible, we use:
1. **Dictionary validation:** Stem must exist in kata_dasar.txt
2. **Longest stem preference:** Maximizes stem length
3. **S1 priority:** Prefer prefix-first strategy

### 4.4 Word Reconstruction

The `reconstruct()` method reverses segmentation:
1. Parse morphemes (split by `~`)
2. Apply morphophonemic rules in reverse
3. Handle reduplication markers
4. Reassemble word

This ensures **idempotency**: `reconstruct(segment(w)) ≈ w`

---

## 5. Experimental Setup

### 5.1 Gold Standard Test Set

We created a gold standard test set covering 14 morphological categories:

| Category | Count | Description |
|----------|-------|-------------|
| Root words | 10 | Pure kata dasar |
| Prefix *meN-* | 19 | Actor focus prefixes |
| Prefix *ber-* | 14 | Stative/active prefixes |
| Prefix *ter-* | 9 | Accidental/agentive prefixes |
| Prefix *di-* | 9 | Passive prefix |
| Suffix *-kan* | 19 | Benefactive suffix |
| Suffix *-i* | 14 | Locative/object suffix |
| Suffix *-an* | 19 | Stative/collective suffix |
| Confix *ke-...-an* | 14 | State circumfix |
| Confix *per-...-an* | 14 | Causative circumfix |
| Confix *peN-...-an* | 14 | Agentive circumfix |
| Possessive | 14 | *-ku, -mu, -nya* |
| Particles | 14 | *-lah, -kah, -pun* |
| Reduplication | 17 | Full, partial, phonetic |

**Total:** 191 words

**Generation method:** DeepSeek API with manual validation (~$1.50 cost)

### 5.2 Dictionary

Our kata_dasar dictionary contains:
- **Source:** PySastrawi + KBBI V
- **Size:** 29,932 root words
- **Format:** UTF-8 text, one word per line
- **Loanwords:** 5,804 additional entries

### 5.3 Evaluation Metrics

We evaluate using:

1. **Word Accuracy:** % of exact segmentations matching gold standard
2. **Stem Accuracy:** % of correct root word identification
3. **Morpheme Precision:** TP / (TP + FP)
4. **Morpheme Recall:** TP / (TP + FN)
5. **Morpheme F1:** 2 × (P × R) / (P + R)

Where TP/FP/FN are computed at morpheme level.

### 5.4 Baseline System

We compare against **PySastrawi**, the most popular open-source Indonesian stemmer.

*Note:* Sastrawi is designed for stemming, not segmentation. We adapt its output for comparison by treating "stem" as the only morpheme.

---

## 6. Results and Discussion

### 6.1 Overall Performance

| Metric | ModernKataKupas | Sastrawi |
|--------|----------------|----------|
| Word Accuracy | 76.96% | 2.09% |
| Stem Accuracy | 80.63% | 0.00% |
| Morpheme F1 | 84.33% | 0.00% |

### 6.2 Per-Category Performance

[Detailed table from SUMMARY.md]

### 6.3 Ablation Study

[Dictionary size impact analysis]

### 6.4 Error Analysis

[Error categorization and discussion]

### 6.5 Discussion

**Strengths:**
- Dictionary size is the dominant factor (+69.63% impact)
- Perfect accuracy on possessives and *di-* prefix
- Strong confix handling (85-93%)

**Weaknesses:**
- Phonetic reduplication remains challenging
- *peN-an* confix shows inconsistent results
- Complex *meN-* allomorphs have edge cases

---

## 7. Limitations and Future Work

### 7.1 Current Limitations

1. **Reduplication coverage:** Phonetic patterns require expanded database
2. **No contextual disambiguation:** Cannot use sentence context
3. **Limited infix handling:** *-el-, -em-, -er* patterns not fully covered
4. **OOV words:** Unknown words return unsegmented

### 7.2 Future Work

1. **Hybrid neural-symbolic approach**
2. **Context-aware disambiguation**
3. **Expanded gold standard (1000+ words)**
4. **Downstream task evaluation** (MT, classification)

---

## 8. Conclusion

ModernKataKupas represents a significant advancement in open-source Indonesian morphological analysis, achieving 76.96% word accuracy with full morpheme segmentation and reconstructibility. The system demonstrates that rule-based approaches combined with comprehensive dictionaries can achieve strong performance on Indonesian morphology, while highlighting areas for future improvement (reduplication, contextual disambiguation). The open-source release provides a foundation for Indonesian NLP research and applications.

---

## References

[To be completed]

- Artiwi, A. (2013). PySastrawi: Indonesian stemming library.
- Asian, J. (2007). Algoritma stemming Bahasa Indonesia.
- Larasati, S. D., et al. (2012). MorphInd: An Indonesian morphological analyzer and part-of-speech tagger.
- ...

---

## Appendix: Sample Segmentations

[Table of correct and incorrect segmentations]
