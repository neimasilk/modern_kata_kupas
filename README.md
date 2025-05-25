# **ModernKataKupas - Indonesian Morphological Separator (V1.0)**

## **Overview**

ModernKataKupas is a Python library for the morphological separation of Indonesian words. It breaks down words into their constituent morphemes: root word, prefixes, suffixes, and reduplication markers. This rule-based tool aims to enhance Natural Language Processing (NLP) tasks by providing linguistically informed sub-word units, particularly useful for applications working with Indonesian text.

## **V1.0 Status**

Version 1.0 provides a foundational rule-based segmenter and reconstructor with the following capabilities:

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

```bash
pip install modern_kata_kupas # Target package name
```

**Dependencies:**
*   Python 3.8+
*   PySastrawi (used by the underlying `IndonesianStemmer` for root word identification in some internal processes like reduplication handling, not directly for the primary rule-based affix stripping).

For development:
```bash
git clone https://github.com/username/modern_kata_kupas.git # Replace with actual repo URL
cd modern_kata_kupas
pip install -e .
```

## **Basic Usage**

```python
from modern_kata_kupas import ModernKataKupas

# Initialize the separator (uses default dictionary and rules if no path provided)
mkk = ModernKataKupas()

# --- Using segment() ---
word1 = "makanan"
segmented1 = mkk.segment(word1)
print(f"'{word1}' -> '{segmented1}'") # Expected: 'makan~an' (if 'makan' is in kata_dasar.txt)

word2 = "memperbarui"
segmented2 = mkk.segment(word2)
print(f"'{word2}' -> '{segmented2}'") # Expected: 'meN~per~baru~i' (if 'baru' is in kata_dasar.txt)

word3 = "rumah-rumah"
segmented3 = mkk.segment(word3)
print(f"'{word3}' -> '{segmented3}'") # Expected: 'rumah~ulg' (if 'rumah' is in kata_dasar.txt)

word4 = "sayur-mayur"
segmented4 = mkk.segment(word4)
print(f"'{word4}' -> '{segmented4}'") # Expected: 'sayur~rs(~mayur)'

word5 = "lelaki"
segmented5 = mkk.segment(word5)
print(f"'{word5}' -> '{segmented5}'") # Expected: 'laki~rp' (if 'laki' is in kata_dasar.txt)

word6 = "di-backup" # Loanword example
segmented6 = mkk.segment(word6)
# Expected: 'di~backup' (if 'backup' is in loanwords.txt and 'di-' rule applies)
# If 'backup' isn't a known loanword, might be 'di-backup' or 'dibackup'
print(f"'{word6}' -> '{segmented6}'")


# --- Using reconstruct() ---
segmented_form1 = "makan~an"
reconstructed1 = mkk.reconstruct(segmented_form1)
print(f"'{segmented_form1}' -> '{reconstructed1}'") # Expected: 'makanan'

segmented_form2 = "meN~per~baru~i"
reconstructed2 = mkk.reconstruct(segmented_form2)
print(f"'{segmented_form2}' -> '{reconstructed2}'") # Expected: 'memperbarui'

segmented_form3 = "rumah~ulg"
reconstructed3 = mkk.reconstruct(segmented_form3)
print(f"'{segmented_form3}' -> '{reconstructed3}'") # Expected: 'rumah-rumah'

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
*Note: Actual segmentation results for words like "makanan", "memperbarui", "dibaca" depend on the contents of `kata_dasar.txt`. If the root word ("makan", "baru", "baca") is not found, the word may be returned unsegmented or only partially segmented.*

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

## **Limitations (V1.0)**

*   **Ambiguitas:** While V1.0 includes basic heuristics for ambiguity (see [Architecture Documentation](memory-bank/architecture.md#penanganan-ambiguitas-dasar-v10)), it may not always choose the most linguistically accurate segmentation in highly ambiguous cases.
*   **Ketergantungan Kamus:** The quality of segmentation heavily depends on the comprehensiveness of the root word dictionary (`kata_dasar.txt`) and the loanword list (`loanwords.txt`). Roots not present in these files may lead to suboptimal segmentation or words being returned unsegmented.
*   **Kompleksitas Morfologis:** V1.0 may not yet support all rare or highly complex morphological variations and affix combinations found in Indonesian.
*   **Idempotency:** For some complex words involving reduplication and unknown roots, the `reconstruct(segment(word))` cycle may not perfectly return the original normalized word due to simplifications in the segmented representation. For example, `segment("berkejar-kejaran")` might yield `berkejar~ulg~an`, which reconstructs to `berkejar-berkejaran`.

## **API Reference (Key Methods)**

For detailed API information, please refer to the docstrings within the source code.

*   **`ModernKataKupas(dictionary_path: Optional[str] = None, rules_file_path: Optional[str] = None)`**
    *   Initializes the segmenter. `dictionary_path` allows specifying a custom root word list, and `rules_file_path` a custom rules JSON. Defaults to packaged files if not provided.
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

Contributions are welcome! Please report issues, suggest features, or submit pull requests via the project's GitHub repository: [https://github.com/USERNAME/modern_kata_kupas](https://github.com/USERNAME/modern_kata_kupas) (Replace with actual URL).

Before contributing, please ensure your code adheres to formatting standards (e.g., using Black and Flake8).

## **Future Work**

*   Enhanced ambiguity resolution mechanisms.
*   More comprehensive handling of idiomatic expressions and multi-word expressions.
*   Expansion of default dictionaries and rule sets.
*   Benchmarking against other Indonesian morphological analyzers.

## **License**

MIT License
(c) 2024 [Your Name/Organization]
