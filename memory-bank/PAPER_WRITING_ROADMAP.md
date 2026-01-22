# ModernKataKupas Paper Writing Roadmap

**Target Paper**: "Revisiting Rule-Based Indonesian Sub-word Separation for Enhanced LLM Performance and Low-Resource NLP"

**Last Updated**: 2026-01-22

---

## 1. Status Overview

### Current State

| Component | Status | Completeness |
|-----------|--------|--------------|
| Chapter 1: Introduction | DONE | 100% |
| Chapter 2: Literature Review | DONE | 100% |
| Chapter 3: Methodology | DONE | 100% |
| Chapter 4: Experimental Setup | DRAFT | 80% |
| Chapter 5: Results & Discussion | DRAFT | 80% |
| Chapter 6: Conclusions | DRAFT | 70% |
| Abstract | NOT STARTED | 0% |
| References/Bibliography | PARTIAL | 30% |

### Implementation Status (LOCKED)
- ModernKataKupas v1.0.1: **COMPLETE**
- Word Accuracy: 73.30%
- Morpheme F1: 82.66%
- Test Coverage: 93 tests passing

---

## 2. Venue Selection Strategy

### Recommended Targets (by feasibility)

#### Tier 1: High Probability (3-6 months)
| Venue | Type | Deadline | Notes |
|-------|------|----------|-------|
| **IALP 2026** | Conference | ~June 2026 | International Conference on Asian Language Processing - ideal fit |
| **PACLIC 2026** | Conference | ~July 2026 | Pacific Asia Conference on Language, Information and Computation |
| **Jurnal ILKOM** (Indonesia) | Journal | Rolling | National accredited journal |
| **Jurnal Linguistik Komputasional** | Journal | Rolling | Indonesian computational linguistics |

#### Tier 2: Medium Probability (6-12 months, needs more experiments)
| Venue | Type | Requirements |
|-------|------|--------------|
| **ACL Workshop (MorphLearn/SouthEastAsia NLP)** | Workshop | Need downstream task experiments |
| **EMNLP Findings** | Conference | Need LLM integration experiments |
| **LREC-COLING** | Conference | Focus on resource contribution |

#### Tier 3: Ambitious (12+ months, major revisions needed)
| Venue | Type | Requirements |
|-------|------|--------------|
| ACL/EMNLP Main | Conference | Novel contribution + extensive experiments |
| TACL | Journal | Significant theoretical/empirical contribution |

### Recommendation
**Start with IALP 2026 or PACLIC 2026** - regional conferences with focus on Asian language processing. The current work is well-suited for these venues.

---

## 3. Paper Writing Phases

### Phase 1: Complete Draft (Current Phase)
**Target**: 2 weeks

- [ ] Finalize Chapter 4: Experimental Setup
- [ ] Finalize Chapter 5: Results & Discussion
- [ ] Finalize Chapter 6: Conclusions & Future Work
- [ ] Write Abstract (150-250 words)
- [ ] Compile References (target: 25-40 citations)

### Phase 2: Internal Review
**Target**: 1 week

- [ ] Check consistency across all chapters
- [ ] Verify all numbers match between text and tables
- [ ] Ensure figures/tables are publication-ready
- [ ] Proofread for grammar and clarity
- [ ] Check citation format consistency

### Phase 3: Formatting & Submission Prep
**Target**: 1 week

- [ ] Select target venue
- [ ] Download venue template (ACL/IEEE/etc)
- [ ] Reformat paper to template
- [ ] Prepare supplementary materials
- [ ] Write cover letter (if required)

### Phase 4: Optional Enhancements (for higher-tier venues)
**Target**: 1-2 months

- [ ] Expand gold standard to 500+ words
- [ ] Add downstream task experiments (text classification)
- [ ] Add BPE/SentencePiece comparison
- [ ] Add LLM tokenization efficiency analysis

---

## 4. Chapter-by-Chapter Checklist

### Chapter 1: Introduction [COMPLETE]
- [x] Background & Problem Statement
- [x] Proposed Solution (ModernKataKupas)
- [x] Research Questions (RQ1-RQ4)
- [x] Anticipated Contributions
- [x] Paper Structure

### Chapter 2: Literature Review [COMPLETE]
- [x] Indonesian Morphology and Stemming
- [x] Sub-word Tokenization in NLP
- [x] Morphology in Neural Models
- [x] Low-Resource NLP
- [x] Positioning Current Research

### Chapter 3: Methodology [COMPLETE]
- [x] Overall Algorithm Architecture
- [x] Foundational Components
- [x] Morphological Segmentation Steps
- [x] Ambiguity Resolution Strategies
- [x] Reconstruction Algorithm
- [x] Implementation Guidelines

### Chapter 4: Experimental Setup [80% COMPLETE]
- [x] Dataset Description (Gold Standard)
- [x] Dictionary Statistics
- [x] Evaluation Metrics
- [x] Baseline Systems
- [x] Ablation Study Design
- [ ] **TODO**: Add hardware/software specifications
- [ ] **TODO**: Add reproducibility statement

### Chapter 5: Results & Discussion [80% COMPLETE]
- [x] Overall Performance Table
- [x] Baseline Comparison
- [x] Per-Category Performance
- [x] Ablation Study Results
- [x] Error Pattern Analysis
- [x] Key Findings Discussion
- [ ] **TODO**: Add statistical significance tests
- [ ] **TODO**: Add qualitative analysis examples
- [ ] **TODO**: Strengthen comparison with related work

### Chapter 6: Conclusions [70% COMPLETE]
- [x] Summary of Contributions
- [x] Current Limitations
- [x] Future Work Directions
- [ ] **TODO**: Add broader impact statement
- [ ] **TODO**: Strengthen conclusion paragraphs

### Abstract [NOT STARTED]
- [ ] Problem statement (1-2 sentences)
- [ ] Approach (1-2 sentences)
- [ ] Key results (2-3 sentences)
- [ ] Significance (1 sentence)

### References [30% COMPLETE]
- [x] Indonesian morphology references
- [x] Sub-word tokenization (BPE, WordPiece, SentencePiece)
- [ ] **TODO**: Add more recent LLM tokenization papers (2023-2026)
- [ ] **TODO**: Add Indonesian NLP papers
- [ ] **TODO**: Verify all citations have complete information
- [ ] **TODO**: Format to target venue style

---

## 5. Missing Experiments (Optional for Higher Venues)

### Priority 1: Quick Wins
| Experiment | Effort | Impact | Notes |
|------------|--------|--------|-------|
| Statistical significance tests | Low | Medium | Bootstrap/McNemar on accuracy |
| More error examples | Low | Medium | Qualitative analysis |
| Timing benchmarks | Low | Low | Processing speed |

### Priority 2: Medium Effort
| Experiment | Effort | Impact | Notes |
|------------|--------|--------|-------|
| Expand gold standard (500 words) | Medium | High | More reliable results |
| BPE/SentencePiece comparison | Medium | High | Key for novelty claim |
| Cross-validation | Medium | Medium | Robustness check |

### Priority 3: Major Effort (for top venues)
| Experiment | Effort | Impact | Notes |
|------------|--------|--------|-------|
| Text classification with LLM | High | Very High | Downstream task |
| NMT experiments | High | Very High | Answer RQ4 |
| Vocabulary reduction analysis | Medium | High | Answer RQ1 |

---

## 6. Reference List (To Complete)

### Core References (Have)
1. Sennrich et al., 2016 - BPE
2. Wu et al., 2016 - WordPiece
3. Kudo & Richardson, 2018 - SentencePiece
4. Sneddon, 1996 - Indonesian Grammar
5. Alwi et al., 2003 - TBBI
6. Sastrawi/Alfina et al., 2017

### To Add
- [ ] Recent Indonesian NLP papers (2023-2026)
- [ ] LLM tokenization analysis papers
- [ ] Morfessor and morphological segmentation papers
- [ ] Low-resource NLP papers
- [ ] Indonesian MT papers

---

## 7. Action Items (Next Steps)

### Immediate (This Week)
1. Complete Chapter 4 with hardware specs & reproducibility
2. Complete Chapter 5 with statistical tests
3. Write Abstract
4. Compile reference list

### Short-term (Next 2 Weeks)
1. Full proofread and consistency check
2. Select target venue
3. Format to venue template

### Medium-term (Next Month)
1. Optional: Expand experiments based on venue requirements
2. Submit to selected venue
3. Prepare for revisions

---

## 8. File Locations

| File | Location | Description |
|------|----------|-------------|
| Paper Draft | `memory-bank/paper-draft.md` | Main paper content |
| Experimental Results | `experiments/results/EXPERIMENTAL_RESULTS_FOR_PAPER.md` | Chapter 4-5 data |
| Gold Standard | `experiments/data/gold_standard.json` | Test dataset |
| Metrics | `experiments/results/metrics.json` | Numerical results |
| Error Analysis | `experiments/results/errors.csv` | Error categorization |

---

## 9. Writing Tips

### For Methodology (Chapter 3)
- Be precise about algorithm steps
- Include pseudocode or flowchart
- Explain design decisions

### For Results (Chapter 5)
- Let data speak first, then interpret
- Compare fairly with baselines
- Acknowledge limitations honestly

### For Conclusions (Chapter 6)
- Don't just summarize - synthesize
- Be specific about contributions
- Future work should be actionable

### General
- Use active voice where appropriate
- Be concise - every sentence should add value
- Use consistent terminology throughout
