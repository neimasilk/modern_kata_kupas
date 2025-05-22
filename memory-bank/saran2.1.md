Baik, saya telah menerapkan saran Anda dengan menambahkan `print` statement untuk debugging pada metode `_strip_prefixes` dan `_strip_suffixes` di file `src/modern_kata_kupas/separator.py`.

Berikut adalah langkah-langkah yang telah saya lakukan:

1.  **Modifikasi `_strip_prefixes`:**
    Menambahkan `print` statement di awal metode untuk memeriksa input dan output stemmer untuk kata "ketua" dan "kesekolah".
    ```python
    # src/modern_kata_kupas/separator.py
    def _strip_prefixes(self, original_word_for_prefix_stripping: str) -> tuple[str, list[str]]:
        # --- BEGIN TEMPORARY DEBUG PRINT ---
        if original_word_for_prefix_stripping in ["ketua", "kesekolah"]:
            print(f"[STEMMER_CHECK] Input to _strip_prefixes: '{original_word_for_prefix_stripping}'")
            # root_from_stemmer dihitung setelah ini, jadi kita panggil lagi di sini untuk debug awal
            # atau kita bisa memindahkan perhitungan root_from_stemmer ke atas sebelum print ini.
            # Untuk sekarang, kita panggil lagi agar tidak mengubah struktur terlalu banyak.
            evaluated_root_from_stemmer = self.stemmer.get_root_word(original_word_for_prefix_stripping)
            print(f"[STEMMER_CHECK] Output of self.stemmer.get_root_word('{original_word_for_prefix_stripping}'): '{evaluated_root_from_stemmer}'")
        # --- END TEMPORARY DEBUG PRINT ---

        current_word = str(original_word_for_prefix_stripping)
        stripped_prefixes_output = []
        # root_from_stemmer akan dihitung di sini dalam kode asli Anda.
        # Untuk keperluan debug di atas, kita mungkin sudah memanggilnya.
        # Pastikan root_from_stemmer yang digunakan di sisa fungsi adalah yang konsisten.
        root_from_stemmer = self.stemmer.get_root_word(original_word_for_prefix_stripping)
        # ... (sisa metode)
    ```

2.  **Modifikasi `_strip_suffixes`:**
    Menambahkan `print` statement detail di berbagai titik di dalam metode untuk melacak pemrosesan kata "kesekolah".
    ```python
    # src/modern_kata_kupas/separator.py
    def _strip_suffixes(self, word: str) -> tuple[str, list[str]]:
        # --- BEGIN TEMPORARY SUFFIX DEBUG PRINT ---
        IS_TARGET_WORD_FOR_SUFFIX_DEBUG = (word == "kesekolah") 

        if IS_TARGET_WORD_FOR_SUFFIX_DEBUG:
            print(f"\n[SUFFIX_DEBUG] --- Entering _strip_suffixes with input word: '{word}' ---")
        # --- END TEMPORARY SUFFIX DEBUG PRINT ---

        current_word = str(word)
        stripped_suffixes_in_stripping_order = []

        suffix_types = [
            ['kah', 'lah', 'pun'], 
            ['ku', 'mu', 'nya'],   
            ['kan', 'i', 'an']     
        ]

        something_stripped = True
        iteration_count = 0
        while something_stripped:
            iteration_count += 1
            if IS_TARGET_WORD_FOR_SUFFIX_DEBUG:
                print(f"[SUFFIX_DEBUG] Iteration {iteration_count}, current_word before stripping: '{current_word}'")

            something_stripped = False
            for idx, suffixes_list in enumerate(suffix_types):
                if IS_TARGET_WORD_FOR_SUFFIX_DEBUG:
                    print(f"[SUFFIX_DEBUG]  Trying suffix type index {idx}: {suffixes_list}")
                for sfx in suffixes_list:
                    if IS_TARGET_WORD_FOR_SUFFIX_DEBUG:
                        print(f"[SUFFIX_DEBUG]   Checking suffix: '{sfx}' against '{current_word}' (original input: '{word}')")
                    if current_word.endswith(sfx):
                        if IS_TARGET_WORD_FOR_SUFFIX_DEBUG:
                            print(f"[SUFFIX_DEBUG]    MATCH FOUND: '{current_word}' ends with '{sfx}'")
                        
                        min_len_check_passed = True 
                        temp_remainder = current_word[:-len(sfx)]

                        if sfx in suffix_types[0]: 
                            if len(temp_remainder) < self.MIN_STEM_LENGTH_FOR_PARTICLE:
                                min_len_check_passed = False
                                if IS_TARGET_WORD_FOR_SUFFIX_DEBUG: print(f"[SUFFIX_DEBUG]     Particle '{sfx}' min_len check FAILED. Remainder '{temp_remainder}', MinLen: {self.MIN_STEM_LENGTH_FOR_PARTICLE}")
                        elif sfx in suffix_types[1]: 
                            if len(temp_remainder) < self.MIN_STEM_LENGTH_FOR_POSSESSIVE:
                                min_len_check_passed = False
                                if IS_TARGET_WORD_FOR_SUFFIX_DEBUG: print(f"[SUFFIX_DEBUG]     Possessive '{sfx}' min_len check FAILED. Remainder '{temp_remainder}', MinLen: {self.MIN_STEM_LENGTH_FOR_POSSESSIVE}")
                        elif sfx in suffix_types[2]: 
                            if len(temp_remainder) < self.MIN_STEM_LENGTH_FOR_DERIVATIONAL_SUFFIX_STRIPPING:
                                min_len_check_passed = False
                                if IS_TARGET_WORD_FOR_SUFFIX_DEBUG: print(f"[SUFFIX_DEBUG]     Derivational '{sfx}' min_len check FAILED. Remainder '{temp_remainder}', MinLen: {self.MIN_STEM_LENGTH_FOR_DERIVATIONAL_SUFFIX_STRIPPING}")
                        
                        if not min_len_check_passed:
                            if IS_TARGET_WORD_FOR_SUFFIX_DEBUG: print(f"[SUFFIX_DEBUG]    Suffix '{sfx}' min_len overall check FAILED, continuing.")
                            continue

                        current_word = temp_remainder
                        stripped_suffixes_in_stripping_order.append(sfx)
                        something_stripped = True
                        if IS_TARGET_WORD_FOR_SUFFIX_DEBUG:
                            print(f"[SUFFIX_DEBUG]    STRIPPED '{sfx}'. current_word is now: '{current_word}'. Stripped list: {stripped_suffixes_in_stripping_order}")
                        break 
                if something_stripped:
                    if IS_TARGET_WORD_FOR_SUFFIX_DEBUG: print(f"[SUFFIX_DEBUG]  Suffix found in type index {idx}, breaking from suffix_types loop to restart while loop.")
                    break 
        
        if IS_TARGET_WORD_FOR_SUFFIX_DEBUG:
            print(f"[SUFFIX_DEBUG] --- Exiting _strip_suffixes. Final current_word: '{current_word}', Final stripped (reversed): {list(reversed(stripped_suffixes_in_stripping_order))} for original input: '{word}' ---")
        
        return current_word, list(reversed(stripped_suffixes_in_stripping_order))
    ```

Saya akan menjalankan `pytest` lagi dengan perintah `pytest tests/test_separator.py -k "test_strip_basic_prefixes or test_strip_combined_affixes" -s` dan melaporkan hasilnya, terutama output dari `[STEMMER_CHECK]` dan `[SUFFIX_DEBUG]`. Ini akan membantu kita memahami perilaku stemmer dan proses pelepasan akhiran untuk kasus-kasus yang bermasalah.

---
```
PS C:\Users\neima\Documents\modern_kata_kupas> pytest tests/test_separator.py -k "test_strip_basic_prefixes or test_strip_combined_affixes" -s
============================= test session starts ==============================
platform win32 -- Python 3.9.0, pytest-8.3.5, pluggy-1.6.0
rootdir: C:\Users\neima\Documents\modern_kata_kupas
configfile: pyproject.toml
plugins: mock-3.14.0
collected 56 items / 52 deselected / 4 selected

tests\test_separator.py::test_strip_basic_prefixes
[STEMMER_CHECK] Input to _strip_prefixes: 'ketua'
[STEMMER_CHECK] Output of self.stemmer.get_root_word('ketua'): 'ketua'      
PASSED tests\test_separator.py::test_strip_derivational_suffixes PASSED
tests\test_separator.py::test_strip_combined_affixes
[STEMMER_CHECK] Input to _strip_prefixes: 'kesekolah'
[STEMMER_CHECK] Output of self.stemmer.get_root_word('kesekolah'): 'sekolah'

[SUFFIX_DEBUG] --- Entering _strip_suffixes with input word: 'kesekolah' ---
[SUFFIX_DEBUG] Iteration 1, current_word before stripping: 'kesekolah'      
[SUFFIX_DEBUG]  Trying suffix type index 0: ['kah', 'lah', 'pun']
[SUFFIX_DEBUG]   Checking suffix: 'kah' against 'kesekolah' (original input: 'kesekolah')
[SUFFIX_DEBUG]   Checking suffix: 'lah' against 'kesekolah' (original input: 'kesekolah')
[SUFFIX_DEBUG]   Checking suffix: 'pun' against 'kesekolah' (original input: 'kesekolah')
[SUFFIX_DEBUG]  Trying suffix type index 1: ['ku', 'mu', 'nya']
[SUFFIX_DEBUG]   Checking suffix: 'ku' against 'kesekolah' (original input: 'kesekolah')
[SUFFIX_DEBUG]   Checking suffix: 'mu' against 'kesekolah' (original input: 'kesekolah')
[SUFFIX_DEBUG]   Checking suffix: 'nya' against 'kesekolah' (original input: 'kesekolah')
[SUFFIX_DEBUG]  Trying suffix type index 2: ['kan', 'i', 'an']
[SUFFIX_DEBUG]   Checking suffix: 'kan' against 'kesekolah' (original input: 'kesekolah')
[SUFFIX_DEBUG]   Checking suffix: 'i' against 'kesekolah' (original input: 'kesekolah')
[SUFFIX_DEBUG]   Checking suffix: 'an' against 'kesekolah' (original input: 'kesekolah')
[SUFFIX_DEBUG] --- Exiting _strip_suffixes. Final current_word: 'kesekolah', Final stripped (reversed): [] for original input: 'kesekolah' ---

[SUFFIX_DEBUG] --- Entering _strip_suffixes with input word: 'kesekolah' ---
[SUFFIX_DEBUG] Iteration 1, current_word before stripping: 'kesekolah'      
[SUFFIX_DEBUG]  Trying suffix type index 0: ['kah', 'lah', 'pun']
[SUFFIX_DEBUG]   Checking suffix: 'kah' against 'kesekolah' (original input: 'kesekolah')
[SUFFIX_DEBUG]   Checking suffix: 'lah' against 'kesekolah' (original input: 'kesekolah')
[SUFFIX_DEBUG]   Checking suffix: 'pun' against 'kesekolah' (original input: 'kesekolah')
[SUFFIX_DEBUG]  Trying suffix type index 1: ['ku', 'mu', 'nya']
[SUFFIX_DEBUG]   Checking suffix: 'ku' against 'kesekolah' (original input: 'kesekolah')
[SUFFIX_DEBUG]   Checking suffix: 'mu' against 'kesekolah' (original input: 'kesekolah')
[SUFFIX_DEBUG]   Checking suffix: 'nya' against 'kesekolah' (original input: 'kesekolah')
[SUFFIX_DEBUG]  Trying suffix type index 2: ['kan', 'i', 'an']
[SUFFIX_DEBUG]   Checking suffix: 'kan' against 'kesekolah' (original input: 'kesekolah')
[SUFFIX_DEBUG]   Checking suffix: 'i' against 'kesekolah' (original input: 'kesekolah')
[SUFFIX_DEBUG]   Checking suffix: 'an' against 'kesekolah' (original input: 'kesekolah')
[SUFFIX_DEBUG] --- Exiting _strip_suffixes. Final current_word: 'kesekolah', Final stripped (reversed): [] for original input: 'kesekolah' ---
[STEMMER_CHECK] Input to _strip_prefixes: 'kesekolah'
[STEMMER_CHECK] Output of self.stemmer.get_root_word('kesekolah'): 'sekolah'
PASSED

============================== 2 passed, 2 deselected in 0.12s ===============================
PS C:\Users\neima\Documents\modern_kata_kupas>
```