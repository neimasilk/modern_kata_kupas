# **Implementation Plan: ModernKataKupas**

**Project:** ModernKataKupas \- Rule-Based Indonesian Morphological Separator and Reconstructor **Document Version:** 1.0 **Date:** May 21, 2025 **Based on:** `ModernKataKupas_PRD_v1.md` and `ModernKataKupas_TechStack_v1.md`

## **Phase 0: Project Setup and Foundational Components**

**Objective:** Prepare the development environment and implement core data structures and utilities.

* **Step 0.1: Project Initialization**  
    
  * **Action:**  
    1. Create a new project directory named `modern_kata_kupas`.  
    2. Initialize a Git repository within this directory.  
    3. Set up a Python virtual environment (e.g., using `venv`: `python -m venv venv_mkk`). Activate it.  
    4. Create a `requirements.txt` file.  
    5. Create a `memory-bank` subdirectory.  
    6. Copy `ModernKataKupas_PRD_v1.md` and `ModernKataKupas_TechStack_v1.md` into `memory-bank`.  
    7. Create empty files: `memory-bank/implementation-plan.md` (this document), `memory-bank/progress.md`, and `memory-bank/architecture.md`.  
    8. Create a `src/modern_kata_kupas` directory for the main library code and a `tests` directory for unit tests.  
  * **Test/Validation:**  
    * Project directory and virtual environment created successfully.  
    * Git repository initialized.  
    * `memory-bank` contains the specified `.md` files.  
    * `src` and `tests` directories exist.


* **Step 0.2: Install Core Dependencies**  
    
  * **Action:**  
    1. Add `PySastrawi` and `PyYAML` (if YAML is chosen for rules, otherwise not needed if only JSON) to `requirements.txt`.  
    2. Add `pytest` to `requirements.txt` (for testing).  
    3. Install dependencies: `pip install -r requirements.txt`.  
  * **Test/Validation:**  
    * `pip list` shows PySastrawi, PyYAML (if applicable), and pytest are installed in the virtual environment.


* **Step 0.3: Root Word Dictionary Management Module**  
    
  * **Action:**  
    1. Create `src/modern_kata_kupas/dictionary_manager.py`.  
    2. Implement a class `RootWordDictionary` with methods:  
       * `__init__(self, dictionary_path="path/to/default_kata_dasar.txt")`: Loads root words from a specified text file into a Python `set` for efficient lookup.  
       * `contains(self, word: str) -> bool`: Checks if a word is in the dictionary.  
       * `add_word(self, word: str)`: Adds a new word to the dictionary set (in-memory).  
       * `load_from_file(self, file_path: str)`: Loads/reloads dictionary from a file.  
    3. Prepare a basic `kata_dasar.txt` (can initially be a copy of Sastrawi's, to be augmented later as per PRD FR3.1). Place it in a `data` subdirectory (e.g., `src/modern_kata_kupas/data/kata_dasar.txt`).  
  * **Test/Validation:**  
    * Create `tests/test_dictionary_manager.py`.  
    * Test dictionary loading from a sample file.  
    * Test `contains()` method with known root words and non-root words.  
    * Test `add_word()` and verify with `contains()`.


* **Step 0.4: Affix Rule Repository Management Module**  
    
  * **Action:**  
    1. Create `src/modern_kata_kupas/rule_manager.py`.  
    2. Implement a class `AffixRuleRepository` with methods:  
       * `__init__(self, rules_file_path="path/to/default_affix_rules.json")`: Loads affix rules from a specified JSON (or YAML) file.  
       * `get_prefix_rules(self) -> dict`: Returns prefix rules.  
       * `get_suffix_rules(self) -> dict`: Returns suffix rules (including particles and possessives).  
       * `get_rule_for_affix(self, affix_canonical_form: str) -> dict`: Retrieves specific rule details.  
    3. Create an initial `affix_rules.json` file in `src/modern_kata_kupas/data/`. Start with a few basic prefix (e.g., `di-`, `ke-`, a simple `meN-` variant) and suffix rules (e.g., `-kan`, `-lah`, `-nya`) based on the structure proposed in Chapter 3.3 of the research paper draft (PRD FR3.2). *Example structure for one affix:*  
         
       {  
         
         "prefixes": {  
         
           "di-": {"canonical": "di", "type": "prefix\_derivational", "surface\_forms": \["di"\]},  
         
           "meN-": {  
         
             "canonical": "meN", "type": "prefix\_derivational",  
         
             "allomorphs": \[  
         
               {"surface": "me", "condition\_root\_starts\_with": \["l","m","n","r","w","y","ng","ny"\], "elision": "none"}  
         
             \]  
         
           }  
         
         },  
         
         "suffixes": {  
         
           "-kan": {"canonical": "kan", "type": "suffix\_derivational", "surface\_forms": \["kan"\]},  
         
           "-lah": {"canonical": "lah", "type": "particle", "surface\_forms": \["lah"\]}  
         
         }  
         
       }

      
  * **Test/Validation:**  
    * Create `tests/test_rule_manager.py`.  
    * Test loading rules from a sample JSON/YAML file.  
    * Test methods for retrieving prefix/suffix rules and specific affix details.


* **Step 0.5: String Alignment Utility**  
    
  * **Action:**  
    1. Create `src/modern_kata_kupas/utils/alignment.py`.  
    2. Implement the Needleman-Wunsch algorithm as a function:  
       * `align(seq1: str, seq2: str, match_score=1, mismatch_penalty=-1, gap_penalty=-1) -> tuple[str, str, str]`: Returns the two aligned sequences and a string indicating matches/mismatches/gaps. (Refer to existing implementations or the original `string_alignment.py` for logic, but rewrite for clarity and integration).  
  * **Test/Validation:**  
    * Create `tests/utils/test_alignment.py`.  
    * Test with simple known alignments (e.g., "apple", "apply").  
    * Test with cases involving insertions, deletions, and substitutions.

## **Phase 1: Core Segmentation Logic \- Base Forms and Simple Affixes**

**Objective:** Implement the basic segmentation pipeline for non-reduplicated words with single, clear affixes.

* **Step 1.1: Text Normalization Module Implementation**  
    
  * **Action:**  
    1. Create `src/modern_kata_kupas/normalizer.py`.  
    2. Implement a class `TextNormalizer` with a method `normalize_word(self, word: str) -> str`.  
    3. Implement lowercase conversion and basic punctuation stripping (e.g., removing trailing `.`, `,`, `?`, `!`). Preserve internal hyphens for now.  
  * **Test/Validation:**  
    * Create `tests/test_normalizer.py`.  
    * Test with various inputs: uppercase, mixed case, words with trailing punctuation, words with internal hyphens.


* **Step 1.2: Stemmer Interface Module**  
    
  * **Action:**  
    1. Create `src/modern_kata_kupas/stemmer_interface.py`.  
    2. Implement a class `IndonesianStemmer` that wraps PySastrawi:  
       * `__init__(self)`: Initializes the Sastrawi stemmer.  
       * `get_root_word(self, word: str) -> str`: Returns the stemmed root word.  
  * **Test/Validation:**  
    * Create `tests/test_stemmer_interface.py`.  
    * Test with known inflected words and their expected roots (e.g., "makanan" \-\> "makan", "berlari" \-\> "lari").  
    * Test behavior with words already in root form.


* **Step 1.3: Main Separator Class Structure (`ModernKataKupas`)**  
    
  * **Action:**  
    1. Create `src/modern_kata_kupas/separator.py`.  
    2. Define the `ModernKataKupas` class.  
    3. In `__init__`: Initialize `TextNormalizer`, `RootWordDictionary`, `AffixRuleRepository`, `IndonesianStemmer`, and the alignment function.  
    4. Define the main public method `segment(self, word: str) -> str` (stub implementation for now, just returns the normalized word).  
    5. Define helper private methods (stubs for now): `_handle_reduplication()`, `_strip_suffixes()`, `_strip_prefixes()`, `_apply_morphophonemic_segmentation_rules()`.  
  * **Test/Validation:**  
    * Class can be instantiated.  
    * `segment()` method exists and returns normalized input.


* **Step 1.4: Basic Suffix Stripping (Particles and Possessives)**  
    
  * **Action:**  
    1. Implement logic within `_strip_suffixes()` in `separator.py`.  
    2. Focus on stripping inflectional particles (`-lah`, `-kah`, `-pun`) and possessive pronouns (`-ku`, `-mu`, `-nya`) first.  
    3. Use `AffixRuleRepository` to get valid suffixes and their forms.  
    4. Stripping order: Particles, then Possessives.  
    5. Update the `current_word` and store stripped suffixes.  
  * **Test/Validation:**  
    * In `tests/test_separator.py`, add tests for:  
      * `bukuku` \-\> `buku~ku` (intermediate: `buku` \+ suffix `~ku`)  
      * `ambilkanlah` \-\> `ambilkan~lah` (intermediate: `ambilkan` \+ suffix `~lah`)  
      * `siapakah` \-\> `siapa~kah`  
      * `miliknya` \-\> `milik~nya`  
      * `rumahkupun` \-\> `rumah~ku~pun` (layered)


* **Step 1.5: Basic Derivational Suffix Stripping (`-kan`, `-i`, `-an`)**  
    
  * **Action:**  
    1. Extend `_strip_suffixes()` to handle `-kan`, `-i`, `-an` after particles/possessives.  
    2. After stripping a derivational suffix, the remaining word should ideally be a known root or a form ready for prefix stripping.  
  * **Test/Validation:**  
    * Add tests for:  
      * `makanan` \-\> `makan~an`  
      * `panasi` \-\> `panas~i`  
      * `lemparkan` \-\> `lempar~kan`  
      * `pukulan` \-\> `pukul~an`  
      * `mainkanlah` \-\> `main~kan~lah` (ensure correct layering with previous step)


* **Step 1.6: Basic Prefix Stripping (Simple, Non-Morphophonemic: `di-`, `ke-`, `se-`)**  
    
  * **Action:**  
    1. Implement logic within `_strip_prefixes()` in `separator.py`.  
    2. Focus on simple prefixes `di-`, `ke-`, `se-` that don't typically involve complex morphophonemic changes with the root.  
    3. Use `AffixRuleRepository`.  
    4. Update `current_word` and store stripped prefixes.  
  * **Test/Validation:**  
    * Add tests for:  
      * `dibaca` \-\> `di~baca`  
      * `kesana` \-\> `ke~sana`  
      * `sebuah` \-\> `se~buah`  
      * `dimakanan` \-\> `di~makan~an` (ensure prefix stripping happens after suffix stripping or on the result) \- *This highlights the need for a clear processing order: Suffixes first, then Prefixes for simple cases*.

## **Phase 2: Advanced Affixation and Morphophonemics**

**Objective:** Implement handling for complex prefixes involving morphophonemic changes and layered affixes.

* **Step 2.1: Advanced Prefix Stripping (`meN-`, `peN-`) with Morphophonemic Rules**  
    
  * **Action:**  
    1. Enhance `_strip_prefixes()` and create/use `_apply_morphophonemic_segmentation_rules()`.  
    2. Implement rules for `meN-` and `peN-` based on the `aturan_afiks` (JSON/YAML), considering allomorphs (`mem-`, `men-`, `meny-`, `meng-`, `menge-`) and elision of root initial consonants (`p, t, k, s`).  
    3. Use the `root_word` (from stemmer) and string alignment to guide the identification of the canonical prefix and the original root form.  
  * **Test/Validation:**  
    * Test extensively:  
      * `membaca` \-\> `meN~baca`  
      * `memukul` \-\> `meN~pukul` (reconstruct `p`)  
      * `menulis` \-\> `meN~tulis` (reconstruct `t`)  
      * `menyapu` \-\> `meN~sapu` (reconstruct `s`)  
      * `mengambil` \-\> `meN~ambil`  
      * `mengupas` \-\> `meN~kupas` (reconstruct `k`)  
      * `mengebom` \-\> `meN~bom`  
      * `pemukul` \-\> `peN~pukul`  
      * `pengirim` \-\> `peN~kirim`


* **Step 2.2: Advanced Prefix Stripping (`ber-`, `ter-`, `per-`) with Morphophonemic Rules**  
    
  * **Action:**  
    1. Continue enhancing `_strip_prefixes()` and `_apply_morphophonemic_segmentation_rules()`.  
    2. Implement rules for `ber-` (e.g., `belajar` \-\> `ber~ajar`; `bekerja` \-\> `ber~kerja`), `ter-` (e.g., `terbawa` \-\> `ter~bawa`; `telanjur` (if `ter`\+`anjur`) \-\> `ter~anjur`), `per-` (e.g., `pelajar` \-\> `per~ajar`; `perbuat` \-\> `per~buat`).  
  * **Test/Validation:**  
    * Test: `belajar`, `bekerja`, `terbawa`, `telanjur`, `perbuat`, `perluas`.


* **Step 2.3: Handling Layered Prefixes and Suffixes (Confixes)**  
    
  * **Action:**  
    1. Ensure the iterative stripping logic in `_strip_suffixes()` and `_strip_prefixes()` can handle multiple affixes correctly.  
    2. The system should be able to strip outer layers first, then inner layers, or vice-versa depending on the standard derivational order. This is implicitly handled by iterating and checking against the dictionary/root word.  
    3. Confixes (`ke-an`, `per-an`, `peN-an`, `ber-an`) are handled by sequential stripping of their prefix and suffix components.  
  * **Test/Validation:**  
    * Test:  
      * `keadilan` \-\> `ke~adil~an`  
      * `perjuangan` \-\> `per~juang~an`  
      * `pembangunan` \-\> `peN~bangun~an`  
      * `mempertaruhkan` \-\> `meN~per~taruh~kan`  
      * `dipertimbangkan` \-\> `di~per~timbang~kan`

## **Phase 3: Reduplication and Reconstruction**

**Objective:** Implement robust handling for various reduplication types and the word reconstruction functionality.

* **Step 3.1: Implement Full Reduplication Logic (Dwilingga)**  
    
  * **Action:**  
    1. Finalize the `_handle_reduplication()` method in `separator.py` for `X-X` patterns.  
    2. Ensure correct interaction with affix stripping (e.g., `mobil-mobilan` \-\> `mobil~ulg~an`).  
  * **Test/Validation:**  
    * Test: `rumah-rumah`, `anak-anak`, `meja-meja`, `bermain-main`, `buku-bukunya`, `tendang-tendangan`.


* **Step 3.2: Implement Dwilingga Salin Suara Logic**  
    
  * **Action:**  
    1. Extend `_handle_reduplication()` for `X-Y` patterns with phonetic changes.  
    2. Requires a list of known pairs or more advanced heuristics.  
  * **Test/Validation:**  
    * Test: `sayur-mayur`, `bolak-balik`, `warna-warni`, `ramah-tamah`.


* **Step 3.3: Implement Dwipurwa Logic**  
    
  * **Action:**  
    1. Extend `_handle_reduplication()` for partial initial syllable reduplication.  
  * **Test/Validation:**  
    * Test: `lelaki`, `sesama`, `tetamu`, `rerata`.


* **Step 3.4: Word Reconstruction Functionality**  
    
  * **Action:**  
    1. Implement the public method `reconstruct(self, segmented_word: str) -> str` in `separator.py`.  
    2. Implement helper `_apply_morphophonemic_reconstruction_rules()`.  
    3. Logic should parse the `~` separated morphemes.  
    4. Re-apply prefixes and suffixes in the correct order, using forward morphophonemic rules from `aturan_afiks` (e.g., `meN~` \+ `pukul` \-\> `memukul`).  
    5. Reconstruct reduplicated forms from their markers.  
  * **Test/Validation:**  
    * For every segmentation test case, add a corresponding reconstruction test to ensure the original word (after normalization) is perfectly recovered.  
    * Test `meN~pukul` \-\> `memukul`.  
    * Test `buku~ulg~nya` \-\> `buku-bukunya`.  
    * Test `per~ajar` \-\> `pelajar`.

## **Phase 4: Refinements, Packaging, and Documentation**

**Objective:** Handle edge cases, improve robustness, package the library, and create documentation.

* **Step 4.1: Loanword Affixation Handling**  
    
  * **Action:**  
    1. Implement the logic described in PRD FR1.7 and Chapter 3.3.5 of the research paper draft.  
    2. Create a small auxiliary list of common English loanwords for initial testing.  
  * **Test/Validation:**  
    * Test: `di-download`, `meng-update`, `mem-backup`, `di-scan-nya`.


* **Step 4.2: Basic Ambiguity Handling**  
    
  * **Action:**  
    1. Implement basic heuristics (e.g., longest valid root match, rule precedence) as outlined in PRD FR1.8 and Chapter 3.4.  
  * **Test/Validation:**  
    * Identify ambiguous words (e.g., `beruang`) and test how the system resolves them or if it needs to output alternatives.


* **Step 4.3: Comprehensive Testing and Edge Cases**  
    
  * **Action:**  
    1. Expand `pytest` test suite to cover a wide range of complex words, edge cases, and known problematic examples from linguistic literature or user feedback.  
    2. Test with empty strings, non-Indonesian words, very long words (if applicable).  
  * **Test/Validation:**  
    * Aim for high test coverage (e.g., \>90%).


* **Step 4.4: API Finalization and Documentation**  
    
  * **Action:**  
    1. Finalize the public API of the `ModernKataKupas` class.  
    2. Write comprehensive docstrings for all public classes and methods.  
    3. Create a `README.md` with installation instructions, usage examples, and a brief overview of the algorithm.  
    4. Consider generating HTML documentation using Sphinx.  
  * **Test/Validation:**  
    * API is clear and easy to use.  
    * Documentation is accurate and complete.


* **Step 4.5: Packaging for Distribution**  
    
  * **Action:**  
    1. Create `setup.py` and other necessary files for packaging using `setuptools`.  
    2. Build source distribution and wheel.  
  * **Test/Validation:**  
    * Library can be installed using `pip` from the built package.  
    * Import and basic usage work correctly after installation.


* **Step 4.6: Update `architecture.md`**  
    
  * **Action:** Document the final software architecture, purpose of each Python file/module, data file structures, and key class interactions in `memory-bank/architecture.md`.  
  * **Test/Validation:** `architecture.md` accurately reflects the developed codebase.

This implementation plan provides a structured approach to developing the "ModernKataKupas" library. Each step should be committed to Git upon successful validation. The `memory-bank/progress.md` file should be updated after each step to track completion.  