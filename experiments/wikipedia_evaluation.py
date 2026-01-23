"""
Wikipedia Indonesia Corpus Evaluation for ModernKataKupas

This module evaluates ModernKataKupas on real-world Indonesian text
from Wikipedia to demonstrate practical utility.

Metrics:
- OOV rate (words not in dictionary)
- Segmentation coverage (% words successfully segmented)
- Processing speed (words/second)
- Qualitative sample analysis

Usage:
    # With local corpus file
    python experiments/wikipedia_evaluation.py --corpus data/wikipedia_id_sample.txt

    # Generate sample from URL (requires internet)
    python experiments/wikipedia_evaluation.py --download --sentences 1000

    # Output to JSON
    python experiments/wikipedia_evaluation.py --corpus data/wiki.txt -o experiments/results/wikipedia_eval.json
"""

import os
import sys
import json
import re
import time
import logging
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter
from dataclasses import dataclass, asdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modern_kata_kupas import ModernKataKupas

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class WikipediaEvalResult:
    """Results from Wikipedia corpus evaluation."""
    corpus_stats: Dict[str, int]
    segmentation_results: Dict[str, Any]
    performance: Dict[str, float]
    oov_analysis: Dict[str, Any]
    sample_segmentations: List[Dict[str, str]]


class WikipediaEvaluator:
    """Evaluate ModernKataKupas on Wikipedia Indonesia corpus."""

    # Indonesian Wikipedia sample URLs (simple Wikipedia articles)
    SAMPLE_URLS = [
        "https://id.wikipedia.org/wiki/Indonesia",
        "https://id.wikipedia.org/wiki/Jakarta",
        "https://id.wikipedia.org/wiki/Bahasa_Indonesia",
        "https://id.wikipedia.org/wiki/Sejarah_Indonesia",
        "https://id.wikipedia.org/wiki/Budaya_Indonesia",
    ]

    def __init__(self):
        self.mkk = ModernKataKupas()
        # Load dictionary for OOV analysis
        self.dictionary = self._load_dictionary()

    def _load_dictionary(self) -> set:
        """Load root words dictionary."""
        dict_path = Path(__file__).parent.parent / "data" / "kata_dasar.txt"
        words = set()
        if dict_path.exists():
            with open(dict_path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip().lower()
                    if word:
                        words.add(word)
        logger.info(f"Loaded {len(words)} dictionary words")
        return words

    def download_wikipedia_sample(self, n_sentences: int = 1000) -> str:
        """
        Download sample text from Indonesian Wikipedia.

        This is a simple method that extracts text from Wikipedia pages.
        For production use, consider using WikiExtractor on the dump.
        """
        all_text = []

        for url in self.SAMPLE_URLS:
            try:
                logger.info(f"Fetching {url}...")
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'ModernKataKupas Research/1.0'}
                )
                with urllib.request.urlopen(req, timeout=30) as response:
                    html = response.read().decode('utf-8')

                # Extract text from paragraphs (simple extraction)
                text = self._extract_text_from_html(html)
                all_text.append(text)

            except Exception as e:
                logger.warning(f"Failed to fetch {url}: {e}")
                continue

        combined = "\n".join(all_text)
        sentences = self._split_sentences(combined)

        # Limit to requested number
        sentences = sentences[:n_sentences]

        logger.info(f"Downloaded {len(sentences)} sentences")
        return "\n".join(sentences)

    def _extract_text_from_html(self, html: str) -> str:
        """Extract plain text from HTML (simple regex-based)."""
        # Remove script and style
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # Extract paragraph content
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, flags=re.DOTALL | re.IGNORECASE)

        text_parts = []
        for p in paragraphs:
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', p)
            # Remove references like [1], [2]
            text = re.sub(r'\[\d+\]', '', text)
            # Clean whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            if text:
                text_parts.append(text)

        return "\n".join(text_parts)

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting on period, question mark, exclamation
        sentences = re.split(r'[.!?]+', text)
        # Clean and filter
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        return sentences

    def load_corpus(self, path: str) -> str:
        """Load corpus from file."""
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        logger.info(f"Loaded corpus from {path}")
        return text

    def save_corpus(self, text: str, path: str) -> None:
        """Save corpus to file."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        logger.info(f"Saved corpus to {path}")

    def extract_words(self, text: str) -> List[str]:
        """Extract Indonesian words from text."""
        # Tokenize: split on non-alphanumeric (keeping hyphens for reduplication)
        # Pattern matches Indonesian words including reduplicated forms
        pattern = r'\b[a-zA-Z]+(?:-[a-zA-Z]+)?\b'
        words = re.findall(pattern, text.lower())

        # Filter: minimum length, no pure numbers
        words = [w for w in words if len(w) >= 2 and not w.isdigit()]

        return words

    def is_oov(self, word: str) -> bool:
        """Check if word is out-of-vocabulary."""
        # Remove hyphen for reduplicated check
        base = word.replace('-', '')

        # Check if word or its base is in dictionary
        if word in self.dictionary:
            return False
        if base in self.dictionary:
            return False

        # Check common prefixes/suffixes stripped
        for prefix in ['me', 'di', 'ber', 'ter', 'pe', 'ke', 'se']:
            if word.startswith(prefix) and word[len(prefix):] in self.dictionary:
                return False

        for suffix in ['kan', 'an', 'i', 'nya']:
            if word.endswith(suffix) and word[:-len(suffix)] in self.dictionary:
                return False

        return True

    def evaluate(
        self,
        text: str,
        max_words: Optional[int] = None,
        sample_size: int = 20
    ) -> WikipediaEvalResult:
        """
        Evaluate ModernKataKupas on corpus text.

        Args:
            text: Corpus text
            max_words: Maximum words to process (None for all)
            sample_size: Number of sample segmentations to include

        Returns:
            WikipediaEvalResult with evaluation metrics
        """
        # Extract words
        all_words = self.extract_words(text)
        sentences = self._split_sentences(text)

        if max_words:
            all_words = all_words[:max_words]

        unique_words = list(set(all_words))

        logger.info(f"Evaluating {len(all_words)} total words ({len(unique_words)} unique)")

        # Corpus statistics
        corpus_stats = {
            "total_sentences": len(sentences),
            "total_words": len(all_words),
            "unique_words": len(unique_words)
        }

        # Segmentation evaluation
        start_time = time.time()

        segmentation_count = 0
        unchanged_count = 0
        error_count = 0
        oov_words = []
        segmented_results = {}

        for word in unique_words:
            try:
                result = self.mkk.segment(word)
                segmented_results[word] = result

                if result == word:
                    unchanged_count += 1
                else:
                    segmentation_count += 1

                # Check OOV
                if self.is_oov(word):
                    oov_words.append(word)

            except Exception as e:
                error_count += 1
                logger.debug(f"Error segmenting '{word}': {e}")

        end_time = time.time()
        processing_time = end_time - start_time

        # Performance metrics
        performance = {
            "total_time_seconds": round(processing_time, 3),
            "words_per_second": round(len(unique_words) / processing_time, 1) if processing_time > 0 else 0,
            "unique_words_processed": len(unique_words)
        }

        # Segmentation results
        segmentation_results = {
            "successfully_segmented": segmentation_count,
            "unchanged": unchanged_count,
            "errors": error_count,
            "segmentation_rate": round(segmentation_count / len(unique_words) * 100, 2) if unique_words else 0,
            "coverage": round((segmentation_count + unchanged_count) / len(unique_words) * 100, 2) if unique_words else 0
        }

        # OOV analysis
        oov_counter = Counter(oov_words)
        oov_analysis = {
            "total_oov": len(oov_words),
            "oov_rate": round(len(oov_words) / len(unique_words) * 100, 2) if unique_words else 0,
            "top_oov_words": oov_counter.most_common(20)
        }

        # Sample segmentations
        samples = []
        segmented_words = [(w, r) for w, r in segmented_results.items() if w != r]

        # Get diverse samples
        import random
        random.seed(42)
        if len(segmented_words) > sample_size:
            sampled = random.sample(segmented_words, sample_size)
        else:
            sampled = segmented_words[:sample_size]

        for word, segmented in sampled:
            samples.append({
                "word": word,
                "segmented": segmented,
                "is_oov": word in oov_words
            })

        return WikipediaEvalResult(
            corpus_stats=corpus_stats,
            segmentation_results=segmentation_results,
            performance=performance,
            oov_analysis=oov_analysis,
            sample_segmentations=samples
        )

    def print_report(self, result: WikipediaEvalResult) -> None:
        """Print evaluation report."""
        print("\n" + "=" * 70)
        print(" WIKIPEDIA INDONESIA CORPUS EVALUATION")
        print("=" * 70)

        # Corpus stats
        stats = result.corpus_stats
        print(f"\n1. CORPUS STATISTICS")
        print("-" * 50)
        print(f"   Total sentences:  {stats['total_sentences']:,}")
        print(f"   Total words:      {stats['total_words']:,}")
        print(f"   Unique words:     {stats['unique_words']:,}")

        # Segmentation results
        seg = result.segmentation_results
        print(f"\n2. SEGMENTATION RESULTS")
        print("-" * 50)
        print(f"   Successfully segmented: {seg['successfully_segmented']:,} ({seg['segmentation_rate']}%)")
        print(f"   Unchanged (root words): {seg['unchanged']:,}")
        print(f"   Errors:                 {seg['errors']}")
        print(f"   Coverage:               {seg['coverage']}%")

        # OOV analysis
        oov = result.oov_analysis
        print(f"\n3. OUT-OF-VOCABULARY ANALYSIS")
        print("-" * 50)
        print(f"   OOV words:  {oov['total_oov']:,}")
        print(f"   OOV rate:   {oov['oov_rate']}%")
        print(f"\n   Top OOV words:")
        for word, count in oov['top_oov_words'][:10]:
            print(f"      {word}: {count}")

        # Performance
        perf = result.performance
        print(f"\n4. PERFORMANCE")
        print("-" * 50)
        print(f"   Processing time:   {perf['total_time_seconds']} seconds")
        print(f"   Speed:             {perf['words_per_second']:,.0f} words/second")

        # Samples
        print(f"\n5. SAMPLE SEGMENTATIONS")
        print("-" * 50)
        for sample in result.sample_segmentations[:10]:
            oov_mark = " [OOV]" if sample['is_oov'] else ""
            print(f"   {sample['word']:<20} -> {sample['segmented']}{oov_mark}")

        print("\n" + "=" * 70)

    def save_results(self, result: WikipediaEvalResult, path: str) -> None:
        """Save results to JSON file."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict
        data = {
            "corpus_stats": result.corpus_stats,
            "segmentation_results": result.segmentation_results,
            "performance": result.performance,
            "oov_analysis": {
                "total_oov": result.oov_analysis["total_oov"],
                "oov_rate": result.oov_analysis["oov_rate"],
                "top_oov_words": result.oov_analysis["top_oov_words"]
            },
            "sample_segmentations": result.sample_segmentations
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to {path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Evaluate ModernKataKupas on Wikipedia Indonesia corpus"
    )
    parser.add_argument(
        "-c", "--corpus",
        help="Path to corpus file (plain text)"
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download sample from Wikipedia"
    )
    parser.add_argument(
        "--sentences",
        type=int,
        default=1000,
        help="Number of sentences to download"
    )
    parser.add_argument(
        "--save-corpus",
        help="Save downloaded corpus to file"
    )
    parser.add_argument(
        "--max-words",
        type=int,
        help="Maximum words to process"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output JSON file for results"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress detailed output"
    )

    args = parser.parse_args()

    evaluator = WikipediaEvaluator()

    # Get corpus text
    if args.corpus:
        text = evaluator.load_corpus(args.corpus)
    elif args.download:
        text = evaluator.download_wikipedia_sample(args.sentences)
        if args.save_corpus:
            evaluator.save_corpus(text, args.save_corpus)
    else:
        # Use sample text for testing
        text = """
        Indonesia adalah negara kepulauan terbesar di dunia yang terletak di Asia Tenggara.
        Negara ini memiliki lebih dari 17.000 pulau dengan penduduk sekitar 270 juta jiwa.
        Bahasa Indonesia adalah bahasa resmi yang digunakan sebagai bahasa pemersatu bangsa.
        Kebudayaan Indonesia sangat beragam dengan ratusan suku bangsa dan bahasa daerah.
        Jakarta merupakan ibu kota negara dan pusat pemerintahan Indonesia.
        Perekonomian Indonesia berkembang pesat dengan berbagai sektor industri dan perdagangan.
        Pendidikan menjadi prioritas pembangunan untuk meningkatkan kualitas sumber daya manusia.
        Kesehatan masyarakat terus ditingkatkan melalui berbagai program pemerintah.
        Pariwisata Indonesia terkenal dengan keindahan alam dan kekayaan budayanya.
        Pembangunan infrastruktur dilakukan untuk mendukung pertumbuhan ekonomi nasional.
        """
        logger.info("Using sample text (use --corpus or --download for real evaluation)")

    # Run evaluation
    result = evaluator.evaluate(text, max_words=args.max_words)

    # Print report
    if not args.quiet:
        evaluator.print_report(result)

    # Save results
    if args.output:
        evaluator.save_results(result, args.output)

    return 0


if __name__ == "__main__":
    exit(main())
