# Paper Writing Status Checklist

**Paper Title**: Revisiting Rule-Based Indonesian Sub-word Separation for Enhanced LLM Performance and Low-Resource NLP

**Version**: Draft 1.0
**Date**: 2026-01-22

---

## Quick Status

```
Overall Progress: ██████████░░░░░ 70%

[████████████████████] Chapter 1: Introduction     - COMPLETE
[████████████████████] Chapter 2: Literature       - COMPLETE
[████████████████████] Chapter 3: Methodology      - COMPLETE
[████████████████░░░░] Chapter 4: Experiments      - 80%
[████████████████░░░░] Chapter 5: Results          - 80%
[██████████████░░░░░░] Chapter 6: Conclusions      - 70%
[░░░░░░░░░░░░░░░░░░░░] Abstract                    - 0%
[██████░░░░░░░░░░░░░░] References                  - 30%
```

---

## Detailed Checklist

### ABSTRACT (0%)
- [ ] Problem statement
- [ ] Methodology summary
- [ ] Key results (73.30% accuracy, 82.66% F1)
- [ ] Significance/contribution
- [ ] Keywords selection

### CHAPTER 1: INTRODUCTION (100%)
- [x] 1.1 Background and Problem Statement
  - [x] Indonesian morphology complexity
  - [x] Vocabulary explosion problem
  - [x] LLM tokenization challenges
- [x] 1.2 Proposed Solution
  - [x] ModernKataKupas description
  - [x] Key aspects
- [x] 1.3 Research Questions
  - [x] RQ1: Vocabulary reduction
  - [x] RQ2: LLM performance
  - [x] RQ3: Comparison with BPE/SentencePiece
  - [x] RQ4: NMT enhancement
- [x] 1.4 Anticipated Contributions
- [x] 1.5 Paper Structure

### CHAPTER 2: LITERATURE REVIEW (100%)
- [x] 2.1 Indonesian Morphology and Stemming
  - [x] Nazief & Adriani
  - [x] Asian (2007)
  - [x] Sastrawi
  - [x] Amien et al. (2022)
- [x] 2.2 Sub-word Tokenization
  - [x] BPE
  - [x] WordPiece
  - [x] SentencePiece
  - [x] Unigram LM
- [x] 2.3 Morphology in Neural Models
- [x] 2.4 Low-Resource NLP
- [x] 2.5 Positioning Current Research

### CHAPTER 3: METHODOLOGY (100%)
- [x] 3.1 Overall Architecture
- [x] 3.2 Foundational Components
  - [x] Text Normalization
  - [x] Root Word Dictionary
  - [x] Underlying Stemmer
  - [x] Affix Rule Repository
- [x] 3.3 Segmentation Algorithm
  - [x] Step 1: Normalization
  - [x] Step 2: Reduplication Handling
  - [x] Step 3: Root Word Identification
  - [x] Step 4: Affix Identification
  - [x] Step 5: Loanword Handling
  - [x] Step 6: Output Formatting
- [x] 3.4 Ambiguity Resolution
- [x] 3.5 Reconstruction Algorithm
- [x] 3.6 Implementation Guidelines

### CHAPTER 4: EXPERIMENTAL SETUP (80%)
- [x] 4.1 Datasets
  - [x] Gold Standard description (191 words, 14 categories)
  - [x] Category breakdown
  - [x] Generation method (DeepSeek API)
- [x] 4.2 Dictionary
  - [x] Size (29,936 root words)
  - [x] Loanwords (5,804)
- [x] 4.3 Evaluation Metrics
  - [x] Word Accuracy
  - [x] Stem Accuracy
  - [x] Morpheme P/R/F1
- [x] 4.4 Baseline Systems
  - [x] Sastrawi description
- [x] 4.5 Ablation Study Design
- [ ] **MISSING**: Hardware/software specifications
- [ ] **MISSING**: Reproducibility statement
- [ ] **MISSING**: Dataset availability statement

### CHAPTER 5: RESULTS (80%)
- [x] 5.1 Overall Performance
  - [x] Main results table
- [x] 5.2 Baseline Comparison
  - [x] vs Sastrawi table
- [x] 5.3 Per-Category Performance
  - [x] All 14 categories
  - [x] Strengths analysis
  - [x] Weaknesses analysis
- [x] 5.4 Ablation Study
  - [x] Dictionary size impact
  - [x] Error pattern analysis
- [x] 5.5 Discussion
  - [x] Key findings
  - [x] Comparison with related work
  - [x] Cost efficiency
- [ ] **MISSING**: Statistical significance tests
- [ ] **MISSING**: More qualitative examples
- [ ] **MISSING**: Deeper error analysis

### CHAPTER 6: CONCLUSIONS (70%)
- [x] 6.1 Summary of contributions
- [x] 6.2 Limitations
  - [x] Reduplication issues
  - [x] Complex allomorphs
- [x] 6.3 Future Work
  - [x] Expanded rules
  - [x] Larger gold standard
  - [x] Downstream tasks
  - [x] Neural-symbolic hybrid
- [ ] **MISSING**: Broader impact statement
- [ ] **MISSING**: Reproducibility commitment
- [ ] **MISSING**: Final concluding remarks

### REFERENCES (30%)
**Total needed**: ~30-40 citations

**Have (estimated):**
- [x] Indonesian morphology: 4-5 refs
- [x] Sub-word tokenization: 4-5 refs
- [x] Neural models: 3-4 refs

**Missing:**
- [ ] Recent LLM papers (2023-2026): 5-8 refs
- [ ] Indonesian NLP recent work: 3-5 refs
- [ ] Low-resource NLP: 3-5 refs
- [ ] Evaluation methodology: 2-3 refs

### SUPPLEMENTARY MATERIALS
- [ ] Code repository link
- [ ] Gold standard dataset
- [ ] Appendix with full results
- [ ] Example segmentations table

---

## Data Verification Checklist

### Numbers to Double-Check
| Metric | Value | Verified |
|--------|-------|----------|
| Total test words | 191 | [ ] |
| Word Accuracy | 73.30% | [ ] |
| Stem Accuracy | 76.44% | [ ] |
| Morpheme F1 | 82.66% | [ ] |
| Root words in dict | 29,936 | [ ] |
| Loanwords | 5,804 | [ ] |
| Categories | 14 | [ ] |
| Tests passing | 93 | [ ] |

### Per-Category Accuracy (to verify)
| Category | Accuracy | Correct/Total |
|----------|----------|---------------|
| possessive | 100.00% | 14/14 |
| prefix_di | 100.00% | 9/9 |
| confix_per_an | 92.86% | 13/14 |
| prefix_ber | 92.86% | 13/14 |
| confix_ke_an | 85.71% | 12/14 |
| particle | 85.71% | 12/14 |
| suffix_kan | 84.21% | 16/19 |
| suffix_an | 78.95% | 15/19 |
| suffix_i | 71.43% | 10/14 |
| prefix_meN | 68.42% | 13/19 |
| prefix_ter | 66.67% | 6/9 |
| confix_peN_an | 42.86% | 6/14 |
| reduplication_partial | 11.11% | 1/9 |
| reduplication_phonetic | 0.00% | 0/9 |

---

## Pre-Submission Checklist

### Content Quality
- [ ] All claims supported by data
- [ ] No overclaiming results
- [ ] Limitations clearly stated
- [ ] Related work fairly compared
- [ ] Contributions clearly articulated

### Technical Quality
- [ ] Algorithm description reproducible
- [ ] Metrics properly defined
- [ ] Statistical tests performed (if needed)
- [ ] Code/data availability stated

### Writing Quality
- [ ] Consistent terminology
- [ ] No grammatical errors
- [ ] Proper citation format
- [ ] Figures/tables properly labeled
- [ ] Abstract within word limit

### Formatting
- [ ] Correct venue template used
- [ ] Page limit respected
- [ ] Font sizes correct
- [ ] Margins correct
- [ ] References formatted correctly

### Ethics & Reproducibility
- [ ] No ethical concerns
- [ ] Data source acknowledged
- [ ] Reproducibility information provided
- [ ] Limitations of approach acknowledged

---

## Timeline

| Phase | Target Date | Status |
|-------|-------------|--------|
| Complete draft | Week 1-2 | In Progress |
| Internal review | Week 3 | Not Started |
| Select venue | Week 3 | Not Started |
| Format to template | Week 4 | Not Started |
| Final review | Week 4 | Not Started |
| Submit | Week 5 | Not Started |

---

## Notes & Decisions

### Venue Decision
- **Primary target**: IALP 2026 or PACLIC 2026
- **Rationale**: Regional conference, good fit for Indonesian NLP

### Scope Decision
- **Current scope**: Intrinsic evaluation only (segmentation accuracy)
- **Future scope**: Downstream tasks (for revision or follow-up paper)

### Known Weaknesses to Address in Writing
1. Small test set (191 words) - acknowledge, promise expansion
2. No downstream evaluation - position as foundation work
3. Reduplication failures - clearly document as limitation
