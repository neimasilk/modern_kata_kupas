"""
Generate Gold Standard Test Set for Indonesian Morphological Segmentation

This script uses DeepSeek API to generate a comprehensive gold standard
dataset for evaluating ModernKataKupas and other Indonesian morphological analyzers.

Output: CSV file with columns: word, gold_segmentation, category, confidence, morphemes

Usage:
    python experiments/generate_gold_standard.py --output data/gold_standard.csv --size 1000
    python experiments/generate_gold_standard.py --validate-only --input data/gold_standard.csv
"""
import os
import sys
import json
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modern_kata_kupas.utils.deepseek_helper import DeepSeekHelper, GenerationResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class GoldStandardEntry:
    """A single entry in the gold standard dataset."""
    word: str
    gold_segmentation: str
    category: str
    subcategory: Optional[str] = None
    confidence: str = "medium"
    morphemes: Optional[str] = None  # JSON string of morpheme list
    notes: Optional[str] = None
    validated: bool = False
    system_prediction: Optional[str] = None  # For comparison later
    agrees: Optional[bool] = None  # Whether system agrees with gold


# ============================================================================
# Category Definitions and Prompts
# ============================================================================

CATEGORY_PROMPTS = {
    "root_pure": """Generate 50 pure Indonesian root words (kata dasar) that are commonly used.
These should be words with NO affixes whatsoever.
Include: basic nouns, common verbs, simple adjectives.

Format: JSON array of strings, e.g., ["buku", "makan", "rumah"]""",

    "prefix_meN": """Generate 30 Indonesian words with the meN- prefix (including allomorphs: me-, men-, meng-, meny-, mem-, menge-).
Each word should have ONLY the meN- prefix attached to a valid root word.
Format: JSON array with objects: {{"word": "menulis", "root": "tulis", "alomorph": "men"}}""",

    "prefix_ber": """Generate 30 Indonesian words with the ber- prefix.
Each word should have ONLY the ber- prefix (or be- allomorph) attached to a valid root word.
Format: JSON array with objects: {{"word": "bermain", "root": "main", "form": "ber"}}""",

    "prefix_ter": """Generate 30 Indonesian words with the ter- prefix.
Each word should have ONLY the ter- prefix attached to a valid root word.
Format: JSON array with objects: {{"word": "terbang", "root": "tengah", "notes": "accidental homonym if any"}}""",

    "prefix_di": """Generate 30 Indonesian words with the di- prefix (passive marker).
Each word should have ONLY the di- prefix attached to a valid root word.
Format: JSON array with objects: {{"word": "makan", "root": "makan", "form": "di"}}""",

    "suffix_kan": """Generate 30 Indonesian words with the -kan suffix.
Each word should be root + kan (causative/benefactive).
Format: JSON array with objects: {{"word": "makanan", "root": "makan", "suffix": "kan"}}""",

    "suffix_i": """Generate 30 Indonesian words with the -i suffix.
Each word should be root + i (locative/repetitive).
Format: JSON array with objects: {{"word": "besari", "root": "besar", "suffix": "i"}}""",

    "suffix_an": """Generate 30 Indonesian words with the -an suffix.
Each word should be root + an (nominalizer).
Format: JSON array with objects: {{"word": "mainan", "root": "main", "suffix": "an"}}""",

    "confix_ke_an": """Generate 30 Indonesian words with the ke-...-an circumfix (confix).
Each word should have ke- prefix and -an suffix around a root.
Format: JSON array with objects: {{"word": "kebiasaan", "root": "biasa", "prefix": "ke", "suffix": "an"}}""",

    "confix_per_an": """Generate 30 Indonesian words with the per-...-an circumfix (confix).
Each word should have per- prefix and -an suffix around a root.
Format: JSON array with objects: {{"word": "permainan", "root": "main", "prefix": "per", "suffix": "an"}}""",

    "confix_peN_an": """Generate 30 Indonesian words with the peN-...-an circumfix (confix).
Note the allomorphs of peN- (pen-, peng-, pem-, penge-, pe-).
Format: JSON array with objects: {{"word": "pembukaan", "root": "buka", "prefix": "peN", "alomorph": "pem", "suffix": "an"}}""",

    "reduplication_full": """Generate 40 Indonesian words with full reduplication (dwilingga).
These are words of the form X-X (e.g., buku-buku, orang-orang).
Format: JSON array with objects: {{"word": "buku-buku", "root": "buku", "type": "full"}}""",

    "reduplication_partial": """Generate 20 Indonesian words with partial reduplication (dwipurwa).
These are words where the first syllable is repeated (e.g., lelaki from laki, sesama from sama).
Format: JSON array with objects: {{"word": "lelaki", "root": "laki", "type": "partial"}}""",

    "reduplication_phonetic": """Generate 20 Indonesian words with reduplication with phonetic change (dwilingga salin suara).
These are words like bolak-balik, sayur-mayur, lauk-pauk where the second part changes phonetically.
Format: JSON array with objects: {{"word": "bolak-balik", "root": "bolak", "variant": "balik", "type": "phonetic"}}""",

    "complex_two_prefix": """Generate 40 Indonesian words with TWO prefixes (layered prefixation).
Examples: memper- (meN- + per-), menge- (for monosyllabic), etc.
Format: JSON array with objects: {{"word": "mempermainkan", "root": "main", "prefixes": ["meN", "per"], "suffixes": ["kan"]}}""",

    "complex_confix_suffix": """Generate 40 Indonesian words with circumfix AND additional suffix.
Examples: memperjuangkannya, mendownloadnya, keberhasilannya.
Format: JSON array with objects: {{"word": "memperjuangkannya", "root": "juang", "prefixes": ["meN", "per"], "suffixes": ["kan", "nya"]}}""",

    "possessive": """Generate 30 Indonesian words with possessive pronouns (-ku, -mu, -nya).
Format: JSON array with objects: {{"word": "bukunya", "root": "buku", "possessive": "nya"}}""",

    "particle": """Generate 30 Indonesian words with particles (-lah, -kah, -pun, -tah).
Format: JSON array with objects: {{"word": "ambilkanlah", "root": "ambil", "affixes": ["kan"], "particle": "lah"}}""",

    "loanword_affixed": """Generate 40 loanwords (from English/Dutch/etc) with Indonesian affixes.
Examples: mendownload, mengkompilasi, diupdate, me-restart (with hyphen).
Format: JSON array with objects: {{"word": "mendownload", "loanroot": "download", "prefix": "meN"}}""",

    "ambiguous": """Generate 30 Indonesian words that are morphologically AMBIGUOUS.
These are words where segmentation could be interpreted multiple ways.
Examples: "beruang" (bear vs prefix+uang), "mengetahui" (prefix+getah+tahu vs prefix+tahu).
Format: JSON array with objects: {{"word": "example", "ambiguity": "explanation"}}""",
}


# ============================================================================
# Gold Standard Generator
# ============================================================================

class GoldStandardGenerator:
    """Generate gold standard dataset using DeepSeek API."""

    def __init__(self, helper: Optional[DeepSeekHelper] = None):
        """Initialize generator."""
        self.helper = helper or DeepSeekHelper()
        self.entries: List[GoldStandardEntry] = []
        self.total_tokens_used = 0

    def generate_for_category(
        self,
        category: str,
        prompt: str,
        count: int = 30
    ) -> List[GoldStandardEntry]:
        """Generate entries for a specific category."""
        logger.info(f"Generating {count} entries for category: {category}")

        # Customize prompt for count
        customized_prompt = prompt.replace(str(prompt.count("30")), str(count))

        result = self.helper._call_api(customized_prompt, temperature=0.7)
        self.total_tokens_used += result.tokens_used

        if not result.success:
            logger.error(f"Failed to generate for category '{category}': {result.error}")
            return []

        # Parse response
        try:
            data = json.loads(result.data)
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict) and "words" in data:
                items = data["words"]
            elif isinstance(data, dict) and "variants" in data:
                items = data["variants"]
            else:
                items = []
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON for category '{category}'")
            return []

        # Convert to GoldStandardEntry objects
        entries = []
        for item in items[:count]:
            if isinstance(item, str):
                word = item
                entry = GoldStandardEntry(
                    word=word,
                    gold_segmentation=word,  # Will be updated with segmentation
                    category=category,
                    confidence="medium"
                )
            elif isinstance(item, dict):
                word = item.get("word", "")
                if not word:
                    continue

                entry = GoldStandardEntry(
                    word=word,
                    gold_segmentation=item.get("segmentation", word),
                    category=category,
                    subcategory=item.get("subcategory"),
                    confidence=item.get("confidence", "medium"),
                    morphemes=json.dumps(item.get("morphemes", [])),
                    notes=item.get("notes", "")
                )
            else:
                continue

            entries.append(entry)

        logger.info(f"Generated {len(entries)} entries for category '{category}'")
        return entries

    def generate_segmentations(self, words: List[str]) -> Dict[str, str]:
        """Get segmentations for a list of words."""
        logger.info(f"Getting segmentations for {len(words)} words")

        segmentations = {}
        for word in words:
            result = self.helper.segment_word(word)
            self.total_tokens_used += result.tokens_used

            if result.success and result.data:
                seg = result.data.get("segmentation", word)
                segmentations[word] = seg
            else:
                logger.warning(f"Failed to segment '{word}'")
                segmentations[word] = word

        return segmentations

    def generate_comprehensive_dataset(
        self,
        categories: Optional[Dict[str, int]] = None,
        validate_with_system: bool = True
    ) -> List[GoldStandardEntry]:
        """
        Generate comprehensive gold standard dataset.

        Args:
            categories: Dict mapping category name to count
            validate_with_system: Whether to also get system predictions

        Returns:
            List of GoldStandardEntry objects
        """
        if categories is None:
            categories = {
                "root_pure": 50,
                "prefix_meN": 40,
                "prefix_ber": 30,
                "prefix_ter": 20,
                "prefix_di": 20,
                "suffix_kan": 40,
                "suffix_i": 30,
                "suffix_an": 40,
                "confix_ke_an": 30,
                "confix_per_an": 30,
                "confix_peN_an": 30,
                "reduplication_full": 40,
                "reduplication_partial": 20,
                "reduplication_phonetic": 20,
                "complex_two_prefix": 40,
                "complex_confix_suffix": 50,
                "possessive": 30,
                "particle": 30,
                "loanword_affixed": 40,
                "ambiguous": 30,
            }

        all_entries = []

        for category, count in categories.items():
            if category in CATEGORY_PROMPTS:
                entries = self.generate_for_category(
                    category,
                    CATEGORY_PROMPTS[category],
                    count
                )
                all_entries.extend(entries)
            else:
                logger.warning(f"Unknown category: {category}")

        logger.info(f"Total entries generated: {len(all_entries)}")
        logger.info(f"Total tokens used: {self.total_tokens_used}")

        self.entries = all_entries
        return all_entries

    def save_to_csv(self, output_path: str) -> None:
        """Save entries to CSV file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', newline='', encoding='utf-8') as f:
            if self.entries:
                fieldnames = list(asdict(self.entries[0]).keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for entry in self.entries:
                    writer.writerow(asdict(entry))

        logger.info(f"Saved {len(self.entries)} entries to {output_path}")

    def load_from_csv(self, input_path: str) -> List[GoldStandardEntry]:
        """Load entries from CSV file."""
        entries = []

        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entries.append(GoldStandardEntry(**row))

        self.entries = entries
        logger.info(f"Loaded {len(entries)} entries from {input_path}")
        return entries

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the dataset."""
        if not self.entries:
            return {}

        category_counts = defaultdict(int)
        confidence_counts = defaultdict(int)

        for entry in self.entries:
            category_counts[entry.category] += 1
            confidence_counts[entry.confidence] += 1

        return {
            "total_entries": len(self.entries),
            "categories": dict(category_counts),
            "confidence_distribution": dict(confidence_counts),
            "tokens_used": self.total_tokens_used
        }


# ============================================================================
# Main
# ============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate Gold Standard Test Set for Indonesian Morphology"
    )
    parser.add_argument(
        "-o", "--output",
        default="data/gold_standard_test.csv",
        help="Output CSV file path"
    )
    parser.add_argument(
        "-s", "--size",
        type=int,
        default=1000,
        help="Target dataset size (approximate)"
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        help="Specific categories to generate (default: all)"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate existing gold standard file"
    )
    parser.add_argument(
        "-i", "--input",
        help="Input CSV file for validation"
    )
    parser.add_argument(
        "--add-segmentations",
        action="store_true",
        help="Add DeepSeek segmentations to existing words"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics and exit"
    )

    args = parser.parse_args()

    # Initialize generator
    try:
        generator = GoldStandardGenerator()
    except Exception as e:
        logger.error(f"Failed to initialize generator: {e}")
        logger.error("Make sure DEEPSEEK_API_KEY is set in .env file")
        return 1

    if args.stats:
        if args.input:
            generator.load_from_csv(args.input)
            stats = generator.get_statistics()
            print(json.dumps(stats, indent=2))
        else:
            print("--stats requires --input file")
        return 0

    if args.validate_only:
        if not args.input:
            print("--validate-only requires --input file")
            return 1

        generator.load_from_csv(args.input)

        # Validate each entry
        print(f"Validating {len(generator.entries)} entries...")
        invalid = 0
        for entry in generator.entries:
            if not entry.word or not entry.gold_segmentation:
                print(f"Invalid entry: {entry}")
                invalid += 1

        print(f"Validation complete. Invalid entries: {invalid}/{len(generator.entries)}")
        return 0

    if args.add_segmentations and args.input:
        # Load existing file and add segmentations
        generator.load_from_csv(args.input)

        words_to_segment = [e.word for e in generator.entries if not e.gold_segmentation or e.gold_segmentation == e.word]
        print(f"Adding segmentations for {len(words_to_segment)} words...")

        segmentations = generator.generate_segmentations(words_to_segment)

        for entry in generator.entries:
            if entry.word in segmentations:
                entry.gold_segmentation = segmentations[entry.word]

        generator.save_to_csv(args.output)
        print(f"Updated file saved to {args.output}")
        return 0

    # Generate new dataset
    print(f"Generating gold standard dataset (~{args.size} entries)")
    print(f"Output: {args.output}")

    # Calculate counts per category
    if args.categories:
        # Use specified categories
        categories = {cat: args.size // len(args.categories) for cat in args.categories}
    else:
        # Auto-calculate based on default distribution
        default_total = sum([30, 30, 30, 20, 20, 40, 30, 40, 30, 30, 30, 40, 20, 20, 40, 50, 30, 30, 40, 30])
        scale = args.size / default_total
        categories = {
            "root_pure": int(50 * scale),
            "prefix_meN": int(40 * scale),
            "prefix_ber": int(30 * scale),
            "prefix_ter": int(20 * scale),
            "prefix_di": int(20 * scale),
            "suffix_kan": int(40 * scale),
            "suffix_i": int(30 * scale),
            "suffix_an": int(40 * scale),
            "confix_ke_an": int(30 * scale),
            "confix_per_an": int(30 * scale),
            "confix_peN_an": int(30 * scale),
            "reduplication_full": int(40 * scale),
            "reduplication_partial": int(20 * scale),
            "reduplication_phonetic": int(20 * scale),
            "complex_two_prefix": int(40 * scale),
            "complex_confix_suffix": int(50 * scale),
            "possessive": int(30 * scale),
            "particle": int(30 * scale),
            "loanword_affixed": int(40 * scale),
            "ambiguous": int(30 * scale),
        }

    entries = generator.generate_comprehensive_dataset(categories)
    generator.save_to_csv(args.output)

    # Show statistics
    stats = generator.get_statistics()
    print("\n=== Generation Complete ===")
    print(json.dumps(stats, indent=2))

    return 0


if __name__ == "__main__":
    exit(main())
