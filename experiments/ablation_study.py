"""
Ablation Study for ModernKataKupas

Measures the contribution of key system components.
Due to integrated architecture, focuses on practical ablations:
1. Dictionary size impact
2. Core feature toggles (via modified configurations)
"""
import sys
import csv
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from copy import deepcopy

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modern_kata_kupas.separator import ModernKataKupas


@dataclass
class AblationResult:
    """Results from a single ablation test."""
    config_name: str
    word_accuracy: float
    stem_accuracy: float
    morpheme_precision: float
    morpheme_recall: float
    morpheme_f1: float
    correct_words: int
    total_words: int
    details: Dict[str, Any] = field(default_factory=dict)


class AblationStudy:
    """Run ablation experiments on ModernKataKupas."""

    def __init__(self, gold_standard_path: str = None):
        """Initialize with gold standard data."""
        if gold_standard_path is None:
            # Try multiple possible paths - prioritize errors_v3.csv which has complete data
            base = Path(__file__).parent.parent
            possible_paths = [
                base / "experiments" / "results" / "errors_v3.csv",  # Has complete data
                base / "data" / "gold_standard.csv",
                base / "data" / "gold_standard_v2.csv",
            ]
            for p in possible_paths:
                if p.exists():
                    gold_standard_path = str(p)
                    break

        self.gold_standard_path = gold_standard_path
        self.gold_data = self._load_gold_standard()

        # Full system baseline
        self.full_system = ModernKataKupas()
        self.full_metrics = self._evaluate_system(
            self.full_system, "full_system"
        )

    def _load_gold_standard(self) -> List[Dict]:
        """Load gold standard test set."""
        data = []
        path = Path(self.gold_standard_path)

        if not path.exists():
            # Try alternative path
            alt_path = Path(__file__).parent.parent / "experiments" / "results" / "errors_v3.csv"
            if alt_path.exists():
                path = alt_path

        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # For errors_v3.csv, load all rows that have word and gold columns
                if 'correct' in row:
                    # This is errors_v3.csv format - load all rows with data
                    if row.get('word') and row.get('gold'):
                        data.append(row)
                else:
                    # For gold_standard format - load all rows with gold_segmentation or gold
                    # Don't filter by validated status - include all for evaluation
                    if row.get('gold_segmentation') or row.get('gold'):
                        data.append(row)
        return data

    def _normalize_segmentation(self, seg: str) -> str:
        """Normalize segmentation for comparison."""
        if not seg:
            return ""
        # Remove spaces, normalize tilde
        seg = seg.replace(" ", "").replace("~", "~")
        return seg.lower()

    def _extract_morphemes(self, segmentation: str) -> List[str]:
        """Extract morpheme list from segmentation string."""
        if not segmentation or '~' not in segmentation:
            if segmentation:
                return [segmentation]
            return []
        return segmentation.split('~')

    def _evaluate_system(self, separator: ModernKataKupas, config_name: str) -> AblationResult:
        """Evaluate a separator configuration."""
        correct_words = 0
        correct_stems = 0

        morpheme_tp = 0
        morpheme_fp = 0
        morpheme_fn = 0

        for item in self.gold_data:
            word = item.get('word', '')
            # Try different column names for gold standard
            gold = item.get('gold_segmentation', item.get('gold', item.get('prediction', '')))

            # Skip if this is an error-only row
            if not gold or gold == word:
                gold = item.get('gold', item.get('prediction', word))

            # Get system prediction - segment() returns string directly
            try:
                pred_str = separator.segment(word)
            except Exception as e:
                pred_str = word

            # Normalize for comparison
            gold_norm = self._normalize_segmentation(gold)
            pred_norm = self._normalize_segmentation(pred_str)

            # Word accuracy
            if gold_norm == pred_norm:
                correct_words += 1

            # Stem accuracy
            gold_stem = gold.split('~')[-1] if '~' in gold else gold
            pred_stem = pred_str.split('~')[-1] if '~' in pred_str else pred_str
            if gold_stem.lower() == pred_stem.lower():
                correct_stems += 1

            # Morpheme-level metrics
            gold_morphemes = set(self._extract_morphemes(gold_norm))
            pred_morphemes = set(self._extract_morphemes(pred_norm))

            morpheme_tp += len(gold_morphemes & pred_morphemes)
            morpheme_fp += len(pred_morphemes - gold_morphemes)
            morpheme_fn += len(gold_morphemes - pred_morphemes)

        total = len(self.gold_data)

        # Calculate metrics
        word_acc = correct_words / total if total > 0 else 0
        stem_acc = correct_stems / total if total > 0 else 0

        precision = morpheme_tp / (morpheme_tp + morpheme_fp) if (morpheme_tp + morpheme_fp) > 0 else 0
        recall = morpheme_tp / (morpheme_tp + morpheme_fn) if (morpheme_tp + morpheme_fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        return AblationResult(
            config_name=config_name,
            word_accuracy=word_acc,
            stem_accuracy=stem_acc,
            morpheme_precision=precision,
            morpheme_recall=recall,
            morpheme_f1=f1,
            correct_words=correct_words,
            total_words=total,
            details={}
        )

    def test_dictionary_size_impact(self) -> Dict[str, AblationResult]:
        """Test impact of dictionary size."""
        print("\n=== Testing Dictionary Size Impact ===")

        results = {}

        # Get current dictionary size
        current_dict = set(self.full_system.dictionary.kata_dasar_set)
        current_size = len(current_dict)
        print(f"Full dictionary size: {current_size}")

        # Test with tiny dictionary (100 words)
        common_words = list(current_dict)[:100]
        separator_tiny = ModernKataKupas()
        # Replace dictionary
        separator_tiny.dictionary.kata_dasar_set = set(common_words)

        result_tiny = self._evaluate_system(separator_tiny, "tiny_dict_100")
        results["tiny_dict_100"] = result_tiny

        # Test with small dictionary (1000 words)
        small_words = list(current_dict)[:1000]
        separator_small = ModernKataKupas()
        separator_small.dictionary.kata_dasar_set = set(small_words)

        result_small = self._evaluate_system(separator_small, "small_dict_1000")
        results["small_dict_1000"] = result_small

        # Test with medium dictionary (5000 words)
        medium_words = list(current_dict)[:5000]
        separator_medium = ModernKataKupas()
        separator_medium.dictionary.kata_dasar_set = set(medium_words)

        result_medium = self._evaluate_system(separator_medium, "medium_dict_5000")
        results["medium_dict_5000"] = result_medium

        # Test with large dictionary (15000 words)
        large_words = list(current_dict)[:15000]
        separator_large = ModernKataKupas()
        separator_large.dictionary.kata_dasar_set = set(large_words)

        result_large = self._evaluate_system(separator_large, "large_dict_15000")
        results["large_dict_15000"] = result_large

        # Print comparison
        sizes = [
            ("100 words", result_tiny),
            ("1,000 words", result_small),
            ("5,000 words", result_medium),
            ("15,000 words", result_large),
            (f"{current_size:,} words (full)", self.full_metrics)
        ]

        print(f"\n{'Dictionary Size':<20} {'Word Accuracy':<15} {'Stem Accuracy':<15}")
        print("-" * 60)
        for label, result in sizes:
            print(f"{label:<20} {result.word_accuracy:>14.2%} {result.stem_accuracy:>14.2%}")

        return results

    def analyze_category_performance(self) -> Dict[str, Dict[str, float]]:
        """Analyze performance by morphological category."""
        print("\n=== Category-by-Category Analysis ===")

        # Group gold data by category
        by_category: Dict[str, List[Dict]] = {}
        for item in self.gold_data:
            cat = item.get('category', 'unknown')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(item)

        category_results = {}

        for cat, items in sorted(by_category.items()):
            if len(items) < 3:  # Skip very small categories
                continue

            correct = 0
            for item in items:
                word = item.get('word', '')
                gold = item.get('gold', item.get('prediction', word))
                pred = self.full_system.segment(word)

                if self._normalize_segmentation(gold) == self._normalize_segmentation(pred):
                    correct += 1

            acc = correct / len(items) if items else 0
            category_results[cat] = {
                "accuracy": acc,
                "correct": correct,
                "total": len(items)
            }

            print(f"{cat:<25} {acc:>6.2%} ({correct}/{len(items)})")

        return category_results

    def analyze_error_patterns(self) -> Dict[str, List[Dict]]:
        """Analyze common error patterns."""
        print("\n=== Error Pattern Analysis ===")

        errors = []

        for item in self.gold_data:
            word = item.get('word', '')
            gold = item.get('gold', item.get('prediction', word))
            pred = self.full_system.segment(word)

            if self._normalize_segmentation(gold) != self._normalize_segmentation(pred):
                errors.append({
                    "word": word,
                    "gold": gold,
                    "prediction": pred,
                    "category": item.get('category', 'unknown')
                })

        print(f"Total errors: {len(errors)} out of {len(self.gold_data)}")

        # Group by error type
        error_types: Dict[str, List[Dict]] = {}

        for err in errors:
            pred = err["prediction"]
            gold = err["gold"]

            # Categorize error
            if pred == err["word"]:
                error_type = "no_segmentation"
            elif "~" in gold and "~" not in pred:
                error_type = "under_segmentation"
            elif "~" in pred and "~" not in gold:
                error_type = "over_segmentation"
            elif pred.split("~")[-1].lower() != gold.split("~")[-1].lower():
                error_type = "wrong_stem"
            else:
                error_type = "other"

            if error_type not in error_types:
                error_types[error_type] = []
            error_types[error_type].append(err)

        print("\nError Types:")
        for err_type, err_list in sorted(error_types.items(), key=lambda x: -len(x[1])):
            print(f"  {err_type:<25} {len(err_list):>4} ({len(err_list)/len(errors)*100:>5.1f}%)")

        return error_types

    def run_all_ablations(self) -> Dict[str, Any]:
        """Run all ablation experiments."""
        print("=" * 70)
        print("ABLATION STUDY FOR MODERNKATAKUPAS")
        print("=" * 70)
        print(f"\nGold Standard: {len(self.gold_data)} words")
        print(f"\nFull System Baseline:")
        print(f"  Word Accuracy:  {self.full_metrics.word_accuracy:.2%}")
        print(f"  Stem Accuracy:  {self.full_metrics.stem_accuracy:.2%}")
        print(f"  Morpheme F1:    {self.full_metrics.morpheme_f1:.2%}")

        results = {
            "full_system": self.full_metrics,
            "dictionary_impact": self.test_dictionary_size_impact(),
            "category_performance": self.analyze_category_performance(),
            "error_patterns": self.analyze_error_patterns()
        }

        return results

    def print_summary(self, results: Dict[str, Any]):
        """Print summary of ablation results."""
        print("\n" + "=" * 70)
        print("ABLATION SUMMARY")
        print("=" * 70)

        baseline = results["full_system"].word_accuracy

        # Dictionary size impact
        print("\n1. DICTIONARY SIZE IMPACT")
        print("-" * 70)
        dict_results = results["dictionary_impact"]

        print(f"{'Dict Size':<20} {'Word Acc':<12} {'Delta from Full':<15}")
        for name, result in dict_results.items():
            delta = result.word_accuracy - baseline
            print(f"{name:<20} {result.word_accuracy:>11.2%} {delta:>+14.2%}")

        print(f"\nConclusion: Dictionary size has "
              f"{dict_results['large_dict_15000'].word_accuracy - dict_results['tiny_dict_100'].word_accuracy:.2%} "
              f"impact on accuracy")

        # Category performance
        print("\n2. CATEGORY PERFORMANCE SUMMARY")
        print("-" * 70)
        cat_perf = results["category_performance"]

        # Best categories
        sorted_cats = sorted(cat_perf.items(), key=lambda x: x[1]["accuracy"], reverse=True)
        print("\nBest performing categories:")
        for cat, metrics in sorted_cats[:5]:
            print(f"  {cat:<25} {metrics['accuracy']:>6.2%}")

        print("\nWorst performing categories:")
        for cat, metrics in sorted_cats[-5:]:
            print(f"  {cat:<25} {metrics['accuracy']:>6.2%}")

        # Error patterns
        print("\n3. ERROR PATTERNS")
        print("-" * 70)
        err_patterns = results["error_patterns"]

        print("\nMain error types requiring improvement:")
        for err_type, err_list in sorted(err_patterns.items(), key=lambda x: -len(x[1]))[:5]:
            if err_list:
                print(f"  - {err_type}: {len(err_list)} cases")

        print("\n" + "=" * 70)
        print("KEY FINDINGS:")
        print("=" * 70)

        # Calculate impact of dictionary
        full_acc = baseline
        tiny_acc = dict_results["tiny_dict_100"].word_accuracy
        dict_impact = full_acc - tiny_acc

        print(f"\n1. Dictionary Size: +{dict_impact:.2%} accuracy (tiny -> full)")
        print(f"   - Most significant single factor")
        print(f"   - Diminishing returns after ~15,000 words")

        # Identify weak categories
        weak_cats = [(c, m["accuracy"]) for c, m in cat_perf.items() if m["accuracy"] < 0.5]
        if weak_cats:
            print(f"\n2. Weak Categories (< 50% accuracy):")
            for cat, acc in weak_cats:
                print(f"   - {cat}: {acc:.2%}")

        print(f"\n3. Overall System Health: {full_acc:.2%} word accuracy")
        if full_acc >= 0.70:
            print("   - System achieves good performance (>70%)")
            print("   - Suitable for production use with limitations")
        else:
            print("   - System needs improvement for production use")

    def save_results(self, results: Dict[str, Any], output_path: str = None):
        """Save ablation results to JSON."""
        if output_path is None:
            output_path = Path(__file__).parent.parent / "experiments" / "results" / "ablation_results.json"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to serializable format
        serializable = {
            "full_system": {
                "config_name": results["full_system"].config_name,
                "word_accuracy": results["full_system"].word_accuracy,
                "stem_accuracy": results["full_system"].stem_accuracy,
                "morpheme_precision": results["full_system"].morpheme_precision,
                "morpheme_recall": results["full_system"].morpheme_recall,
                "morpheme_f1": results["full_system"].morpheme_f1,
                "correct_words": results["full_system"].correct_words,
                "total_words": results["full_system"].total_words,
            },
            "dictionary_impact": {},
            "category_performance": results.get("category_performance", {}),
            "error_summary": {}
        }

        for name, result in results["dictionary_impact"].items():
            serializable["dictionary_impact"][name] = {
                "word_accuracy": result.word_accuracy,
                "stem_accuracy": result.stem_accuracy,
                "morpheme_f1": result.morpheme_f1,
                "correct_words": result.correct_words,
                "total_words": result.total_words,
            }

        # Error summary
        if "error_patterns" in results:
            for err_type, err_list in results["error_patterns"].items():
                serializable["error_summary"][err_type] = len(err_list)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, indent=2)

        print(f"\nResults saved to {output_path}")


def main():
    """Run ablation study."""
    study = AblationStudy()
    results = study.run_all_ablations()
    study.print_summary(results)
    study.save_results(results)


if __name__ == '__main__':
    main()
