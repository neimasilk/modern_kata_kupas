# Panduan Prioritas 4 & 5: Future Features

**Target:** Programmer Junior - Intermediate
**Timeline:** v1.1 (1-2 bulan), v2.0 (3-6 bulan)

---

## Prioritas 4: Features untuk v1.1 (SHORT-TERM)

### 🎯 Tujuan
Meningkatkan performa, error handling, dan user experience tanpa mengubah API secara signifikan.

---

### 📦 Feature 4.1: Performance Optimization

#### Tujuan
Mempercepat segmentasi, terutama untuk batch processing.

#### Ideas & Implementation

**A. Dictionary Lookup Optimization**

Current: Linear search in set/list
Improvement: Trie data structure

```python
# src/modern_kata_kupas/data_structures.py
"""Efficient data structures for dictionary lookup."""

class Trie:
    """Trie (prefix tree) for fast word lookup."""

    def __init__(self):
        self.root = {}
        self.end_marker = '#'

    def insert(self, word: str) -> None:
        """Insert a word into the trie."""
        node = self.root
        for char in word:
            if char not in node:
                node[char] = {}
            node = node[char]
        node[self.end_marker] = True

    def search(self, word: str) -> bool:
        """Check if word exists in trie."""
        node = self.root
        for char in word:
            if char not in node:
                return False
            node = node[char]
        return self.end_marker in node

    def starts_with(self, prefix: str) -> bool:
        """Check if any word starts with prefix."""
        node = self.root
        for char in prefix:
            if char not in node:
                return False
            node = node[char]
        return True
```

**Implementation Steps:**
1. Create Trie class in new module
2. Modify DictionaryManager to use Trie instead of set
3. Benchmark before/after with 10,000 words
4. Expected improvement: 20-30% faster for dictionary lookups

**B. Caching Frequent Segmentations**

```python
# src/modern_kata_kupas/cache.py
"""LRU cache for segmentation results."""

from functools import lru_cache
from typing import Dict

class SegmentationCache:
    """Cache for frequently segmented words."""

    def __init__(self, max_size: int = 10000):
        self._cache: Dict[str, str] = {}
        self._max_size = max_size

    @lru_cache(maxsize=10000)
    def get(self, word: str) -> str:
        """Get cached result or None."""
        return self._cache.get(word)

    def set(self, word: str, result: str) -> None:
        """Cache a segmentation result."""
        if len(self._cache) >= self._max_size:
            # Remove oldest entry (simple FIFO, can improve to LRU)
            first_key = next(iter(self._cache))
            del self._cache[first_key]
        self._cache[word] = result
```

Usage in ModernKataKupas.segment():
```python
def segment(self, word: str) -> str:
    # Check cache first
    cached = self.cache.get(word)
    if cached is not None:
        return cached

    # Segment as usual
    result = self._segment_internal(word)

    # Cache result
    self.cache.set(word, result)
    return result
```

**C. Profiling & Benchmarking**

Create benchmark script:

```python
# benchmarks/benchmark_performance.py
"""Benchmark segmentation performance."""

import time
from modern_kata_kupas import ModernKataKupas

def benchmark(mkk, words, iterations=1000):
    """Benchmark segmentation speed."""
    start = time.time()
    for _ in range(iterations):
        for word in words:
            mkk.segment(word)
    end = time.time()
    return end - start

if __name__ == "__main__":
    mkk = ModernKataKupas()

    # Test words
    test_words = [
        "menulis", "membaca", "makanan", "rumah-rumah",
        "mempertaruhkan", "keberlangsungan", "dipersemakmurkan"
    ]

    # Benchmark
    total_time = benchmark(mkk, test_words, iterations=1000)
    words_per_sec = (len(test_words) * 1000) / total_time

    print(f"Total time: {total_time:.2f}s")
    print(f"Words/sec: {words_per_sec:.2f}")
    print(f"Avg time per word: {(total_time / (len(test_words) * 1000)) * 1000:.2f}ms")
```

---

### 🔧 Feature 4.2: Error Handling & Logging

#### Better Error Messages

```python
# src/modern_kata_kupas/exceptions.py (extend)

class SegmentationWarning(UserWarning):
    """Warning for non-critical segmentation issues."""
    pass

class DictionaryIncompleteWarning(SegmentationWarning):
    """Warning when word cannot be segmented due to missing dictionary entries."""
    pass

# Usage in separator.py
import warnings

def segment(self, word: str) -> str:
    # ... existing code ...

    if stem not in self.dictionary.kata_dasar:
        warnings.warn(
            f"Word '{word}' could not be fully segmented. "
            f"Possible missing root: '{stem}'. "
            f"Consider adding to dictionary or checking spelling.",
            DictionaryIncompleteWarning
        )

    return result
```

#### Logging System

```python
# src/modern_kata_kupas/logger.py
"""Logging configuration for ModernKataKupas."""

import logging
from typing import Optional

def setup_logger(
    name: str = "modern_kata_kupas",
    level: Optional[int] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """Setup logger with consistent formatting."""

    logger = logging.getLogger(name)

    if level is None:
        level = logging.WARNING

    logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
```

Usage:
```python
# In ModernKataKupas.__init__
from .logger import setup_logger

class ModernKataKupas:
    def __init__(self, ..., log_level=None, log_file=None):
        self.logger = setup_logger(level=log_level, log_file=log_file)

    def segment(self, word: str) -> str:
        self.logger.debug(f"Segmenting word: {word}")
        # ... process ...
        self.logger.debug(f"Result: {result}")
        return result
```

---

### 💻 Feature 4.3: CLI Enhancements

#### Progress Bar for Batch Processing

```python
# cli.py (modify segment_file command)

from tqdm import tqdm  # pip install tqdm

@cli.command("segment-file")
@click.argument("input_file", type=click.File('r', encoding='utf-8'))
@click.option("--output", "-o", type=click.File('w', encoding='utf-8'))
@click.option("--show-progress/--no-progress", default=True)
def segment_file(input_file, output, show_progress):
    """Segment words from a file (one word per line)."""
    mkk = ModernKataKupas()

    # Read all lines
    lines = input_file.readlines()

    # Create progress bar if enabled
    iterator = tqdm(lines, desc="Segmenting") if show_progress else lines

    results = []
    for line in iterator:
        word = line.strip()
        if word:
            segmented = mkk.segment(word)
            results.append(f"{word} → {segmented}")

    # Output
    if output:
        output.write('\n'.join(results))
    else:
        for result in results:
            click.echo(result)
```

#### Interactive Mode

```python
@cli.command("interactive")
@click.option("--dictionary", "-d", type=click.Path(exists=True))
def interactive(dictionary):
    """Interactive segmentation mode."""
    mkk = ModernKataKupas(dictionary_path=dictionary)

    click.echo("ModernKataKupas Interactive Mode")
    click.echo("Type 'exit' to quit, 'help' for commands\n")

    while True:
        try:
            user_input = click.prompt("Word", type=str, default="")

            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'help':
                click.echo("\nCommands:")
                click.echo("  exit - Quit interactive mode")
                click.echo("  help - Show this help")
                click.echo("  stats - Show statistics")
                continue
            elif user_input.lower() == 'stats':
                click.echo(f"Dictionary size: {len(mkk.dictionary.kata_dasar)}")
                continue

            if user_input.strip():
                result = mkk.segment(user_input)
                click.echo(f"  → {result}")

        except (KeyboardInterrupt, EOFError):
            click.echo("\nExiting...")
            break
```

---

## Prioritas 5: Features untuk v2.0 (LONG-TERM)

### 🤖 Feature 5.1: Machine Learning Integration

#### Context-Aware Disambiguation

**Goal:** Use ML model to choose best segmentation in ambiguous cases.

**Approach:**
1. Collect dataset of correct segmentations (human annotated)
2. Train classifier to predict correct segmentation
3. Use as tie-breaker when rule-based system has multiple candidates

**Tech Stack:**
- scikit-learn or PyTorch
- Features: word context, POS tags, ngrams
- Model: Random Forest or small neural network

**Prototype Code:**

```python
# src/modern_kata_kupas/ml_disambiguator.py
"""ML-based disambiguation (v2.0 feature)."""

from typing import List, Tuple
import pickle

class MLDisambiguator:
    """Machine learning disambiguator for ambiguous segmentations."""

    def __init__(self, model_path: str = None):
        self.model = None
        if model_path:
            self.load_model(model_path)

    def load_model(self, path: str):
        """Load trained model."""
        with open(path, 'rb') as f:
            self.model = pickle.load(f)

    def extract_features(self, word: str, candidates: List[str]) -> dict:
        """Extract features for ML model."""
        return {
            'word_length': len(word),
            'num_candidates': len(candidates),
            'avg_morpheme_length': sum(len(c.split('~')) for c in candidates) / len(candidates),
            # Add more features
        }

    def disambiguate(self, word: str, candidates: List[Tuple[str, float]]) -> str:
        """Choose best candidate using ML model."""
        if not self.model or len(candidates) == 1:
            return candidates[0][0]

        features = self.extract_features(word, [c[0] for c in candidates])
        prediction = self.model.predict([features])
        return candidates[prediction[0]][0]
```

---

### 🌐 Feature 5.2: API Server

#### REST API with FastAPI

```python
# api/main.py
"""REST API for ModernKataKupas (v2.0 feature)."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from modern_kata_kupas import ModernKataKupas

app = FastAPI(title="ModernKataKupas API", version="2.0.0")

# Initialize segmenter
mkk = ModernKataKupas()

class SegmentRequest(BaseModel):
    word: str

class SegmentResponse(BaseModel):
    word: str
    segmented: str
    morphemes: list[str]

@app.post("/segment", response_model=SegmentResponse)
async def segment_word(request: SegmentRequest):
    """Segment a single Indonesian word."""
    try:
        result = mkk.segment(request.word)
        morphemes = result.split('~')
        return SegmentResponse(
            word=request.word,
            segmented=result,
            morphemes=morphemes
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/segment-batch")
async def segment_batch(words: list[str]):
    """Segment multiple words."""
    results = []
    for word in words:
        result = mkk.segment(word)
        results.append({
            "word": word,
            "segmented": result
        })
    return {"results": results}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}
```

Deploy:
```bash
# Install dependencies
pip install fastapi uvicorn

# Run server
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Test
curl -X POST http://localhost:8000/segment \
  -H "Content-Type: application/json" \
  -d '{"word": "menulis"}'
```

---

### 📚 Feature 5.3: Dialect Support

Support for regional Indonesian dialects.

**Implementation Idea:**

```python
# src/modern_kata_kupas/dialect.py
"""Dialect-aware segmentation (v2.0 feature)."""

class DialectAdapter:
    """Adapter for different Indonesian dialects."""

    DIALECTS = {
        'standard': 'Standard Indonesian (KBBI)',
        'jakarta': 'Jakarta/Betawi dialect',
        'java': 'Javanese-influenced Indonesian',
        'sumatra': 'Sumatran dialects',
    }

    def __init__(self, dialect: str = 'standard'):
        self.dialect = dialect
        self.load_dialect_rules(dialect)

    def load_dialect_rules(self, dialect: str):
        """Load dialect-specific rules and vocabulary."""
        # Load dialect-specific dictionary additions
        # Load dialect-specific affix variations
        pass

    def adapt_word(self, word: str) -> str:
        """Adapt word from dialect to standard for segmentation."""
        # E.g., Jakarta: "gue" → "saya", "ngapain" → "mengapakan"
        return word
```

---

### 📊 Feature 5.4: Evaluation & Benchmarking Suite

Create comprehensive evaluation against gold standard.

```python
# evaluation/evaluate.py
"""Evaluation script against gold standard dataset."""

from modern_kata_kupas import ModernKataKupas
import json

def load_gold_standard(path: str):
    """Load gold standard segmentations."""
    with open(path, 'r') as f:
        return json.load(f)

def evaluate(mkk, gold_standard):
    """Evaluate segmenter against gold standard."""
    correct = 0
    total = len(gold_standard)

    for item in gold_standard:
        word = item['word']
        expected = item['segmented']
        result = mkk.segment(word)

        if result == expected:
            correct += 1

    accuracy = correct / total
    return {
        'accuracy': accuracy,
        'correct': correct,
        'total': total
    }

if __name__ == "__main__":
    mkk = ModernKataKupas()
    gold = load_gold_standard('data/gold_standard.json')
    results = evaluate(mkk, gold)
    print(f"Accuracy: {results['accuracy']:.2%}")
```

---

## 📋 Implementation Roadmap

### v1.1 Timeline (1-2 bulan)

**Month 1:**
- Week 1-2: Performance optimization (Trie, caching)
- Week 3: Better error handling & logging
- Week 4: CLI enhancements (progress bar, interactive mode)

**Month 2:**
- Week 1: Testing & bug fixes
- Week 2: Documentation updates
- Week 3: Beta release & user feedback
- Week 4: Final release v1.1

### v2.0 Timeline (3-6 bulan)

**Month 1-2: Research & Prototyping**
- Collect annotated dataset for ML
- Research ML approaches
- Prototype disambiguation model

**Month 3-4: Core Development**
- Implement ML disambiguator
- Build API server
- Develop dialect support

**Month 5: Integration & Testing**
- Integrate all features
- Comprehensive testing
- Performance benchmarking

**Month 6: Release**
- Beta testing
- Documentation
- Final release v2.0

---

## ✅ Success Metrics

### v1.1 Targets:
- [ ] Segmentation speed: 2x faster (from ~100 words/sec to ~200 words/sec)
- [ ] Cache hit rate: >80% for common words
- [ ] User-friendly error messages for 100% of error cases
- [ ] CLI with progress indication for batch >100 words

### v2.0 Targets:
- [ ] Disambiguation accuracy: >95% on ambiguous cases
- [ ] API response time: <100ms per word
- [ ] Dialect support: 3+ major dialects
- [ ] Benchmark score: Top 3 among Indonesian morphological analyzers

---

## 📚 Resources for Learning

### For Feature 4 (v1.1):
- **Performance:** Python profiling (cProfile, line_profiler)
- **Data Structures:** Trie implementation tutorials
- **CLI:** Click advanced features documentation

### For Feature 5 (v2.0):
- **ML:** scikit-learn tutorials, NLP with spaCy
- **API:** FastAPI documentation
- **Linguistics:** Papers on Indonesian morphology
- **Benchmarking:** CoNLL shared tasks, UD treebanks

---

**End of Panduan Prioritas 4 & 5**

Kembali ke: [Panduan Langkah Selanjutnya](panduan-langkah-selanjutnya.md)
