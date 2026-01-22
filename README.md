# **ModernKataKupas - Indonesian Morphological Separator (V1.0.1)**

[![PyPI version](https://badge.fury.io/py/modern-kata-kupas.svg)](https://badge.fury.io/py/modern-kata-kupas)
[![Python Version](https://img.shields.io/pypi/pyversions/modern-kata-kupas.svg)](https://pypi.org/project/modern-kata-kupas/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-93%20passed-brightgreen.svg)](https://github.com/neimasilk/modern_kata_kupas)

## **Overview**

ModernKataKupas is a Python library for the morphological separation of Indonesian words. It breaks down words into their constituent morphemes: root word, prefixes, suffixes, and reduplication markers. This rule-based tool aims to enhance Natural Language Processing (NLP) tasks by providing linguistically informed sub-word units, particularly useful for applications working with Indonesian text.

## **V1.0.1 Status**

Version 1.0.1 provides a foundational rule-based segmenter and reconstructor with the following capabilities:

*   **Text Normalization:** Input words are normalized (lowercase, whitespace stripping, common trailing punctuation removal).
*   **Prefix Segmentation:**
    *   Simple prefixes: `di-`, `ke-`, `se-`.
    *   Complex prefixes with morphophonemic changes: `meN-` (e.g., `mem-`, `men-`, `meng-`), `peN-`, `ber-` (e.g., `bel-`, `be-`), `ter-` (e.g., `tel-`), `per-`.
*   **Suffix Segmentation:**
    *   Particles: `-lah`, `-kah`, `-pun`.
    *   Possessive pronouns: `-ku`, `-mu`, `-nya`.
    *   Common derivational suffixes: `-kan`, `-i`, `-an`.
*   **Layered Affixes & Basic Confixes:** Handles combinations like `ke-an`, `per-an`, `meN-kan`, `di-i`, etc., by applying prefix and suffix rules iteratively.
*   **Reduplication Handling:**
    *   Dwilingga (Full Reduplication): e.g., `rumah-rumah` (`rumah~ulg`), `buku-bukunya` (`buku~ulg~nya`).
    *   Dwilingga Salin Suara (Phonetic Change Reduplication): e.g., `sayur-mayur` (`sayur~rs(~mayur)`).
    *   Dwipurwa (Partial Initial Syllable Reduplication): e.g., `lelaki` (`laki~rp`).
*   **Loanword Affixation:** Basic handling for loanwords that have taken Indonesian affixes (e.g., `di-scan`, `mem-backup-nya`). Recognition depends on the loanword root being present in a configurable loanword list.
*   **Word Reconstruction:** Reconstructs the original word from its segmented form.
*   **Basic Ambiguity Resolution:** Employs heuristics (dictionary checks, rule order, longest stem preference) to choose between segmentation strategies. See [Architecture Documentation](memory-bank/architecture.md#penanganan-ambiguitas-dasar-v10) for details.

## **Features**

*   **Rule-Based Analysis:** Utilizes a configurable set of morphological rules for Indonesian.
*   **Morpheme Segmentation:** Identifies root words and various affixes.
*   **Handles Complex Morphology:** Addresses allomorphic variations of prefixes, some phonological adjustments at morpheme boundaries, layered affixation, and common confixes.
*   **Multiple Reduplication Types:** Detects Dwilingga, Dwilingga Salin Suara, and Dwipurwa.
*   **Customizable Dictionaries:** Allows users to provide custom root word and loanword lists.
*   **Extensible Rules:** Morphological rules are defined in an external JSON file, allowing for modification and extension.
*   **Word Reconstruction:** Capable of reconstructing full words from their segmented morpheme strings.

## **Installation**

There are several ways to install ModernKataKupas:

**1. From PyPI (Recommended):**

```bash
pip install modern-kata-kupas
```

**2. From a Local Wheel File:**

If you have a wheel file (e.g., `modern_kata_kupas-1.0.1-py3-none-any.whl`):
```bash
pip install path/to/your/modern_kata_kupas-1.0.1-py3-none-any.whl
```

**3. For Development (from cloned repository):**
```bash
git clone https://github.com/neimasilk/modern_kata_kupas.git
cd modern_kata_kupas
pip install -e .
```

**Dependencies:**
*   Python 3.8+
*   PySastrawi (used by the underlying `IndonesianStemmer` for root word identification in some internal processes like reduplication handling, not directly for the primary rule-based affix stripping).

## **Basic Usage**

```python
from modern_kata_kupas import ModernKataKupas

# Initialize the separator (uses default dictionary and rules if no path provided)
mkk = ModernKataKupas()

# --- Using segment() ---
word1 = "makanan"
segmented1 = mkk.segment(word1)
print(f"'{word1}' -> '{segmented1}'") # Expected: 'makan~an'

word2 = "memperbarui" # Assuming 'baru' is in kata_dasar.txt
segmented2 = mkk.segment(word2)
print(f"'{word2}' -> '{segmented2}'") # Expected: 'meN~per~baru~i'

# Example that might not segment if root is missing from kata_dasar.txt
word_dibaca = "dibaca"
segmented_dibaca = mkk.segment(word_dibaca)
print(f"'{word_dibaca}' -> '{segmented_dibaca}'") # Expected: 'dibaca'

word_mempertaruhkan = "mempertaruhkan"
segmented_mempertaruhkan = mkk.segment(word_mempertaruhkan)
print(f"'{word_mempertaruhkan}' -> '{segmented_mempertaruhkan}'") # Expected: 'mempertaruhkan'

word3 = "rumah-rumah" # Assuming 'rumah' is in kata_dasar.txt
segmented3 = mkk.segment(word3)
print(f"'{word3}' -> '{segmented3}'") # Expected: 'rumah~ulg'

# Example for 'bermain-main'
word_bermain_main = "bermain-main"
segmented_bermain_main = mkk.segment(word_bermain_main)
print(f"'{word_bermain_main}' -> '{segmented_bermain_main}'") # Expected: 'bermain~ulg'

word4 = "sayur-mayur"
segmented4 = mkk.segment(word4)
print(f"'{word4}' -> '{segmented4}'") # Expected: 'sayur~rs(~mayur)'

word5 = "lelaki"
segmented5 = mkk.segment(word5)
print(f"'{word5}' -> '{segmented5}'") # Expected: 'laki~rp' (if 'laki' is in kata_dasar.txt)

word6 = "di-backup" # Loanword example
segmented6 = mkk.segment(word6)
# Expected: 'di~backup' (if 'backup' is in loanwords.txt).
# If 'backup' is not in loanwords.txt, it might be returned as 'dibackup' (normalized)
# or 'di-backup' if normalization doesn't strip the hyphen before other checks.
# The V1.0 loanword handler expects 'backup' (no hyphen) in loanwords.txt.
print(f"'{word6}' -> '{segmented6}'")


# --- Using reconstruct() ---
segmented_form1 = "makan~an"
reconstructed1 = mkk.reconstruct(segmented_form1)
print(f"'{segmented_form1}' -> '{reconstructed1}'") # Expected: 'makanan'

segmented_form2 = "meN~per~baru~i"
reconstructed2 = mkk.reconstruct(segmented_form2)
print(f"'{segmented_form2}' -> '{reconstructed2}'") # Expected: 'memperbarui'

# Reconstruction for 'dibaca' (remains unsegmented)
segmented_dibaca_form = "dibaca"
reconstructed_dibaca = mkk.reconstruct(segmented_dibaca_form)
print(f"'{segmented_dibaca_form}' -> '{reconstructed_dibaca}'") # Expected: 'dibaca'

# Reconstruction for 'mempertaruhkan' (remains unsegmented)
segmented_mempertaruhkan_form = "mempertaruhkan"
reconstructed_mempertaruhkan = mkk.reconstruct(segmented_mempertaruhkan_form)
print(f"'{segmented_mempertaruhkan_form}' -> '{reconstructed_mempertaruhkan}'") # Expected: 'mempertaruhkan'

segmented_form3 = "rumah~ulg"
reconstructed3 = mkk.reconstruct(segmented_form3)
print(f"'{segmented_form3}' -> '{reconstructed3}'") # Expected: 'rumah-rumah'

# Reconstruction for 'bermain-main'
segmented_bermain_main_form = "bermain~ulg"
reconstructed_bermain_main = mkk.reconstruct(segmented_bermain_main_form)
print(f"'{segmented_bermain_main_form}' -> '{reconstructed_bermain_main}'") # Expected: 'bermain-main'

segmented_form4 = "sayur~rs(~mayur)"
reconstructed4 = mkk.reconstruct(segmented_form4)
print(f"'{segmented_form4}' -> '{reconstructed4}'") # Expected: 'sayur-mayur'

segmented_form5 = "laki~rp"
reconstructed5 = mkk.reconstruct(segmented_form5)
print(f"'{segmented_form5}' -> '{reconstructed5}'") # Expected: 'lelaki'

segmented_form6 = "di~backup"
reconstructed6 = mkk.reconstruct(segmented_form6)
print(f"'{segmented_form6}' -> '{reconstructed6}'") # Expected: 'dibackup'
```
*Note: Actual segmentation results depend on the contents of `kata_dasar.txt` (e.g., for "makan", "baru", "rumah", "laki") and `loanwords.txt` (e.g., for "backup"). If a root word is not found, the word may be returned unsegmented or only partially segmented. For example, "dibaca" and "mempertaruhkan" remain unsegmented if "baca" and "taruh" are not in the dictionary.*

## **CLI Usage**

ModernKataKupas provides a command-line interface (`mkk`) for quick segmentation and reconstruction tasks.

**Basic Commands:**

```bash
# Segment a single word
mkk segment "mempertaruhkan"
# Output: mempertaruhkan → meN~per~taruh~kan

# Reconstruct from segmented form
mkk reconstruct "meN~tulis"
# Output: meN~tulis → menulis

# Get help
mkk --help
mkk segment --help
```

**Batch Processing:**

```bash
# Create input file
echo "menulis" > words.txt
echo "membaca" >> words.txt
echo "mempertaruhkan" >> words.txt

# Segment all words in file
mkk segment-file words.txt

# Save output to file
mkk segment-file words.txt -o output.txt

# Output in different formats
mkk segment-file words.txt --format json
mkk segment-file words.txt --format csv
```

**Custom Configuration:**

```bash
# Use custom dictionary
mkk --dictionary /path/to/custom_dict.txt segment "kata"

# Use custom rules
mkk --rules /path/to/custom_rules.json segment "kata"

# Use custom configuration
mkk --config /path/to/custom_config.yaml segment "kata"
```

**JSON Output:**

```bash
mkk segment "menulis" --format json
# Output: {"word": "menulis", "segmented": "meN~tulis"}
```

## **Configuration**

ModernKataKupas supports configuration via YAML files for customizing behavior without modifying code.

**Configuration File Structure:**

```yaml
# config.yaml
min_stem_lengths:
  possessive: 3      # Minimum stem length for -ku, -mu, -nya
  derivational: 4    # Minimum stem length for -kan, -i, -an
  particle: 3        # Minimum stem length for -lah, -kah, -pun

dwilingga_salin_suara_pairs:
  - base: "sayur"
    variant: "mayur"
  - base: "bolak"
    variant: "balik"
  # Add more pairs as needed

features:
  enable_loanword_affixation: true
  enable_reduplication: true
  enable_morphophonemic_rules: true
```

**Using Custom Configuration:**

```python
from modern_kata_kupas import ModernKataKupas

# Load with custom config
mkk = ModernKataKupas(config_path="/path/to/config.yaml")

# Or use default packaged config
mkk = ModernKataKupas()  # Uses built-in config.yaml
```

## **Development Setup**

For contributors and developers:

**Install Development Dependencies:**

```bash
# Clone repository
git clone https://github.com/neimasilk/modern_kata_kupas.git
cd modern_kata_kupas

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

**Run Tests:**

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=modern_kata_kupas --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

**Code Quality:**

```bash
# Run type checking
mypy src/modern_kata_kupas

# Run linter
flake8 src/modern_kata_kupas

# Format code
black src/modern_kata_kupas

# Run all checks (pre-commit)
pre-commit run --all-files
```

**CI/CD:**

This project uses GitHub Actions for continuous integration:
- Automated testing on Python 3.8, 3.9, 3.10, 3.11
- Code coverage reporting
- Code quality checks (mypy, flake8, black)
- CLI functionality tests

## **Output Format for `segment()`**

The `segment()` method returns a string where morphemes are separated by a tilde (`~`).
*   **Canonical Affixes:** Prefixes are generally represented in their canonical forms (e.g., `meN-` for `meng-`, `mem-`, `meny-`, etc.; `peN-` for `peng-`, `pem-`, etc.).
*   **Reduplication Markers:**
    *   `~ulg`: Dwilingga (full reduplication), e.g., `rumah~ulg` for "rumah-rumah". Suffixes attached to the reduplicated form appear after the marker, e.g., `mobil~ulg~an` for "mobil-mobilan".
    *   `~rp`: Dwipurwa (initial syllable reduplication), e.g., `laki~rp` for "lelaki".
    *   `~rs(~VARIANT)`: Dwilingga Salin Suara (phonetic change reduplication), e.g., `sayur~rs(~mayur)` for "sayur-mayur". The `~VARIANT` part captures the changed stem.
*   **No Special Compound Marker:** Compound words are not explicitly marked with `_` unless the underscore is part of the root word itself as defined in `kata_dasar.txt`.

## **Handling of OOV (Out-Of-Vocabulary) Words**

When `segment()` encounters a word:
1.  It first normalizes the word.
2.  If the normalized word is already in `kata_dasar.txt`, it's returned as is.
3.  Otherwise, the system attempts to strip known affixes according to morphological rules.
4.  If, after stripping affixes, the remaining stem is found in `kata_dasar.txt`, the segmented form is returned.
5.  If the remaining stem is NOT in `kata_dasar.txt`, the system may try loanword affixation rules if the stem is found in `loanwords.txt`.
6.  If no segmentation rule can be successfully applied to find a known root word (either from `kata_dasar.txt` or `loanwords.txt` via loanword handling), the word is typically returned in its normalized form.

## **Limitations (V1.0.1)**

*   **Ambiguitas:** While V1.0.1 includes basic heuristics for ambiguity (see [Architecture Documentation](memory-bank/architecture.md#penanganan-ambiguitas-dasar-v10)), it may not always choose the most linguistically accurate segmentation in highly ambiguous cases.
*   **Ketergantungan Kamus:** The quality of segmentation heavily depends on the comprehensiveness of the root word dictionary (`kata_dasar.txt`) and the loanword list (`loanwords.txt`). Roots not present in these files may lead to suboptimal segmentation or words being returned unsegmented.
*   **Kompleksitas Morfologis:** V1.0.1 may not yet support all rare or highly complex morphological variations and affix combinations found in Indonesian.
*   **Idempotency:** For some complex words involving reduplication and unknown roots, the `reconstruct(segment(word))` cycle may not perfectly return the original normalized word due to simplifications in the segmented representation. For example, `segment("berkejar-kejaran")` might yield `berkejar~ulg~an`, which reconstructs to `berkejar-berkejaran`.

## **API Reference (Key Methods)**

For detailed API information, please refer to the docstrings within the source code.

*   **`ModernKataKupas(dictionary_path: Optional[str] = None, rules_file_path: Optional[str] = None, config_path: Optional[str] = None)`**
    *   Initializes the segmenter.
    *   `dictionary_path`: Custom root word list (one word per line, UTF-8).
    *   `rules_file_path`: Custom morphological rules JSON file.
    *   `config_path`: Custom configuration YAML file (min stem lengths, reduplication pairs, feature flags).
    *   All parameters default to packaged files if not provided.
*   **`ModernKataKupas.segment(word: str) -> str`**
    *   Segments an Indonesian word into its morphemes.
    *   Returns a tilde-separated string of morphemes.
*   **`ModernKataKupas.reconstruct(segmented_word: str) -> str`**
    *   Reconstructs the original word from a tilde-separated morpheme string.

## **Customization**

*   **Root Word Dictionary:** Provide a path to your own UTF-8 encoded text file (one word per line) to the `dictionary_path` parameter of `ModernKataKupas`.
*   **Affix Rules:** Supply a path to your custom JSON rules file to the `rules_file_path` parameter.
*   **Loanwords:** Provide a path to your own UTF-8 encoded text file (one word per line) of loanword roots to the `loanword_list_path` parameter of `DictionaryManager` (if using `DictionaryManager` directly) or ensure your custom dictionary for `ModernKataKupas` also contains loanwords to be recognized as roots after Indonesian affix stripping. The default `DictionaryManager` used by `ModernKataKupas` will try to load a `loanwords.txt` from the package data.

## **Contributing**

Contributions are welcome! Please report issues, suggest features, or submit pull requests via the project's GitHub repository: [https://github.com/neimasilk/modern_kata_kupas](https://github.com/neimasilk/modern_kata_kupas).

Before contributing, please ensure your code adheres to formatting standards (e.g., using Black and Flake8).

## **Future Work**

*   Enhanced ambiguity resolution mechanisms.
*   More comprehensive handling of idiomatic expressions and multi-word expressions.
*   Expansion of default dictionaries and rule sets.
*   Benchmarking against other Indonesian morphological analyzers.

## **License**

MIT License
(c) 2024 Tim ModernKataKupas
