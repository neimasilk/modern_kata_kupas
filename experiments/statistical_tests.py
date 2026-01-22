"""
Statistical Significance Tests for ModernKataKupas Paper

This module provides statistical tests to validate the significance
of experimental results:

1. McNemar's test - Compare two classifiers on paired samples
2. Bootstrap confidence intervals - Estimate accuracy uncertainty
3. Chi-squared test - Compare distributions
4. Effect size (Cohen's kappa) - Measure agreement

Usage:
    python experiments/statistical_tests.py --gold data/gold_standard_v3.csv
    python experiments/statistical_tests.py --metrics experiments/results/metrics.json
"""

import os
import sys
import json
import csv
import math
import random
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modern_kata_kupas import ModernKataKupas

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class StatisticalResult:
    """Result of a statistical test."""
    test_name: str
    statistic: float
    p_value: float
    significant: bool  # at alpha=0.05
    confidence_interval: Optional[Tuple[float, float]] = None
    effect_size: Optional[float] = None
    interpretation: str = ""


class StatisticalAnalyzer:
    """Perform statistical analysis on segmentation results."""

    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha
        self.mkk = ModernKataKupas()

    def load_gold_standard(self, path: str) -> List[Dict[str, str]]:
        """Load gold standard data from CSV."""
        data = []
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        logger.info(f"Loaded {len(data)} entries from {path}")
        return data

    def get_predictions(self, data: List[Dict[str, str]]) -> List[Tuple[str, str, str, bool]]:
        """
        Get predictions for each word.

        Returns:
            List of (word, prediction, gold, correct) tuples
        """
        results = []
        for item in data:
            word = item.get("word", "")
            gold = item.get("gold_segmentation", "")

            if not word or not gold:
                continue

            try:
                prediction = self.mkk.segment(word)
            except Exception:
                prediction = word

            correct = (prediction == gold)
            results.append((word, prediction, gold, correct))

        return results

    def bootstrap_confidence_interval(
        self,
        correct_list: List[bool],
        n_bootstrap: int = 1000,
        confidence: float = 0.95
    ) -> Tuple[float, float, float]:
        """
        Calculate bootstrap confidence interval for accuracy.

        Args:
            correct_list: List of boolean values (True if correct)
            n_bootstrap: Number of bootstrap samples
            confidence: Confidence level (e.g., 0.95 for 95%)

        Returns:
            Tuple of (mean_accuracy, lower_bound, upper_bound)
        """
        n = len(correct_list)
        if n == 0:
            return 0.0, 0.0, 0.0

        # Original accuracy
        original_acc = sum(correct_list) / n

        # Bootstrap samples
        bootstrap_accs = []
        for _ in range(n_bootstrap):
            sample = random.choices(correct_list, k=n)
            acc = sum(sample) / n
            bootstrap_accs.append(acc)

        # Sort for percentile calculation
        bootstrap_accs.sort()

        # Calculate confidence interval
        lower_idx = int((1 - confidence) / 2 * n_bootstrap)
        upper_idx = int((1 + confidence) / 2 * n_bootstrap) - 1

        lower_bound = bootstrap_accs[lower_idx]
        upper_bound = bootstrap_accs[upper_idx]

        return original_acc, lower_bound, upper_bound

    def mcnemar_test(
        self,
        correct_a: List[bool],
        correct_b: List[bool]
    ) -> StatisticalResult:
        """
        McNemar's test for comparing two classifiers on paired samples.

        Tests whether the disagreement between two classifiers is significant.

        Args:
            correct_a: Correctness list for system A
            correct_b: Correctness list for system B

        Returns:
            StatisticalResult with test statistics
        """
        if len(correct_a) != len(correct_b):
            raise ValueError("Lists must have same length")

        n = len(correct_a)

        # Build contingency table
        # b = number where A is correct, B is wrong
        # c = number where A is wrong, B is correct
        b = sum(1 for i in range(n) if correct_a[i] and not correct_b[i])
        c = sum(1 for i in range(n) if not correct_a[i] and correct_b[i])

        # McNemar statistic (with continuity correction)
        if b + c == 0:
            chi2 = 0.0
            p_value = 1.0
        else:
            chi2 = (abs(b - c) - 1) ** 2 / (b + c)
            # Approximate p-value from chi-squared distribution with 1 df
            p_value = self._chi2_p_value(chi2, df=1)

        significant = p_value < self.alpha

        interpretation = ""
        if significant:
            if b > c:
                interpretation = "System A significantly outperforms System B"
            else:
                interpretation = "System B significantly outperforms System A"
        else:
            interpretation = "No significant difference between systems"

        return StatisticalResult(
            test_name="McNemar's Test",
            statistic=chi2,
            p_value=p_value,
            significant=significant,
            interpretation=interpretation
        )

    def _chi2_p_value(self, chi2: float, df: int = 1) -> float:
        """
        Approximate p-value for chi-squared distribution.

        Uses the incomplete gamma function approximation.
        """
        if chi2 <= 0:
            return 1.0

        # Simple approximation for df=1
        # P(X > x) ≈ erfc(sqrt(x/2)) for chi2 with df=1
        # erfc(x) ≈ exp(-x^2) / (x * sqrt(pi)) for large x

        # More accurate: use normal approximation
        # For df=1: sqrt(2*chi2) - sqrt(2*df-1) ~ N(0,1)
        z = math.sqrt(2 * chi2) - math.sqrt(2 * df - 1) if df > 0.5 else math.sqrt(chi2)

        # Standard normal CDF approximation
        p_value = 1 - self._normal_cdf(z)

        return max(0.0, min(1.0, p_value))

    def _normal_cdf(self, x: float) -> float:
        """Approximate standard normal CDF using error function."""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def cohens_kappa(
        self,
        predictions: List[str],
        gold: List[str]
    ) -> float:
        """
        Calculate Cohen's Kappa for agreement between prediction and gold.

        Returns:
            Kappa value (-1 to 1, where 1 is perfect agreement)
        """
        if len(predictions) != len(gold):
            raise ValueError("Lists must have same length")

        n = len(predictions)
        if n == 0:
            return 0.0

        # Observed agreement
        po = sum(1 for i in range(n) if predictions[i] == gold[i]) / n

        # Get unique categories
        categories = set(predictions) | set(gold)

        # Expected agreement by chance
        pe = 0.0
        for cat in categories:
            pred_freq = sum(1 for p in predictions if p == cat) / n
            gold_freq = sum(1 for g in gold if g == cat) / n
            pe += pred_freq * gold_freq

        # Cohen's Kappa
        if pe == 1.0:
            return 1.0 if po == 1.0 else 0.0

        kappa = (po - pe) / (1 - pe)
        return kappa

    def per_category_significance(
        self,
        data: List[Dict[str, str]],
        predictions: List[Tuple[str, str, str, bool]]
    ) -> Dict[str, StatisticalResult]:
        """
        Calculate significance for each morphological category.

        Returns:
            Dictionary of category -> StatisticalResult
        """
        # Group by category
        category_results = defaultdict(list)

        pred_map = {p[0]: p[3] for p in predictions}  # word -> correct

        for item in data:
            word = item.get("word", "")
            category = item.get("category", "unknown")

            if word in pred_map:
                category_results[category].append(pred_map[word])

        # Calculate CI for each category
        results = {}
        for category, correct_list in category_results.items():
            acc, lower, upper = self.bootstrap_confidence_interval(correct_list)

            results[category] = StatisticalResult(
                test_name="Bootstrap CI",
                statistic=acc,
                p_value=0.0,  # Not applicable
                significant=lower > 0.5,  # Significantly better than random
                confidence_interval=(lower, upper),
                interpretation=f"Accuracy: {acc:.2%} (95% CI: [{lower:.2%}, {upper:.2%}])"
            )

        return results

    def run_all_tests(
        self,
        gold_path: str,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run all statistical tests on gold standard data.

        Args:
            gold_path: Path to gold standard CSV
            output_path: Optional path to save results

        Returns:
            Dictionary of all test results
        """
        # Load data
        data = self.load_gold_standard(gold_path)
        predictions = self.get_predictions(data)

        if not predictions:
            logger.error("No predictions generated")
            return {}

        # Extract correctness list
        correct_list = [p[3] for p in predictions]

        # 1. Bootstrap confidence interval for overall accuracy
        acc, lower, upper = self.bootstrap_confidence_interval(correct_list)

        overall_ci = StatisticalResult(
            test_name="Bootstrap CI (Overall)",
            statistic=acc,
            p_value=0.0,
            significant=lower > 0.5,
            confidence_interval=(lower, upper),
            interpretation=f"Overall accuracy: {acc:.2%} (95% CI: [{lower:.2%}, {upper:.2%}])"
        )

        # 2. Per-category analysis
        category_results = self.per_category_significance(data, predictions)

        # 3. McNemar test vs baseline (word = unchanged)
        # Create baseline where system never segments
        baseline_correct = [p[2] == p[0] for p in predictions]  # gold == word (no change)
        mcnemar_result = self.mcnemar_test(correct_list, baseline_correct)

        # 4. Cohen's Kappa
        pred_segments = [p[1] for p in predictions]
        gold_segments = [p[2] for p in predictions]
        kappa = self.cohens_kappa(pred_segments, gold_segments)

        # Compile results
        results = {
            "overall": {
                "accuracy": acc,
                "confidence_interval": {
                    "lower": lower,
                    "upper": upper,
                    "level": 0.95
                },
                "total_words": len(predictions),
                "correct_words": sum(correct_list)
            },
            "mcnemar_vs_baseline": {
                "chi_squared": mcnemar_result.statistic,
                "p_value": mcnemar_result.p_value,
                "significant": mcnemar_result.significant,
                "interpretation": mcnemar_result.interpretation
            },
            "cohens_kappa": {
                "kappa": kappa,
                "interpretation": self._interpret_kappa(kappa)
            },
            "per_category": {
                cat: {
                    "accuracy": res.statistic,
                    "ci_lower": res.confidence_interval[0] if res.confidence_interval else 0,
                    "ci_upper": res.confidence_interval[1] if res.confidence_interval else 0,
                    "significant_above_random": res.significant
                }
                for cat, res in category_results.items()
            }
        }

        # Print report
        self.print_report(results)

        # Save if requested
        if output_path:
            self.save_results(results, output_path)

        return results

    def _interpret_kappa(self, kappa: float) -> str:
        """Interpret Cohen's Kappa value."""
        if kappa < 0:
            return "Less than chance agreement"
        elif kappa < 0.20:
            return "Slight agreement"
        elif kappa < 0.40:
            return "Fair agreement"
        elif kappa < 0.60:
            return "Moderate agreement"
        elif kappa < 0.80:
            return "Substantial agreement"
        else:
            return "Almost perfect agreement"

    def print_report(self, results: Dict[str, Any]) -> None:
        """Print statistical analysis report."""
        print("\n" + "=" * 70)
        print(" STATISTICAL ANALYSIS REPORT")
        print("=" * 70)

        # Overall
        overall = results["overall"]
        ci = overall["confidence_interval"]
        print(f"\n1. OVERALL ACCURACY")
        print("-" * 50)
        print(f"   Accuracy: {overall['accuracy']:.2%}")
        print(f"   95% CI:   [{ci['lower']:.2%}, {ci['upper']:.2%}]")
        print(f"   N:        {overall['total_words']}")

        # McNemar
        mcnemar = results["mcnemar_vs_baseline"]
        print(f"\n2. McNEMAR'S TEST (vs No-Segmentation Baseline)")
        print("-" * 50)
        print(f"   Chi-squared:  {mcnemar['chi_squared']:.4f}")
        print(f"   p-value:      {mcnemar['p_value']:.6f}")
        print(f"   Significant:  {'Yes' if mcnemar['significant'] else 'No'} (alpha=0.05)")
        print(f"   {mcnemar['interpretation']}")

        # Cohen's Kappa
        kappa = results["cohens_kappa"]
        print(f"\n3. COHEN'S KAPPA")
        print("-" * 50)
        print(f"   Kappa: {kappa['kappa']:.4f}")
        print(f"   {kappa['interpretation']}")

        # Per-category
        print(f"\n4. PER-CATEGORY 95% CONFIDENCE INTERVALS")
        print("-" * 50)
        print(f"   {'Category':<25} {'Accuracy':>10} {'95% CI':>20}")
        print("-" * 50)

        for cat, data in sorted(results["per_category"].items()):
            ci_str = f"[{data['ci_lower']:.2%}, {data['ci_upper']:.2%}]"
            sig = "*" if data['significant_above_random'] else ""
            print(f"   {cat:<25} {data['accuracy']:>9.2%} {ci_str:>20} {sig}")

        print("\n   * = Significantly above random (50%)")
        print("\n" + "=" * 70)

    def save_results(self, results: Dict[str, Any], output_path: str) -> None:
        """Save results to JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Results saved to {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Statistical significance tests for segmentation"
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
        "--bootstrap-samples",
        type=int,
        default=1000,
        help="Number of bootstrap samples"
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="Significance level"
    )

    args = parser.parse_args()

    analyzer = StatisticalAnalyzer(alpha=args.alpha)
    analyzer.run_all_tests(args.gold, args.output)

    return 0


if __name__ == "__main__":
    exit(main())
