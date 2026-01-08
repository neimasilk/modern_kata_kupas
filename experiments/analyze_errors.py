"""
Error Analysis Script using DeepSeek API

Analyzes segmentation errors and provides insights for improvement.
"""
import sys
import csv
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modern_kata_kupas.utils.deepseek_helper import DeepSeekHelper

def load_errors(error_csv_path):
    """Load errors from CSV file."""
    errors = []
    with open(error_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('correct') == 'False':
                errors.append(row)
    return errors

def analyze_errors_batch(helper, errors, max_per_category=3):
    """Analyze errors using DeepSeek API."""
    # Group by error type
    from collections import defaultdict
    by_type = defaultdict(list)

    for error in errors:
        error_type = error.get('error_type', 'unknown')
        by_type[error_type].append(error)

    results = {}

    for error_type, error_list in by_type.items():
        # Analyze sample errors
        samples = error_list[:max_per_category]

        for error in samples:
            word = error['word']
            prediction = error['prediction']
            gold = error['gold']

            # Skip if no actual difference
            if prediction == word and gold == word:
                continue

            print(f"Analyzing: {word} (pred: {prediction}, gold: {gold})")
            result = helper.categorize_error(word, prediction, gold)

            if result.success:
                results[word] = result.data
            else:
                results[word] = {"error": result.error}

    return results

def analyze_reduplication_errors(helper, errors):
    """Specifically analyze reduplication errors."""
    redup_errors = [e for e in errors if 'redup' in e.get('category', '')]

    print(f"\n=== REDUPLICATION ERROR ANALYSIS ({len(redup_errors)} errors) ===\n")

    results = {}
    for error in redup_errors[:5]:  # Analyze first 5
        word = error['word']
        prediction = error['prediction']
        gold = error['gold']

        prompt = f"""Analyze this Indonesian morphological segmentation error:

Word: {word}
System prediction: {prediction}
Correct (gold): {gold}

The word appears to involve reduplication. Explain:
1. What type of reduplication this is (full/dwilingga, partial/dwipurwa, or phonetic change/dwilingga salin suara)
2. What the system did wrong
3. How to fix the algorithm to handle this case

Provide concise technical explanation."""

        result = helper._call_api(prompt, temperature=0.3)

        if result.success:
            results[word] = {
                'analysis': result.data,
                'tokens_used': result.tokens_used
            }
            print(f"\n{word}:")
            print(result.data[:500] if len(result.data) > 500 else result.data)

    return results

def generate_improvement_suggestions(helper, error_categories):
    """Generate improvement suggestions based on error patterns."""

    suggestions = {}

    # Reduplication improvements
    if 'reduplication_phonetic' in error_categories:
        prompt = """Based on the following reduplication errors in Indonesian morphological segmentation:

Words: bolak-balik, sayur-mayur, lauk-pauk, gerak-gerik, serba-serbi, ramah-tamah

The system is predicting: X~rs(~Y) format
Expected: X~ulg~Y or similar

Explain:
1. What is "dwilingga salin suara" (reduplication with phonetic change)
2. How to modify the algorithm to detect this pattern
3. Suggest specific rule changes

Be specific about Indonesian morphological rules."""

        result = helper._call_api(prompt, temperature=0.5)
        if result.success:
            suggestions['reduplication_phonetic'] = result.data

    # Partial reduplication (dwipurwa)
    if 'reduplication_partial' in error_categories:
        prompt = """Based on these Indonesian morphological segmentation errors:

Words with partial reduplication (dwipurwa): lelaki, sesama, tetua, dedaun, sesepuh, leluhur

Issues:
- System predicts: X~rp (e.g., "laki~rp")
- Expected: se~sama or similar

Explain the dwipurwa pattern and suggest algorithm improvements."""

        result = helper._call_api(prompt, temperature=0.5)
        if result.success:
            suggestions['reduplication_partial'] = result.data

    return suggestions

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--errors', default='experiments/results/errors_v3.csv')
    parser.add_argument('--category', help='Analyze specific category only')
    parser.add_argument('--max-samples', type=int, default=3)
    args = parser.parse_args()

    # Load errors
    errors = []
    with open(args.errors, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('correct') == 'False':
                if args.category is None or row.get('category') == args.category:
                    errors.append(row)

    print(f"Loaded {len(errors)} errors to analyze")

    # Initialize helper
    helper = DeepSeekHelper()

    # Analyze specific problematic categories
    if args.category:
        # Analyze specific category
        print(f"\n=== ANALYZING CATEGORY: {args.category} ===\n")

        if 'redup' in args.category:
            results = analyze_reduplication_errors(helper, errors)

            # Save results
            output = f'experiments/results/analysis_{args.category}.json'
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to {output}")
    else:
        # Generate improvement suggestions
        error_categories = set(e.get('category', '') for e in errors)

        print(f"\n=== GENERATING IMPROVEMENT SUGGESTIONS ===")
        print(f"Categories with errors: {error_categories}\n")

        suggestions = generate_improvement_suggestions(helper, error_categories)

        # Save suggestions
        output = 'experiments/results/improvement_suggestions.json'
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(suggestions, f, indent=2, ensure_ascii=False)
        print(f"\nSuggestions saved to {output}")

if __name__ == '__main__':
    main()
