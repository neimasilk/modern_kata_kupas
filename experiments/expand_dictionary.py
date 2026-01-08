"""
Expand Indonesian Root Word Dictionary using PySastrawi and DeepSeek

This script:
1. Extracts root words from PySastrawi's dictionary
2. Validates them using DeepSeek API
3. Merges with existing kata_dasar.txt
4. Outputs a comprehensive dictionary file

Usage:
    python experiments/expand_dictionary.py --output data/kata_dasar_full.txt
    python experiments/expand_dictionary.py --validate-only --input data/kata_dasar_candidate.txt
"""
import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Set, Dict, Optional, Tuple
from collections import defaultdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modern_kata_kupas.utils.deepseek_helper import DeepSeekHelper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DictionaryExpander:
    """Expand Indonesian root word dictionary."""

    def __init__(self, helper: Optional[DeepSeekHelper] = None):
        """Initialize expander."""
        self.helper = helper or DeepSeekHelper()
        self.root_words: Set[str] = set()
        self.validated: Dict[str, Dict] = {}
        self.rejected: Set[str] = set()
        self.total_tokens = 0

    def load_pysastrawi_dictionary(self) -> Set[str]:
        """Load root words from PySastrawi package."""
        logger.info("Loading PySastrawi dictionary...")

        try:
            from Sastrawi.Dictionary.ArrayDictionary import ArrayDictionary
            from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

            # Get the dictionary from Sastrawi
            factory = StemmerFactory()
            stemmer = factory.create_stemmer()
            dictionary = factory.get_words()

            logger.info(f"Loaded {len(dictionary)} words from PySastrawi")
            return set(dictionary)

        except ImportError:
            logger.warning("PySastrawi not installed. Trying alternative method...")

            # Try to load from file directly
            sastrawi_paths = [
                Path(__file__).parent.parent / "src" / "modern_kata_kupas" / "data" / "sastrawi_dict.txt",
                Path.home() / ".local" / "lib" / "python*" / "site-packages" / "Sastrawi" / "Dictionary" / "words.txt",
            ]

            for path in sastrawi_paths:
                if path.exists():
                    words = set()
                    with open(path, 'r', encoding='utf-8') as f:
                        for line in f:
                            word = line.strip()
                            if word:
                                words.add(word)
                    logger.info(f"Loaded {len(words)} words from {path}")
                    return words

            logger.error("Could not find PySastrawi dictionary")
            return set()

    def load_existing_dictionary(self, path: str) -> Set[str]:
        """Load existing root words from file."""
        logger.info(f"Loading existing dictionary from {path}...")

        words = set()
        path = Path(path)

        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word and not word.startswith('#'):  # Skip comments
                        words.add(word.lower())

            logger.info(f"Loaded {len(words)} existing root words")
        else:
            logger.warning(f"File not found: {path}")

        return words

    def validate_root_word(self, word: str) -> Optional[Dict]:
        """
        Validate if a word is a true root word using DeepSeek.

        Returns validation dict or None if failed.
        """
        result = self.helper.validate_root_word(word)
        self.total_tokens += result.tokens_used

        if result.success and result.data:
            return result.data

        return None

    def validate_batch(
        self,
        words: Set[str],
        batch_size: int = 100,
        show_progress: bool = True
    ) -> Dict[str, Dict]:
        """
        Validate a batch of words.

        Returns dict mapping word to validation result.
        """
        results = {}
        word_list = list(words)

        # Progress bar
        if show_progress:
            try:
                from tqdm import tqdm
                word_list = tqdm(word_list, desc="Validating words")
            except ImportError:
                pass

        for word in word_list:
            validation = self.validate_root_word(word)

            if validation:
                results[word] = validation
                if validation.get('is_root_word', False):
                    self.root_words.add(word)
                else:
                    self.rejected.add(word)
            else:
                # If validation failed, conservatively keep it
                results[word] = {"is_root_word": True, "confidence": "unknown"}

        return results

    def expand_from_pysastrawi(
        self,
        validate_sample: bool = True,
        sample_size: int = 500
    ) -> Set[str]:
        """
        Expand dictionary using PySastrawi as source.

        Args:
            validate_sample: If True, validate a sample with DeepSeek
            sample_size: Number of words to validate

        Returns:
            Set of validated root words
        """
        sastrawi_words = self.load_pysastrawi_dictionary()

        if not sastrawi_words:
            logger.error("No words from PySastrawi")
            return set()

        if validate_sample:
            # Validate a sample to estimate accuracy
            import random
            sample = set(random.sample(list(sastrawi_words), min(sample_size, len(sastrawi_words))))

            logger.info(f"Validating sample of {len(sample)} words...")
            validated = self.validate_batch(sample, show_progress=True)

            # Calculate acceptance rate
            accepted = sum(1 for v in validated.values() if v.get('is_root_word', False))
            rate = accepted / len(validated) if validated else 0

            logger.info(f"Sample validation: {accepted}/{len(validated)} accepted ({rate:.1%})")

            # If acceptance rate is high, use all Sastrawi words
            # If low, we might want to validate more
            if rate > 0.8:
                logger.info("High acceptance rate. Using all PySastrawi words.")
                return sastrawi_words
            else:
                logger.warning(f"Lower acceptance rate ({rate:.1%}). Consider validating full set.")
                # Return only validated ones
                return {w for w, v in validated.items() if v.get('is_root_word', False)}
        else:
            return sastrawi_words

    def merge_and_deduplicate(
        self,
        sources: List[Set[str]],
        min_length: int = 2,
        max_length: int = 20
    ) -> Set[str]:
        """
        Merge multiple word sources and apply filters.

        Args:
            sources: List of word sets to merge
            min_length: Minimum word length
            max_length: Maximum word length

        Returns:
            Filtered and deduplicated set of words
        """
        merged = set()
        for source in sources:
            merged.update(source)

        # Apply filters
        filtered = set()
        for word in merged:
            word = word.lower().strip()
            if min_length <= len(word) <= max_length:
                # Check if it looks like a word (only letters, no spaces)
                if word.isalpha():
                    filtered.add(word)

        logger.info(f"Merged and filtered: {len(filtered)} unique words")
        return filtered

    def remove_affixed_words(self, words: Set[str]) -> Set[str]:
        """
        Remove words that are clearly affixed (heuristic).

        This is a basic filter to remove obvious non-root words.
        """
        # Common prefixes
        prefixes = (
            'me', 'men', 'meng', 'meny', 'mem', 'menge',
            'ber', 'bel', 'be',
            'ter', 'te',
            'di',
            'pe', 'pen', 'peng', 'pem', 'peny', 'penge',
            'per', 'pel',
            'ke', 'se',
        )

        # Common suffixes
        suffixes = ('kan', 'i', 'an', 'is', 'nya', 'ku', 'mu', 'lah', 'kah', 'pun', 'tah')

        filtered = set()

        for word in words:
            is_affixed = False

            # Check for prefixes
            for pref in prefixes:
                if word.startswith(pref):
                    # Check if what remains could be a word
                    remaining = word[len(pref):]
                    if len(remaining) >= 2 and remaining in words:
                        is_affixed = True
                        break

            # Check for suffixes
            if not is_affixed:
                for suff in suffixes:
                    if word.endswith(suff):
                        remaining = word[:-len(suff)]
                        if len(remaining) >= 2 and remaining in words:
                            is_affixed = True
                            break

            if not is_affixed:
                filtered.add(word)

        removed = len(words) - len(filtered)
        if removed > 0:
            logger.info(f"Removed {removed} obviously affixed words")

        return filtered

    def save_dictionary(self, words: Set[str], output_path: str) -> None:
        """Save dictionary to file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Sort alphabetically
        sorted_words = sorted(words)

        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write("# Indonesian Root Words Dictionary (Kata Dasar)\n")
            f.write(f"# Generated by ModernKataKupas DictionaryExpander\n")
            f.write(f"# Total entries: {len(sorted_words)}\n")
            f.write("#\n")

            # Write words
            for word in sorted_words:
                f.write(f"{word}\n")

        logger.info(f"Saved {len(sorted_words)} words to {output_path}")

    def get_statistics(self, words: Set[str]) -> Dict:
        """Get statistics about the word set."""
        from collections import Counter

        # Length distribution
        lengths = [len(w) for w in words]

        # First letter distribution
        first_letters = Counter(w[0] for w in words if w)

        # Last letter distribution
        last_letters = Counter(w[-1] for w in words if w)

        return {
            "total_words": len(words),
            "min_length": min(lengths) if lengths else 0,
            "max_length": max(lengths) if lengths else 0,
            "avg_length": sum(lengths) / len(lengths) if lengths else 0,
            "first_letter_distribution": dict(first_letters.most_common(10)),
            "last_letter_distribution": dict(last_letters.most_common(10)),
        }


# ============================================================================
# Main
# ============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Expand Indonesian Root Word Dictionary"
    )
    parser.add_argument(
        "-o", "--output",
        default="data/kata_dasar_full.txt",
        help="Output dictionary file path"
    )
    parser.add_argument(
        "-i", "--input",
        default="data/kata_dasar.txt",
        help="Existing dictionary to merge with"
    )
    parser.add_argument(
        "--from-sastrawi",
        action="store_true",
        help="Expand from PySastrawi dictionary"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate words using DeepSeek API"
    )
    parser.add_argument(
        "--validate-sample",
        type=int,
        default=500,
        help="Number of words to validate (if --validate)"
    )
    parser.add_argument(
        "--filter-affixed",
        action="store_true",
        help="Apply heuristic filter to remove affixed words"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics only"
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=2,
        help="Minimum word length (default: 2)"
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=20,
        help="Maximum word length (default: 20)"
    )

    args = parser.parse_args()

    try:
        expander = DictionaryExpander()
    except Exception as e:
        logger.error(f"Failed to initialize expander: {e}")
        return 1

    # Load existing dictionary
    existing_words = expander.load_existing_dictionary(args.input)
    all_words = set(existing_words)

    # Expand from PySastrawi
    if args.from_sastrawi:
        logger.info("Expanding from PySastrawi...")
        sastrawi_words = expander.expand_from_pysastrawi(
            validate_sample=args.validate,
            sample_size=args.validate_sample
        )
        all_words.update(sastrawi_words)

    # Apply filters
    if args.filter_affixed:
        logger.info("Filtering affixed words...")
        all_words = expander.remove_affixed_words(all_words)

    # Length filter
    all_words = {
        w for w in all_words
        if args.min_length <= len(w) <= args.max_length
    }

    # Show statistics
    stats = expander.get_statistics(all_words)
    print("\n=== Dictionary Statistics ===")
    print(json.dumps(stats, indent=2))
    print(f"\nTotal tokens used: {expander.total_tokens}")

    if args.stats:
        return 0

    # Save to file
    expander.save_dictionary(all_words, args.output)

    print(f"\nComplete! Dictionary saved to {args.output}")
    return 0


if __name__ == "__main__":
    exit(main())
