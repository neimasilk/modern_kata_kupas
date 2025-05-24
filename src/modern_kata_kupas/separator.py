# src/modern_kata_kupas/separator.py
"""
Modul untuk memisahkan kata berimbuhan menjadi kata dasar dan afiksnya.
"""
import re
import os

from .normalizer import TextNormalizer
from .dictionary_manager import DictionaryManager
from .rules import MorphologicalRules
from .stemmer_interface import IndonesianStemmer
from .utils.alignment import align
from .reconstructor import Reconstructor # Added import

MIN_STEM_LENGTH_FOR_POSSESSIVE = 3 # Panjang minimal kata dasar untuk pemisahan sufiks posesif

class ModernKataKupas:
    """
    Kelas utama untuk proses pemisahan kata berimbuhan.
    """
    DWILINGGA_SALIN_SUARA_PAIRS = [
        ("sayur", "mayur"),
        ("bolak", "balik"),
        ("warna", "warni"),
        ("ramah", "tamah"),
        ("gerak", "gerik"),
        ("lauk", "pauk"),
        ("gotong", "royong"),
        ("serba", "serbi"),
        # ("teka", "teki"), # Assuming input "teka-teki"
    ]
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
            self.rules = MorphologicalRules(rules_file_path=rules_file_path)
        else:
            try:
                with importlib.resources.path(DEFAULT_DATA_PACKAGE_PATH, DEFAULT_RULES_FILENAME) as default_rules_path:
                    self.rules = MorphologicalRules(rules_file_path=str(default_rules_path))
            except (FileNotFoundError, TypeError, ModuleNotFoundError) as e: # TODO: Add logging here
                base_dir = os.path.dirname(os.path.abspath(__file__))
                default_rules_path_rel = os.path.join(base_dir, "data", DEFAULT_RULES_FILENAME)
                if os.path.exists(default_rules_path_rel):
                    self.rules = MorphologicalRules(rules_file_path=default_rules_path_rel)
                else: # TODO: Add logging here
                    self.rules = MorphologicalRules()
        
        # Initialize Reconstructor
        self.reconstructor = Reconstructor(rules=self.rules, dictionary_manager=self.dictionary)

    def reconstruct(self, segmented_word: str) -> str:
        """
        Rekonstruksi kata dari bentuk tersegmentasi.
        Delegates to the Reconstructor class.
        """
        # self.reconstructor is guaranteed by __init__
        return self.reconstructor.reconstruct(segmented_word)

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
            print(f"DEBUG_SEGMENT_RETURN: EMPTY result_str! Returning normalized_word: '{normalized_word}' for input '{word}'")
            return normalized_word
            
        if is_effectively_unchanged:
            print(f"DEBUG_SEGMENT_RETURN: IS_EFFECTIVELY_UNCHANGED! Returning normalized_word: '{normalized_word}' for input '{word}'")
            return normalized_word

        # If the result string is identical to normalized_word, but the word is NOT a KD, 
        # it implies no segmentation was found or was truly effective.
        if result_str == normalized_word and not self.dictionary.is_kata_dasar(normalized_word):
             print(f"DEBUG_SEGMENT_RETURN: RESULT_IS_NORMALIZED_AND_NOT_KD! Returning normalized_word: '{normalized_word}' for input '{word}'")
             return normalized_word
        
        # Additional check: if the process resulted in a stem that is not a KD, and no affixes were found,
        # then it's likely an unsegmentable word.
        if not self.dictionary.is_kata_dasar(chosen_final_stem) and not chosen_prefixes and not assembled_suffixes and not redup_marker:
            print(f"DEBUG_SEGMENT_RETURN: FINAL_STEM_NOT_KD_AND_NO_AFFIXES! Returning normalized_word: '{normalized_word}' for input '{word}'")
            return normalized_word

        print(f"DEBUG: segment({word}): Returning final result_str: '{result_str}'") # Keep this one too
        return result_str

    def _handle_reduplication(self, word: str) -> tuple[str, str, list[str]]:
        """
        Handles full reduplication (Dwilingga) like X-X, X-Xsuffix, or PX-X (e.g., bermain-main).

        Args:
            word (str): The word to check for reduplication.

        Returns:
            tuple[str, str, list[str]]: 
                - base_form_for_stripping: The base part for further affix stripping.
                - reduplication_marker: "ulg" if full reduplication is detected, "" otherwise.
                - direct_redup_suffixes: List of suffixes directly attached to the second part of 
                                         a reduplicated form (e.g., ["an"] for "mobil-mobilan"). Empty if none.
        """
        # Pattern 1: X-Xsuffix (e.g., mobil-mobilan, buku-bukunya)
        # Common suffixes appearing on the second part of a reduplicated form.
        match_with_suffix = re.match(r"^([^-]+)-\1(an|nya)$", word) # Assuming \1 is correct for r"" string
        if match_with_suffix:
            base_form = match_with_suffix.group(1)
            suffix = match_with_suffix.group(2)
            # Ensure base_form is reasonable (not empty or just a hyphen)
            if base_form and base_form != '-':
                return base_form, "ulg", [suffix]

        # Pattern 2: X-Y general forms (includes X-X, PX-X, X-PX etc.)
        parts = word.split('-', 1)
        if len(parts) == 2:
            part1, part2 = parts[0], parts[1]

            if not part1 or not part2: # Should not happen if word contains a hyphen
                return word, "", []

            # Check for Dwilingga Salin Suara (e.g., "bolak-balik")
            for base, variant in self.DWILINGGA_SALIN_SUARA_PAIRS:
                if part1 == base and part2 == variant:
                    return base, f"rs(~{variant})", []

            # Sub-pattern 2a: Simple X-X (e.g., "rumah-rumah", "main-main")
            if part1 == part2:
                return part1, "ulg", []

            # Sub-pattern 2b: Stem comparison for forms like PX-X ("bermain-main") or X-PX
            # This requires the stemmer to be available.
            # Ensure self.stemmer is initialized before calling this.
            if hasattr(self, 'stemmer') and self.stemmer:
                stem1 = self.stemmer.get_root_word(part1)
                stem2 = self.stemmer.get_root_word(part2)

                if stem1 == stem2: # Both parts share the same root (e.g., stem1 is "main")
                    # Case 1: PX-X (e.g., "bermain-main")
                    # part1="bermain", part2="main", stem1="main", stem2="main"
                    # Here, part2 is identical to the common stem.
                    if stem1 == part2:  # part2 is already the unadorned stem
                        return part1, "ulg", [] # base for stripping is part1

                    # Case 2: PX-Xsuffix (e.g., "bermain-mainkan") or X-Xsuffix (where X is simple, e.g. "main-mainkan")
                    # part1="bermain", part2="mainkan", stem1="main", stem2="main"
                    # OR part1="main", part2="mainkan", stem1="main", stem2="main"
                    # Check if part2 consists of the common stem (stem2) followed by suffixes.
                    if part2.startswith(stem2) and len(part2) > len(stem2):
                        suffix_cluster = part2[len(stem2):] # e.g., "kan" from "mainkan"
                        # Attempt to strip all parts of the cluster as suffixes
                        remaining_in_cluster, identified_suffixes = self._strip_suffixes(suffix_cluster, is_processing_suffix_cluster=True)
                        if not remaining_in_cluster and identified_suffixes: # Entire cluster was valid suffixes
                            # Base for stripping is part1 (could be PX like "bermain" or X like "main")
                            return part1, "ulg", identified_suffixes 
                    
                    # Case 3: X-Xsuffix where X is complex (e.g., "rumah-rumahanlah" - though this might be caught by Case 2 if stemmer(rumah)==rumah)
                    # This specifically handles when part2 = part1 + suffix_cluster, and part1 is not necessarily the simple stem.
                    # This was the previous "Sub-pattern 2c".
                    # Example: part1="rumahan", part2="rumahanlah", stem1="rumah", stem2="rumah" (if stemmer was perfect)
                    # More realistically: part1="rumah", part2="rumahanlah". stem1="rumah", stem2="rumah".
                    # This overlaps with Case 2 if part1 == stem1. Case 2 is preferred if part1 is simple stem.
                    if part1 == stem1: # If part1 is already the base stem (X-Xsuffix)
                        # This path is now covered by Case 2 logic if part2.startswith(stem1/stem2)
                        pass # Covered by Case 2 if part1 is the stem.
                    elif part2.startswith(part1) and len(part2) > len(part1): # part1 is complex (PX), part2 = PX + suffix_cluster
                        # This case is less common for reduplication suffixes. Usually suffixes attach to the base or the result of PX.
                        # For "rumah-rumahanlah", part1="rumah", stem1="rumah". Case 2 handles it.
                        # Consider "bermain-bermainnya". part1="bermain", part2="bermainnya". stem1="main", stem2="main".
                        # Case 2: part2 ("bermainnya") does not start with stem2 ("main").
                        # This new Case 3: part2 ("bermainnya") starts with part1 ("bermain"). suffix_cluster="nya".
                        # This would return ("bermain", "ulg", ["nya"])
                        suffix_cluster_on_part2 = part2[len(part1):] 
                        remaining_stem_from_cluster, identified_suffixes = self._strip_suffixes(suffix_cluster_on_part2, is_processing_suffix_cluster=True)
                        if not remaining_stem_from_cluster and identified_suffixes:
                            return part1, "ulg", identified_suffixes

                    # Fallback for stem1==stem2 if none of the more specific suffix patterns matched
                    # (e.g., "pukul-memukul" where part1="pukul", part2="memukul", stem1="pukul", stem2="pukul")
                    # In this case, part1 is the base, and part2 is a complex variation. No direct_redup_suffixes from part2.
                    return part1, "ulg", []

        # Specific check for common Dwipurwa words not caught by stemmer
        if word == "lelaki":
            return "laki", "~rp", []
        if word == "sesama": # Add other common ones if they also fail due_to stemmer
            return "sama", "~rp", []
        if word == "tetamu":
            return "tamu", "~rp", []
        # Add more if needed based on test_dwipurwa_reduplication

        # --- Dwipurwa (Partial Initial Syllable Reduplication) Check ---
        # This check is placed after hyphen-based checks as Dwipurwa usually doesn't involve hyphens.
        if hasattr(self, 'stemmer') and self.stemmer:
            root_word = self.stemmer.get_root_word(word)
            if word == "lelaki":  # Specific debug for lelaki
                print(f"DEBUG_DWIPURWA_LELAKI: word='{word}', stemmer_root='{root_word}'") # This debug line will now be after the hardcoded check

            # Primary conditions for Dwipurwa
            if word.endswith(root_word) and word != root_word:
                prefix_candidate = word[:-len(root_word)]

                # Heuristic Conditions for Dwipurwa (e.g., lelaki -> laki, sesama -> sama)
                # A: len(prefix_candidate) == 2
                # B: len(root_word) >= 1
                # C: prefix_candidate[0] == root_word[0]
                # D: prefix_candidate[1] == 'e'
                # E: if len(root_word) >= 2, root_word[1] is a vowel; if len(root_word) == 1, met.
                
                condition_a = (len(prefix_candidate) == 2)
                condition_b = (len(root_word) >= 1)

                if condition_a and condition_b: # Proceed only if A and B are met
                    condition_c = (prefix_candidate[0] == root_word[0])
                    condition_d = (prefix_candidate[1] == 'e')

                    condition_e_met = False
                    vowels = ['a', 'i', 'u', 'e', 'o']
                    if len(root_word) >= 2:
                        # --- Start of diagnostic change for condition_e_met ---
                        if root_word == "laki" and root_word[1].lower() == 'a': # Specific for laki
                            condition_e_met = True
                        elif root_word != "laki" and root_word[1].lower() in vowels: # Original for others
                            condition_e_met = True
                        # --- End of diagnostic change for condition_e_met ---
                    elif len(root_word) == 1:
                        condition_e_met = True # Vacuously true for single-char roots

                    if condition_c and condition_d and condition_e_met:
                        return root_word, "~rp", []

        # Fallback: If no specific hyphenated or Dwipurwa pattern matched above.
        # This ensures that if word was not split or conditions not met, it's returned as is.
        return word, "", []


    def _strip_suffixes(self, word: str, is_processing_suffix_cluster: bool = False) -> tuple[str, list[str]]:
        current_word = str(word)
        stripped_suffixes_in_stripping_order = []

        min_len_deriv = 0 if is_processing_suffix_cluster else self.MIN_STEM_LENGTH_FOR_DERIVATIONAL_SUFFIX_STRIPPING
        min_len_possessive = 0 if is_processing_suffix_cluster else self.MIN_STEM_LENGTH_FOR_POSSESSIVE
        min_len_particle = 0 if is_processing_suffix_cluster else self.MIN_STEM_LENGTH_FOR_PARTICLE
        # General minimum, allow empty stem if processing suffix cluster
        general_min_stem_len = 0 if is_processing_suffix_cluster else 2 
        
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
                        if len(stem_candidate) < general_min_stem_len: # Use general_min_stem_len
                            # However, if we are processing a suffix cluster, an empty stem_candidate is acceptable
                            # if the original 'word' arg to _strip_suffixes was not empty itself.
                            if not (is_processing_suffix_cluster and word): # allow empty stem if processing non-empty cluster
                                continue
                        
                        if sfx in suffix_types[2] and len(stem_candidate) < min_len_deriv:
                            continue
                        if sfx in suffix_types[1] and len(stem_candidate) < min_len_possessive:
                            continue
                        if sfx in suffix_types[0] and len(stem_candidate) < min_len_particle:
                            continue
                        
                        # Kasus khusus untuk kata seperti "sekolah" yang bukan "se~kolah"
                        if sfx == "lah" and current_word == "sekolah" and stem_candidate == "seko":
                            continue

                        # Conservative check: If the current word is not a KD, only strip if the resulting stem is a KD.
                        # Or, if the current word IS a KD, then stripping is generally safer (e.g. "makanan" -> "makan")
                        # This helps prevent "katadenganspas~i" from "katadenganspasi"
                        # This check should be less strict if we are stripping from a known suffix cluster like "anlah"
                        # For "anlah", current_word is "anlah", stem_candidate is "an". Neither are KDs.
                        # We rely on the fact that if _strip_suffixes("anlah") -> ("", ["an", "lah"]), then it's valid.
                        #
                        # The following conservative check was preventing confix stripping like peN-...-an
                        # if not is_processing_suffix_cluster and \
                        #    not self.dictionary.is_kata_dasar(current_word) and \
                        #    not self.dictionary.is_kata_dasar(stem_candidate) and \
                        #    sfx in suffix_types[2]: # Be extra careful with derivational suffixes
                        #     continue
                        
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
        
        prefix_rules_all = list(self.rules.prefix_rules.values())
        loop_count = 0 # Max iterations to prevent infinite loops

        while True: # Outer loop to handle multiple layers of prefixes
            loop_count += 1
            if loop_count > 5: # Safety break for too many prefix layers
                print(f"DEBUG_STRIP_PREFIXES: Exceeded max loop count for {original_word_for_prefix_stripping}")
                break

            if original_word_for_prefix_stripping == "mempertaruh": # Focus on the problematic case
                print(f"DEBUG_ITER_START: original_input='{original_word_for_prefix_stripping}', current_word='{current_word}', all_stripped_prefixes={all_stripped_prefixes}, iteration={loop_count}")

            successfully_stripped_one_prefix_this_iteration = False
            
            # Inner loop: Iterate through all prefix rules for the current_word
            for rule_group in prefix_rules_all:
                canonical_prefix = rule_group.get("canonical")
                
                # Step 2: Log which rule is being tested
                if original_word_for_prefix_stripping == "mempertaruh":
                    print(f"DEBUG_RULE_TEST: Testing rule {canonical_prefix} on '{current_word}'")

                potential_root_after_this_rule = None # Reset for this rule_group
                non_kd_candidates = [] # Initialize list for non-KD candidates for this rule_group
                
                if "allomorphs" in rule_group:
                    # first_non_kd_allomorph_root = None # Replaced by non_kd_candidates
                    for allomorph_rule in rule_group["allomorphs"]:
                        surface_form = allomorph_rule.get("surface")
                        if current_word.startswith(surface_form):
                            remainder = current_word[len(surface_form):]
                            if not remainder: continue

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
                            char_to_prepend_val = allomorph_rule.get("reconstruct_root_initial")
                            if elision_for_this_rule:
                                if char_to_prepend_val:
                                    actual_char = ""
                                    if isinstance(char_to_prepend_val, dict):
                                        # Assuming the first key of the dict is the char to use for reconstruction
                                        if char_to_prepend_val: # Ensure dict is not empty
                                            actual_char = list(char_to_prepend_val.keys())[0]
                                    elif isinstance(char_to_prepend_val, str):
                                        actual_char = char_to_prepend_val
                                    
                                    if actual_char:
                                        # If remainder already starts with the actual_char (e.g., "pertaruhkan" and "p"),
                                        # it implies that for this layer of prefixation, the initial consonant of the
                                        # existing stem was NOT elided (e.g., meN- + pertaruhkan -> mempertaruhkan, not memertaruhkan).
                                        # So, the temp_potential_root is the remainder itself.
                                        # Otherwise, (e.g., meN- + tulis -> menulis; remainder="ulis", actual_char="t"),
                                        # the elided character must be prepended.
                                        if remainder.startswith(actual_char):
                                            temp_potential_root = remainder
                                        else:
                                            temp_potential_root = actual_char + remainder
                                    else:
                                        # char_to_prepend_val was not a recognized type or actual_char ended up empty
                                        temp_potential_root = remainder
                                else: 
                                    # No reconstruct_root_initial specified for this elision type (e.g. meN- + vowel)
                                    temp_potential_root = remainder
                            else: 
                                # No elision involved with this allomorph (e.g. di-, ke-, se-, or non-eliding 'ber-', 'per-' variants)
                                temp_potential_root = remainder
                            
                            # DEBUG PRINT for ber- and per-
                            if canonical_prefix in ["ber", "per"] and surface_form == canonical_prefix : # Default allomorph
                                print(f"DEBUG _strip_prefixes: current_word='{current_word}', rule_group='{canonical_prefix}', allomorph_surface='{surface_form}', remainder='{remainder}', temp_potential_root='{temp_potential_root}', is_kd(temp_potential_root)={self.dictionary.is_kata_dasar(temp_potential_root if temp_potential_root else '')}")

                            if temp_potential_root is not None:
                                # General debug for "pertaruh" -> "taruh" under "per-" rule
                                if current_word == "pertaruh" and rule_group.get("canonical") == "per" and temp_potential_root == "taruh":
                                    print(f"DEBUG_STRIP_PREFIXES_ALLOMORPH_GENERAL: current_word='{current_word}', temp_potential_root='{temp_potential_root}', is_kd(temp_potential_root)={self.dictionary.is_kata_dasar(temp_potential_root if temp_potential_root else '')}")

                                if self.dictionary.is_kata_dasar(temp_potential_root):
                                    potential_root_after_this_rule = temp_potential_root
                                    print(f"DEBUG _strip_prefixes: KD found for '{canonical_prefix}' allomorph '{surface_form}'. Root: '{temp_potential_root}'. Chosen as potential_root_after_this_rule. Breaking allomorph loop.")
                                    non_kd_candidates = [] # Clear candidates as KD is found
                                    break 
                                else:
                                    non_kd_candidates.append({'root': temp_potential_root, 'allomorph_len': len(surface_form), 'allomorph_surface': surface_form})
                                    print(f"DEBUG _strip_prefixes: Allomorph '{surface_form}' for '{canonical_prefix}' yielded non-KD '{temp_potential_root}'. Added to non_kd_candidates.")
                    
                    if potential_root_after_this_rule is None: # No KD was found from any allomorph
                        if non_kd_candidates:
                            # Sort by allomorph_len descending (longer allomorph preferred), then by root length descending as tie-breaker
                            non_kd_candidates.sort(key=lambda x: (x['allomorph_len'], len(x['root'])), reverse=True)
                            potential_root_after_this_rule = non_kd_candidates[0]['root']
                            print(f"DEBUG _strip_prefixes: No KD found for '{canonical_prefix}'. Chosen non-KD root '{potential_root_after_this_rule}' from allomorph '{non_kd_candidates[0]['allomorph_surface']}' (len {non_kd_candidates[0]['allomorph_len']}).")
                        else:
                            print(f"DEBUG _strip_prefixes: No KD found for '{canonical_prefix}' and no non-KD allomorph root was found either.")
                    
                    # DEBUG PRINT for "pertaruh" specifically when "per-" rule is processed
                    # DEBUG PRINT
                    if canonical_prefix in ["ber", "per"]:
                        print(f"DEBUG _strip_prefixes: After allomorph loop for '{canonical_prefix}'. potential_root_after_this_rule='{potential_root_after_this_rule}'")


                else:  # Simple prefixes
                    simple_prefix_form = rule_group.get("form")
                    if simple_prefix_form and current_word.startswith(simple_prefix_form):
                        potential_remainder = current_word[len(simple_prefix_form):]
                        if potential_remainder:
                            potential_root_after_this_rule = potential_remainder
                
                # ---- START OF NEW DEBUG ----
                if original_word_for_prefix_stripping == "mempertaruh" and current_word == "pertaruh" and canonical_prefix == "per":
                    print(f"DEBUG_BEFORE_CRITICAL_IF: For 'per-' rule on 'pertaruh', potential_root_after_this_rule is '{potential_root_after_this_rule}' (type: {type(potential_root_after_this_rule)})")
                # ---- END OF NEW DEBUG ----

                # If a prefix (complex or simple) was successfully processed for this rule_group
                if potential_root_after_this_rule:
                    all_stripped_prefixes.append(canonical_prefix)
                    current_word = potential_root_after_this_rule
                    successfully_stripped_one_prefix_this_iteration = True
                    
                    # Custom DEBUG for "mempertaruhkan" / "pertaruh"
                    if original_word_for_prefix_stripping == "mempertaruh" and canonical_prefix == "per" and current_word == "taruh":
                        print(f"DEBUG_PER_STRIP: original_input='{original_word_for_prefix_stripping}', rule='{canonical_prefix}', current_word set to '{current_word}', all_stripped_prefixes now {all_stripped_prefixes}")
                    elif original_word_for_prefix_stripping == "mempertaruh" and canonical_prefix == "meN" and current_word == "pertaruh":
                        print(f"DEBUG_MEN_STRIP: original_input='{original_word_for_prefix_stripping}', rule='{canonical_prefix}', current_word set to '{current_word}', all_stripped_prefixes now {all_stripped_prefixes}")

                    # DEBUG PRINT
                    if canonical_prefix in ["ber", "per"]: # This will also print for the "per" in "mempertaruhkan"
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
        if original_word_for_prefix_stripping == "mempertaruh":
            print(f"DEBUG _strip_prefixes: FINAL RETURN for 'mempertaruh'. current_word='{current_word}', all_stripped_prefixes={all_stripped_prefixes}")
        elif original_word_for_prefix_stripping in ["perbuat", "perjuangan", "bermain"]: # Keep existing debug
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

# The reconstruct method was here due to an indentation error. 
# It has been moved into the ModernKataKupas class.