# ModernKataKupas: Next Development Steps

**Purpose**: Detailed implementation guide for achieving ACL workshop submission level

**Last Updated**: 2026-01-23

---

## Phase 2: Corpus & Baseline Expansion

### Step 2.1: Wikipedia Indonesia Corpus Evaluation

**Priority**: HIGH | **Effort**: Medium | **ETA**: 1 week

#### Objective
Evaluate ModernKataKupas on real-world Indonesian text to demonstrate practical utility and measure OOV handling.

#### Implementation Plan

1. **Download Wikipedia Indonesia Dump**
   ```bash
   # Download latest Indonesian Wikipedia dump
   wget https://dumps.wikimedia.org/idwiki/latest/idwiki-latest-pages-articles.xml.bz2

   # Or use WikiExtractor for cleaner text
   pip install wikiextractor
   python -m wikiextractor.WikiExtractor idwiki-latest-pages-articles.xml.bz2 -o extracted/
   ```

2. **Create Evaluation Script** (`experiments/wikipedia_evaluation.py`)
   ```python
   """
   Wikipedia Indonesia Corpus Evaluation

   Metrics:
   - OOV rate (words not in dictionary)
   - Segmentation coverage (% words successfully segmented)
   - Processing speed (words/second)
   - Qualitative sample analysis
   """

   # Key functions to implement:
   # - load_wikipedia_sample(path, n_sentences=10000)
   # - extract_words(text) -> List[str]
   # - evaluate_segmentation(words) -> Dict[str, Any]
   # - analyze_oov_patterns(oov_words) -> Dict[str, Any]
   ```

3. **Expected Results Format**
   ```json
   {
     "corpus_stats": {
       "total_sentences": 10000,
       "total_words": 150000,
       "unique_words": 25000
     },
     "segmentation_results": {
       "successfully_segmented": 22500,
       "oov_words": 2500,
       "oov_rate": 10.0
     },
     "performance": {
       "words_per_second": 5000,
       "total_time_seconds": 30
     }
   }
   ```

4. **Paper Section Update**
   - Add to Chapter 5: "5.X Real Corpus Evaluation"
   - Report OOV rate, coverage, speed
   - Qualitative examples of successful/failed segmentations

---

### Step 2.2: Morfessor Baseline Comparison

**Priority**: MEDIUM | **Effort**: Low | **ETA**: 3 days

#### Objective
Compare ModernKataKupas with unsupervised morphological segmentation (Morfessor).

#### Implementation Plan

1. **Install Morfessor**
   ```bash
   pip install morfessor
   ```

2. **Create Comparison Script** (`experiments/morfessor_comparison.py`)
   ```python
   """
   Morfessor Baseline Comparison

   Compare:
   1. Train Morfessor on Indonesian corpus (kata_dasar.txt + affixed forms)
   2. Evaluate on gold standard
   3. Compare accuracy, speed, interpretability
   """

   import morfessor

   # Key steps:
   # 1. Train Morfessor model on Indonesian text
   # 2. Segment gold standard words with Morfessor
   # 3. Compare to gold standard and MKK output
   ```

3. **Expected Comparison Table**
   | Method | Accuracy | Avg Tokens/Word | Interpretability | Speed |
   |--------|----------|-----------------|------------------|-------|
   | ModernKataKupas | 70.0% | 1.66 | High (morphemes) | Fast |
   | Morfessor | TBD | TBD | Medium (statistical) | Medium |
   | BPE (SentencePiece) | N/A | 2.23 | Low (subwords) | Fast |

---

### Step 2.3: Gold Standard Expansion

**Priority**: HIGH | **Effort**: High | **ETA**: 1-2 weeks

#### Objective
Expand gold standard from 360 to 500+ words with balanced category coverage.

#### Implementation Plan

1. **Identify Categories Needing Expansion**
   ```
   prefix_di:              9 → 20 (+11)
   prefix_ter:             9 → 20 (+11)
   reduplication_partial:  9 → 25 (+16)
   reduplication_phonetic: 9 → 25 (+16)
   confix_ke_an:          14 → 25 (+11)
   confix_per_an:         14 → 25 (+11)
   confix_peN_an:         14 → 25 (+11)

   Total new words needed: ~90-100
   ```

2. **Generation Methods**

   **Option A: DeepSeek API (Recommended)**
   ```bash
   # Set API key
   export DEEPSEEK_API_KEY=your_key

   # Run expansion script
   python experiments/expand_gold_standard.py --target 500
   ```

   **Option B: Manual Generation**
   - Use dictionary to generate affixed forms
   - Native speaker validation
   - Cross-reference with KBBI

3. **Validation Process**
   - Run MKK on generated words
   - Compare with expected segmentation
   - Manual review of disagreements
   - Final validation by native speaker

4. **Output**
   - `data/gold_standard_v4.csv` (500+ words)
   - Category distribution report
   - Validation summary

---

## Phase 3: Downstream Task Evaluation

### Step 3.1: Text Classification Experiment

**Priority**: HIGH | **Effort**: High | **ETA**: 2-3 weeks

#### Objective
Demonstrate that MKK preprocessing improves downstream NLP task performance.

#### Dataset Selection

1. **IndoNLU Sentiment** (Recommended)
   - Source: https://github.com/indobenchmark/indonlu
   - Task: Sentiment analysis (positive/negative)
   - Size: ~10K samples
   - Why: Well-established benchmark

2. **Alternatives**
   - Indonesian News Classification (topic)
   - Hate Speech Detection (binary)

#### Experimental Design

```
Experiment 1: Baseline (No Preprocessing)
- Input: Raw text
- Tokenizer: Standard word tokenizer
- Model: fastText / BiLSTM / BERT-base

Experiment 2: BPE Preprocessing
- Input: Raw text → SentencePiece BPE
- Model: Same as baseline

Experiment 3: MKK Preprocessing
- Input: Raw text → MKK segmentation
- Tokenizer: Split on ~ separator
- Model: Same as baseline

Metrics:
- Accuracy
- Macro F1
- Training convergence speed
```

#### Implementation Plan

1. **Create Script** (`experiments/text_classification_eval.py`)
   ```python
   """
   Text Classification Downstream Evaluation

   Compares:
   - No preprocessing (baseline)
   - BPE preprocessing
   - MKK preprocessing

   On: IndoNLU Sentiment dataset
   Using: fastText classifier
   """

   # Key functions:
   # - load_indonlu_sentiment()
   # - preprocess_with_mkk(texts)
   # - preprocess_with_bpe(texts)
   # - train_classifier(train_data, method)
   # - evaluate(model, test_data)
   ```

2. **Expected Results**
   | Preprocessing | Accuracy | F1 | Training Time |
   |---------------|----------|----|--------------|
   | None (baseline) | ~85% | ~84% | 1x |
   | BPE | ~85% | ~84% | 1x |
   | MKK | ~86-87% | ~85-86% | 0.9x |

   *Note: Even if MKK doesn't improve accuracy, report:*
   - *Comparable performance with interpretability benefit*
   - *Potentially faster training (smaller vocabulary)*

3. **If MKK Doesn't Improve Accuracy**

   Reframe contribution:
   - "MKK provides comparable performance while maintaining linguistic interpretability"
   - "Morphological tokens enable better error analysis"
   - "Potential for low-resource scenarios"

---

## Implementation Checklist

### Week 1-2: Corpus & Baseline
- [x] Download Wikipedia Indonesia sample (10K sentences) - **DONE**
- [x] Implement `experiments/wikipedia_evaluation.py` - **DONE**
- [x] Run Wikipedia evaluation and save results - **DONE** (2026-01-23)
- [x] Install Morfessor and implement comparison - **DONE**
- [x] Run Morfessor baseline comparison - **DONE** (2026-01-23)

### Week 3-4: Gold Standard
- [ ] Identify category gaps
- [ ] Generate candidate words (DeepSeek or manual)
- [ ] Validate new words
- [ ] Create `data/gold_standard_v4.csv`
- [ ] Re-run statistical tests on expanded set

### Week 5-6: Downstream Task
- [ ] Download IndoNLU Sentiment dataset
- [ ] Implement preprocessing pipelines
- [ ] Train baseline classifier
- [ ] Train MKK classifier
- [ ] Compare and analyze results

### Week 7-8: Paper Update
- [ ] Add Wikipedia evaluation results to Chapter 5
- [ ] Add Morfessor comparison to Chapter 5
- [ ] Add downstream task results to Chapter 5
- [ ] Update Abstract and Conclusions
- [ ] Format for ACL template

---

## Quick Reference: Commands

```bash
# Current experiments (working)
python experiments/statistical_tests.py -g data/gold_standard_v3.csv
python experiments/tokenization_comparison.py --generate-corpus --size 10000 -o experiments/results/tokenization.json

# TODO experiments
python experiments/wikipedia_evaluation.py -o experiments/results/wikipedia_eval.json
python experiments/morfessor_comparison.py -o experiments/results/morfessor_comparison.json
python experiments/text_classification_eval.py -o experiments/results/classification_eval.json
```

---

## Contact & Resources

- **Repository**: https://github.com/neimasilk/modern_kata_kupas
- **Paper Draft**: `memory-bank/paper-draft.md`
- **Roadmap**: `memory-bank/PAPER_WRITING_ROADMAP.md`

---

*Document version 1.0 - Created 2026-01-23*
