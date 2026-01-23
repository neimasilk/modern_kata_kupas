"""
Morfessor Baseline Comparison for ModernKataKupas

This module compares ModernKataKupas with Morfessor, an unsupervised
morphological segmentation tool.

Comparison metrics:
- Accuracy on gold standard
- Segmentation granularity (avg tokens per word)
- Processing speed
- Linguistic interpretability

Usage:
    # Install morfessor first: pip install morfessor

    # Train and compare
    python experiments/morfessor_comparison.py --gold data/gold_standard_v3.csv

    # With custom training corpus
    python experiments/morfessor_comparison.py --gold data/gold_standard_v3.csv --train-corpus data/kata_dasar.txt

    # Output to JSON
    python experiments/morfessor_comparison.py --gold data/gold_standard_v3.csv -o experiments/results/morfessor_comparison.json
"""

import os
import sys
import json
import csv
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modern_kata_kupas import ModernKataKupas

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ComparisonResult:
    """Results from Morfessor comparison."""
    mkk_results: Dict[str, Any]
    morfessor_results: Dict[str, Any]
    comparison: Dict[str, Any]
    sample_comparisons: List[Dict[str, Any]]


class MorfessorComparator:
    """Compare ModernKataKupas with Morfessor."""

    def __init__(self):
        self.mkk = ModernKataKupas()
        self.morfessor_model = None
        self._morfessor_available = self._check_morfessor()

    def _check_morfessor(self) -> bool:
        """Check if Morfessor is installed."""
        try:
            import morfessor
            return True
        except ImportError:
            logger.warning("Morfessor not installed. Run: pip install morfessor")
            return False

    def load_gold_standard(self, path: str) -> List[Dict[str, str]]:
        """Load gold standard data."""
        data = []
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        logger.info(f"Loaded {len(data)} gold standard entries")
        return data

    def create_training_corpus(self, gold_data: List[Dict[str, str]]) -> List[str]:
        """Create training corpus from gold standard words and dictionary."""
        words = set()

        # Add gold standard words
        for item in gold_data:
            word = item.get("word", "").strip()
            if word:
                words.add(word)

        # Add dictionary words
        dict_path = Path(__file__).parent.parent / "data" / "kata_dasar.txt"
        if dict_path.exists():
            with open(dict_path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word:
                        words.add(word)

        logger.info(f"Training corpus: {len(words)} unique words")
        return list(words)

    def train_morfessor(self, corpus: List[str]) -> None:
        """Train Morfessor model on corpus."""
        if not self._morfessor_available:
            return

        import morfessor

        # Create I/O handler and model
        io = morfessor.MorfessorIO()
        model = morfessor.BaselineModel()

        # Train on corpus (each word with count 1)
        logger.info("Training Morfessor model...")
        start_time = time.time()

        # Load data as (count, word) tuples
        data = [(1, word) for word in corpus]
        model.load_data(data)

        # Train with default parameters
        model.train_batch()

        train_time = time.time() - start_time
        logger.info(f"Morfessor training completed in {train_time:.2f}s")

        self.morfessor_model = model

    def segment_with_morfessor(self, word: str) -> str:
        """Segment word using Morfessor."""
        if not self.morfessor_model:
            return word

        try:
            segments = self.morfessor_model.viterbi_segment(word)[0]
            return "~".join(segments)
        except Exception:
            return word

    def evaluate_on_gold(
        self,
        gold_data: List[Dict[str, str]]
    ) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]]]:
        """
        Evaluate both systems on gold standard.

        Returns:
            Tuple of (mkk_results, morfessor_results, sample_comparisons)
        """
        mkk_correct = 0
        morfessor_correct = 0
        mkk_total_tokens = 0
        morfessor_total_tokens = 0

        comparisons = []

        start_mkk = time.time()
        for item in gold_data:
            word = item.get("word", "").strip()
            gold = item.get("gold_segmentation", "").strip()

            if not word or not gold:
                continue

            # MKK segmentation
            mkk_result = self.mkk.segment(word)
            mkk_tokens = len(mkk_result.split("~"))
            mkk_total_tokens += mkk_tokens

            mkk_match = (mkk_result == gold)
            if mkk_match:
                mkk_correct += 1

        mkk_time = time.time() - start_mkk

        # Morfessor evaluation
        start_morf = time.time()
        for item in gold_data:
            word = item.get("word", "").strip()
            gold = item.get("gold_segmentation", "").strip()

            if not word or not gold:
                continue

            # Morfessor segmentation
            if self._morfessor_available and self.morfessor_model:
                morf_result = self.segment_with_morfessor(word)
            else:
                morf_result = word  # Fallback: no segmentation

            morf_tokens = len(morf_result.split("~"))
            morfessor_total_tokens += morf_tokens

            morf_match = (morf_result == gold)
            if morf_match:
                morfessor_correct += 1

            # Store comparison
            comparisons.append({
                "word": word,
                "gold": gold,
                "mkk": self.mkk.segment(word),
                "morfessor": morf_result,
                "mkk_correct": (self.mkk.segment(word) == gold),
                "morfessor_correct": morf_match
            })

        morf_time = time.time() - start_morf

        n = len([c for c in comparisons if c["word"]])

        mkk_results = {
            "accuracy": round(mkk_correct / n * 100, 2) if n > 0 else 0,
            "correct": mkk_correct,
            "total": n,
            "avg_tokens_per_word": round(mkk_total_tokens / n, 2) if n > 0 else 0,
            "processing_time": round(mkk_time, 3),
            "words_per_second": round(n / mkk_time, 1) if mkk_time > 0 else 0
        }

        morfessor_results = {
            "accuracy": round(morfessor_correct / n * 100, 2) if n > 0 else 0,
            "correct": morfessor_correct,
            "total": n,
            "avg_tokens_per_word": round(morfessor_total_tokens / n, 2) if n > 0 else 0,
            "processing_time": round(morf_time, 3),
            "words_per_second": round(n / morf_time, 1) if morf_time > 0 else 0,
            "available": self._morfessor_available and self.morfessor_model is not None
        }

        return mkk_results, morfessor_results, comparisons

    def compute_comparison_stats(
        self,
        mkk_results: Dict[str, Any],
        morfessor_results: Dict[str, Any],
        comparisons: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute comparison statistics."""
        # Agreement analysis
        both_correct = sum(1 for c in comparisons if c["mkk_correct"] and c["morfessor_correct"])
        mkk_only = sum(1 for c in comparisons if c["mkk_correct"] and not c["morfessor_correct"])
        morf_only = sum(1 for c in comparisons if not c["mkk_correct"] and c["morfessor_correct"])
        both_wrong = sum(1 for c in comparisons if not c["mkk_correct"] and not c["morfessor_correct"])

        n = len(comparisons)

        return {
            "accuracy_difference": round(mkk_results["accuracy"] - morfessor_results["accuracy"], 2),
            "agreement": {
                "both_correct": both_correct,
                "mkk_only_correct": mkk_only,
                "morfessor_only_correct": morf_only,
                "both_wrong": both_wrong,
                "agreement_rate": round((both_correct + both_wrong) / n * 100, 2) if n > 0 else 0
            },
            "granularity": {
                "mkk_avg_tokens": mkk_results["avg_tokens_per_word"],
                "morfessor_avg_tokens": morfessor_results["avg_tokens_per_word"],
                "difference": round(mkk_results["avg_tokens_per_word"] - morfessor_results["avg_tokens_per_word"], 2)
            },
            "speed": {
                "mkk_wps": mkk_results["words_per_second"],
                "morfessor_wps": morfessor_results["words_per_second"],
                "mkk_faster": mkk_results["words_per_second"] > morfessor_results["words_per_second"]
            }
        }

    def run_comparison(
        self,
        gold_path: str,
        output_path: Optional[str] = None
    ) -> ComparisonResult:
        """
        Run full comparison between MKK and Morfessor.

        Args:
            gold_path: Path to gold standard CSV
            output_path: Optional path to save results

        Returns:
            ComparisonResult with all metrics
        """
        # Load gold standard
        gold_data = self.load_gold_standard(gold_path)

        # Create training corpus and train Morfessor
        if self._morfessor_available:
            corpus = self.create_training_corpus(gold_data)
            self.train_morfessor(corpus)

        # Evaluate both systems
        mkk_results, morfessor_results, comparisons = self.evaluate_on_gold(gold_data)

        # Compute comparison stats
        comparison_stats = self.compute_comparison_stats(mkk_results, morfessor_results, comparisons)

        # Get sample comparisons (interesting cases)
        samples = []

        # Cases where systems disagree
        disagree = [c for c in comparisons if c["mkk_correct"] != c["morfessor_correct"]]
        samples.extend(disagree[:10])

        # Cases where both are wrong
        both_wrong = [c for c in comparisons if not c["mkk_correct"] and not c["morfessor_correct"]]
        samples.extend(both_wrong[:5])

        result = ComparisonResult(
            mkk_results=mkk_results,
            morfessor_results=morfessor_results,
            comparison=comparison_stats,
            sample_comparisons=samples[:20]
        )

        # Print report
        self.print_report(result)

        # Save results
        if output_path:
            self.save_results(result, output_path)

        return result

    def print_report(self, result: ComparisonResult) -> None:
        """Print comparison report."""
        print("\n" + "=" * 70)
        print(" MORFESSOR BASELINE COMPARISON")
        print("=" * 70)

        mkk = result.mkk_results
        morf = result.morfessor_results
        comp = result.comparison

        print(f"\n1. ACCURACY COMPARISON")
        print("-" * 50)
        print(f"   {'Method':<20} {'Accuracy':>12} {'Correct':>10} {'Total':>8}")
        print("-" * 50)
        print(f"   {'ModernKataKupas':<20} {mkk['accuracy']:>11.2f}% {mkk['correct']:>10} {mkk['total']:>8}")

        if morf['available']:
            print(f"   {'Morfessor':<20} {morf['accuracy']:>11.2f}% {morf['correct']:>10} {morf['total']:>8}")
            print(f"\n   Difference: {comp['accuracy_difference']:+.2f}% (MKK {'better' if comp['accuracy_difference'] > 0 else 'worse'})")
        else:
            print(f"   {'Morfessor':<20} {'N/A (not installed)':>30}")

        print(f"\n2. AGREEMENT ANALYSIS")
        print("-" * 50)
        if morf['available']:
            agree = comp['agreement']
            print(f"   Both correct:          {agree['both_correct']}")
            print(f"   MKK only correct:      {agree['mkk_only_correct']}")
            print(f"   Morfessor only correct:{agree['morfessor_only_correct']}")
            print(f"   Both wrong:            {agree['both_wrong']}")
            print(f"   Agreement rate:        {agree['agreement_rate']}%")
        else:
            print("   (Morfessor not available)")

        print(f"\n3. SEGMENTATION GRANULARITY")
        print("-" * 50)
        print(f"   MKK avg tokens/word:       {mkk['avg_tokens_per_word']}")
        if morf['available']:
            print(f"   Morfessor avg tokens/word: {morf['avg_tokens_per_word']}")
            print(f"   Difference:                {comp['granularity']['difference']:+.2f}")

        print(f"\n4. PROCESSING SPEED")
        print("-" * 50)
        print(f"   MKK:       {mkk['words_per_second']:,.0f} words/sec")
        if morf['available']:
            print(f"   Morfessor: {morf['words_per_second']:,.0f} words/sec")

        print(f"\n5. SAMPLE COMPARISONS (Disagreements)")
        print("-" * 50)
        for sample in result.sample_comparisons[:10]:
            mkk_mark = "v" if sample['mkk_correct'] else "x"
            morf_mark = "v" if sample['morfessor_correct'] else "x"
            print(f"   {sample['word']:<15}")
            print(f"      Gold:      {sample['gold']}")
            print(f"      MKK [{mkk_mark}]:   {sample['mkk']}")
            print(f"      Morf [{morf_mark}]: {sample['morfessor']}")
            print()

        print("=" * 70)

    def save_results(self, result: ComparisonResult, path: str) -> None:
        """Save results to JSON file."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        data = {
            "mkk_results": result.mkk_results,
            "morfessor_results": result.morfessor_results,
            "comparison": result.comparison,
            "sample_comparisons": result.sample_comparisons
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to {path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Compare ModernKataKupas with Morfessor"
    )
    parser.add_argument(
        "-g", "--gold",
        required=True,
        help="Path to gold standard CSV file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output JSON file for results"
    )
    parser.add_argument(
        "--train-corpus",
        help="Additional corpus for Morfessor training"
    )

    args = parser.parse_args()

    comparator = MorfessorComparator()
    comparator.run_comparison(args.gold, args.output)

    return 0


if __name__ == "__main__":
    exit(main())
