"""
Tokenization Comparison Experiment for ModernKataKupas Paper

This module compares different tokenization approaches:
1. Word-level tokenization (baseline)
2. BPE tokenization (SentencePiece)
3. ModernKataKupas morphological segmentation

Metrics measured:
- Vocabulary size reduction
- Average tokens per word
- Morpheme boundary alignment (qualitative)
- OOV rate simulation

This directly answers RQ1 and RQ3 from the paper.

Usage:
    python experiments/tokenization_comparison.py --corpus data/sample_corpus.txt
    python experiments/tokenization_comparison.py --generate-corpus --size 10000
"""

import os
import sys
import json
import csv
import logging
import tempfile
import random
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass, field
from collections import Counter

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modern_kata_kupas import ModernKataKupas

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TokenizationResult:
    """Result of tokenizing a corpus with a specific method."""
    method: str
    vocabulary_size: int
    total_tokens: int
    total_words: int
    avg_tokens_per_word: float
    unique_tokens: Set[str] = field(default_factory=set)
    token_frequencies: Dict[str, int] = field(default_factory=dict)
    sample_tokenizations: List[Dict[str, Any]] = field(default_factory=list)


class TokenizationComparator:
    """Compare different tokenization methods."""

    def __init__(self):
        self.mkk = ModernKataKupas()
        self.results: Dict[str, TokenizationResult] = {}

    def load_corpus(self, path: str) -> List[str]:
        """Load corpus from file (one sentence/word per line)."""
        words = []
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    # Split line into words
                    for word in line.split():
                        # Basic cleanup
                        word = word.lower().strip('.,!?;:"\'()[]{}')
                        if word and word.isalpha():
                            words.append(word)
        logger.info(f"Loaded {len(words)} words from {path}")
        return words

    def generate_sample_corpus(
        self,
        dictionary_path: str,
        size: int = 10000,
        include_affixed: bool = True
    ) -> List[str]:
        """
        Generate a sample corpus from dictionary.

        Args:
            dictionary_path: Path to kata_dasar.txt
            size: Number of words to generate
            include_affixed: Whether to include affixed variants

        Returns:
            List of words
        """
        # Load root words
        with open(dictionary_path, 'r', encoding='utf-8') as f:
            root_words = [line.strip() for line in f if line.strip()]

        logger.info(f"Loaded {len(root_words)} root words")

        corpus = []

        # Common Indonesian prefixes
        prefixes = ['meN', 'ber', 'ter', 'di', 'per', 'ke', 'se']
        prefix_forms = {
            'meN': ['me', 'mem', 'men', 'meng', 'meny', 'menge'],
            'ber': ['ber', 'be', 'bel'],
            'ter': ['ter', 'te'],
            'di': ['di'],
            'per': ['per', 'pel'],
            'ke': ['ke'],
            'se': ['se']
        }

        # Common suffixes
        suffixes = ['kan', 'i', 'an', 'nya', 'ku', 'mu', 'lah', 'kah']

        for _ in range(size):
            root = random.choice(root_words)

            if include_affixed and random.random() < 0.7:
                # 70% chance to add affixes
                word = root

                # Maybe add prefix
                if random.random() < 0.5:
                    prefix = random.choice(prefixes)
                    form = random.choice(prefix_forms[prefix])
                    word = form + word

                # Maybe add suffix
                if random.random() < 0.5:
                    suffix = random.choice(suffixes)
                    word = word + suffix

                corpus.append(word)
            else:
                corpus.append(root)

        logger.info(f"Generated corpus with {len(corpus)} words")
        return corpus

    def tokenize_word_level(self, words: List[str]) -> TokenizationResult:
        """Word-level tokenization (baseline)."""
        token_counts = Counter(words)

        result = TokenizationResult(
            method="word_level",
            vocabulary_size=len(token_counts),
            total_tokens=len(words),
            total_words=len(words),
            avg_tokens_per_word=1.0,
            unique_tokens=set(token_counts.keys()),
            token_frequencies=dict(token_counts)
        )

        # Sample tokenizations
        for word in random.sample(words, min(20, len(words))):
            result.sample_tokenizations.append({
                "word": word,
                "tokens": [word],
                "token_count": 1
            })

        return result

    def tokenize_bpe(
        self,
        words: List[str],
        vocab_size: int = 8000
    ) -> TokenizationResult:
        """
        BPE tokenization using SentencePiece.

        Falls back to character-level if SentencePiece not available.
        """
        try:
            import sentencepiece as spm

            # Create temporary files for training
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                for word in words:
                    f.write(word + '\n')
                train_file = f.name

            model_prefix = tempfile.mktemp()

            # Train SentencePiece model
            spm.SentencePieceTrainer.train(
                input=train_file,
                model_prefix=model_prefix,
                vocab_size=vocab_size,
                model_type='bpe',
                character_coverage=1.0,
                normalization_rule_name='identity'
            )

            # Load model
            sp = spm.SentencePieceProcessor()
            sp.load(model_prefix + '.model')

            # Tokenize all words
            all_tokens = []
            token_counts = Counter()
            samples = []

            sample_words = random.sample(words, min(50, len(words)))

            for word in words:
                tokens = sp.encode_as_pieces(word)
                all_tokens.extend(tokens)
                token_counts.update(tokens)

                if word in sample_words[:20]:
                    samples.append({
                        "word": word,
                        "tokens": tokens,
                        "token_count": len(tokens)
                    })

            # Cleanup
            os.unlink(train_file)
            os.unlink(model_prefix + '.model')
            os.unlink(model_prefix + '.vocab')

            result = TokenizationResult(
                method="bpe_sentencepiece",
                vocabulary_size=len(token_counts),
                total_tokens=len(all_tokens),
                total_words=len(words),
                avg_tokens_per_word=len(all_tokens) / len(words),
                unique_tokens=set(token_counts.keys()),
                token_frequencies=dict(token_counts),
                sample_tokenizations=samples
            )

            return result

        except ImportError:
            logger.warning("SentencePiece not installed. Using simulated BPE.")
            return self._simulate_bpe(words, vocab_size)

    def _simulate_bpe(
        self,
        words: List[str],
        target_vocab_size: int = 8000
    ) -> TokenizationResult:
        """
        Simulate BPE-like tokenization without SentencePiece.
        Uses character bigrams as approximation.
        """
        all_tokens = []
        token_counts = Counter()
        samples = []

        sample_words = random.sample(words, min(50, len(words)))

        for word in words:
            # Simple character-level with common bigrams
            tokens = []
            i = 0
            while i < len(word):
                # Try to find common bigrams/trigrams
                if i + 2 <= len(word):
                    bigram = word[i:i+2]
                    # Common Indonesian character combinations
                    if bigram in ['ng', 'ny', 'an', 'in', 'en', 'ar', 'er', 'kan', 'men', 'ber']:
                        tokens.append(bigram)
                        i += 2
                        continue
                tokens.append(word[i])
                i += 1

            all_tokens.extend(tokens)
            token_counts.update(tokens)

            if word in sample_words[:20]:
                samples.append({
                    "word": word,
                    "tokens": tokens,
                    "token_count": len(tokens)
                })

        result = TokenizationResult(
            method="bpe_simulated",
            vocabulary_size=len(token_counts),
            total_tokens=len(all_tokens),
            total_words=len(words),
            avg_tokens_per_word=len(all_tokens) / len(words),
            unique_tokens=set(token_counts.keys()),
            token_frequencies=dict(token_counts),
            sample_tokenizations=samples
        )

        return result

    def tokenize_morphological(self, words: List[str]) -> TokenizationResult:
        """Morphological tokenization using ModernKataKupas."""
        all_tokens = []
        token_counts = Counter()
        samples = []

        sample_words = random.sample(words, min(50, len(words)))

        for word in words:
            try:
                segmented = self.mkk.segment(word)
                # Parse morphemes
                if '~' in segmented:
                    tokens = [t for t in segmented.split('~') if t]
                else:
                    tokens = [segmented]

                all_tokens.extend(tokens)
                token_counts.update(tokens)

                if word in sample_words[:20]:
                    samples.append({
                        "word": word,
                        "tokens": tokens,
                        "token_count": len(tokens),
                        "segmented": segmented
                    })
            except Exception as e:
                # Fallback to word itself
                all_tokens.append(word)
                token_counts[word] += 1
                logger.debug(f"Error segmenting '{word}': {e}")

        result = TokenizationResult(
            method="morphological_mkk",
            vocabulary_size=len(token_counts),
            total_tokens=len(all_tokens),
            total_words=len(words),
            avg_tokens_per_word=len(all_tokens) / len(words),
            unique_tokens=set(token_counts.keys()),
            token_frequencies=dict(token_counts),
            sample_tokenizations=samples
        )

        return result

    def compare_methods(
        self,
        words: List[str],
        bpe_vocab_size: int = 8000
    ) -> Dict[str, TokenizationResult]:
        """Compare all tokenization methods on the same corpus."""
        logger.info("Running word-level tokenization...")
        self.results["word_level"] = self.tokenize_word_level(words)

        logger.info("Running BPE tokenization...")
        self.results["bpe"] = self.tokenize_bpe(words, bpe_vocab_size)

        logger.info("Running morphological tokenization...")
        self.results["morphological"] = self.tokenize_morphological(words)

        return self.results

    def compute_vocabulary_reduction(self) -> Dict[str, Any]:
        """Compute vocabulary reduction metrics."""
        if "word_level" not in self.results:
            return {}

        baseline = self.results["word_level"].vocabulary_size

        reduction = {}
        for method, result in self.results.items():
            reduction[method] = {
                "vocab_size": result.vocabulary_size,
                "reduction_absolute": baseline - result.vocabulary_size,
                "reduction_percent": (baseline - result.vocabulary_size) / baseline * 100 if baseline > 0 else 0,
                "avg_tokens_per_word": result.avg_tokens_per_word
            }

        return reduction

    def analyze_morpheme_alignment(self) -> Dict[str, Any]:
        """
        Analyze how well tokenization aligns with morpheme boundaries.

        This provides qualitative evidence for RQ3.
        """
        if "morphological" not in self.results or "bpe" not in self.results:
            return {}

        mkk_samples = self.results["morphological"].sample_tokenizations
        bpe_samples = self.results["bpe"].sample_tokenizations

        # Create word -> tokenization mapping
        bpe_map = {s["word"]: s["tokens"] for s in bpe_samples}

        alignment_analysis = []

        for mkk_sample in mkk_samples:
            word = mkk_sample["word"]
            mkk_tokens = mkk_sample["tokens"]
            bpe_tokens = bpe_map.get(word, [word])

            # Check if BPE tokens align with morpheme boundaries
            mkk_str = '|'.join(mkk_tokens)
            bpe_str = '|'.join(bpe_tokens)

            # Simple alignment check: do BPE boundaries match MKK boundaries?
            mkk_boundaries = set()
            pos = 0
            for token in mkk_tokens[:-1]:
                pos += len(token)
                mkk_boundaries.add(pos)

            bpe_boundaries = set()
            pos = 0
            for token in bpe_tokens[:-1]:
                clean_token = token.lstrip('▁')  # SentencePiece prefix
                pos += len(clean_token)
                bpe_boundaries.add(pos)

            # Calculate overlap
            if mkk_boundaries:
                alignment_score = len(mkk_boundaries & bpe_boundaries) / len(mkk_boundaries)
            else:
                alignment_score = 1.0 if not bpe_boundaries else 0.0

            alignment_analysis.append({
                "word": word,
                "mkk_tokens": mkk_tokens,
                "bpe_tokens": bpe_tokens,
                "mkk_boundaries": list(mkk_boundaries),
                "bpe_boundaries": list(bpe_boundaries),
                "alignment_score": alignment_score,
                "morphologically_aligned": alignment_score > 0.5
            })

        # Summary statistics
        alignment_scores = [a["alignment_score"] for a in alignment_analysis]
        aligned_count = sum(1 for a in alignment_analysis if a["morphologically_aligned"])

        return {
            "samples": alignment_analysis,
            "avg_alignment_score": sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0,
            "percent_aligned": aligned_count / len(alignment_analysis) * 100 if alignment_analysis else 0,
            "total_samples": len(alignment_analysis)
        }

    def print_report(self) -> None:
        """Print comparison report."""
        print("\n" + "=" * 70)
        print(" TOKENIZATION COMPARISON REPORT")
        print("=" * 70)

        print("\n1. VOCABULARY SIZE COMPARISON")
        print("-" * 50)
        print(f"{'Method':<25} {'Vocab Size':>12} {'Reduction':>12} {'Avg Tok/Word':>12}")
        print("-" * 50)

        reduction = self.compute_vocabulary_reduction()
        for method, data in reduction.items():
            red_pct = f"{data['reduction_percent']:.1f}%" if data['reduction_percent'] > 0 else "-"
            print(f"{method:<25} {data['vocab_size']:>12,} {red_pct:>12} {data['avg_tokens_per_word']:>12.2f}")

        print("\n2. SAMPLE TOKENIZATIONS")
        print("-" * 50)

        if "morphological" in self.results:
            print("\nMorphological (ModernKataKupas):")
            for sample in self.results["morphological"].sample_tokenizations[:10]:
                print(f"  {sample['word']:<20} -> {' + '.join(sample['tokens'])}")

        if "bpe" in self.results:
            print("\nBPE/SentencePiece:")
            for sample in self.results["bpe"].sample_tokenizations[:10]:
                tokens_str = ' '.join(sample['tokens'])
                print(f"  {sample['word']:<20} -> {tokens_str}")

        alignment = self.analyze_morpheme_alignment()
        if alignment:
            print("\n3. MORPHEME BOUNDARY ALIGNMENT")
            print("-" * 50)
            print(f"  Average alignment score: {alignment['avg_alignment_score']:.2%}")
            print(f"  Morphologically aligned: {alignment['percent_aligned']:.1f}%")

        print("\n" + "=" * 70)

    def save_results(self, output_path: str) -> None:
        """Save results to JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Prepare serializable results
        serializable = {}
        for method, result in self.results.items():
            serializable[method] = {
                "method": result.method,
                "vocabulary_size": result.vocabulary_size,
                "total_tokens": result.total_tokens,
                "total_words": result.total_words,
                "avg_tokens_per_word": result.avg_tokens_per_word,
                "sample_tokenizations": result.sample_tokenizations[:20]
            }

        output = {
            "results": serializable,
            "vocabulary_reduction": self.compute_vocabulary_reduction(),
            "morpheme_alignment": self.analyze_morpheme_alignment()
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Compare tokenization methods for Indonesian text"
    )
    parser.add_argument(
        "-c", "--corpus",
        help="Path to corpus file (one word/sentence per line)"
    )
    parser.add_argument(
        "--generate-corpus",
        action="store_true",
        help="Generate sample corpus from dictionary"
    )
    parser.add_argument(
        "-d", "--dictionary",
        default="data/kata_dasar.txt",
        help="Path to root word dictionary"
    )
    parser.add_argument(
        "-s", "--size",
        type=int,
        default=10000,
        help="Size of generated corpus"
    )
    parser.add_argument(
        "--bpe-vocab-size",
        type=int,
        default=8000,
        help="Target vocabulary size for BPE"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output JSON file for results"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output"
    )

    args = parser.parse_args()

    comparator = TokenizationComparator()

    # Get or generate corpus
    if args.corpus:
        words = comparator.load_corpus(args.corpus)
    elif args.generate_corpus:
        words = comparator.generate_sample_corpus(
            args.dictionary,
            size=args.size
        )
    else:
        # Default: generate small sample
        words = comparator.generate_sample_corpus(
            args.dictionary,
            size=5000
        )

    if not words:
        logger.error("No words to process")
        return 1

    # Run comparison
    comparator.compare_methods(words, args.bpe_vocab_size)

    # Print report
    if not args.quiet:
        comparator.print_report()

    # Save results
    if args.output:
        comparator.save_results(args.output)

    return 0


if __name__ == "__main__":
    exit(main())
