"""
SUPERSEDED (Sep 2026): single run, no significance test, and baseline/MKK use different
punctuation cleaning. Use experiments/downstream_significance.py.

Text Classification Downstream Evaluation for ModernKataKupas

This module evaluates the impact of MKK preprocessing on text classification tasks.
Uses IndoNLU SmSA (Sentiment Analysis) dataset.

Compares:
1. Baseline (no preprocessing)
2. BPE preprocessing (SentencePiece)
3. MKK preprocessing (ModernKataKupas)

Metrics:
- Accuracy
- Macro F1 Score
- Training time

Usage:
    python text_classification_eval.py [options]

Options:
    --sample-size N     Use only N samples per split (for testing)
    --output PATH       Output JSON path
    --skip-bpe          Skip BPE experiment (if SentencePiece not available)
"""

import argparse
import json
import logging
import os
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modern_kata_kupas import ModernKataKupas

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Result from a single classification experiment."""
    method: str
    accuracy: float
    f1_macro: float
    f1_weighted: float
    train_time_seconds: float
    vocab_size: int
    total_samples: int
    preprocessing_time_seconds: float = 0.0


@dataclass
class ExperimentResults:
    """Full experiment results."""
    dataset: str
    total_train: int
    total_test: int
    num_classes: int
    results: Dict[str, ClassificationResult] = field(default_factory=dict)
    comparison: Dict[str, Any] = field(default_factory=dict)


class TextClassificationEvaluator:
    """Evaluate text classification with different preprocessing methods."""

    def __init__(self):
        self.mkk = ModernKataKupas()
        self._check_dependencies()

    def _check_dependencies(self):
        """Check required dependencies."""
        try:
            import datasets
            self._datasets_available = True
        except ImportError:
            self._datasets_available = False
            logger.warning("datasets library not available. Install with: pip install datasets")

        try:
            import sklearn
            self._sklearn_available = True
        except ImportError:
            self._sklearn_available = False
            logger.warning("scikit-learn not available. Install with: pip install scikit-learn")

        try:
            import sentencepiece
            self._spm_available = True
        except ImportError:
            self._spm_available = False
            logger.warning("SentencePiece not available. BPE will be skipped.")

    def load_dataset(self, sample_size: Optional[int] = None) -> Tuple[List[str], List[int], List[str], List[int]]:
        """
        Load IndoNLU SmSA dataset from GitHub.

        Returns:
            Tuple of (train_texts, train_labels, test_texts, test_labels)
        """
        import urllib.request
        import csv

        # SmSA dataset URLs from IndoNLU GitHub
        base_url = "https://raw.githubusercontent.com/indobenchmark/indonlu/master/dataset/smsa_doc-sentiment-prosa"
        train_url = f"{base_url}/train_preprocess.tsv"
        test_url = f"{base_url}/test_preprocess.tsv"

        # Local cache directory
        cache_dir = Path(__file__).parent / "data" / "smsa_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        train_cache = cache_dir / "train_preprocess.tsv"
        test_cache = cache_dir / "test_preprocess.tsv"

        def download_if_needed(url: str, cache_path: Path) -> Path:
            if not cache_path.exists():
                logger.info(f"Downloading {cache_path.name}...")
                urllib.request.urlretrieve(url, cache_path)
            return cache_path

        def load_tsv(path: Path) -> Tuple[List[str], List[int]]:
            texts = []
            labels = []
            label_map = {"positive": 2, "neutral": 1, "negative": 0}
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 2:
                        texts.append(row[0])
                        label_str = row[1].strip().lower()
                        labels.append(label_map.get(label_str, 1))
            return texts, labels

        logger.info("Loading IndoNLU SmSA dataset from GitHub...")

        # Download if needed
        download_if_needed(train_url, train_cache)
        download_if_needed(test_url, test_cache)

        # Load data
        train_texts, train_labels = load_tsv(train_cache)
        test_texts, test_labels = load_tsv(test_cache)

        # Sample if requested
        if sample_size:
            train_texts = train_texts[:sample_size]
            train_labels = train_labels[:sample_size]
            test_texts = test_texts[:min(sample_size // 2, len(test_texts))]
            test_labels = test_labels[:min(sample_size // 2, len(test_labels))]

        logger.info(f"Loaded {len(train_texts)} train, {len(test_texts)} test samples")
        logger.info(f"Labels: {set(train_labels)}")

        return train_texts, train_labels, test_texts, test_labels

    def preprocess_baseline(self, texts: List[str]) -> List[str]:
        """Baseline preprocessing: lowercase and simple tokenization."""
        processed = []
        for text in texts:
            # Simple preprocessing: lowercase, split on whitespace
            tokens = text.lower().split()
            processed.append(" ".join(tokens))
        return processed

    def preprocess_mkk(self, texts: List[str]) -> List[str]:
        """Preprocess using ModernKataKupas morphological segmentation."""
        processed = []
        for text in texts:
            words = text.lower().split()
            segmented_words = []
            for word in words:
                # Clean word of punctuation for segmentation
                clean_word = ''.join(c for c in word if c.isalnum() or c == '-')
                if clean_word:
                    try:
                        result = self.mkk.segment(clean_word)
                        # Split on ~ separator and flatten
                        morphemes = result.replace("~", " ")
                        segmented_words.append(morphemes)
                    except Exception:
                        segmented_words.append(clean_word)
                else:
                    segmented_words.append(word)
            processed.append(" ".join(segmented_words))
        return processed

    def preprocess_bpe(self, texts: List[str], vocab_size: int = 8000) -> List[str]:
        """Preprocess using SentencePiece BPE."""
        if not self._spm_available:
            logger.warning("SentencePiece not available, falling back to baseline")
            return self.preprocess_baseline(texts)

        import sentencepiece as spm

        # Train BPE model on texts
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            for text in texts:
                f.write(text.lower() + '\n')
            temp_corpus = f.name

        model_prefix = tempfile.mktemp()

        try:
            spm.SentencePieceTrainer.train(
                input=temp_corpus,
                model_prefix=model_prefix,
                vocab_size=vocab_size,
                model_type='bpe',
                character_coverage=1.0,
                pad_id=3
            )

            sp = spm.SentencePieceProcessor()
            sp.load(f"{model_prefix}.model")

            processed = []
            for text in texts:
                tokens = sp.encode_as_pieces(text.lower())
                processed.append(" ".join(tokens))

            return processed

        finally:
            # Cleanup temp files
            for ext in ['.txt', '.model', '.vocab']:
                try:
                    os.unlink(temp_corpus if ext == '.txt' else f"{model_prefix}{ext}")
                except Exception:
                    pass

    def train_and_evaluate(
        self,
        train_texts: List[str],
        train_labels: List[int],
        test_texts: List[str],
        test_labels: List[int],
        method_name: str
    ) -> ClassificationResult:
        """Train classifier and evaluate on test set."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, f1_score

        logger.info(f"Training classifier for method: {method_name}")

        # Vectorize
        vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2))
        X_train = vectorizer.fit_transform(train_texts)
        X_test = vectorizer.transform(test_texts)

        vocab_size = len(vectorizer.vocabulary_)
        logger.info(f"Vocabulary size: {vocab_size}")

        # Train
        start_time = time.time()
        classifier = LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1)
        classifier.fit(X_train, train_labels)
        train_time = time.time() - start_time

        # Predict
        predictions = classifier.predict(X_test)

        # Calculate metrics
        accuracy = accuracy_score(test_labels, predictions)
        f1_macro = f1_score(test_labels, predictions, average='macro')
        f1_weighted = f1_score(test_labels, predictions, average='weighted')

        logger.info(f"  Accuracy: {accuracy:.4f}")
        logger.info(f"  F1 Macro: {f1_macro:.4f}")
        logger.info(f"  Train time: {train_time:.2f}s")

        return ClassificationResult(
            method=method_name,
            accuracy=accuracy,
            f1_macro=f1_macro,
            f1_weighted=f1_weighted,
            train_time_seconds=train_time,
            vocab_size=vocab_size,
            total_samples=len(train_texts) + len(test_texts)
        )

    def run_experiments(
        self,
        sample_size: Optional[int] = None,
        skip_bpe: bool = False
    ) -> ExperimentResults:
        """Run all classification experiments."""

        # Load dataset
        train_texts, train_labels, test_texts, test_labels = self.load_dataset(sample_size)

        results = ExperimentResults(
            dataset="IndoNLU SmSA (Sentiment)",
            total_train=len(train_texts),
            total_test=len(test_texts),
            num_classes=len(set(train_labels))
        )

        # Experiment 1: Baseline
        logger.info("\n" + "=" * 60)
        logger.info("EXPERIMENT 1: Baseline (No Preprocessing)")
        logger.info("=" * 60)

        start_pp = time.time()
        baseline_train = self.preprocess_baseline(train_texts)
        baseline_test = self.preprocess_baseline(test_texts)
        pp_time = time.time() - start_pp

        baseline_result = self.train_and_evaluate(
            baseline_train, train_labels,
            baseline_test, test_labels,
            "Baseline"
        )
        baseline_result.preprocessing_time_seconds = pp_time
        results.results["baseline"] = baseline_result

        # Experiment 2: MKK Preprocessing
        logger.info("\n" + "=" * 60)
        logger.info("EXPERIMENT 2: MKK Preprocessing")
        logger.info("=" * 60)

        start_pp = time.time()
        mkk_train = self.preprocess_mkk(train_texts)
        mkk_test = self.preprocess_mkk(test_texts)
        pp_time = time.time() - start_pp
        logger.info(f"MKK preprocessing time: {pp_time:.2f}s")

        mkk_result = self.train_and_evaluate(
            mkk_train, train_labels,
            mkk_test, test_labels,
            "MKK"
        )
        mkk_result.preprocessing_time_seconds = pp_time
        results.results["mkk"] = mkk_result

        # Experiment 3: BPE Preprocessing
        if not skip_bpe and self._spm_available:
            logger.info("\n" + "=" * 60)
            logger.info("EXPERIMENT 3: BPE Preprocessing")
            logger.info("=" * 60)

            start_pp = time.time()
            bpe_train = self.preprocess_bpe(train_texts)
            bpe_test = self.preprocess_bpe(test_texts)
            pp_time = time.time() - start_pp
            logger.info(f"BPE preprocessing time: {pp_time:.2f}s")

            bpe_result = self.train_and_evaluate(
                bpe_train, train_labels,
                bpe_test, test_labels,
                "BPE"
            )
            bpe_result.preprocessing_time_seconds = pp_time
            results.results["bpe"] = bpe_result

        # Compute comparison
        results.comparison = self._compute_comparison(results)

        return results

    def _compute_comparison(self, results: ExperimentResults) -> Dict[str, Any]:
        """Compute comparison metrics between methods."""
        comparison = {}

        baseline = results.results.get("baseline")
        mkk = results.results.get("mkk")
        bpe = results.results.get("bpe")

        if baseline and mkk:
            comparison["mkk_vs_baseline"] = {
                "accuracy_diff": mkk.accuracy - baseline.accuracy,
                "f1_diff": mkk.f1_macro - baseline.f1_macro,
                "vocab_reduction_pct": (1 - mkk.vocab_size / baseline.vocab_size) * 100 if baseline.vocab_size > 0 else 0,
                "mkk_better_accuracy": mkk.accuracy > baseline.accuracy,
                "mkk_better_f1": mkk.f1_macro > baseline.f1_macro
            }

        if mkk and bpe:
            comparison["mkk_vs_bpe"] = {
                "accuracy_diff": mkk.accuracy - bpe.accuracy,
                "f1_diff": mkk.f1_macro - bpe.f1_macro,
                "mkk_better_accuracy": mkk.accuracy > bpe.accuracy,
                "mkk_better_f1": mkk.f1_macro > bpe.f1_macro
            }

        return comparison

    def print_report(self, results: ExperimentResults):
        """Print formatted comparison report."""
        print("\n" + "=" * 70)
        print(" TEXT CLASSIFICATION EVALUATION RESULTS")
        print("=" * 70)
        print(f"\nDataset: {results.dataset}")
        print(f"Train samples: {results.total_train}")
        print(f"Test samples: {results.total_test}")
        print(f"Classes: {results.num_classes}")

        print("\n" + "-" * 70)
        print(" RESULTS BY METHOD")
        print("-" * 70)
        print(f"{'Method':<15} {'Accuracy':>10} {'F1 Macro':>10} {'F1 Weighted':>12} {'Vocab Size':>12} {'Train Time':>12}")
        print("-" * 70)

        for name, result in results.results.items():
            print(f"{result.method:<15} {result.accuracy:>10.4f} {result.f1_macro:>10.4f} {result.f1_weighted:>12.4f} {result.vocab_size:>12} {result.train_time_seconds:>11.2f}s")

        if results.comparison:
            print("\n" + "-" * 70)
            print(" COMPARISON")
            print("-" * 70)

            if "mkk_vs_baseline" in results.comparison:
                comp = results.comparison["mkk_vs_baseline"]
                print(f"\nMKK vs Baseline:")
                print(f"  Accuracy diff: {comp['accuracy_diff']:+.4f}")
                print(f"  F1 diff: {comp['f1_diff']:+.4f}")
                print(f"  Vocab reduction: {comp['vocab_reduction_pct']:.1f}%")

            if "mkk_vs_bpe" in results.comparison:
                comp = results.comparison["mkk_vs_bpe"]
                print(f"\nMKK vs BPE:")
                print(f"  Accuracy diff: {comp['accuracy_diff']:+.4f}")
                print(f"  F1 diff: {comp['f1_diff']:+.4f}")

        print("\n" + "=" * 70)

    def save_results(self, results: ExperimentResults, path: str):
        """Save results to JSON file."""
        import numpy as np

        # Custom encoder for numpy types
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (np.bool_, np.integer)):
                    return int(obj)
                if isinstance(obj, np.floating):
                    return float(obj)
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super().default(obj)

        # Convert to dict
        data = {
            "dataset": results.dataset,
            "total_train": results.total_train,
            "total_test": results.total_test,
            "num_classes": results.num_classes,
            "results": {k: asdict(v) for k, v in results.results.items()},
            "comparison": results.comparison,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

        logger.info(f"Results saved to: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Text Classification Downstream Evaluation for ModernKataKupas"
    )
    parser.add_argument(
        "--sample-size", "-s",
        type=int,
        default=None,
        help="Use only N samples (for testing)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="experiments/results/text_classification_eval.json",
        help="Output JSON path"
    )
    parser.add_argument(
        "--skip-bpe",
        action="store_true",
        help="Skip BPE experiment"
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print(" ModernKataKupas Text Classification Evaluation")
    print("=" * 70)

    evaluator = TextClassificationEvaluator()

    try:
        results = evaluator.run_experiments(
            sample_size=args.sample_size,
            skip_bpe=args.skip_bpe
        )

        evaluator.print_report(results)
        evaluator.save_results(results, args.output)

        # Summary
        print("\n[OK] Experiment completed successfully!")
        print(f"Results saved to: {args.output}")

        return 0

    except Exception as e:
        logger.error(f"Experiment failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
