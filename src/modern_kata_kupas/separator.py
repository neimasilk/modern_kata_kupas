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
        DEFAULT_DATA_PACKAGE_PATH = 'modern_kata_kupas.data'
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

        # 3. Initial Suffix Stripping (primarily for particles like -lah, -kah, -pun
        #    that might be outside the core reduplication pattern or main derivational affixes)
        word_after_initial_suffixes, initial_suffixes = self._strip_suffixes(normalized_word)
        
        # 4. Handle Reduplication
        #    word_to_process is the base part (e.g., "mobil" from "mobil-mobilan", "main" from "bermain-main")
        #    direct_redup_suffixes are those like "-an" in "X-Xan" (e.g. "mobil-mobilan" -> direct_redup_suffixes = ["an"])
        word_to_process, redup_marker, direct_redup_suffixes = self._handle_reduplication(word_after_initial_suffixes)

        # 5. Affix Stripping Strategies on word_to_process
        # Strategy 1: Prefixes then Suffixes on word_to_process
        stem_after_prefixes_s1, prefixes_s1 = self._strip_prefixes(word_to_process)
        final_stem_s1, suffixes_s1_from_base = self._strip_suffixes(stem_after_prefixes_s1)
        is_s1_valid_root = self.dictionary.is_kata_dasar(final_stem_s1)

        # Strategy 2: Suffixes then Prefixes on word_to_process
        stem_after_suffixes_s2, suffixes_s2_from_base = self._strip_suffixes(word_to_process)
        final_stem_s2, prefixes_s2 = self._strip_prefixes(stem_after_suffixes_s2)
        is_s2_valid_root = self.dictionary.is_kata_dasar(final_stem_s2)
        
        # 6. Determine Best Result from strategies
        chosen_final_stem = None
        chosen_prefixes = []
        chosen_main_suffixes = [] # These are suffixes stripped from word_to_process

        if is_s1_valid_root:
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

        # 7. Assemble Final Result
        final_parts = []
        if chosen_prefixes:
            final_parts.extend(chosen_prefixes)
        
        final_parts.append(chosen_final_stem)
        
        if redup_marker: # "ulg"
            final_parts.append(redup_marker)
        if direct_redup_suffixes: # e.g. ["an"] from X-Xan
            final_parts.extend(direct_redup_suffixes)
        if chosen_main_suffixes: # Suffixes from stripping word_to_process
            final_parts.extend(chosen_main_suffixes)
        if initial_suffixes: # Suffixes from initial strip (e.g. -lah)
            final_parts.extend(initial_suffixes)
            
        # Filter out any None or empty strings that might have crept in, though unlikely with append/extend.
        # Ensure chosen_final_stem is not None before joining.
        # If chosen_final_stem ended up being an empty string (e.g. if word_to_process was empty and dictionary allows empty KD)
        # this could lead to "pref~~suffix". Filter empty strings before join.
        valid_parts = [part for part in final_parts if part] 
        result_str = '~'.join(valid_parts)

        # 8. Return Logic
        # Condition 1: No effective segmentation occurred (all parts are empty except the stem,
        # and the stem is the original normalized word). This also covers cases where original word is not in KD.
        is_effectively_unchanged = (not chosen_prefixes and 
                                    not redup_marker and 
                                    not direct_redup_suffixes and 
                                    not chosen_main_suffixes and 
                                    not initial_suffixes and
                                    chosen_final_stem == normalized_word)

        if not result_str: # Handles if valid_parts was empty for some reason
            return normalized_word
            
        if is_effectively_unchanged:
            # If it's unchanged AND it's not a known kata_dasar (already handled at the top),
            # it means it's an unsegmentable, unknown word. Return it as is.
            # If it IS a kata_dasar, it would have been returned at step 2.
            return normalized_word

        # If the result string is identical to normalized_word, but affixes *were* identified (e.g. "di~makan" for "dimakan")
        # then it's a valid segmentation. The is_effectively_unchanged handles the other case.
        # However, if result_str == normalized_word and the word is NOT a KD, it implies no segmentation found.
        if result_str == normalized_word and not self.dictionary.is_kata_dasar(normalized_word):
             return normalized_word

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
                        
                        # Tambahkan sufiks ke daftar dan perbarui kata saat ini
                        current_word = stem_candidate
                        stripped_suffixes_in_stripping_order.append(sfx)
                        something_stripped = True
                        # Restart the stripping process from the outermost suffix type
                        # This handles cases like 'rumahkupun' where 'pun' is stripped, then 'ku' can be stripped from 'rumahku'
                        break # Break inner loop (suffixes_list)
                if something_stripped:
                    break # Break outer loop (suffix_types) and restart while loop
        
        # `stripped_suffixes_in_stripping_order` contains suffixes in stripping order (outermost to innermost).
        # For test output expecting order like ['kan', 'lah'], we need to reverse it.
        return current_word, list(reversed(stripped_suffixes_in_stripping_order))

        # Kode di bawah ini sudah tidak digunakan lagi karena sudah digantikan dengan implementasi di atas
        # Tetap disimpan sebagai referensi untuk pengembangan lebih lanjut

        # Define suffix types and their order of stripping preference (outermost first)
        suffix_types = [
            ['kah', 'lah', 'pun'], # Particles
            ['ku', 'mu', 'nya'],   # Possessives
            ['kan', 'i', 'an']     # Derivational
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
                        # Check minimum stem length for possessive and derivational
                        if (sfx in suffix_types[1] and len(current_word[:-len(sfx)]) < self.MIN_STEM_LENGTH_FOR_POSSESSIVE) or \
                           (sfx in suffix_types[2] and len(current_word[:-len(sfx)]) < self.MIN_STEM_LENGTH_FOR_DERIVATIONAL_SUFFIX_STRIPPING):
                            continue # Skip stripping if minimum stem length is not met

                        current_word = current_word[:-len(sfx)]
                        stripped_suffixes_in_stripping_order.append(sfx)
                        something_stripped = True
                        # Restart the stripping process from the outermost suffix type
                        # This handles cases like 'rumahkupun' where 'pun' is stripped, then 'ku' can be stripped from 'rumahku'
                        break # Break inner loop (suffixes_list)
                if something_stripped:
                    break # Break outer loop (suffix_types) and restart while loop

        # `stripped_suffixes_in_stripping_order` contains suffixes in stripping order (outermost to innermost).
        # For test output expecting order like ['kan', 'lah'], we need to reverse it.
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
                
                potential_root_after_this_rule = None # Stores the root if this rule_group matches
                
                if "allomorphs" in rule_group:  # Handles any complex prefix (meN, peN, ber, ter, per, etc.)
                    for allomorph_rule in rule_group["allomorphs"]:
                        surface_form = allomorph_rule.get("surface")

                        if current_word.startswith(surface_form):
                            remainder = current_word[len(surface_form):]
                            if not remainder: # Cannot be a valid root if empty
                                continue

                            # --- Allomorph Applicability Checks ---
                            next_char_conditions = allomorph_rule.get("next_char_is")
                            if next_char_conditions:
                                applicable_by_next_char = False
                                for cond_char in next_char_conditions:
                                    if remainder.startswith(cond_char):
                                        applicable_by_next_char = True
                                        break
                                if not applicable_by_next_char:
                                    continue

                            if allomorph_rule.get("is_monosyllabic_root"):
                                if not self.dictionary.is_kata_dasar(remainder) or \
                                   not self._is_monosyllabic(remainder):
                                    continue
                            # --- End of Applicability Checks ---

                            # Determine potential_root based on elision and reconstruction rules
                            temp_potential_root = None
                            if allomorph_rule.get("elision"):
                                reconstruct_rule = allomorph_rule.get("reconstruct_root_initial")
                                if reconstruct_rule:
                                    elided_char_key = list(reconstruct_rule.keys())[0]
                                    temp_reconstructed = elided_char_key + remainder
                                    if self.dictionary.is_kata_dasar(temp_reconstructed):
                                        temp_potential_root = temp_reconstructed
                                else: # Elision true, but no reconstruction rule (e.g., ber- -> bel-)
                                    if self.dictionary.is_kata_dasar(remainder):
                                        temp_potential_root = remainder
                            else: # No elision
                                if self.dictionary.is_kata_dasar(remainder):
                                    temp_potential_root = remainder
                            
                            if temp_potential_root:
                                potential_root_after_this_rule = temp_potential_root
                                break # Found a matching allomorph for this rule_group
                                
                else:  # Simple prefixes (e.g., "di-", "ke-", "se-", without allomorphs)
                    simple_prefix_form = rule_group.get("form")
                    if simple_prefix_form and current_word.startswith(simple_prefix_form):
                        potential_remainder = current_word[len(simple_prefix_form):]
                        if potential_remainder and self.dictionary.is_kata_dasar(potential_remainder):
                            potential_root_after_this_rule = potential_remainder
                
                # If a prefix (complex or simple) was successfully processed for this rule_group
                if potential_root_after_this_rule:
                    all_stripped_prefixes.append(canonical_prefix)
                    current_word = potential_root_after_this_rule
                    successfully_stripped_one_prefix_this_iteration = True
                    break # Break from the inner for rule_group loop to restart the while loop
            
            # If a full pass through all prefix rules did not strip any prefix
            if not successfully_stripped_one_prefix_this_iteration:
                break # Break from the outer while True loop
            
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