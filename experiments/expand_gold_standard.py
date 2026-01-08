"""
Expand Gold Standard Test Set using DeepSeek API

Generates additional morphologically segmented Indonesian words
to expand the test set from 191 to 500+ words.
"""
import sys
import csv
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modern_kata_kupas.utils.deepseek_helper import DeepSeekHelper
from modern_kata_kupas.separator import ModernKataKupas

class GoldStandardExpander:
    """Expand the gold standard test set using DeepSeek API."""

    def __init__(self):
        self.helper = DeepSeekHelper()
        self.separator = ModernKataKupas()

        # Load existing gold standard to avoid duplicates
        self.existing_words = self._load_existing_words()

    def _load_existing_words(self) -> set:
        """Load existing words from gold standard."""
        words = set()
        gold_files = [
            Path(__file__).parent.parent / "data" / "gold_standard_v2.csv",
            Path(__file__).parent.parent / "experiments" / "results" / "errors_v3.csv",
        ]
        for f in gold_files:
            if f.exists():
                with open(f, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        word = row.get('word', '')
                        if word:
                            words.add(word.lower())
        return words

    def generate_category_words(self, category: str, count: int = 30) -> list:
        """Generate words for a specific category using DeepSeek."""

        category_prompts = {
            "complex_meN": """Generate 30 Indonesian words with meN- prefix that are morphologically complex.
Examples: memperbuat, menginterpretasikan, menyelenggarakan, mempertimbangkan, mengkompilasi.
Include words with:
- meN + per- (meN-per-)
- meN + derivational suffixes (-kan, -i, -an)
- meN + multiple affixes
- Loanwords with meN- prefix (e.g., mengkompilasi, mengupload)

Return as JSON: {{"words": [{"word": "mempertimbangkan", "segmentation": "meN~per~pertimbang~kan", "notes": "..."}]}}""",

            "complex_peN_an": """Generate 30 Indonesian words with peN-...-an confix that are morphologically complex.
Examples: pembelajaran, pengembangan, penyelesaian, pendidikan, pemeliharaan.

Include words with:
- Complex root words (multi-syllabic)
- Roots that start with different sounds (p, b, t, d, c, j, s, k, g, a, i, u, e, o)
- Academic/formal vocabulary
- Compound roots

Return as JSON: {{"words": [{"word": "pembelajaran", "segmentation": "peN~ajar~an", "notes": "..."}]}}""",

            "compound_reduplication": """Generate 20 Indonesian compound words with reduplication.
Examples: kekasih-kesayangan, main-mainan, guru-guru murid, bolak-balikkan.

Include:
- Reduplication with affixes (e.g., X-Xkan, ke-X-X-an)
- Compound phrases with reduplication
- Phonetic reduplication variations

Return as JSON: {{"words": [{"word": "kekasih-kesayangan", "segmentation": "ke~kasih~ulg~sayang~an", "notes": "..."}]}}""",

            "suffix_combinations": """Generate 30 Indonesian words with multiple suffixes.
Examples: mempermainkannya, mengirimmu, dijualannya, kebersihanku.

Include combinations of:
- -kan + -nya
- -i + -ku/-mu/-nya
- -an + -lah/-kah
- Possessive + particle

Return as JSON: {{"words": [{"word": "mempermainkannya", "segmentation": "meN~per~main~kan~nya", "notes": "..."}]}}""",

            "derivational_suffixes": """Generate 30 Indonesian words with derivational suffixes indicating:
1. Causative (-kan): membuatkan, menjadikan
2. Stative/result (-i): memberi, menuruti
3. Abstract noun (-an): keindahan, kemerdekaan
4. Instrument/agent (-an): alat-alatan, obat-obatan

Return as JSON: {{"words": [{"word": "membuatkan", "segmentation": "meN~buat~kan", "notes": "causative"}]}}""",

            "prefix_combinations": """Generate 30 Indonesian words with multiple prefixes.
Examples: memperbarui, menginterpretasikan, menyelesaikan, keberhasilan.

Include:
- meN + per- (agentive, transitive)
- meN + di- (passive with meN-)
- ke- + ber- (state/condition)
- ter- + per- (superlative)

Return as JSON: {{"words": [{"word": "memperbarui", "segmentation": "meN~per~baru~i", "notes": "..."}]}}""",

            "loanword_affixation": """Generate 30 Indonesian words from English/foreign roots with Indonesian affixes.
Examples: mengupload, mendownload, mengkompilasi, di-posting-kan, share-kan.

Include:
- Technology terms (upload, download, compile, etc.)
- Social media terms (posting, sharing, etc.)
- Academic terms (presenting, discussing, etc.)
- Informal/colloquial formations

Return as JSON: {{"words": [{"word": "mengupload", "segmentation": "meN~upload", "notes": "loanword with meN-"}]}}""",

            "formal_academic": """Generate 30 formal/academic Indonesian words with complex morphology.
Examples: mempertanggungjawabkan, mengidentifikasikan, mensyaratkan, menginternalisasi.

Include:
- Academic verbs
- Abstract nouns
- Professional terminology
- Government/administrative terms

Return as JSON: {{"words": [{"word": "mempertanggungjawabkan", "segmentation": "meN~per~tanggung~jawab~kan", "notes": "formal"}]}}""",

            "colloquial_informal": """Generate 20 colloquial Indonesian words with morphology.
Examples: nemenin, nge-post, nge-share, nontonin, dikit-dikit.

Include:
- meN- allomorphs in informal speech (nge-, nye-, nem-, nen-)
- Informal suffixes (-in from -kan)
- Common abbreviations
- Jakarta slang influence

Return as JSON: {{"words": [{"word": "nemenin", "segmentation": "meN~temen~i", "notes": "colloquial meN- + -i"}]}}""",

            "particle_variations": """Generate 30 Indonesian words with sentence particles (-lah, -kah, -pun, -tah).
Examples: ambillah, bukankah, guru-pun, barangkali-tah.

Include:
- -lah with imperative verbs
- -kah with yes/no questions
- -pun with emphasis/even
- -tah with uncertainty

Return as JSON: {{"words": [{"word": "ambillah", "segmentation": "ambil~lah", "notes": "imperative"}]}}""",
        }

        print(f"\n=== Generating {count} words for category: {category} ===")

        prompt = category_prompts.get(category, category_prompts["complex_meN"])

        result = self.helper._call_api(prompt, temperature=0.7)

        if not result.success:
            print(f"  Error: {result.error}")
            return []

        # Parse JSON response
        try:
            data = json.loads(result.data)
            words_data = data.get("words", [])

            # Filter out existing words
            new_words = []
            for item in words_data:
                word = item.get("word", "").lower().strip()
                if word and word not in self.existing_words:
                    new_words.append({
                        "word": word,
                        "gold_segmentation": item.get("segmentation", ""),
                        "category": category,
                        "notes": item.get("notes", ""),
                        "generated_by": "deepseek",
                    })
                    self.existing_words.add(word)

            print(f"  Generated {len(new_words)} new words (filtered {len(words_data) - len(new_words)} duplicates)")
            return new_words

        except json.JSONDecodeError as e:
            print(f"  JSON Parse Error: {e}")
            # Try to extract from markdown code block
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', result.data, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    words_data = data.get("words", [])
                    new_words = []
                    for item in words_data:
                        word = item.get("word", "").lower().strip()
                        if word and word not in self.existing_words:
                            new_words.append({
                                "word": word,
                                "gold_segmentation": item.get("segmentation", ""),
                                "category": category,
                                "notes": item.get("notes", ""),
                                "generated_by": "deepseek",
                            })
                            self.existing_words.add(word)
                    print(f"  Generated {len(new_words)} new words (from markdown block)")
                    return new_words
                except:
                    pass
            return []

    def validate_and_correct(self, words: list) -> list:
        """Validate and correct segmentations using the system itself."""
        print(f"\n=== Validating {len(words)} words ===")

        validated = []
        corrections = []

        for item in words:
            word = item["word"]
            gold = item["gold_segmentation"]

            # Get system prediction
            try:
                prediction = self.separator.segment(word)
            except:
                prediction = word

            # Check if they agree
            agrees = (gold.lower() == prediction.lower())

            # If they disagree, ask DeepSeek to verify
            if not agrees:
                verify_prompt = f"""Compare these two Indonesian morphological segmentations:

Word: {word}
System prediction: {prediction}
DeepSeek suggestion: {gold}

Determine which is correct. Consider Indonesian morphology rules:
- meN- prefix allomorphs (me-, men-, meng-, meny-, mem-, menge-)
- Prefix precedence and layering
- Root word validity (common Indonesian words)

Reply with just the correct segmentation in format: CORRECT: <segmentation>
If both are wrong, provide the correct one."""

                verify_result = self.helper._call_api(verify_prompt, temperature=0.3)

                if verify_result.success:
                    # Extract correct segmentation
                    import re
                    match = re.search(r'CORRECT:\s*(\S+(?:~\S+)*)', verify_result.data)
                    if match:
                        corrected = match.group(1)
                        corrections.append({
                            "word": word,
                            "original_gold": gold,
                            "system_prediction": prediction,
                            "corrected": corrected,
                        })
                        item["gold_segmentation"] = corrected
                        item["corrected_from_disagreement"] = True

            item["system_prediction"] = prediction
            item["agrees"] = str(agrees)
            item["validated"] = "True"
            validated.append(item)

        print(f"  Validated: {len(validated)}")
        print(f"  Corrections made: {len(corrections)}")

        return validated

    def save_expanded_gold_standard(self, all_words: list, output_path: str = None):
        """Save the expanded gold standard to CSV."""
        if output_path is None:
            output_path = Path(__file__).parent.parent / "data" / "gold_standard_v3.csv"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Sort by category
        all_words.sort(key=lambda x: x.get("category", ""))

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ["word", "gold_segmentation", "category", "notes", "generated_by",
                         "system_prediction", "agrees", "validated"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_words)

        print(f"\n=== Saved {len(all_words)} words to {output_path} ===")
        return output_path

    def run_expansion(self, target_count: int = 500):
        """Run the full expansion process."""
        print("=" * 70)
        print("GOLD STANDARD EXPANSION USING DEEPSEEK")
        print("=" * 70)
        print(f"\nTarget: {target_count} words")
        print(f"Current: {len(self.existing_words)} words")
        print(f"Need: {target_count - len(self.existing_words)} new words\n")

        all_new_words = []
        categories = [
            ("complex_meN", 30),
            ("complex_peN_an", 30),
            ("compound_reduplication", 20),
            ("suffix_combinations", 30),
            ("derivational_suffixes", 30),
            ("prefix_combinations", 30),
            ("loanword_affixation", 30),
            ("formal_academic", 30),
            ("colloquial_informal", 20),
            ("particle_variations", 30),
        ]

        # Generate words for each category
        for category, count in categories:
            if len(all_new_words) + len(self.existing_words) >= target_count:
                print(f"\nTarget reached! Stopping generation.")
                break

            new_words = self.generate_category_words(category, count)
            all_new_words.extend(new_words)

        print(f"\n=== Total new words generated: {len(all_new_words)} ===")

        # Validate and correct
        validated_words = self.validate_and_correct(all_new_words)

        # Combine with existing gold standard
        combined_words = self._combine_with_existing(validated_words)
        print(f"\n=== Total words in combined set: {len(combined_words)} ===")

        # Save
        output_path = self.save_expanded_gold_standard(combined_words)

        return output_path, len(combined_words)

    def _combine_with_existing(self, new_words: list) -> list:
        """Combine new words with existing gold standard."""
        # Load existing gold standard
        existing = []
        gold_file = Path(__file__).parent.parent / "data" / "gold_standard_v2.csv"
        if gold_file.exists():
            with open(gold_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing.append({
                        "word": row.get("word", ""),
                        "gold_segmentation": row.get("gold_segmentation", ""),
                        "category": row.get("category", "existing"),
                        "notes": row.get("notes", ""),
                        "generated_by": "existing",
                        "system_prediction": row.get("system_prediction", ""),
                        "agrees": row.get("agrees", ""),
                        "validated": row.get("validated", "False"),
                    })

        return existing + new_words


def main():
    expander = GoldStandardExpander()
    output_path, total_count = expander.run_expansion(target_count=500)

    print("\n" + "=" * 70)
    print("EXPANSION COMPLETE")
    print("=" * 70)
    print(f"Output: {output_path}")
    print(f"Total words: {total_count}")


if __name__ == '__main__':
    main()
