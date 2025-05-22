# src/modern_kata_kupas/separator.py
"""
Modul untuk memisahkan kata berimbuhan menjadi kata dasar dan afiksnya.
"""
import re

from .normalizer import TextNormalizer
from .dictionary_manager import DictionaryManager
from .rules import MorphologicalRules
from .stemmer_interface import IndonesianStemmer
from .utils.alignment import align

MIN_STEM_LENGTH_FOR_POSSESSIVE = 3 # Panjang minimal kata dasar untuk pemisahan sufiks posesif

class ModernKataKupas:
    """
    Kelas utama untuk proses pemisahan kata berimbuhan.
    """
    MIN_STEM_LENGTH_FOR_POSSESSIVE = 3 # Define minimum stem length for possessive stripping
    MIN_STEM_LENGTH_FOR_DERIVATIONAL_SUFFIX_STRIPPING = 4 # Define minimum stem length for derivational suffix stripping
    MIN_STEM_LENGTH_FOR_PARTICLE = 3 # Define minimum stem length for particle stripping
    def __init__(self, dictionary_path: str = None, rules_file_path: str = None):
        """
Inisialisasi ModernKataKupas dengan dependensi yang diperlukan.

        Args:
            dictionary_path (str, optional): Path ke file kamus khusus.
                                            Jika None, kamus default akan dimuat.
            rules_file_path (str, optional): Path ke file aturan khusus.
                                           Jika None, file aturan default akan dimuat.
        """
        import importlib
        
        # Constants for default rules file location
        DEFAULT_DATA_PACKAGE_PATH = 'src.modern_kata_kupas.data' # Corrected path
        DEFAULT_RULES_FILENAME = 'affix_rules.json'
        
        self.normalizer = TextNormalizer()
        self.dictionary = DictionaryManager(dictionary_path=dictionary_path)
        self.stemmer = IndonesianStemmer()
        self.aligner = align

        if rules_file_path:
            self.rules = MorphologicalRules(rules_path=rules_file_path)
        else:
            try:
                with importlib.resources.path(DEFAULT_DATA_PACKAGE_PATH, DEFAULT_RULES_FILENAME) as default_rules_path:
                    self.rules = MorphologicalRules(rules_path=str(default_rules_path))
            except (FileNotFoundError, TypeError, ModuleNotFoundError) as e: # TODO: Add logging here
                base_dir = os.path.dirname(os.path.abspath(__file__))
                default_rules_path_rel = os.path.join(base_dir, "data", DEFAULT_RULES_FILENAME)
                if os.path.exists(default_rules_path_rel):
                    self.rules = MorphologicalRules(rules_path=default_rules_path_rel)
                else: # TODO: Add logging here
                    self.rules = MorphologicalRules()

    def segment(self, word: str) -> str:
        """
        Memisahkan kata berimbuhan menjadi kata dasar dan afiksnya,
        termasuk menangani reduplikasi.
        """
        # 1. Normalisasi kata
        normalized_word = self.normalizer.normalize_word(word)
        if not normalized_word: # Handle empty string after normalization
            return ""

        # 2. Jika kata sudah merupakan kata dasar, langsung kembalikan
        if self.dictionary.is_kata_dasar(normalized_word):
            return normalized_word

        # 3. Handle Reduplication
        #    word_to_process is the base part (e.g., "mobil" from "mobil-mobilan", "main" from "bermain-main")
        #    direct_redup_suffixes are those like "-an" in "X-Xan" (e.g. "mobil-mobilan" -> direct_redup_suffixes = ["an"])
        word_to_process, redup_marker, direct_redup_suffixes = self._handle_reduplication(normalized_word)
        if word == "bermain-main": # DEBUG for bermain-main specifically
            print(f"DEBUG: segment({word}): after _handle_reduplication: word_to_process='{word_to_process}', redup_marker='{redup_marker}'")
        initial_suffixes = [] # Initialize initial_suffixes, its role is re-evaluated

        # 4. Affix Stripping Strategies on word_to_process
        # Strategy 1: Prefixes then Suffixes on word_to_process
        print(f"DEBUG: S1 calling _strip_prefixes with word_to_process: '{word_to_process}' (orig_word='{word}')")
        stem_after_prefixes_s1, prefixes_s1 = self._strip_prefixes(word_to_process)
        final_stem_s1, suffixes_s1_from_base = self._strip_suffixes(stem_after_prefixes_s1)
        is_s1_valid_root = self.dictionary.is_kata_dasar(final_stem_s1)
        print(f"DEBUG: segment({word}): S1 result: final_stem='{final_stem_s1}', prefixes={prefixes_s1}, suffixes={suffixes_s1_from_base}, is_valid={is_s1_valid_root}")

        # Strategy 2: Suffixes then Prefixes on word_to_process
        stem_after_suffixes_s2, suffixes_s2_from_base = self._strip_suffixes(word_to_process)
        print(f"DEBUG: S2 calling _strip_prefixes with stem_after_suffixes_s2: '{stem_after_suffixes_s2}' (orig_word='{word}')")
        final_stem_s2, prefixes_s2 = self._strip_prefixes(stem_after_suffixes_s2)
        is_s2_valid_root = self.dictionary.is_kata_dasar(final_stem_s2)
        print(f"DEBUG: segment({word}): S2 result: final_stem='{final_stem_s2}', prefixes={prefixes_s2}, suffixes={suffixes_s2_from_base}, is_valid={is_s2_valid_root}")
        
        # 6. Determine Best Result from strategies
        chosen_final_stem = None
        chosen_prefixes = []
        chosen_main_suffixes = [] # These are suffixes stripped from word_to_process

        if is_s1_valid_root and is_s2_valid_root:
            if len(final_stem_s1) >= len(final_stem_s2):
                chosen_final_stem = final_stem_s1
                chosen_prefixes = prefixes_s1
                chosen_main_suffixes = suffixes_s1_from_base
            else:
                chosen_final_stem = final_stem_s2
                chosen_prefixes = prefixes_s2
                chosen_main_suffixes = suffixes_s2_from_base
        elif is_s1_valid_root:
            chosen_final_stem = final_stem_s1
            chosen_prefixes = prefixes_s1
            chosen_main_suffixes = suffixes_s1_from_base
        elif is_s2_valid_root:
            chosen_final_stem = final_stem_s2
            chosen_prefixes = prefixes_s2
            chosen_main_suffixes = suffixes_s2_from_base
        else:
            # If neither strategy yielded a valid root for word_to_process,
            # consider word_to_process itself as the stem for this part.
            # This is important if word_to_process is already a base word (e.g. "main" from "bermain-main")
            # or if it's an unanalyzable stem after reduplication handling.
            if self.dictionary.is_kata_dasar(word_to_process):
                 chosen_final_stem = word_to_process
            # If word_to_process is NOT a KD, and no strategy worked, then it's possible
            # that the original word was not correctly segmented or is an unknown base.
            # In this scenario, if redup_marker is present, we might still want to show it.
            # If no redup_marker, and no initial_suffixes, then likely it's just normalized_word.
            else: # word_to_process is not a KD, and strategies failed
                chosen_final_stem = word_to_process # Fallback to word_to_process
                                                # Prefixes/suffixes remain empty for this part.
        
        # If after all this, chosen_final_stem is still None (e.g. if word_to_process was empty, though unlikely here)
        # or if chosen_final_stem is not a KD and no affixes found at all, we might revert.
        # However, the logic above ensures chosen_final_stem is at least word_to_process.
        
        # Debug prints for chosen components
        print(f"DEBUG: segment({word}): Chosen final_stem: '{chosen_final_stem}'")
        print(f"DEBUG: segment({word}): Chosen prefixes: {chosen_prefixes}")
        print(f"DEBUG: segment({word}): Chosen main_suffixes: {chosen_main_suffixes}")
        print(f"DEBUG: segment({word}): Redup_marker: '{redup_marker}'")
        print(f"DEBUG: segment({word}): Direct_redup_suffixes: {direct_redup_suffixes}")
        print(f"DEBUG: segment({word}): Initial_suffixes: {initial_suffixes}")

        # 7. Assemble Final Result
        # Suffixes are assembled in a specific order:
        # main_suffixes (from S1/S2 on word_to_process) -> direct_redup_suffixes -> initial_suffixes (if any, from original word)
        
        final_parts = []
        if chosen_prefixes:
            final_parts.extend(chosen_prefixes)
        
        final_parts.append(chosen_final_stem)
        
        if redup_marker: # "ulg"
            final_parts.append(redup_marker)
        
        # Assemble suffixes in order: main_suffixes, then direct_redup_suffixes, then initial_suffixes
        assembled_suffixes = []
        if chosen_main_suffixes:
            assembled_suffixes.extend(chosen_main_suffixes)
        if direct_redup_suffixes:
            assembled_suffixes.extend(direct_redup_suffixes)
        if initial_suffixes: # Suffixes from initial strip (e.g. -lah) - currently, this will be empty
            assembled_suffixes.extend(initial_suffixes)
        
        if assembled_suffixes:
             final_parts.extend(assembled_suffixes)
        
        print(f"DEBUG: segment({word}): final_parts before join: {final_parts}")
            
        valid_parts = [part for part in final_parts if part] 
        result_str = '~'.join(valid_parts)
        print(f"DEBUG: segment({word}): result_str: '{result_str}'")

        # 8. Return Logic
        # Condition 1: No effective segmentation occurred
        is_effectively_unchanged = (not chosen_prefixes and 
                                    not redup_marker and 
                                    not assembled_suffixes and # Check assembled_suffixes instead of individual lists
                                    chosen_final_stem == normalized_word)

        if not result_str: 
            print(f"DEBUG: segment({word}): Returning (empty result_str) normalized_word: '{normalized_word}'")
            return normalized_word
            
        if is_effectively_unchanged:
            print(f"DEBUG: segment({word}): Returning (is_effectively_unchanged) normalized_word: '{normalized_word}'")
            return normalized_word

        # If the result string is identical to normalized_word, but the word is NOT a KD, 
        # it implies no segmentation was found or was truly effective.
        if result_str == normalized_word and not self.dictionary.is_kata_dasar(normalized_word):
             print(f"DEBUG: segment({word}): Returning (result_str == normalized_word and not KD) normalized_word: '{normalized_word}'")
             return normalized_word
        
        # Additional check: if the process resulted in a stem that is not a KD, and no affixes were found,
        # then it's likely an unsegmentable word.
        if not self.dictionary.is_kata_dasar(chosen_final_stem) and not chosen_prefixes and not assembled_suffixes and not redup_marker:
            print(f"DEBUG: segment({word}): Returning (final_stem not KD and no affixes/redup) normalized_word: '{normalized_word}'")
            return normalized_word

        print(f"DEBUG: segment({word}): Returning final result_str: '{result_str}'")
        return result_str

    def _handle_reduplication(self, word: str) -> tuple[str, str, list[str]]:
        """
        Handles full reduplication (Dwilingga) like X-X or X-Xsuffix.

        Args:
            word (str): The word to check for reduplication.

        Returns:
            tuple[str, str, list[str]]: 
                - base_form_for_stripping: The base part (X) for further affix stripping.
                - reduplication_marker: "ulg" if full reduplication is detected, "" otherwise.
                - direct_redup_suffixes: List of suffixes directly attached to reduplication 
                                         (e.g., ["an"] for "mobil-mobilan"). Empty if none.
        """
        # Check for X-Xsuffix (e.g., mobil-mobilan, buku-bukunya)
        # Suffixes considered: an, nya.
        match_with_suffix = re.match(r"^([^-]+)-\1(an|nya)$", word)
        if match_with_suffix:
            base_form = match_with_suffix.group(1)
            suffix = match_with_suffix.group(2)
            # Validate that the base_form is not empty or just a hyphen (though regex should prevent this)
            if base_form and base_form != '-':
                return base_form, "ulg", [suffix]

        # Check for X-X (e.g., rumah-rumah, bermain-main)
        match_simple = re.match(r"^([^-]+)-\1$", word)
        if match_simple:
            base_form = match_simple.group(1)
            # Validate that the base_form is not empty or just a hyphen
            if base_form and base_form != '-':
                return base_form, "ulg", []

        # No reduplication pattern matched
        return word, "", []


    def _strip_suffixes(self, word: str) -> tuple[str, list[str]]:
        current_word = str(word)
        stripped_suffixes_in_stripping_order = []
        
        # Urutan prioritas pelepasan sufiks (dari luar ke dalam)
        # 1. Partikel: -lah, -kah, -pun
        # 2. Posesif: -ku, -mu, -nya
        # 3. Derivasional: -kan, -i, -an
        suffix_types = [
            ["lah", "kah", "pun"],  # Partikel
            ["ku", "mu", "nya"],    # Posesif
            ["kan", "i", "an"]      # Derivasional
        ]
        
        # Iteratively strip suffixes until no more known suffixes are found
        something_stripped = True
        while something_stripped:
            something_stripped = False
            # Try stripping each type of suffix in order
            for suffixes_list in suffix_types:
                # Check for each suffix within the current type list
                for sfx in suffixes_list:
                    if current_word.endswith(sfx):
                        stem_candidate = current_word[:-len(sfx)]
                        
                        # Validasi panjang stem minimal
                        if len(stem_candidate) < 2:
                            continue
                            
                        # Untuk sufiks derivatif, cek panjang minimal
                        if sfx in suffix_types[2] and len(stem_candidate) < self.MIN_STEM_LENGTH_FOR_DERIVATIONAL_SUFFIX_STRIPPING:
                            continue
                            
                        # Untuk sufiks posesif, cek panjang minimal
                        if sfx in suffix_types[1] and len(stem_candidate) < self.MIN_STEM_LENGTH_FOR_POSSESSIVE:
                            continue
                            
                        # Untuk sufiks partikel, cek panjang minimal
                        if sfx in suffix_types[0] and len(stem_candidate) < self.MIN_STEM_LENGTH_FOR_PARTICLE:
                            continue
                        
                        # Kasus khusus untuk kata seperti "sekolah" yang bukan "se~kolah"
                        if sfx == "lah" and current_word == "sekolah" and stem_candidate == "seko":
                            continue

                        # Conservative check: If the current word is not a KD, only strip if the resulting stem is a KD.
                        # Or, if the current word IS a KD, then stripping is generally safer (e.g. "makanan" -> "makan")
                        # This helps prevent "katadenganspas~i" from "katadenganspasi"
                        if not self.dictionary.is_kata_dasar(current_word) and \
                           not self.dictionary.is_kata_dasar(stem_candidate) and \
                           sfx in suffix_types[2]: # Be extra careful with derivational suffixes
                            continue
                        
                        # Tambahkan sufiks ke daftar dan perbarui kata saat ini
                        current_word = stem_candidate
                        stripped_suffixes_in_stripping_order.append(sfx)
                        something_stripped = True
                        # Restart the stripping process from the outermost suffix type
                        break 
                if something_stripped:
                    break 
        
        return current_word, list(reversed(stripped_suffixes_in_stripping_order))

    def _is_monosyllabic(self, word: str) -> bool:
        """
        Helper sederhana untuk mengecek apakah sebuah kata (calon akar) monosilabik.
        Ini adalah placeholder, Anda mungkin memerlukan logika yang lebih baik
        atau daftar kata dasar monosilabik.
        """
        if not word:
            return False
        # Logika deteksi suku kata bisa kompleks. Untuk awal:
        # Anggap saja jika pendek dan ada di kamus, atau jika hanya punya satu vokal.
        # Ini perlu disempurnakan. Contoh: 'bom', 'cat', 'las'.
        vowels = "aiueo"
        vowel_count = sum(1 for char in word if char in vowels)
        # Kasar: jika jumlah vokal = 1 dan ada di kamus ATAU sangat pendek
        if vowel_count == 1 and (len(word) <= 3 or self.dictionary.is_kata_dasar(word)):
            return True
        # Ini hanya contoh kasar, perlu analisis lebih lanjut atau daftar kata monosilabik.
        # Untuk kasus seperti "tes", "kon" (dari "rekonstruksi"), "bor"
        # Mungkin lebih baik jika aturan "menge-" hanya berlaku jika sisanya adalah kata dasar yang diketahui monosilabik.
        if self.dictionary.is_kata_dasar(word):
            # Jika kata ada di kamus, baru cek suku katanya (logika bisa rumit)
            # Untuk sekarang, kita asumsikan jika kata ada di kamus dan jumlah vokal=1, itu monosilabik.
             return vowel_count == 1
        return False # Default

    def _strip_prefixes(self, original_word_for_prefix_stripping: str) -> tuple[str, list[str]]:
        current_word = str(original_word_for_prefix_stripping)
        all_stripped_prefixes = [] # Accumulates all stripped prefixes in order
        
        prefix_rules_all = self.rules.get_prefix_rules()

        while True: # Outer loop to handle multiple layers of prefixes
            successfully_stripped_one_prefix_this_iteration = False
            
            # Inner loop: Iterate through all prefix rules for the current_word
            for rule_group in prefix_rules_all:
                canonical_prefix = rule_group.get("canonical")
                
                potential_root_after_this_rule = None # Reset for this rule_group
                
                if "allomorphs" in rule_group:
                    first_non_kd_allomorph_root = None # Store the first non-KD root from this group
                    # potential_root_after_this_rule is already None from outside the allomorph loop
                    for allomorph_rule in rule_group["allomorphs"]:
                        surface_form = allomorph_rule.get("surface")

                        if current_word.startswith(surface_form):
                            remainder = current_word[len(surface_form):]
                            if not remainder:
                                continue

                            elision_for_this_rule = allomorph_rule.get("elision")
                            applicable_allomorph = True
                            if not elision_for_this_rule:
                                next_char_conditions = allomorph_rule.get("next_char_is")
                                if next_char_conditions:
                                    if not any(remainder.startswith(c) for c in next_char_conditions):
                                        applicable_allomorph = False
                            
                            if not applicable_allomorph:
                                continue

                            if allomorph_rule.get("is_monosyllabic_root"):
                                if not self.dictionary.is_kata_dasar(remainder) or \
                                   not self._is_monosyllabic(remainder):
                                    continue
                            
                            temp_potential_root = None
                            reconstruct_dict = allomorph_rule.get("reconstruct_root_initial")
                            if elision_for_this_rule:
                                if reconstruct_dict:
                                    key_to_prepend = list(reconstruct_dict.keys())[0]
                                    temp_potential_root = key_to_prepend + remainder
                                else:
                                    temp_potential_root = remainder
                            else:
                                temp_potential_root = remainder
                            
                            # DEBUG PRINT for ber- and per-
                            if canonical_prefix in ["ber", "per"] and surface_form == canonical_prefix : # Default allomorph
                                print(f"DEBUG _strip_prefixes: current_word='{current_word}', rule_group='{canonical_prefix}', allomorph_surface='{surface_form}', remainder='{remainder}', temp_potential_root='{temp_potential_root}', is_kd(temp_potential_root)={self.dictionary.is_kata_dasar(temp_potential_root if temp_potential_root else '')}")

                            if temp_potential_root is not None:
                                if self.dictionary.is_kata_dasar(temp_potential_root):
                                    potential_root_after_this_rule = temp_potential_root
                                    # DEBUG PRINT
                                    print(f"DEBUG _strip_prefixes: KD found for '{canonical_prefix}' allomorph '{surface_form}'. Root: '{temp_potential_root}'. Breaking allomorph loop.")
                                    break # Found KD, this is the one for this rule_group. Exit allomorph loop.
                                if first_non_kd_allomorph_root is None: # Capture the first non-KD result
                                    first_non_kd_allomorph_root = temp_potential_root
                    
                    if potential_root_after_this_rule is None: # No KD was found from any allomorph
                        potential_root_after_this_rule = first_non_kd_allomorph_root # Use the first non-KD attempt
                    # DEBUG PRINT
                    if canonical_prefix in ["ber", "per"]:
                        print(f"DEBUG _strip_prefixes: After allomorph loop for '{canonical_prefix}'. potential_root_after_this_rule='{potential_root_after_this_rule}'")


                else:  # Simple prefixes
                    simple_prefix_form = rule_group.get("form")
                    if simple_prefix_form and current_word.startswith(simple_prefix_form):
                        potential_remainder = current_word[len(simple_prefix_form):]
                        if potential_remainder:
                            potential_root_after_this_rule = potential_remainder
                
                # If a prefix (complex or simple) was successfully processed for this rule_group
                if potential_root_after_this_rule:
                    all_stripped_prefixes.append(canonical_prefix)
                    current_word = potential_root_after_this_rule
                    successfully_stripped_one_prefix_this_iteration = True
                    # DEBUG PRINT
                    if canonical_prefix in ["ber", "per"]:
                         print(f"DEBUG _strip_prefixes: Rule group '{canonical_prefix}' processed. current_word='{current_word}', all_stripped_prefixes={all_stripped_prefixes}")

                    # If the new current_word is a KD, this is a valid segmentation point.
                    # _strip_prefixes will return this as the result for this path.
                    if self.dictionary.is_kata_dasar(current_word):
                        # DEBUG PRINT
                        if canonical_prefix in ["ber", "per"]:
                            print(f"DEBUG _strip_prefixes: Early KD exit. current_word='{current_word}', all_stripped_prefixes={all_stripped_prefixes}")
                        return current_word, all_stripped_prefixes # Exit early
                    
                    # Break from the rule_group loop to restart the while loop for further stripping on new current_word
                    break 
            
            # If a full pass through all prefix rules did not strip any prefix
            if not successfully_stripped_one_prefix_this_iteration:
                # DEBUG PRINT
                if original_word_for_prefix_stripping in ["perbuat", "perjuangan", "bermain"]:
                    print(f"DEBUG _strip_prefixes: No prefix stripped in full pass for '{original_word_for_prefix_stripping}'. current_word='{current_word}'")
                break # Break from the outer while True loop (no more layers of prefixes)
        
        # DEBUG PRINT
        if original_word_for_prefix_stripping in ["perbuat", "perjuangan", "bermain"]:
            print(f"DEBUG _strip_prefixes: Final return for '{original_word_for_prefix_stripping}'. current_word='{current_word}', all_stripped_prefixes={all_stripped_prefixes}")
        return current_word, all_stripped_prefixes

    def _apply_morphophonemic_segmentation_rules(self, word: str) -> str:
        """
        Helper method to apply morphophonemic segmentation rules (stub).
        """
        pass # Stub implementation

# Example usage (can be removed or commented out later)
if __name__ == '__main__':
    # Example usage will require initializing dependencies
    # For now, just demonstrate instantiation
    try:
        mkk = ModernKataKupas()
        print("ModernKataKupas class instantiated successfully.")
        # print(f"Segmenting 'makanan': {mkk.segment('makanan')}") # This will work with the current stub
    except Exception as e:
        print(f"Error instantiating ModernKataKupas: {e}")