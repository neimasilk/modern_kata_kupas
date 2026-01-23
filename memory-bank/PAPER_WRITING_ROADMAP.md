# ModernKataKupas Paper Writing Roadmap

**Target Paper**: "Revisiting Rule-Based Indonesian Sub-word Separation for Enhanced LLM Performance and Low-Resource NLP"

**Target Venue**: ACL 2026 Workshop (e.g., RepL4NLP, MRL, or similar)

**Last Updated**: 2026-01-23 (Major Update)

---

## 1. Executive Summary

### Current State (2026-01-23)

| Metric | Value | Status |
|--------|-------|--------|
| Word Accuracy | **70.00%** | +3.06% from baseline |
| Cohen's Kappa | **0.70** | Substantial Agreement |
| Phonetic Reduplication | **77.78%** | Fixed (was 0%) |
| Partial Reduplication | **55.56%** | Improved (was 11%) |
| BPE Alignment | **41.7%** | Real SentencePiece |
| Gold Standard | 360 words | Need 500+ |

### Target: ACL Workshop Level

To reach ACL workshop level, we need:
1. **Downstream Task Evaluation** - Show practical utility
2. **Real Corpus Evaluation** - Wikipedia/news corpus
3. **Expanded Gold Standard** - 500-1000 words
4. **Additional Baselines** - Morfessor, neural approaches

---

## 2. Roadmap Phases

### Phase 1: Foundation (COMPLETED)

| Task | Status | Notes |
|------|--------|-------|
| Core algorithm implementation | DONE | ModernKataKupas v1.0.1 |
| Gold standard creation (360 words) | DONE | 21 categories |
| Statistical validation | DONE | Bootstrap CI, McNemar |
| Real SentencePiece comparison | DONE | 41.7% alignment |
| Reduplication handling | DONE | +77.78% phonetic |
| Paper draft | DONE | 80% complete |

### Phase 2: Corpus & Baseline Expansion (NEXT)

**Timeline**: 2-3 weeks

| Task | Priority | Effort | Description |
|------|----------|--------|-------------|
| Wikipedia ID corpus eval | HIGH | Medium | Evaluate on 10K real sentences |
| Expand gold standard | HIGH | High | 360 → 500+ words |
| Add Morfessor baseline | MEDIUM | Low | Unsupervised morphology |
| News corpus evaluation | MEDIUM | Medium | Domain diversity |

### Phase 3: Downstream Tasks (KEY FOR ACL)

**Timeline**: 3-4 weeks

| Task | Priority | Effort | Description |
|------|----------|--------|-------------|
| Text Classification | HIGH | High | Sentiment/topic with MKK preprocessing |
| Named Entity Recognition | MEDIUM | High | NER with morphological features |
| Machine Translation | LOW | Very High | ID-EN MT evaluation (future work) |

### Phase 4: Paper Finalization

**Timeline**: 1-2 weeks

| Task | Priority | Description |
|------|----------|-------------|
| Update all results | HIGH | Incorporate new experiments |
| Add figures/visualizations | MEDIUM | Architecture, results plots |
| Complete references | HIGH | 30+ citations |
| Format for venue | HIGH | ACL template |

---

## 3. Detailed Task Specifications

### 3.1 Wikipedia Corpus Evaluation

**Objective**: Evaluate segmentation accuracy on real-world Indonesian text

**Implementation**:
```python
# experiments/wikipedia_evaluation.py
# 1. Download Wikipedia Indonesia dump (subset)
# 2. Extract sentences and tokenize to words
# 3. Run ModernKataKupas segmentation
# 4. Measure: OOV rate, coverage, processing speed
```

**Expected Output**:
- OOV rate on real corpus
- Processing speed (words/second)
- Coverage analysis (% words successfully segmented)
- Sample segmentations for qualitative analysis

**Script Location**: `experiments/wikipedia_evaluation.py`

### 3.2 Gold Standard Expansion

**Objective**: Expand from 360 to 500+ words

**Categories Needing Expansion**:
| Category | Current | Target | Gap |
|----------|---------|--------|-----|
| prefix_di | 9 | 20 | +11 |
| prefix_ter | 9 | 20 | +11 |
| reduplication_partial | 9 | 25 | +16 |
| reduplication_phonetic | 9 | 25 | +16 |
| confix_ke_an | 14 | 25 | +11 |
| confix_per_an | 14 | 25 | +11 |
| confix_peN_an | 14 | 25 | +11 |

**Method**:
1. Use `experiments/expand_gold_standard.py` with DeepSeek API
2. Manual validation by native speakers
3. Cross-reference with KBBI

**Script Location**: `experiments/expand_gold_standard.py`

### 3.3 Text Classification Experiment

**Objective**: Demonstrate downstream task improvement with MKK preprocessing

**Dataset Options**:
1. **IndoNLU Sentiment** - Sentiment analysis
2. **Indonesian News** - Topic classification
3. **Hate Speech Detection** - Binary classification

**Experimental Design**:
```
Condition A: Raw text → Tokenizer → Classifier
Condition B: Raw text → MKK → Tokenizer → Classifier
Condition C: Raw text → BPE → Classifier

Metrics: Accuracy, F1, Training convergence
```

**Implementation**:
```python
# experiments/text_classification_eval.py
# 1. Load dataset (train/val/test split)
# 2. Preprocess with MKK vs baseline
# 3. Train simple classifier (e.g., fastText, LSTM)
# 4. Compare performance metrics
```

**Script Location**: `experiments/text_classification_eval.py`

### 3.4 Morfessor Baseline

**Objective**: Compare with unsupervised morphological segmentation

**Implementation**:
```bash
pip install morfessor
```

```python
# experiments/morfessor_comparison.py
# 1. Train Morfessor on Indonesian corpus
# 2. Evaluate on same gold standard
# 3. Compare: accuracy, interpretability, speed
```

**Script Location**: `experiments/morfessor_comparison.py`

---

## 4. Research Questions (Updated)

| RQ | Question | Current Status | Target |
|----|----------|----------------|--------|
| RQ1 | Segmentation accuracy | **70.00%** | Maintain |
| RQ2 | Dictionary impact | **+60.66%** | Maintain |
| RQ3 | vs BPE comparison | **41.7% align** | Add Morfessor |
| RQ4 | Category challenges | **Identified** | Detailed analysis |
| **RQ5 (NEW)** | Downstream task benefit | NOT STARTED | Text classification |
| **RQ6 (NEW)** | Real corpus performance | NOT STARTED | Wikipedia eval |

---

## 5. File Structure

```
modern_kata_kupas/
├── memory-bank/
│   ├── paper-draft.md                    # Main paper (UPDATED)
│   ├── PAPER_STATUS_CHECKLIST.md         # Progress tracking
│   ├── PAPER_WRITING_ROADMAP.md          # This file
│   └── NEXT_STEPS.md                     # Detailed next steps
│
├── experiments/
│   ├── results/
│   │   ├── statistical_results.json      # Current results
│   │   ├── tokenization_comparison_real_bpe.json  # BPE comparison
│   │   └── ...
│   │
│   ├── statistical_tests.py              # Statistical analysis
│   ├── tokenization_comparison.py        # BPE comparison
│   ├── expand_gold_standard.py           # Gold standard expansion
│   │
│   ├── wikipedia_evaluation.py           # TODO: Real corpus eval
│   ├── text_classification_eval.py       # TODO: Downstream task
│   └── morfessor_comparison.py           # TODO: Baseline comparison
│
├── data/
│   ├── gold_standard_v3.csv              # Current gold standard (360)
│   ├── kata_dasar.txt                    # Dictionary (29,936)
│   └── ...
│
└── src/modern_kata_kupas/                # Core implementation
```

---

## 6. Timeline to ACL Workshop Submission

### Month 1: Corpus & Baseline

| Week | Tasks | Deliverables |
|------|-------|--------------|
| 1 | Wikipedia corpus download & preprocessing | `data/wikipedia_id_sample.txt` |
| 2 | Wikipedia evaluation script | `experiments/wikipedia_evaluation.py` |
| 3 | Morfessor baseline implementation | `experiments/morfessor_comparison.py` |
| 4 | Gold standard expansion (100+ words) | `data/gold_standard_v4.csv` |

### Month 2: Downstream Tasks

| Week | Tasks | Deliverables |
|------|-------|--------------|
| 1-2 | Text classification dataset setup | Dataset prepared |
| 3 | Classification experiments | Results JSON |
| 4 | Analysis & paper update | Updated Chapter 5 |

### Month 3: Paper Finalization

| Week | Tasks | Deliverables |
|------|-------|--------------|
| 1 | Complete all experiments | Final results |
| 2 | Update paper with new results | Complete draft |
| 3 | Format for ACL template | Formatted paper |
| 4 | Internal review & polish | Submission-ready |

---

## 7. Success Metrics

### For ACL Workshop Acceptance

| Criterion | Current | Target | Gap |
|-----------|---------|--------|-----|
| Gold standard size | 360 | 500+ | +140 |
| Baselines compared | 1 (BPE) | 3+ | +2 |
| Real corpus eval | No | Yes | Required |
| Downstream task | No | 1+ | Required |
| Novelty claim | Moderate | Clear | Strengthen |

### Paper Quality Indicators

- [ ] Clear contribution statement
- [ ] Reproducible experiments
- [ ] Statistical significance for all claims
- [ ] Comprehensive related work
- [ ] Honest limitations discussion
- [ ] Future work clearly scoped

---

## 8. Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Downstream task shows no improvement | Medium | High | Frame as "comparable with interpretability benefit" |
| Wikipedia OOV rate too high | Medium | Medium | Discuss domain adaptation needs |
| Gold standard expansion slow | Low | Medium | Prioritize critical categories |
| ACL deadline missed | Low | High | Fall back to EMNLP or regional venue |

---

## 9. Contribution Claims (ACL Level)

### Primary Contributions
1. **Comprehensive Rule-Based Indonesian Morphological Segmenter**
   - 70% accuracy on gold standard
   - Handles all major morphological phenomena
   - Open-source implementation

2. **Empirical Comparison with Statistical Tokenization**
   - Real SentencePiece BPE comparison
   - 42% morpheme boundary alignment analysis
   - Morfessor baseline (TODO)

3. **Downstream Task Evaluation** (TODO)
   - Text classification with morphological preprocessing
   - Quantified benefit of morphological awareness

4. **Linguistic Resource**
   - 500+ word gold standard for Indonesian morphology
   - Comprehensive category coverage

### Secondary Contributions
- Ablation study on dictionary size impact
- Per-category error analysis
- Real corpus coverage analysis

---

## 10. Quick Start for New Contributors

### Setup
```bash
git clone https://github.com/neimasilk/modern_kata_kupas.git
cd modern_kata_kupas
pip install -e ".[dev]"
pytest tests/  # Should pass 101 tests
```

### Run Current Experiments
```bash
# Statistical tests
python experiments/statistical_tests.py -g data/gold_standard_v3.csv

# Tokenization comparison
python experiments/tokenization_comparison.py --generate-corpus --size 10000
```

### Next Experiments to Implement
1. `experiments/wikipedia_evaluation.py` - Real corpus evaluation
2. `experiments/text_classification_eval.py` - Downstream task
3. `experiments/morfessor_comparison.py` - Additional baseline

---

*Roadmap version 2.0 - Updated 2026-01-23*
*Target: ACL 2026 Workshop submission*
