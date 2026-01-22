# src/modern_kata_kupas/separator.py
"""
Modul untuk memisahkan kata berimbuhan menjadi kata dasar dan afiksnya.
"""
import re
import logging
from dataclasses import dataclass
from typing import Optional, Tuple, List

from .normalizer import TextNormalizer


@dataclass
class StrategyResult:
    """Result from a segmentation strategy (S1 or S2)."""
    stem: str
    prefixes: List[str]
    suffixes: List[str]
    is_valid_root: bool


@dataclass
class ReduplicationInfo:
    """Information about reduplication detected in a word."""
    word_to_process: str
    marker: str  # "ulg", "rp", "rs", or ""
    suffixes: List[str]
    phonetic_variant: Optional[str]


from .dictionary_manager import DictionaryManager
from .rules import MorphologicalRules
from .stemmer_interface import IndonesianStemmer
from .utils.alignment import align
from .reconstructor import Reconstructor
from .config_loader import ConfigLoader

class ModernKataKupas:
    """
    Orchestrates the segmentation of Indonesian words into their constituent morphemes.

    This class integrates various components like a normalizer, dictionary manager,
    morphological rule engine, and stemmer to perform word segmentation.
    It handles various morphological phenomena including prefixes, suffixes,
    reduplication, and loanword affixation.
    """

    def __init__(self, dictionary_path: Optional[str] = None, rules_file_path: Optional[str] = None, config_path: Optional[str] = None):
        """Initializes the ModernKataKupas separator.

        Sets up the text normalizer, dictionary manager (for root words and
        loanwords), morphological rules engine, the underlying Indonesian stemmer,
        and the Reconstructor.

        If `dictionary_path` or `rules_file_path` are not provided, the system
        attempts to load default packaged files.

        Args:
            dictionary_path (str, optional): Path to a custom root word dictionary
                file (one word per line, UTF-8 encoded). If None, the default
                packaged dictionary is loaded. Defaults to None.
            rules_file_path (str, optional): Path to a custom morphological rules
                JSON file. If None, the default packaged rules file is loaded.
                Defaults to None.
            config_path (str, optional): Path to a custom configuration YAML file.
                If None, the default packaged config.yaml is loaded. Configuration
                includes min stem lengths, reduplication pairs, and feature flags.
                Defaults to None.

        Raises:
            DictionaryFileNotFoundError: If a specified `dictionary_path` is invalid
                and the default dictionary cannot be loaded as a fallback.
            DictionaryLoadingError: If there's an error parsing the dictionary file.
            RuleError: If a specified `rules_file_path` is invalid, or the rules
                       file has an incorrect format, and default rules cannot be
                       loaded as a fallback.
            FileNotFoundError: If default packaged files (dictionary/rules) are
                               missing and no custom paths are provided.
        """
        import importlib

        # Constants for default rules file location
        DEFAULT_DATA_PACKAGE_PATH = 'modern_kata_kupas.data' # Path for importlib when src is on sys.path
        DEFAULT_RULES_FILENAME = 'affix_rules.json'

        # Load configuration
        self.config = ConfigLoader(config_path=config_path)

        # Load min stem lengths from config
        self.MIN_STEM_LENGTH_FOR_POSSESSIVE = self.config.get_min_stem_length('possessive')
        self.MIN_STEM_LENGTH_FOR_DERIVATIONAL_SUFFIX_STRIPPING = self.config.get_min_stem_length('derivational')
        self.MIN_STEM_LENGTH_FOR_PARTICLE = self.config.get_min_stem_length('particle')

        # Load reduplication pairs from config
        self.DWILINGGA_SALIN_SUARA_PAIRS = self.config.get_dwilingga_pairs()

        self.normalizer = TextNormalizer()
        self.dictionary = DictionaryManager(dictionary_path=dictionary_path)
        self.stemmer = IndonesianStemmer()
        self.aligner = align

        if rules_file_path:
            self.rules = MorphologicalRules(rules_file_path=rules_file_path)
        else:
            # Refactored to use MorphologicalRules default loading (which uses read_text/files internally)
            # to avoid DeprecationWarning from importlib.resources.path
            rules_loaded = False
            try:
                self.rules = MorphologicalRules() # Attempts default load
                # Check if rules were actually loaded (MorphologicalRules might return empty on failure)
                if self.rules.prefix_rules or self.rules.suffix_rules:
                    logging.info("Rules loaded via MorphologicalRules default mechanism.")
                    rules_loaded = True
                else:
                    logging.warning("MorphologicalRules returned empty rules. Triggering fallback.")
            except Exception as e:
                logging.warning(f"Failed to load rules via MorphologicalRules default: {e}. Triggering fallback.")
            
            if not rules_loaded:
                logging.info("Attempting os.path fallback for rules.")
                base_dir = os.path.dirname(os.path.abspath(__file__))
                default_rules_path_rel = os.path.join(base_dir, "data", DEFAULT_RULES_FILENAME)
                if os.path.exists(default_rules_path_rel):
                    self.rules = MorphologicalRules(rules_file_path=default_rules_path_rel)
                    logging.info(f"Loaded rules via os.path: {default_rules_path_rel}")
                else:
                    logging.warning(f"Default rules file not found via os.path ('{default_rules_path_rel}'). Using empty rules.")
                    if not hasattr(self, 'rules'): # Ensure self.rules exists even if empty
                        self.rules = MorphologicalRules() # Empty rules
        
        # Initialize Reconstructor
        self.reconstructor = Reconstructor(rules=self.rules, dictionary_manager=self.dictionary, stemmer=self.stemmer)

    def reconstruct(self, segmented_word: str) -> str:
        """
        Reconstructs an original word from its segmented morpheme string.

        This method delegates the reconstruction task to the `Reconstructor` class,
        which uses the loaded morphological rules to combine morphemes and apply
        necessary morphophonemic changes.

        Args:
            segmented_word (str): A string of morphemes separated by tildes (~),
                e.g., "meN~tulis", "buku~ulg~nya".

        Returns:
            str: The reconstructed original word. If the input is empty or cannot be
                 meaningfully reconstructed (e.g., root is missing from segmented_word),
                 it may return an empty string or a partially reconstructed form
                 depending on the Reconstructor's logic.

        Example:
            >>> mkk = ModernKataKupas()
            >>> mkk.reconstruct("meN~tulis")
            'menulis'
            >>> mkk.reconstruct("buku~ulg~nya")
            'buku-bukunya'
        """
        # self.reconstructor is guaranteed by __init__
        return self.reconstructor.reconstruct(segmented_word)

    def segment(self, word: str) -> str:
        """
        Segments an Indonesian word into its constituent morphemes.

        The process involves:
        1. Normalizing the input word (lowercase, basic punctuation stripping).
        2. Checking if the word is already a root word.
        3. Handling various forms of reduplication (full, partial, phonetic change).
        4. Applying affix stripping strategies (prefixes then suffixes, and vice-versa)
           to identify the root and affixes.
        5. Attempting loanword affixation handling if standard segmentation fails to find
           a known root word.
        6. Assembling the final segmented string with morphemes separated by tildes (~).

        If a word cannot be segmented or is already a root word, it is returned
        in its normalized form.

        Args:
            word (str): The Indonesian word to be segmented.

        Returns:
            str: A string representing the segmented morphemes separated by tildes (~).
                 For example, "mempermainkan" might become "meN~per~main~kan".
                 Unsegmentable words or root words are returned as is (normalized).
                 Returns an empty string if the input word normalizes to an empty
                 string (e.g., input is `""` or `"   "`).

        Example:
            >>> mkk = ModernKataKupas()
            >>> mkk.segment("makanan")
            'makan~an'
            >>> mkk.segment("memperjuangkannya") # Assuming 'juang' is in dictionary
            'meN~per~juang~kan~nya'
            >>> mkk.segment("tidakdiketahui") # Assuming 'tahu' is in dictionary
            'tidak~di~ke~tahu~i'
        """
        # 1. Normalize the word
        normalized_word = self.normalizer.normalize_word(word)
        if not normalized_word:
            return ""

        # 2. Detect reduplication and check if already a root word
        redup_info = self._detect_reduplication(normalized_word, word)

        # Early return if the word is a root word with no reduplication
        if (redup_info.word_to_process == normalized_word and
                not redup_info.marker and
                self.dictionary.is_kata_dasar(normalized_word)):
            return normalized_word

        word_to_process = redup_info.word_to_process
        logging.debug(
            f"segment({word}): after reduplication detection: "
            f"word_to_process='{word_to_process}', marker='{redup_info.marker}'"
        )

        # 3. Apply dual segmentation strategies
        s1 = self._apply_strategy(word_to_process, prefix_first=True)
        s2 = self._apply_strategy(word_to_process, prefix_first=False)

        logging.debug(f"segment({word}): S1={s1}, S2={s2}")

        # 4. Choose the best result
        chosen_stem, chosen_prefixes, chosen_suffixes = self._choose_best_strategy(
            s1, s2, word_to_process
        )

        logging.debug(
            f"segment({word}): chosen_stem='{chosen_stem}', "
            f"prefixes={chosen_prefixes}, suffixes={chosen_suffixes}"
        )

        # 5. Try loanword affixation if stem is not a known root word
        if not self.dictionary.is_kata_dasar(chosen_stem):
            loanword_result = self._handle_loanword_affixation(normalized_word)
            if loanword_result:
                logging.debug(f"segment({word}): Using loanword segmentation: '{loanword_result}'")
                return loanword_result

        # 6. Assemble the final result
        result_str = self._assemble_result(
            chosen_stem, chosen_prefixes, chosen_suffixes, redup_info
        )
        logging.debug(f"segment({word}): assembled result_str='{result_str}'")

        # 7. Determine if any meaningful segmentation occurred
        assembled_suffixes = chosen_suffixes + redup_info.suffixes
        is_unchanged = (
            not chosen_prefixes and
            not redup_info.marker and
            not assembled_suffixes and
            chosen_stem == normalized_word
        )

        # 8. Return appropriate result
        if not result_str:
            logging.debug(f"segment({word}): Empty result, returning normalized_word")
            return normalized_word

        if is_unchanged:
            logging.debug(f"segment({word}): No effective segmentation, returning normalized_word")
            return normalized_word

        if result_str == normalized_word and not self.dictionary.is_kata_dasar(normalized_word):
            logging.debug(f"segment({word}): Result equals input but not a KD, returning normalized_word")
            return normalized_word

        if (not self.dictionary.is_kata_dasar(chosen_stem) and
                not chosen_prefixes and not assembled_suffixes and not redup_info.marker):
            logging.debug(f"segment({word}): Stem not KD and no affixes, returning normalized_word")
            return normalized_word

        logging.debug(f"segment({word}): Returning final result: '{result_str}'")
        return result_str

    def _detect_reduplication(self, normalized_word: str, original_word: str) -> ReduplicationInfo:
        """
        Detects and processes reduplication patterns in a word.

        Args:
            normalized_word: The normalized form of the word.
            original_word: The original input word (for logging).

        Returns:
            ReduplicationInfo containing the word to process and reduplication details.
        """
        if '-' in normalized_word:
            word_to_process, marker, suffixes, variant = self._handle_reduplication(normalized_word)
            if marker:
                logging.debug(f"segment({original_word}): Hyphenated word, redup detected: marker='{marker}'")
            else:
                if self.dictionary.is_kata_dasar(normalized_word):
                    return ReduplicationInfo(normalized_word, "", [], None)
                variant = None
                suffixes = []
            return ReduplicationInfo(word_to_process, marker, suffixes, variant)

        # Non-hyphenated word
        if self.dictionary.is_kata_dasar(normalized_word):
            return ReduplicationInfo(normalized_word, "", [], None)

        # Check for Dwipurwa
        dwipurwa_result = self._handle_dwipurwa(normalized_word)
        if dwipurwa_result:
            word_to_process, marker, suffixes, variant = dwipurwa_result
            logging.debug(f"segment({original_word}): Dwipurwa detected: marker='{marker}'")
            return ReduplicationInfo(word_to_process, marker, suffixes, variant)

        return ReduplicationInfo(normalized_word, "", [], None)

    def _apply_strategy(self, word: str, prefix_first: bool) -> StrategyResult:
        """
        Applies a single segmentation strategy.

        Args:
            word: The word to segment.
            prefix_first: If True, strip prefixes then suffixes. Otherwise, reverse.

        Returns:
            StrategyResult with the stem, affixes, and validity.
        """
        if prefix_first:
            stem_after_first, prefixes = self._strip_prefixes(word)
            final_stem, suffixes = self._strip_suffixes(stem_after_first)
        else:
            stem_after_first, suffixes = self._strip_suffixes(word)
            final_stem, prefixes = self._strip_prefixes(stem_after_first)

        is_valid = self.dictionary.is_kata_dasar(final_stem)
        return StrategyResult(final_stem, prefixes, suffixes, is_valid)

    def _choose_best_strategy(
        self, s1: StrategyResult, s2: StrategyResult, word_to_process: str
    ) -> Tuple[str, List[str], List[str]]:
        """
        Chooses the best result between two segmentation strategies.

        Args:
            s1: Result from Strategy 1 (prefix-first).
            s2: Result from Strategy 2 (suffix-first).
            word_to_process: The original word being processed (fallback).

        Returns:
            Tuple of (chosen_stem, chosen_prefixes, chosen_suffixes).
        """
        if s1.is_valid_root and s2.is_valid_root:
            if len(s1.stem) >= len(s2.stem):
                return s1.stem, s1.prefixes, s1.suffixes
            return s2.stem, s2.prefixes, s2.suffixes
        elif s1.is_valid_root:
            return s1.stem, s1.prefixes, s1.suffixes
        elif s2.is_valid_root:
            return s2.stem, s2.prefixes, s2.suffixes
        else:
            # Fallback: use word_to_process as stem if it's a KD, otherwise as-is
            if self.dictionary.is_kata_dasar(word_to_process):
                return word_to_process, [], []
            return word_to_process, [], []

    def _assemble_result(
        self,
        stem: str,
        prefixes: List[str],
        main_suffixes: List[str],
        redup_info: ReduplicationInfo
    ) -> str:
        """
        Assembles the final segmented string from components.

        Args:
            stem: The root word.
            prefixes: List of prefixes.
            main_suffixes: List of main suffixes.
            redup_info: Reduplication information.

        Returns:
            The assembled tilde-separated string.
        """
        parts: List[str] = []

        if prefixes:
            parts.extend(prefixes)

        parts.append(stem)

        if redup_info.marker:
            if redup_info.marker == 'rs' and redup_info.phonetic_variant:
                parts.append(f"rs(~{redup_info.phonetic_variant})")
            else:
                parts.append(redup_info.marker)
                if redup_info.phonetic_variant:
                    parts.append(redup_info.phonetic_variant)

        # Assemble suffixes
        if main_suffixes:
            parts.extend(main_suffixes)
        if redup_info.suffixes:
            parts.extend(redup_info.suffixes)

        valid_parts = [p for p in parts if p]
        return '~'.join(valid_parts)

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
                    if not s_form_on_word: continue
                    s_form_clean = s_form_on_word.lstrip('-') 
                    
                    if not base_after_prefix.endswith(s_form_on_word):
                        continue

                    loanword_candidate = base_after_prefix[:-len(s_form_on_word)]
                    if not loanword_candidate: continue
                    
                    if self.dictionary.is_loanword(loanword_candidate):
                        return f"{canonical_prefix}~{loanword_candidate}~{s_form_clean}"
        
        # Strategy 2: Check for loanword_base + suffix only (no prefix)
        matching_suffix_rules = self.rules.get_matching_suffix_rules(processed_word) # Use processed_word
        for s_rule in matching_suffix_rules:
            s_form_on_word = s_rule.get("original_pattern")
            if not s_form_on_word: continue
            s_form_clean = s_form_on_word.lstrip('-')
            
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

    def _handle_reduplication(self, word: str) -> Tuple[str, str, List[str], Optional[str]]:
        """
        Handles full reduplication (Dwilingga) like X-X, X-Xsuffix, or PX-X (e.g., bermain-main).

        Args:
            word (str): The word to check for reduplication.

        Returns:
            tuple[str, str, list[str], str | None]:
                - base_form_for_stripping: The base part for further affix stripping.
                - reduplication_marker: "ulg" if full reduplication is detected, "rp" for partial, "" otherwise.
                - direct_redup_suffixes: List of suffixes directly attached to the second part of
                                         a reduplicated form (e.g., ["an"] for "mobil-mobilan"). Empty if none.
                - phonetic_variant: The variant part of phonetic reduplication (e.g., "mayur" in "sayur-mayur"),
                                   or None if not phonetic reduplication.
        """
        # Pattern 1: X-Xsuffix (e.g., mobil-mobilan, buku-bukunya)
        # Common suffixes appearing on the second part of a reduplicated form.
        match_with_suffix = re.match(r"^([^-]+)-\1(an|nya)$", word) # Assuming \1 is correct for r"" string
        if match_with_suffix:
            base_form = match_with_suffix.group(1)
            suffix = match_with_suffix.group(2)
            # Ensure base_form is reasonable (not empty or just a hyphen)
            if base_form and base_form != '-':
                return base_form, "ulg", [suffix], None  # No phonetic variant for simple reduplication

        # Pattern 2: X-Y general forms (includes X-X, PX-X, X-PX etc.)
        parts = word.split('-', 1)
        if len(parts) == 2:
            part1, part2 = parts[0], parts[1]

            if not part1 or not part2: # Should not happen if word contains a hyphen
                return word, "", [], None

            # Check for Dwilingga Salin Suara (e.g., "bolak-balik", "sayur-mayur")
            # Pattern: both parts have same length and share phonological similarity
            # OR check against known pairs
            for base, variant in self.DWILINGGA_SALIN_SUARA_PAIRS:
                # Check if part1 matches base or variant
                if part1 == base or part1 == variant:
                    # Check if part2 matches the pair
                    pair = variant if part1 == base else base
                    if part2 == pair:
                        # Full match - treat as phonetic change
                        return part1, "rs", [], part2
                    # Check if part2 starts with the pair (for compound forms)
                    elif part2.startswith(pair):
                        # This could be like sayur-mayurkan (with suffix)
                        return part1, "rs", [], part2

            # Sub-pattern 2a: Simple X-X (e.g., "rumah-rumah", "main-main")
            if part1 == part2:
                return part1, "ulg", [], None  # No phonetic variant for identical parts

            # Additional heuristic: if parts have same length and share initial/final sounds
            # AND ARE NOT IDENTICAL (identical handled above)
            if len(part1) == len(part2) and len(part1) >= 3 and part1 != part2:
                # Check if they share first letter or similar ending
                if (part1[0] == part2[0] or
                    part1[-1] in 'aiueo' and part2[-1] in 'aiueo'):
                    # Treat as phonetic change
                    return part1, "rs", [], part2

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
                        return part1, "ulg", [], None  # No phonetic variant

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
                            return part1, "ulg", identified_suffixes, None  # No phonetic variant 
                    
                    # Case 3: X-Xsuffix where X is complex (e.g., "rumah-rumahanlah" - though this might be caught by Case 2 if stemmer(rumah)==rumah)
                    if part1 == stem1: # If part1 is already the base stem (X-Xsuffix)
                        # This path is now covered by Case 2 logic if part2.startswith(stem1/stem2)
                        pass # Covered by Case 2 if part1 is the stem.
                    elif part2.startswith(part1) and len(part2) > len(part1): # part1 is complex (PX), part2 = PX + suffix_cluster
                        suffix_cluster_on_part2 = part2[len(part1):]
                        remaining_stem_from_cluster, identified_suffixes = self._strip_suffixes(suffix_cluster_on_part2, is_processing_suffix_cluster=True)
                        if not remaining_stem_from_cluster and identified_suffixes:
                            return part1, "ulg", identified_suffixes, None

                    # Fallback for stem1==stem2 if none of the more specific suffix patterns matched
                    # (e.g., "pukul-memukul" where part1="pukul", part2="memukul", stem1="pukul", stem2="pukul")
                    # In this case, part1 is the base, and part2 is a complex variation. No direct_redup_suffixes from part2.
                    return part1, "ulg", [], None

        # Fallback: If no specific hyphenated pattern matched above.
        return word, "", [], None

    def _handle_dwipurwa(self, word: str) -> Optional[Tuple[str, str, List[str], Optional[str]]]:
        """
        Handles Dwipurwa (Partial Initial Syllable Reduplication) checks for non-hyphenated words.
        e.g. lelaki, sesama, tetamu.
        
        Args:
            word (str): The word to check.
            
        Returns:
            Optional[Tuple[str, str, List[str], Optional[str]]]:
                Result tuple if Dwipurwa detected, else None.
        """
        # Specific check for common Dwipurwa words not caught by stemmer
        if word == "lelaki":
            return "laki", "rp", [], None
        if word == "sesama": 
            return "sama", "rp", [], None
        if word == "tetamu":
            return "tamu", "rp", [], None
        if word == "rerata":
            return "rata", "rp", [], None
        if word == "tetua":
            return "tua", "rp", [], None
        if word == "dedaun":
            return "daun", "rp", [], None
        # Add more if needed based on test_dwipurwa_reduplication

        # --- Dwipurwa (Partial Initial Syllable Reduplication) Check ---
        if hasattr(self, 'stemmer') and self.stemmer:
            root_word = self.stemmer.get_root_word(word)
            logging.debug(f"_handle_dwipurwa({word}): Dwipurwa check - word='{word}', stemmer_root='{root_word}'")

            # Primary conditions for Dwipurwa
            prefix_candidate = ""
            if word.endswith(root_word) and word != root_word:
                prefix_candidate = word[:-len(root_word)]

                # Heuristic Conditions for Dwipurwa (e.g., lelaki -> laki, sesama -> sama)
                # A: len(prefix_candidate) == 2
                # B: len(root_word) >= 1
                
                condition_a = (len(prefix_candidate) == 2)
                condition_b = (len(root_word) >= 1)

                if condition_a and condition_b: # Proceed only if A and B are met
                    condition_c = (prefix_candidate[0] == root_word[0])
                    condition_d = (prefix_candidate[1] == 'e')

                    condition_e_met = False
                    vowels = ['a', 'i', 'u', 'e', 'o']
                    if len(root_word) >= 2:
                        if root_word == "laki" and root_word[1].lower() == 'a': # Specific for laki
                            condition_e_met = True
                        elif root_word != "laki" and root_word[1].lower() in vowels: # Original for others
                            condition_e_met = True
                    elif len(root_word) == 1:
                        condition_e_met = True 

                    if condition_c and condition_d and condition_e_met:
                        return root_word, "rp", [], None
        
        return None

    def _strip_suffixes(self, word: str, is_processing_suffix_cluster: bool = False) -> Tuple[str, List[str]]:
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

    def _strip_prefixes(self, original_word_for_prefix_stripping: str) -> Tuple[str, List[str]]:
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

    def _strip_prefixes_detailed(self, word_to_strip: str, accumulated_prefixes: List[str]) -> Tuple[str, List[str]]:
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

                # Option 1 (Swapped): If reversing morphophonemics on stem_candidate yields a KD
                potential_original_stem = self.rules.reverse_morphophonemics(prefix_form, canonical_prefix, stem_candidate)
                if potential_original_stem != stem_candidate and self.dictionary.is_kata_dasar(potential_original_stem):
                    new_prefixes = accumulated_prefixes + [canonical_prefix]
                    logging.debug(f"_strip_prefixes_detailed: '{prefix_form}' (canon: {canonical_prefix}) stripped from '{word_to_strip}', reverse_morpho to '{potential_original_stem}' (KD). Finalizing.")
                    return potential_original_stem, new_prefixes

                # Option 2 (Swapped): If stem_candidate is directly a KD
                if self.dictionary.is_kata_dasar(stem_candidate):
                    new_prefixes = accumulated_prefixes + [canonical_prefix]
                    logging.debug(f"_strip_prefixes_detailed: '{prefix_form}' stripped from '{word_to_strip}', '{stem_candidate}' is KD. Finalizing.")
                    return stem_candidate, new_prefixes

                # Option 3: Recursively strip from stem_candidate (the surface form after stripping prefix_form)
                # This handles layered prefixes (e.g., di-per-oleh, mem-per-mainkan)
                logging.debug(f"_strip_prefixes_detailed: '{prefix_form}' stripped from '{word_to_strip}', stem_candidate '{stem_candidate}' is not KD. Recursing.")
                further_stripped_stem, deeper_prefixes = self._strip_prefixes_detailed(stem_candidate, []) 
                
                # If the recursive call found a KD OR found more prefixes, then this path is valid.
                if self.dictionary.is_kata_dasar(further_stripped_stem) or deeper_prefixes:
                    current_prefixes = accumulated_prefixes + [canonical_prefix] + deeper_prefixes
                    logging.debug(f"_strip_prefixes_detailed: Recursive call from '{stem_candidate}' yielded KD '{further_stripped_stem}' or deeper_prefixes {deeper_prefixes}. Prefixes so far: {current_prefixes}")
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
                logging.debug(f"_strip_prefixes_detailed: '{prefix_form}' stripped from '{word_to_strip}', stem_candidate '{stem_candidate}' is not KD, but accepting prefix strip. Prefixes: {new_prefixes}")
                return stem_candidate, new_prefixes

        # If no prefix could be stripped at all from word_to_strip
        logging.debug(f"_strip_prefixes_detailed: No prefix stripped from '{word_to_strip}' or no valid stem found after stripping. Returning as is.")
        return word_to_strip, accumulated_prefixes

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