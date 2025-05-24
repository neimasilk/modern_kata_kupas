import re
import logging
from .rules import MorphologicalRules
from .dictionary_manager import DictionaryManager
# from typing import TYPE_CHECKING # Optional, for type hinting
# if TYPE_CHECKING:
#     from .rules import MorphologicalRules
#     from .dictionary_manager import DictionaryManager

class Reconstructor:
    """
    Reconstructs an Indonesian word from its segmented morpheme string.

    This class uses morphological rules and dictionary information to correctly
    reassemble a word from its components (root, prefixes, suffixes, reduplication markers),
    applying necessary morphophonemic changes in the process.

    Attributes:
        rules (MorphologicalRules): An instance of MorphologicalRules containing
                                    the affix rules and morphophonemic rules.
        dictionary (DictionaryManager): An instance of DictionaryManager for
                                        validating root words, if needed during reconstruction.
    """
    def __init__(self, rules: 'MorphologicalRules', dictionary_manager: 'DictionaryManager'):
        """
        Initializes the Reconstructor.

        Args:
            rules (MorphologicalRules): An instance of MorphologicalRules, providing
                                        access to affix definitions and morphophonemic rules.
            dictionary_manager (DictionaryManager): An instance of DictionaryManager,
                                                    used for dictionary lookups (e.g.
                                                    validating monosyllabic roots).
        """
        self.rules = rules
        self.dictionary = dictionary_manager

    def parse_segmented_string(self, segmented_word: str) -> dict:
        """
        Parses a tilde-separated segmented word string into its morphemic components.

        The method identifies the root, prefixes, various types of suffixes
        (derivational, particle, possessive, suffixes after reduplication),
        and reduplication markers including any variants for phonetic change reduplication.

        Args:
            segmented_word (str): The segmented word string, e.g., "meN~per~main~kan~lah".
                                  An empty string or a string without tildes (assumed root)
                                  are handled gracefully.

        Returns:
            dict: A dictionary containing the parsed morphemes. Keys include:
                  "root" (str|None): The identified root word.
                  "prefixes" (list[str]): List of identified prefixes.
                  "suffixes_derivational" (list[str]): List of derivational suffixes.
                  "suffixes_particle" (list[str]): List of particle suffixes.
                  "suffixes_possessive" (list[str]): List of possessive suffixes.
                  "suffixes_after_reduplication" (list[str]): Derivational suffixes
                                                             attached after a reduplication marker.
                  "redup_marker" (str|None): The reduplication marker ("ulg", "rp", "rs").
                  "redup_variant" (str|None): The variant part for "rs" (e.g., "mayur").
                  Returns a dict with None/empty lists if input is empty.
                  If input has no tildes, "root" is set to the input string.
        """
        logging.debug(f"parse_segmented_string CALLED with: '{segmented_word}'")
        result = {
            "root": None,
            "prefixes": [],
            "suffixes_derivational": [],
            "suffixes_particle": [],
            "suffixes_possessive": [],
            "suffixes_after_reduplication": [], # New category
            "redup_marker": None, # "ulg", "rp", "rs"
            "redup_variant": None, # e.g., "mayur" for "rs(~mayur)"
        }

        if not segmented_word:
            return result # Return empty dict if input is empty
        
        if '~' not in segmented_word:
            result["root"] = segmented_word
            return result

        # Placeholder strategy for rs(~variant)
        rs_placeholder = "__RS_VARIANT_MARKER__"
        original_rs_segment = None

        # Find if rs(~variant) exists
        # Example: "sayur~rs(~mayur)" or "rs(~mayur)" or "prefix~rs(~mayur)~suffix"
        # Regex to find "rs(~...)" that is a whole segment (preceded by ~ or start, followed by ~ or end)
        
        # First, try to isolate the rs(~...) segment string if it exists
        # This regex captures "rs(~...)"
        rs_pattern_match = re.search(r"(rs\(\~[^)]+\))", segmented_word)
        
        temp_word_for_splitting = segmented_word
        
        if rs_pattern_match:
            original_rs_segment = rs_pattern_match.group(1) # This is "rs(~mayur)"
            # Replace it with a placeholder before splitting
            temp_word_for_splitting = segmented_word.replace(original_rs_segment, rs_placeholder, 1)

        parts = temp_word_for_splitting.split('~')
        
        # Restore the original_rs_segment if placeholder is present
        for i, p in enumerate(parts):
            if p == rs_placeholder:
                parts[i] = original_rs_segment # Restore "rs(~mayur)"

        if segmented_word == "sayur~rs(~mayur)":
            logging.debug(f"parse_segmented_string: Input for 'sayur~rs(~mayur)': '{segmented_word}'")
            logging.debug(f"parse_segmented_string: Temp word for splitting for 'sayur~rs(~mayur)': '{temp_word_for_splitting}'")
            logging.debug(f"parse_segmented_string: Parts after split and restore for 'sayur~rs(~mayur)': {parts}")
            
        root_candidates = []
        previous_part_was_redup_marker = False

        for part_idx, part in enumerate(parts):
            logging.debug(f"parse_segmented_string: Processing part '{part}' from {parts}")
            current_part_is_redup_marker = False
            if segmented_word == "sayur~rs(~mayur)": # Keep this specific detail log if needed for this case
                logging.debug(f"parse_segmented_string (sayur~rs(~mayur)): Current part: '{part}', startswith('rs('): {part.startswith('rs(')}, endswith(')'): {part.endswith(')')}")
            
            if not part: # Handle cases like "~~" or trailing/leading "~"
                previous_part_was_redup_marker = False # Reset if empty part
                continue

            # 1. Check for Reduplication Markers
            if part == "ulg":
                result["redup_marker"] = "ulg"
                current_part_is_redup_marker = True
                logging.debug(f"parse_segmented_string:   Part '{part}' identified as redup_marker='ulg'")
            elif part == "rp":
                result["redup_marker"] = "rp"
                current_part_is_redup_marker = True
                logging.debug(f"parse_segmented_string:   Part '{part}' identified as redup_marker='rp'")
            elif part.startswith("rs(") and part.endswith(")") and part.count('~') == 1 and part.startswith("rs(~"):
                result["redup_marker"] = "rs"
                variant = part[len("rs(~"):-1] 
                if variant: 
                    result["redup_variant"] = variant
                current_part_is_redup_marker = True
                logging.debug(f"parse_segmented_string:   Part '{part}' identified as redup_marker='rs' with variant='{variant}'")
            elif part.startswith("rs(") and part.endswith(")"): # Fallback for rs(variant) without internal tilde
                result["redup_marker"] = "rs"
                variant = part[len("rs("):-1]
                if variant:
                    result["redup_variant"] = variant
                current_part_is_redup_marker = True
                logging.debug(f"parse_segmented_string:   Part '{part}' identified as redup_marker='rs' (no tilde) with variant='{variant}'")
            
            if current_part_is_redup_marker:
                previous_part_was_redup_marker = True
                continue

            # 2. Check for Prefixes using MorphologicalRules
            is_pfx = self.rules.is_prefix(part)
            if is_pfx:
                result["prefixes"].append(part)
                logging.debug(f"parse_segmented_string:   Part '{part}' identified as PREFIX. Current prefixes: {result['prefixes']}")
                previous_part_was_redup_marker = False # Reset
                continue
            
            # 3. Check for Suffixes using MorphologicalRules
            is_sfx = self.rules.is_suffix(part)
            if is_sfx:
                suffix_type = self.rules.get_suffix_type(part)
                logging.debug(f"parse_segmented_string:   Part '{part}' identified as SUFFIX of type '{suffix_type}'")
                if previous_part_was_redup_marker and suffix_type == "suffix_derivational":
                    result["suffixes_after_reduplication"].append(part)
                    logging.debug(f"parse_segmented_string:     Added '{part}' to suffixes_after_reduplication. Current: {result['suffixes_after_reduplication']}")
                elif suffix_type == "suffix_derivational":
                    result["suffixes_derivational"].append(part)
                    logging.debug(f"parse_segmented_string:     Added '{part}' to suffixes_derivational. Current: {result['suffixes_derivational']}")
                elif suffix_type == "particle":
                    result["suffixes_particle"].append(part)
                elif suffix_type == "possessive":
                    result["suffixes_possessive"].append(part)
                else: # Should not happen if suffix_type is one of the above
                    root_candidates.append(part) 
                previous_part_was_redup_marker = False # Reset
                continue
            
            # 4. If not a known marker or affix, it's a root candidate
            root_candidates.append(part)
            previous_part_was_redup_marker = False # Reset

        # Root Identification:
        if root_candidates:
            found_dict_root = False
            logging.debug(f"parse_segmented_string: Root candidates: {root_candidates}")
            # Prioritize candidates that are known dictionary words
            for r_cand in root_candidates:
                is_kd = self.dictionary.is_kata_dasar(r_cand)
                logging.debug(f"parse_segmented_string:   Checking root candidate '{r_cand}'. Is KD? {is_kd}")
                if is_kd:
                    result["root"] = r_cand
                    found_dict_root = True
                    logging.debug(f"parse_segmented_string:     Root identified as '{r_cand}' (is KD)")
                    break
            if not found_dict_root:
                result["root"] = root_candidates[0] 
                logging.debug(f"parse_segmented_string:   No KD root found in candidates. Fallback: root set to first candidate '{result['root']}'")
        
        logging.debug(f"parse_segmented_string: Returning parsed result: {result}")
        return result

    def _apply_reduplication_reconstruction(self, stem: str, marker: str, variant: str = None) -> str:
        if not stem: # Should not happen if called correctly
            return ""

        if marker == "ulg":
            return f"{stem}-{stem}"
        elif marker == "rp":
            # Reverses the Dwipurwa segmentation (e.g., laki -> lelaki)
            # Assumes the first char of stem is consonant, followed by 'e'
            if len(stem) >= 1:
                return stem[0] + 'e' + stem 
            else: # Should not happen with valid stem for Dwipurwa
                return stem 
        elif marker == "rs":
            if variant:
                # The variant as parsed from "rs(variant_content)" will just be "variant_content"
                # If variant is "~mayur", we want "mayur"
                actual_variant = variant
                if actual_variant.startswith("~"):
                    actual_variant = actual_variant[1:]
                return f"{stem}-{actual_variant}"
            else:
                # This case (rs marker without variant) should ideally not occur if parsing is correct
                return f"{stem}-<unknown_variant>" # Or just stem
        else: # Unknown marker
            return stem

    def reconstruct(self, segmented_word: str) -> str:
        """
        Reconstructs an original Indonesian word from its tilde-separated morpheme string.

        The process involves:
        1. Parsing the segmented string into its constituent morphemes.
        2. Applying derivational suffixes to the root.
        3. Applying reduplication rules if a marker is present.
        4. Applying any suffixes that appear after reduplication.
        5. Applying possessive and particle suffixes.
        6. Applying prefixes in reverse order, with morphophonemic changes.

        Args:
            segmented_word (str): A string of morphemes separated by tildes (~),
                                  e.g., "meN~tulis", "buku~ulg~nya".

        Returns:
            str: The reconstructed original word. Returns an empty string if the input
                 is empty or if the root cannot be identified from parsing.
        """
        logging.debug(f"Reconstructor.reconstruct CALLED with segmented_word='{segmented_word}'")
        if not segmented_word:
            logging.debug("Reconstructor.reconstruct: Empty segmented_word, returning empty string.")
            return ""
        
        parsed_morphemes = self.parse_segmented_string(segmented_word)
        logging.debug(f"Reconstructor.reconstruct: Parsed morphemes for '{segmented_word}': {parsed_morphemes}")
        
        if segmented_word == "makan~an": # Example of keeping a specific detailed log
            logging.debug(f"Reconstructor.reconstruct (makan~an): Parsed morphemes: {parsed_morphemes}")
        if segmented_word == "sayur~rs(~mayur)": # Example of keeping a specific detailed log
            logging.debug(f"Reconstructor.reconstruct (sayur~rs(~mayur)): Parsed morphemes: {parsed_morphemes}")
            
        current_form = parsed_morphemes.get("root")
        if not current_form:
            logging.debug(f"Reconstructor.reconstruct: Root is None after parsing. segmented_word='{segmented_word}'. Returning based on tilde presence.")
            return segmented_word if '~' not in segmented_word and parsed_morphemes.get("root") == segmented_word else ""

        logging.debug(f"Reconstructor.reconstruct: Initial current_form (root): '{current_form}'")

        # 1. Apply DERIVATIONAL suffixes first
        derivational_suffixes = parsed_morphemes.get("suffixes_derivational", [])
        if derivational_suffixes:
            logging.debug(f"Reconstructor.reconstruct: Applying derivational suffixes: {derivational_suffixes}")
        for suffix in derivational_suffixes:
            current_form += suffix
            logging.debug(f"Reconstructor.reconstruct:   After suffix '{suffix}', current_form: '{current_form}'")

        # 2. Apply Reduplication
        redup_marker = parsed_morphemes.get("redup_marker")
        redup_variant = parsed_morphemes.get("redup_variant")
        
        if redup_marker:
            logging.debug(f"Reconstructor.reconstruct: Applying reduplication. Marker: '{redup_marker}', Variant: '{redup_variant}', Base: '{current_form}'")
            current_form = self._apply_reduplication_reconstruction(current_form, redup_marker, redup_variant)
            logging.debug(f"Reconstructor.reconstruct:   After reduplication, current_form: '{current_form}'")

        # 3. Apply SUFFIXES_AFTER_REDUPLICATION
        suffixes_after_redup = parsed_morphemes.get("suffixes_after_reduplication", [])
        if suffixes_after_redup:
            logging.debug(f"Reconstructor.reconstruct: Applying suffixes_after_reduplication: {suffixes_after_redup}")
        for suffix in suffixes_after_redup:
            current_form += suffix # Suffixes are typically simple appends at this stage
            logging.debug(f"Reconstructor.reconstruct:   After suffix_after_redup '{suffix}', current_form: '{current_form}'")

        # 4. Apply POSSESSIVE and PARTICLE suffixes 
        possessive_suffixes = parsed_morphemes.get("suffixes_possessive", [])
        if possessive_suffixes:
            logging.debug(f"Reconstructor.reconstruct: Applying possessive suffixes: {possessive_suffixes}")
        for suffix in possessive_suffixes:
            current_form += suffix
            logging.debug(f"Reconstructor.reconstruct:   After suffix '{suffix}', current_form: '{current_form}'")
            
        particle_suffixes = parsed_morphemes.get("suffixes_particle", [])
        if particle_suffixes:
            logging.debug(f"Reconstructor.reconstruct: Applying particle suffixes: {particle_suffixes}")
        for suffix in particle_suffixes:
            current_form += suffix
            logging.debug(f"Reconstructor.reconstruct:   After suffix '{suffix}', current_form: '{current_form}'")
        
        # 5. Apply Prefixes
        prefixes_to_apply = parsed_morphemes.get("prefixes", [])
        if prefixes_to_apply:
            logging.debug(f"Reconstructor.reconstruct: Applying prefixes (in reverse): {prefixes_to_apply}")
        for prefix_morpheme in reversed(prefixes_to_apply):
            logging.debug(f"Reconstructor.reconstruct:   Calling _apply_forward_morphophonemics for prefix '{prefix_morpheme}' on base '{current_form}' with original_root='{parsed_morphemes.get('root')}'")
            current_form = self._apply_forward_morphophonemics(prefix_morpheme, current_form, original_root=parsed_morphemes.get('root'))
            logging.debug(f"Reconstructor.reconstruct:   After prefix '{prefix_morpheme}', current_form: '{current_form}'")

        logging.debug(f"Reconstructor.reconstruct: Final reconstructed form for '{segmented_word}': '{current_form}'")
        return current_form

    def _is_monosyllabic_heuristic(self, word: str) -> bool:
        """
        Heuristic check if a word is monosyllabic and a known kata dasar.
        """
        if not word:
            return False
        vowels = "aiueoAIUEO"
        vowel_count = sum(1 for char in word if char in vowels)
        # A word is considered monosyllabic if it has one vowel sound AND is in the dictionary.
        return vowel_count == 1 and self.dictionary.is_kata_dasar(word)

    def _apply_forward_morphophonemics(self, prefix_canonical_form: str, base_word: str, original_root: str = None) -> str:
        """
        Applies forward morphophonemic rules for a given prefix and base word.
        Example: prefix_canonical_form="meN", base_word="pukul" -> "memukul"
                 prefix_canonical_form="ber", base_word="ajar" -> "belajar"
        Args:
            prefix_canonical_form (str): The canonical form of the prefix.
            base_word (str): The current form of the word to which the prefix is being attached.
            original_root (str, optional): The original root word from segmentation. Used for specific checks like monosyllabicity.
        """
        logging.debug(f"_apply_forward_morphophonemics CALLED with prefix_canonical_form='{prefix_canonical_form}', base_word='{base_word}', original_root='{original_root}'")

        if not base_word:
            logging.debug(f"_apply_forward_morphophonemics: base_word is empty. Returning prefix_canonical_form: '{prefix_canonical_form}'")
            return prefix_canonical_form

        # self.rules.prefix_rules is now keyed by canonical forms (e.g., "meN", "di").
        # The value is a list of rule dictionaries (usually one for canonical keys).
        relevant_rule_list = self.rules.prefix_rules.get(prefix_canonical_form)
        
        if not relevant_rule_list:
            logging.debug(f"_apply_forward_morphophonemics: No relevant_rule_list found for prefix_canonical_form='{prefix_canonical_form}'. Returning prefix_canonical_form + base_word: '{prefix_canonical_form + base_word}'")
            return prefix_canonical_form + base_word

        # relevant_rule_list is a list of rule dicts. We typically expect one dict for a canonical prefix.
        actual_rule_details_dict = None
        if relevant_rule_list and isinstance(relevant_rule_list[0], dict):
            actual_rule_details_dict = relevant_rule_list[0]
            logging.debug(f"_apply_forward_morphophonemics: actual_rule_details_dict set to: {actual_rule_details_dict}")
        
        if not actual_rule_details_dict:
            logging.debug(f"_apply_forward_morphophonemics: actual_rule_details_dict is None. Returning prefix_canonical_form + base_word: '{prefix_canonical_form + base_word}'")
            return prefix_canonical_form + base_word

        allomorphs = actual_rule_details_dict.get("allomorphs")
        logging.debug(f"_apply_forward_morphophonemics: Allomorphs for '{prefix_canonical_form}': {allomorphs}")

        if not allomorphs:
            prefix_to_attach = prefix_canonical_form
            if 'surface' in actual_rule_details_dict:
                 prefix_to_attach = actual_rule_details_dict['surface']
                 logging.debug(f"_apply_forward_morphophonemics: No allomorphs. Using 'surface' for prefix_to_attach: '{prefix_to_attach}'")
            elif 'form' in actual_rule_details_dict:
                 # Using canonical form as `form` usually contains hyphen, e.g. "di-"
                 logging.debug(f"_apply_forward_morphophonemics: No allomorphs. Using canonical_form for prefix_to_attach: '{prefix_to_attach}' (rule form was '{actual_rule_details_dict['form']}')")
            else:
                 logging.debug(f"_apply_forward_morphophonemics: No allomorphs and no surface/form key. Using canonical_form for prefix_to_attach: '{prefix_to_attach}'")

            result = prefix_to_attach + base_word
            logging.debug(f"_apply_forward_morphophonemics: No allomorphs. Returning prefix_to_attach + base_word: '{result}'")
            return result

        for allomorph_rule in allomorphs:
            logging.debug(f"_apply_forward_morphophonemics: Evaluating allomorph_rule: {allomorph_rule}")
            surface_form = allomorph_rule.get("surface")
            if not surface_form:
                logging.debug("_apply_forward_morphophonemics:   No surface_form in rule. Skipping.")
                continue

            match = False
            # 1. Check for monosyllabic root condition
            if "is_monosyllabic_root" in allomorph_rule:
                # Use original_root for this check if available, otherwise fallback to base_word
                word_for_monosyllabic_check = original_root if original_root else base_word
                is_mono = self._is_monosyllabic_heuristic(word_for_monosyllabic_check)
                logging.debug(f"_apply_forward_morphophonemics:   Checking is_monosyllabic_root for word_for_check='{word_for_monosyllabic_check}'. Heuristic result: {is_mono}")
                if is_mono:
                    match = True
                    logging.debug("_apply_forward_morphophonemics:     is_monosyllabic_root MATCHED.")
            
            # 2. Check for exact root condition
            if not match and "condition_exact_root" in allomorph_rule:
                logging.debug(f"_apply_forward_morphophonemics:   Checking condition_exact_root for base_word='{base_word}'. Exact roots: {allomorph_rule['condition_exact_root']}")
                if base_word in allomorph_rule["condition_exact_root"]:
                    match = True
                    logging.debug("_apply_forward_morphophonemics:     condition_exact_root MATCHED.")
            
            # 3. Check for root starting character condition (using "next_char_is" from rules.json)
            if not match and "next_char_is" in allomorph_rule:
                starts_with_chars = allomorph_rule['next_char_is']
                logging.debug(f"_apply_forward_morphophonemics:   Checking next_char_is for base_word='{base_word}'. Starts with: {starts_with_chars}")
                if any(base_word.startswith(char) for char in starts_with_chars):
                    match = True
                    logging.debug("_apply_forward_morphophonemics:     next_char_is MATCHED.")
            
            is_default_allomorph = not any(k in allomorph_rule for k in 
                                           ["is_monosyllabic_root",
                                            "condition_exact_root", 
                                            "next_char_is"])
            if not match and is_default_allomorph:
                match = True
                logging.debug("_apply_forward_morphophonemics:   Is DEFAULT allomorph. MATCHED.")


            if match:
                logging.debug(f"_apply_forward_morphophonemics:   Allomorph rule MATCHED. Surface form: '{surface_form}'")
                current_base_word = base_word # Initialize with original base word
                elision_char = allomorph_rule.get("reconstruct_root_initial")
                elision_applies = allomorph_rule.get("elision", False)

                # Special condition for meN- + per- combination: avoid eliding 'p' from 'per'
                is_men_per_combination = (prefix_canonical_form == "meN" and 
                                          base_word.startswith("per") and 
                                          elision_char == "p")

                if elision_char and elision_applies and not is_men_per_combination:
                    logging.debug(f"_apply_forward_morphophonemics:     Elision char specified: '{elision_char}'. current_base_word starts with it? {current_base_word.startswith(elision_char)}")
                    if current_base_word.startswith(elision_char):
                        current_base_word = current_base_word[len(elision_char):]
                        logging.debug(f"_apply_forward_morphophonemics:     Elision applied. New current_base_word: '{current_base_word}'")
                    else:
                        logging.debug("_apply_forward_morphophonemics:     Elision char specified, but base does not start with it. Elision NOT applied.")
                elif is_men_per_combination:
                    logging.debug("_apply_forward_morphophonemics:     meN-per- combination detected. Suppressing elision of 'p' from 'per'.")
                
                result = surface_form + current_base_word
                logging.debug(f"_apply_forward_morphophonemics:   Returning surface_form + current_base_word: '{result}'")
                return result
            else:
                logging.debug("_apply_forward_morphophonemics:   Allomorph rule DID NOT MATCH.")
        
        # Fallback if no allomorphs matched
        prefix_surface_form = actual_rule_details_dict.get("form", prefix_canonical_form)
        result = prefix_surface_form + base_word
        logging.debug(f"_apply_forward_morphophonemics: No allomorphs matched in loop. Returning fallback: '{result}' (used prefix_surface_form='{prefix_surface_form}')")
        return result
