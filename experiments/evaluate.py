"""
Quantitative Evaluation Module for Indonesian Morphological Segmentation

This module provides functions to evaluate morphological segmentation systems
against gold standard data with metrics like:
- Word-level accuracy
- Morpheme-level precision, recall, F1
- Stem accuracy
- Affix accuracy
- Per-category breakdown
- Error analysis

Usage:
    python experiments/evaluate.py --gold data/gold_standard.csv --system modernkatakupas
    python experiments/evaluate.py --compare --systems modernkatakupas sastrawi
"""
import os
import sys
import json
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from enum import Enum

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modern_kata_kupas import ModernKataKupas

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class SegmentationResult:
    """Result of segmenting a single word."""
    word: str
    prediction: str
    gold: str
    correct: bool = False
    morphemes_pred: List[str] = field(default_factory=list)
    morphemes_gold: List[str] = field(default_factory=list)
    category: Optional[str] = None
    error_type: Optional[str] = None


@dataclass
class EvaluationMetrics:
    """Container for evaluation metrics."""
    # Word-level metrics
    word_accuracy: float = 0.0
    total_words: int = 0
    correct_words: int = 0

    # Morpheme-level metrics
    morpheme_precision: float = 0.0
    morpheme_recall: float = 0.0
    morpheme_f1: float = 0.0
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0

    # Stem accuracy
    stem_accuracy: float = 0.0
    correct_stems: int = 0

    # Affix accuracy
    prefix_accuracy: float = 0.0
    suffix_accuracy: float = 0.0
    correct_prefixes: int = 0
    correct_suffixes: int = 0

    # Per-category metrics
    category_metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # Error distribution
    error_distribution: Dict[str, int] = field(default_factory=dict)

    # Confusion data
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "word_accuracy": self.word_accuracy,
            "total_words": self.total_words,
            "correct_words": self.correct_words,
            "morpheme_precision": self.morpheme_precision,
            "morpheme_recall": self.morpheme_recall,
            "morpheme_f1": self.morpheme_f1,
            "true_positives": self.true_positives,
            "false_positives": self.false_positives,
            "false_negatives": self.false_negatives,
            "stem_accuracy": self.stem_accuracy,
            "correct_stems": self.correct_stems,
            "prefix_accuracy": self.prefix_accuracy,
            "suffix_accuracy": self.suffix_accuracy,
            "correct_prefixes": self.correct_prefixes,
            "correct_suffixes": self.correct_suffixes,
            "category_metrics": self.category_metrics,
            "error_distribution": self.error_distribution,
        }


# ============================================================================
# Evaluation Functions
# ============================================================================

class MorphologicalEvaluator:
    """Evaluator for Indonesian morphological segmentation systems."""

    def __init__(self, system: Optional[Any] = None):
        """
        Initialize evaluator.

        Args:
            system: Segmentation system with segment(word) method.
                   If None, uses ModernKataKupas.
        """
        self.system = system or ModernKataKupas()
        self.results: List[SegmentationResult] = []

    def parse_segmentation(self, seg: str) -> List[str]:
        """
        Parse segmentation string into morpheme list.

        Args:
            seg: Segmentation string (e.g., "meN~tulis~kan")

        Returns:
            List of morphemes
        """
        if not seg or seg == seg.strip('~'):
            return [seg]

        # Split by ~ and filter empty strings
        morphemes = [m for m in seg.split('~') if m]
        return morphemes

    def extract_stem(self, morphemes: List[str]) -> Optional[str]:
        """
        Extract stem (root word) from morphemes.

        The stem is typically the morpheme that doesn't match
        known affix patterns.

        Args:
            morphemes: List of morphemes

        Returns:
            Stem or None
        """
        # Known affixes (canonical forms)
        prefixes = {'meN', 'ber', 'ter', 'di', 'peN', 'per', 'ke', 'se'}
        suffixes = {'kan', 'i', 'an', 'lah', 'kah', 'pun', 'tah', 'nya', 'ku', 'mu'}
        markers = {'ulg', 'rp', 'rs'}  # Reduplication markers

        for m in morphemes:
            if (m not in prefixes and
                m not in suffixes and
                m not in markers and
                not m.startswith('rs(')):
                return m
        return None

    def extract_affixes(self, morphemes: List[str]) -> Tuple[List[str], List[str]]:
        """
        Extract prefixes and suffixes from morphemes.

        Args:
            morphemes: List of morphemes

        Returns:
            Tuple of (prefixes, suffixes)
        """
        prefixes = {'meN', 'ber', 'ter', 'di', 'peN', 'per', 'ke', 'se'}
        suffixes = {'kan', 'i', 'an', 'lah', 'kah', 'pun', 'tah', 'nya', 'ku', 'mu'}
        markers = {'ulg', 'rp', 'rs'}

        pref_list = []
        suff_list = []
        after_root = False

        for m in morphemes:
            if m in markers or m.startswith('rs('):
                after_root = True
            elif m in prefixes:
                pref_list.append(m)
            elif m in suffixes:
                suff_list.append(m)
                after_root = True
            elif after_root:
                # After we hit a suffix-like marker, everything after is suffix
                suff_list.append(m)
            else:
                # This is likely the root
                after_root = True

        return pref_list, suff_list

    def segment_word(self, word: str) -> str:
        """Segment a word using the configured system."""
        try:
            return self.system.segment(word)
        except Exception as e:
            logger.warning(f"Error segmenting '{word}': {e}")
            return word

    def evaluate_word(
        self,
        word: str,
        gold_segmentation: str,
        category: Optional[str] = None
    ) -> SegmentationResult:
        """Evaluate segmentation of a single word."""
        prediction = self.segment_word(word)

        morphemes_pred = self.parse_segmentation(prediction)
        morphemes_gold = self.parse_segmentation(gold_segmentation)

        # Word-level correctness
        correct = (prediction == gold_segmentation)

        result = SegmentationResult(
            word=word,
            prediction=prediction,
            gold=gold_segmentation,
            correct=correct,
            morphemes_pred=morphemes_pred,
            morphemes_gold=morphemes_gold,
            category=category
        )

        return result

    def evaluate_dataset(
        self,
        data: List[Dict[str, str]],
        word_col: str = "word",
        gold_col: str = "gold_segmentation",
        category_col: Optional[str] = "category",
        show_progress: bool = True
    ) -> EvaluationMetrics:
        """
        Evaluate on a dataset.

        Args:
            data: List of dictionaries with word and gold segmentation
            word_col: Column name for words
            gold_col: Column name for gold segmentations
            category_col: Column name for categories (optional)
            show_progress: Whether to show progress bar

        Returns:
            EvaluationMetrics object
        """
        results = []

        iterator = data
        if show_progress:
            try:
                from tqdm import tqdm
                iterator = tqdm(data, desc="Evaluating")
            except ImportError:
                pass

        for item in iterator:
            word = item.get(word_col, "")
            gold = item.get(gold_col, "")
            category = item.get(category_col) if category_col else None

            result = self.evaluate_word(word, gold, category)
            results.append(result)

        self.results = results
        return self.compute_metrics(results)

    def load_gold_standard(
        self,
        path: str
    ) -> List[Dict[str, str]]:
        """Load gold standard from CSV file."""
        data = []

        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)

        logger.info(f"Loaded {len(data)} entries from {path}")
        return data

    def compute_metrics(self, results: List[SegmentationResult]) -> EvaluationMetrics:
        """Compute metrics from evaluation results."""
        metrics = EvaluationMetrics()

        if not results:
            return metrics

        metrics.total_words = len(results)

        # Word-level accuracy
        metrics.correct_words = sum(1 for r in results if r.correct)
        metrics.word_accuracy = metrics.correct_words / metrics.total_words

        # Morpheme-level metrics
        tp, fp, fn = 0, 0, 0

        # Stem accuracy
        correct_stems = 0

        # Affix accuracy
        correct_prefixes = 0
        correct_suffixes = 0
        total_prefixes = 0
        total_suffixes = 0

        # Category metrics
        category_counts = defaultdict(int)
        category_correct = defaultdict(int)

        # Error distribution
        error_types = Counter()

        for r in results:
            # Category tracking
            if r.category:
                category_counts[r.category] += 1
                if r.correct:
                    category_correct[r.category] += 1

            # Skip if prediction equals word (no segmentation)
            if r.prediction == r.word:
                continue

            # Morpheme-level comparison (using set for exact match)
            pred_set = set(r.morphemes_pred)
            gold_set = set(r.morphemes_gold)

            tp += len(pred_set & gold_set)
            fp += len(pred_set - gold_set)
            fn += len(gold_set - pred_set)

            # Stem comparison
            pred_stem = self.extract_stem(r.morphemes_pred)
            gold_stem = self.extract_stem(r.morphemes_gold)

            if pred_stem and pred_stem == gold_stem:
                correct_stems += 1

            # Prefix comparison
            pred_prefs, _ = self.extract_affixes(r.morphemes_pred)
            gold_prefs, _ = self.extract_affixes(r.morphemes_gold)

            if set(pred_prefs) == set(gold_prefs):
                correct_prefixes += 1
            total_prefixes += 1 if gold_prefs else 1

            # Suffix comparison
            _, pred_suffs = self.extract_affixes(r.morphemes_pred)
            _, gold_suffs = self.extract_affixes(r.morphemes_gold)

            if set(pred_suffs) == set(gold_suffs):
                correct_suffixes += 1
            total_suffixes += 1 if gold_suffs else 1

            # Error classification
            if not r.correct:
                error_type = self._classify_error(r)
                error_types[error_type] += 1

                # Store for detailed analysis
                metrics.errors.append({
                    "word": r.word,
                    "prediction": r.prediction,
                    "gold": r.gold,
                    "error_type": error_type,
                    "category": r.category
                })

        metrics.true_positives = tp
        metrics.false_positives = fp
        metrics.false_negatives = fn

        # Calculate precision, recall, F1
        if tp + fp > 0:
            metrics.morpheme_precision = tp / (tp + fp)
        if tp + fn > 0:
            metrics.morpheme_recall = tp / (tp + fn)
        if metrics.morpheme_precision + metrics.morpheme_recall > 0:
            metrics.morpheme_f1 = (
                2 * metrics.morpheme_precision * metrics.morpheme_recall /
                (metrics.morpheme_precision + metrics.morpheme_recall)
            )

        # Stem accuracy
        if results:
            metrics.stem_accuracy = correct_stems / len(results)

        metrics.correct_stems = correct_stems

        # Affix accuracy
        if total_prefixes > 0:
            metrics.prefix_accuracy = correct_prefixes / total_prefixes
        if total_suffixes > 0:
            metrics.suffix_accuracy = correct_suffixes / total_suffixes

        metrics.correct_prefixes = correct_prefixes
        metrics.correct_suffixes = correct_suffixes

        # Per-category metrics
        for cat in category_counts:
            metrics.category_metrics[cat] = {
                "accuracy": category_correct[cat] / category_counts[cat],
                "total": category_counts[cat],
                "correct": category_correct[cat]
            }

        metrics.error_distribution = dict(error_types)

        return metrics

    def _classify_error(self, result: SegmentationResult) -> str:
        """Classify the type of error in a segmentation result."""
        pred = result.morphemes_pred
        gold = result.morphemes_gold

        pred_set = set(pred)
        gold_set = set(gold)

        # Check for various error types
        if not pred_set or pred == [result.word]:
            return "no_segmentation"

        # Count affixes
        pred_prefs, pred_suffs = self.extract_affixes(pred)
        gold_prefs, gold_suffs = self.extract_affixes(gold)

        # Stem error
        pred_stem = self.extract_stem(pred)
        gold_stem = self.extract_stem(gold)

        if pred_stem != gold_stem:
            return "wrong_stem"

        # Prefix errors
        if set(pred_prefs) != set(gold_prefs):
            if pred_prefs and not gold_prefs:
                return "false_positive_prefix"
            elif gold_prefs and not pred_prefs:
                return "false_negative_prefix"
            else:
                return "wrong_prefix"

        # Suffix errors
        if set(pred_suffs) != set(gold_suffs):
            if pred_suffs and not gold_suffs:
                return "false_positive_suffix"
            elif gold_suffs and not pred_suffs:
                return "false_negative_suffix"
            else:
                return "wrong_suffix"

        # Reduplication errors
        has_pred_redup = any(m in pred for m in ['ulg', 'rp', 'rs'])
        has_gold_redup = any(m in gold for m in ['ulg', 'rp', 'rs'])

        if has_pred_redup != has_gold_redup:
            return "reduplication_error"

        # Morpheme order error
        if pred_set == gold_set and not result.correct:
            return "morpheme_order_error"

        return "other"

    def print_report(self, metrics: EvaluationMetrics) -> None:
        """Print a formatted evaluation report."""
        print("\n" + "=" * 60)
        print(" MORPHOLOGICAL SEGMENTATION EVALUATION REPORT")
        print("=" * 60)

        print(f"\nOverall Performance:")
        print(f"  Word Accuracy:      {metrics.word_accuracy:.2%} ({metrics.correct_words}/{metrics.total_words})")
        print(f"  Stem Accuracy:      {metrics.stem_accuracy:.2%} ({metrics.correct_stems}/{metrics.total_words})")

        print(f"\nMorpheme-Level Metrics:")
        print(f"  Precision:          {metrics.morpheme_precision:.2%}")
        print(f"  Recall:             {metrics.morpheme_recall:.2%}")
        print(f"  F1 Score:           {metrics.morpheme_f1:.2%}")

        print(f"\nAffix Accuracy:")
        print(f"  Prefix Accuracy:    {metrics.prefix_accuracy:.2%}")
        print(f"  Suffix Accuracy:    {metrics.suffix_accuracy:.2%}")

        if metrics.category_metrics:
            print(f"\nPer-Category Performance:")
            for cat, cat_metrics in sorted(metrics.category_metrics.items()):
                print(f"  {cat:25s} {cat_metrics['accuracy']:6.2%} ({cat_metrics['correct']}/{cat_metrics['total']})")

        if metrics.error_distribution:
            print(f"\nError Distribution:")
            for error_type, count in sorted(metrics.error_distribution.items(), key=lambda x: -x[1]):
                pct = count / metrics.total_words * 100
                print(f"  {error_type:25s} {count:4d} ({pct:5.1f}%)")

        print("\n" + "=" * 60)

    def save_metrics(self, metrics: EvaluationMetrics, output_path: str) -> None:
        """Save metrics to JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metrics.to_dict(), f, indent=2)

        logger.info(f"Metrics saved to {output_path}")

    def save_errors(self, output_path: str, limit: Optional[int] = None) -> None:
        """Save error analysis to CSV file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        errors = sorted(
            self.results,
            key=lambda r: not r.correct  # Incorrect first
        )

        if limit:
            errors = errors[:limit]

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['word', 'prediction', 'gold', 'category', 'correct', 'error_type']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for r in errors:
                writer.writerow({
                    'word': r.word,
                    'prediction': r.prediction,
                    'gold': r.gold,
                    'category': r.category,
                    'correct': r.correct,
                    'error_type': self._classify_error(r) if not r.correct else ''
                })

        logger.info(f"Errors saved to {output_path}")


# ============================================================================
# Comparison Functions
# ============================================================================

class SystemComparator:
    """Compare multiple segmentation systems."""

    def __init__(self):
        self.systems: Dict[str, Any] = {}
        self.metrics: Dict[str, EvaluationMetrics] = {}

    def add_system(self, name: str, system: Any) -> None:
        """Add a system to comparison."""
        self.systems[name] = system

    def compare(
        self,
        gold_data: List[Dict[str, str]],
        word_col: str = "word",
        gold_col: str = "gold_segmentation",
        category_col: Optional[str] = "category"
    ) -> Dict[str, EvaluationMetrics]:
        """Compare all systems on the same gold data."""
        results = {}

        for name, system in self.systems.items():
            logger.info(f"Evaluating system: {name}")
            evaluator = MorphologicalEvaluator(system)
            metrics = evaluator.evaluate_dataset(
                gold_data,
                word_col=word_col,
                gold_col=gold_col,
                category_col=category_col
            )
            results[name] = metrics
            self.metrics[name] = metrics

        return results

    def print_comparison_table(self) -> None:
        """Print a comparison table of all systems."""
        if not self.metrics:
            print("No metrics to display.")
            return

        print("\n" + "=" * 80)
        print(" SYSTEM COMPARISON")
        print("=" * 80)
        print(f"{'System':<20} {'Word Acc':<10} {'Stem Acc':<10} {'F1':<10} {'Precision':<10} {'Recall':<10}")
        print("-" * 80)

        for name, metrics in self.metrics.items():
            print(f"{name:<20} {metrics.word_accuracy:>9.2%} {metrics.stem_accuracy:>9.2%} "
                  f"{metrics.morpheme_f1:>9.2%} {metrics.morpheme_precision:>9.2%} "
                  f"{metrics.morpheme_recall:>9.2%}")

        print("=" * 80)

    def save_comparison(self, output_path: str) -> None:
        """Save comparison to JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        comparison = {
            name: metrics.to_dict()
            for name, metrics in self.metrics.items()
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2)

        logger.info(f"Comparison saved to {output_path}")


# ============================================================================
# Main
# ============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Evaluate Indonesian Morphological Segmentation"
    )
    parser.add_argument(
        "-g", "--gold",
        required=True,
        help="Gold standard CSV file"
    )
    parser.add_argument(
        "-s", "--system",
        default="modernkatakupas",
        choices=["modernkatakupas", "sastrawi"],
        help="System to evaluate"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output JSON file for metrics"
    )
    parser.add_argument(
        "--errors",
        help="Output CSV file for error analysis"
    )
    parser.add_argument(
        "--limit-errors",
        type=int,
        help="Limit number of errors to save"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare multiple systems"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress report output"
    )

    args = parser.parse_args()

    # Load gold standard
    evaluator = MorphologicalEvaluator()
    gold_data = evaluator.load_gold_standard(args.gold)

    if not gold_data:
        logger.error("No gold standard data loaded")
        return 1

    if args.compare:
        # Compare multiple systems
        comparator = SystemComparator()

        # Add ModernKataKupas
        comparator.add_system("modernkatakupas", ModernKataKupas())

        # Add Sastrawi (as baseline stemmer)
        try:
            from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

            class SastrawiWrapper:
                def __init__(self):
                    factory = StemmerFactory()
                    self.stemmer = factory.create_stemmer()

                def segment(self, word: str) -> str:
                    # Sastrawi only stems, doesn't do full segmentation
                    # So we just return the stem for comparison
                    return self.stemmer.stem(word)

            comparator.add_system("sastrawi", SastrawiWrapper())
        except ImportError:
            logger.warning("Sastrawi not installed, skipping")

        # Run comparison
        comparator.compare(gold_data)
        comparator.print_comparison_table()

        if args.output:
            comparator.save_comparison(args.output)

    else:
        # Single system evaluation
        metrics = evaluator.evaluate_dataset(gold_data)

        if not args.quiet:
            evaluator.print_report(metrics)

        if args.output:
            evaluator.save_metrics(metrics, args.output)

        if args.errors:
            evaluator.save_errors(args.errors, args.limit_errors)

    return 0


if __name__ == "__main__":
    exit(main())
