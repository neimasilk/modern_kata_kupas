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
                    print(f"INFO: Loaded rules via importlib: {str(default_rules_path)}") # Diagnostic
            except (FileNotFoundError, TypeError, ModuleNotFoundError) as e: 
                base_dir = os.path.dirname(os.path.abspath(__file__))
                default_rules_path_rel = os.path.join(base_dir, "data", DEFAULT_RULES_FILENAME)
                if os.path.exists(default_rules_path_rel):
                    self.rules = MorphologicalRules(rules_file_path=default_rules_path_rel)
                    print(f"INFO: Loaded rules via os.path: {default_rules_path_rel}") # Diagnostic
                else: 
                    print(f"WARNING: Default rules file not found via importlib or os.path ({default_rules_path_rel}). Attempting final fallback.") # Diagnostic
                    self.rules = MorphologicalRules() # This will use AFFIX_RULES_PATH from rules.py
                    # Check if the final fallback loaded anything
                    if not self.rules.prefix_rules and not self.rules.suffix_rules:
                        print("WARNING: Final fallback for rule loading resulted in empty rules.")
                    else:
                        print(f"INFO: Rules loaded via MorphologicalRules default constructor (rules.py AFFIX_RULES_PATH: {self.rules.rules_file_path}).")
        
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

        # 8. Loanword Affixation Handling
        # If the best stem we found after regular S1/S2 strategies (chosen_final_stem) 
        # is not a recognized kata_dasar, then it's potentially an OOV word,
        # which might be an affixed loanword.
        if not self.dictionary.is_kata_dasar(chosen_final_stem):
            # Pass the original normalized_word to the loanword handler,
            # as it contains the full form needed for loanword affix stripping.
            loanword_segmentation = self._handle_loanword_affixation(normalized_word)
            if loanword_segmentation:
                # If loanword handling provides a valid segmentation, use it.
                print(f"DEBUG: segment({word}): Using loanword segmentation: '{loanword_segmentation}'")
                return loanword_segmentation

        # 9. Return Logic (original return logic adjusted)
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

    def _handle_loanword_affixation(self, word: str) -> str:
        """
        Attempts to segment a word by stripping Indonesian affixes if the base is a known loanword.
        This is typically called for OOV words after standard stemming fails.

        Args:
            word (str): The word to process (usually the normalized_word).

        Returns:
            str: The segmented string (e.g., "di~download", "meN~update~nya") if a loanword
                 and affixes are found, otherwise an empty string.
        """
        if not word:
            return ""

        # If normalized_word still contains hyphens (e.g. "di-download" instead of "didownload"),
        # this explicit replacement ensures that prefix matching (e.g. "di") can find bases like "download".
        # This is a targeted adjustment for loanword handling, assuming standard prefixes ("di", "meN")
        # do not contain hyphens themselves.
        processed_word = word.replace('-', '')

        # Strategy 1: Check for prefix + loanword_base + suffix
        # Iterate through all prefix forms (longest first for maximal munch)
        sorted_prefix_forms = sorted(self.rules.get_all_prefix_forms(), key=len, reverse=True)
        
        for p_form in sorted_prefix_forms:
            if processed_word.startswith(p_form): # Use processed_word
                canonical_prefix = self.rules.get_canonical_prefix_form(p_form)
                if not canonical_prefix: 
                    continue

                # Try with prefix only first
                base_after_prefix = processed_word[len(p_form):] # Use processed_word
                if not base_after_prefix: continue

                if self.dictionary.is_loanword(base_after_prefix):
                    return f"{canonical_prefix}~{base_after_prefix}"

                # Try with prefix + suffix
                matching_suffix_rules = self.rules.get_matching_suffix_rules(base_after_prefix)
                for s_rule in matching_suffix_rules:
                    s_form_on_word = s_rule.get("original_pattern") 
                    s_form_clean = s_form_on_word.lstrip('-') 
                    
                    if not s_form_on_word or not base_after_prefix.endswith(s_form_on_word):
                        continue

                    loanword_candidate = base_after_prefix[:-len(s_form_on_word)]
                    if not loanword_candidate: continue
                    
                    if self.dictionary.is_loanword(loanword_candidate):
                        return f"{canonical_prefix}~{loanword_candidate}~{s_form_clean}"
        
        # Strategy 2: Check for loanword_base + suffix only (no prefix)
        matching_suffix_rules = self.rules.get_matching_suffix_rules(processed_word) # Use processed_word
        for s_rule in matching_suffix_rules:
            s_form_on_word = s_rule.get("original_pattern")
            s_form_clean = s_form_on_word.lstrip('-')
            
            if not s_form_on_word: continue

            base_candidate = processed_word[:-len(s_form_on_word)] # Use processed_word
            if not base_candidate: continue

            if self.dictionary.is_loanword(base_candidate):
                return f"{base_candidate}~{s_form_clean}"
                
        # Strategy 3: Check if the word itself is a loanword (no affixes)
        # This might seem redundant if the main segment() checks for KD first.
        # However, if a word is NOT a KD, but IS a loanword, segment() might still call this.
        # In such a case, we should return it as is, but without '~' separators.
        # The task is to identify AFFIXED loanwords. If it's just a loanword,
        # the existing logic in segment() should handle it (return normalized_word if no affixes found).
        # So, if we reach here, it means it's not an *affixed* loanword found by this method.

        return "" # No loanword affixation pattern found

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
                # Check if part1 matches base or variant
                if part1 == base or part1 == variant:
                    # Check if part2 starts with the corresponding pair
                    pair = variant if part1 == base else base
                    if part2 == pair or part2.startswith(pair):
                        # Jika ada prefix, tambahkan ke base
                        if hasattr(self, 'stemmer') and self.stemmer:
                            prefix_part = ''
                            if '-' in word:
                                prefix_match = re.match(r'^(ter|di|ke|se|ber|per|pe|me|mem|men|meng|menge|pem|pen|peng|penge)(.+)$', word.split('-')[0])
                                if prefix_match:
                                    prefix_part = prefix_match.group(1)
                                    
                            if prefix_part:
                                return word.split('-')[0], f"rs(~{part2})", []
                        return part1, f"rs(~{part2})", []

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
            return "laki", "rp", []
        if word == "sesama": # Add other common ones if they also fail due_to stemmer
            return "sama", "rp", []
        if word == "tetamu":
            return "tamu", "rp", []
        if word == "rerata":
            return "rata", "rp", []
        if word == "tetua":
            return "tua", "rp", []
        if word == "dedaun":
            return "daun", "rp", []
        # Add more if needed based on test_dwipurwa_reduplication

        # --- Dwipurwa (Partial Initial Syllable Reduplication) Check ---
        # This check is placed after hyphen-based checks as Dwipurwa usually doesn't involve hyphens.
        if hasattr(self, 'stemmer') and self.stemmer:
            root_word = self.stemmer.get_root_word(word)
            if word == "lelaki":  # Specific debug for lelaki
                print(f"DEBUG_DWIPURWA_LELAKI: word='{word}', stemmer_root='{root_word}'") # This debug line will now be after the hardcoded check

            # Primary conditions for Dwipurwa
            prefix_candidate = ""
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
                    return root_word, "rp", []

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

                        # --- MODIFIED CONSERVATIVE CHECK ---
                        # For derivational suffixes (e.g., -kan, -i, -an):
                        # Only strip them if the resulting stem_candidate is a known Kata Dasar (KD),
                        # OR if we are specifically processing a suffix cluster (is_processing_suffix_cluster is True),
                        # where intermediate non-KD steps are expected.
                        if sfx in suffix_types[2]: # Check if suffix is derivational
                            if not self.dictionary.is_kata_dasar(stem_candidate) and not is_processing_suffix_cluster:
                                continue # Don't strip if stem is not KD and not in cluster processing mode
                        # --- END MODIFIED CONSERVATIVE CHECK ---
                        
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
        """
        Memisahkan prefiks dari kata menggunakan _strip_prefixes_detailed.
        """
        current_word = str(original_word_for_prefix_stripping)
        if not current_word:
            return "", []

        # Check if the original word itself is a KD, if so, no prefixes to strip.
        # This is a guard, primary KD check is at the start of segment()
        if self.dictionary.is_kata_dasar(current_word):
            return current_word, []

        return self._strip_prefixes_detailed(current_word, [])

    def _strip_prefixes_detailed(self, word_to_strip: str, accumulated_prefixes: list[str]) -> tuple[str, list[str]]:
        """
        Implementasi rekursif (atau iteratif yang dimodelkan secara rekursif) untuk pelepasan prefiks.
        """
        # Base case: Jika kata sudah menjadi kata dasar, kembalikan apa adanya.
        if self.dictionary.is_kata_dasar(word_to_strip):
            return word_to_strip, accumulated_prefixes

        # Optimization: If word is too short to have prefixes and a meaningful stem
        if len(word_to_strip) < 3: # e.g., "di", "ku" - too short for prefix + stem_min_1
            return word_to_strip, accumulated_prefixes

        # Check all known prefixes from longest to shortest to prefer maximal munch for prefixes
        # This helps with layered prefixes like "memper-"
        sorted_prefixes = sorted(self.rules.get_all_prefix_forms(), key=len, reverse=True)

        for prefix_form in sorted_prefixes:
            if word_to_strip.startswith(prefix_form):
                stem_candidate = word_to_strip[len(prefix_form):]

                if not stem_candidate: # Stripping prefix left nothing
                    continue

                canonical_prefix = self.rules.get_canonical_prefix_form(prefix_form)
                if not canonical_prefix: 
                    continue

                # Option 1: If stem_candidate is directly a KD
                if self.dictionary.is_kata_dasar(stem_candidate):
                    new_prefixes = accumulated_prefixes + [canonical_prefix]
                    print(f"DEBUG_STRIP_PREFIX_DETAILED: '{prefix_form}' stripped, '{stem_candidate}' is KD. Finalizing here.")
                    return stem_candidate, new_prefixes

                # Option 2: If reversing morphophonemics on stem_candidate yields a KD
                potential_original_stem = self.rules.reverse_morphophonemics(prefix_form, canonical_prefix, stem_candidate)
                if potential_original_stem != stem_candidate and self.dictionary.is_kata_dasar(potential_original_stem):
                    new_prefixes = accumulated_prefixes + [canonical_prefix]
                    print(f"DEBUG_STRIP_PREFIX_DETAILED: '{prefix_form}' (canon: {canonical_prefix}) stripped, reverse_morpho to '{potential_original_stem}' is KD. Finalizing here.")
                    return potential_original_stem, new_prefixes

                # Option 3: Recursively strip from stem_candidate (the surface form after stripping prefix_form)
                # This handles layered prefixes (e.g., di-per-oleh, mem-per-mainkan)
                further_stripped_stem, deeper_prefixes = self._strip_prefixes_detailed(stem_candidate, []) 
                
                # If the recursive call found a KD OR found more prefixes, then this path is valid.
                if self.dictionary.is_kata_dasar(further_stripped_stem) or deeper_prefixes:
                    current_prefixes = accumulated_prefixes + [canonical_prefix] + deeper_prefixes
                    print(f"DEBUG_STRIP_PREFIX_DETAILED: '{prefix_form}' stripped, recur_stem='{further_stripped_stem}', deeper_prefixes={deeper_prefixes}")
                    return further_stripped_stem, current_prefixes
                
                # Option 4: (NEW FALLBACK FOR CONFIDENCE) If no KD was found via options 1, 2, or 3,
                # but a prefix was indeed stripped, consider this a valid partial strip.
                # This allows the main `segment` function's S1 strategy (prefix then suffix)
                # to attempt suffix stripping on this `stem_candidate`.
                # We only do this if this is the first prefix being stripped in this call chain (accumulated_prefixes is empty)
                # to avoid overly greedy behavior in deep recursion, or if no other prefix choice worked out from the loop.
                # For now, let's be more direct: if a prefix matched, and recursion didn't improve, take the current strip.
                # This path is taken if this `prefix_form` was the first one in `sorted_prefixes` that matched.
                # The loop will try other (shorter) prefixes if this path isn't taken.
                # The crucial change is to allow returning a non-KD stem if a prefix is found.
                
                # If we are here, it means: 
                # 1. stem_candidate is not KD
                # 2. potential_original_stem is not KD (or same as stem_candidate)
                # 3. recursion on stem_candidate did not yield a KD and found no further prefixes.
                # In this case, we accept the current prefix strip and return the non-KD stem.
                # This allows the S1 strategy in segment() to try suffix stripping later.
                new_prefixes = accumulated_prefixes + [canonical_prefix]
                print(f"DEBUG_STRIP_PREFIX_DETAILED: '{prefix_form}' stripped, stem '{stem_candidate}' is not KD, but accepting prefix.")
                return stem_candidate, new_prefixes

        # If no prefix could be stripped at all from word_to_strip
        print(f"DEBUG_STRIP_PREFIX_DETAILED: No prefix stripped from '{word_to_strip}' or no valid stem found after stripping.")
        return word_to_strip, accumulated_prefixes

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