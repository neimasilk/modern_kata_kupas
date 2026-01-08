# Experiments for ModernKataKupas Research Paper

This directory contains scripts and tools for generating data, running experiments, and evaluating the ModernKataKupas system for research purposes.

## Setup

### 1. Install Dependencies

```bash
pip install -e ".[experiments]"
```

This installs:
- `python-dotenv` - For environment variable management
- `openai` - For DeepSeek API calls
- `pandas` - For data manipulation
- `tqdm` - For progress bars

### 2. Configure API Key

Copy the example environment file and add your DeepSeek API key:

```bash
cp .env.example .env
```

Edit `.env` and add:
```
DEEPSEEK_API_KEY=your_api_key_here
```

**IMPORTANT:** Never commit `.env` to GitHub. It is already in `.gitignore`.

---

## Scripts Overview

### 1. DeepSeek Helper Module

**Location:** `src/modern_kata_kupas/utils/deepseek_helper.py`

Core module for interacting with DeepSeek API.

**Features:**
- Generate root words by category
- Segment words with AI assistance
- Generate affixed variants
- Validate root words
- Categorize errors
- Analyze morphophonemic changes

**Usage:**
```python
from modern_kata_kupas.utils.deepseek_helper import DeepSeekHelper

helper = DeepSeekHelper()
result = helper.segment_word("mempermainkan")
print(result.data)
```

---

### 2. Generate Gold Standard Test Set

**Location:** `experiments/generate_gold_standard.py`

Generate a comprehensive gold standard dataset for evaluation.

**Usage:**
```bash
# Generate 1000 entries covering all categories
python experiments/generate_gold_standard.py -o data/gold_standard.csv -s 1000

# Generate specific categories only
python experiments/generate_gold_standard.py -o data/gold_standard.csv --categories prefix_meN suffix_kan

# Add segmentations to existing word list
python experiments/generate_gold_standard.py --add-segmentations -i data/words.csv -o data/gold_standard.csv

# Show statistics
python experiments/generate_gold_standard.py --stats -i data/gold_standard.csv
```

**Output Format (CSV):**
| word | gold_segmentation | category | subcategory | confidence | morphemes | notes |
|------|-------------------|----------|-------------|------------|-----------|-------|
| mempermainkan | meN~per~main~kan | complex_two_prefix | | high | [...] | |

**Categories Generated:**
- `root_pure` - Pure root words without affixes
- `prefix_meN` - Words with meN- prefix
- `prefix_ber` - Words with ber- prefix
- `prefix_ter` - Words with ter- prefix
- `prefix_di` - Words with di- prefix
- `suffix_kan` - Words with -kan suffix
- `suffix_i` - Words with -i suffix
- `suffix_an` - Words with -an suffix
- `confix_ke_an` - Words with ke-...-an circumfix
- `confix_per_an` - Words with per-...-an circumfix
- `confix_peN_an` - Words with peN-...-an circumfix
- `reduplication_full` - Full reduplication (X-X)
- `reduplication_partial` - Partial reduplication (dwipurwa)
- `reduplication_phonetic` - Reduplication with sound change
- `complex_two_prefix` - Words with layered prefixes
- `complex_confix_suffix` - Words with circumfix + suffix
- `possessive` - Words with possessive pronouns
- `particle` - Words with particles
- `loanword_affixed` - Loanwords with Indonesian affixes
- `ambiguous` - Ambiguous cases

---

### 3. Expand Dictionary

**Location:** `experiments/expand_dictionary.py`

Expand the root word dictionary using PySastrawi and/or DeepSeek validation.

**Usage:**
```bash
# Expand from PySastrawi (recommended first step)
python experiments/expand_dictionary.py --from-sastrawi -o data/kata_dasar_full.txt

# Expand with DeepSeek validation
python experiments/expand_dictionary.py --from-sastrawi --validate --validate-sample 500

# Filter obviously affixed words
python experiments/expand_dictionary.py --from-sastrawi --filter-affixed

# Show statistics only
python experiments/expand_dictionary.py --stats -i data/kata_dasar.txt
```

**Output Format:**
```
# Indonesian Root Words Dictionary
# Total entries: 12543
#
buku
makan
rumah
...
```

---

### 4. Evaluate System

**Location:** `experiments/evaluate.py`

Evaluate the segmentation system against gold standard data.

**Usage:**
```bash
# Basic evaluation
python experiments/evaluate.py -g data/gold_standard.csv

# Save metrics to JSON
python experiments/evaluate.py -g data/gold_standard.csv -o experiments/results/metrics.json

# Save error analysis
python experiments/evaluate.py -g data/gold_standard.csv --errors experiments/results/errors.csv

# Compare multiple systems
python experiments/evaluate.py -g data/gold_standard.csv --compare -o experiments/results/comparison.json

# Quiet mode (no console output)
python experiments/evaluate.py -g data/gold_standard.csv -o experiments/results/metrics.json --quiet
```

**Metrics Computed:**
- **Word Accuracy** - Percentage of exact segmentations
- **Stem Accuracy** - Percentage of correct root words identified
- **Morpheme Precision/Recall/F1** - Morpheme-level metrics
- **Prefix/Suffix Accuracy** - Affix-level metrics
- **Per-Category Breakdown** - Performance by morphological category
- **Error Distribution** - Types and frequencies of errors

**Output Format (JSON):**
```json
{
  "word_accuracy": 0.875,
  "total_words": 1000,
  "correct_words": 875,
  "morpheme_precision": 0.92,
  "morpheme_recall": 0.89,
  "morpheme_f1": 0.905,
  "stem_accuracy": 0.91,
  "prefix_accuracy": 0.88,
  "suffix_accuracy": 0.93,
  "category_metrics": {
    "prefix_meN": {"accuracy": 0.92, "total": 40, "correct": 37},
    ...
  },
  "error_distribution": {
    "wrong_stem": 50,
    "false_positive_prefix": 25,
    ...
  }
}
```

---

## Typical Workflow for Paper

### Phase 1: Data Preparation (Week 1)

```bash
# 1. Expand root word dictionary
python experiments/expand_dictionary.py --from-sastrawi -o data/kata_dasar_full.txt

# 2. Generate gold standard test set
python experiments/generate_gold_standard.py -o data/gold_standard.csv -s 1000
```

### Phase 2: Evaluation (Week 1-2)

```bash
# 3. Run evaluation
python experiments/evaluate.py -g data/gold_standard.csv \
    -o experiments/results/metrics.json \
    --errors experiments/results/errors.csv

# 4. Compare with baselines
python experiments/evaluate.py -g data/gold_standard.csv \
    --compare \
    -o experiments/results/comparison.json
```

### Phase 3: Analysis (Week 2)

```bash
# 5. Generate error categorization with DeepSeek
# (Script to be added: analyze_errors.py)

# 6. Run ablation study
# (Script to be added: ablation_study.py)
```

---

## Output Directory Structure

```
experiments/
├── README.md
├── generate_gold_standard.py
├── expand_dictionary.py
├── evaluate.py
├── results/
│   ├── metrics.json
│   ├── errors.csv
│   ├── comparison.json
│   └── ablation.json
└── logs/
    └── generation.log
```

---

## Cost Estimation (DeepSeek API)

Based on ~1000 gold standard entries:

| Operation | Estimated Calls | Cost (DeepSeek) |
|-----------|-----------------|-----------------|
| Generate words | ~50 | $0.10 |
| Segment words | ~1000 | $0.50 |
| Validate roots | ~500 (optional) | $0.25 |
| **Total** | | **~$1-2** |

DeepSeek is significantly cheaper than alternatives, making it ideal for research data generation.

---

## Troubleshooting

### API Key Error
```
ValueError: DeepSeek API key not found
```
**Solution:** Make sure `.env` file exists with valid `DEEPSEEK_API_KEY`.

### Import Error
```
ImportError: Required dependencies not installed
```
**Solution:** Install extras: `pip install -e ".[experiments]"`

### Empty Gold Standard
```
Loaded 0 entries from gold_standard.csv
```
**Solution:** Check CSV format matches expected columns.

---

## Next Steps

See `../memory-bank/status-todolist-saran.md` for the full research roadmap.
