import re
from .rules import MorphologicalRules
from .dictionary_manager import DictionaryManager
# from typing import TYPE_CHECKING # Optional, for type hinting
# if TYPE_CHECKING:
#     from .rules import MorphologicalRules
#     from .dictionary_manager import DictionaryManager

class Reconstructor:
    def __init__(self, rules: 'MorphologicalRules', dictionary_manager: 'DictionaryManager'):
        self.rules = rules
        self.dictionary = dictionary_manager

    def parse_segmented_string(self, segmented_word: str) -> dict:
        result = {
            "root": None,
            "prefixes": [],
            "suffixes_derivational": [],
            "suffixes_particle": [],
            "suffixes_possessive": [],
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
            print(f"DEBUG_SAYUR: Input to parse_segmented_string: '{segmented_word}'")
            print(f"DEBUG_SAYUR: Temp word for splitting: '{temp_word_for_splitting}'")
            print(f"DEBUG_SAYUR: Parts after split and restore: {parts}")
            
        root_candidates = []

        for part_idx, part in enumerate(parts):
            if segmented_word == "sayur~rs(~mayur)":
                print(f"DEBUG_SAYUR: Current part: '{part}'")
                print(f"DEBUG_SAYUR: part.startswith('rs('): {part.startswith('rs(')}")
                print(f"DEBUG_SAYUR: part.endswith(')'): {part.endswith(')')}")
            
            if not part: # Handle cases like "~~" or trailing/leading "~"
                continue

            # 1. Check for Reduplication Markers
            if part == "ulg":
                result["redup_marker"] = "ulg"
                continue
            if part == "rp":
                result["redup_marker"] = "rp"
                continue
            # This now expects `part` to be exactly "rs(~mayur)"
            if part.startswith("rs(") and part.endswith(")") and part.count('~') == 1 and part.startswith("rs(~"):
                result["redup_marker"] = "rs"
                variant = part[len("rs(~"):-1] # Extracts "mayur" from "rs(~mayur)"
                if variant: 
                    result["redup_variant"] = variant # variant is "mayur"
                continue
            # Fallback for rs(variant) without internal tilde, if ever needed.
            elif part.startswith("rs(") and part.endswith(")"):
                result["redup_marker"] = "rs"
                variant = part[len("rs("):-1] # Extracts "mayur" from "rs(mayur)"
                if variant:
                    result["redup_variant"] = variant
                continue

            # 2. Check for Prefixes using MorphologicalRules
            if self.rules.is_prefix(part): # Assumes is_prefix checks canonical forms
                result["prefixes"].append(part)
                continue
            
            # 3. Check for Suffixes using MorphologicalRules
            if self.rules.is_suffix(part): # Assumes is_suffix checks canonical forms
                suffix_type = self.rules.get_suffix_type(part)
                if suffix_type == "suffix_derivational":
                    result["suffixes_derivational"].append(part)
                elif suffix_type == "particle":
                    result["suffixes_particle"].append(part)
                elif suffix_type == "possessive":
                    result["suffixes_possessive"].append(part)
                else:
                    root_candidates.append(part) # Unknown suffix type
                continue
            
            # 4. If not a known marker or affix, it's a root candidate
            root_candidates.append(part)

        # Root Identification:
        if root_candidates:
            found_dict_root = False
            # Prioritize candidates that are known dictionary words
            for r_cand in root_candidates:
                if self.dictionary.is_kata_dasar(r_cand): # Assumes is_kata_dasar is available
                    result["root"] = r_cand
                    found_dict_root = True
                    break
            if not found_dict_root:
                # Fallback: if no candidate is in dictionary, use the first one.
                # This could be refined (e.g., longest, or specific position)
                result["root"] = root_candidates[0] 
        
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
        if not segmented_word:
            return ""
        
        parsed_morphemes = self.parse_segmented_string(segmented_word)
        
        if segmented_word == "makan~an":
            print(f"DEBUG parsed_morphemes for makan~an: {parsed_morphemes}")
        if segmented_word == "sayur~rs(~mayur)":
            print(f"DEBUG parsed_morphemes for sayur~rs(~mayur): {parsed_morphemes}")
            
        current_form = parsed_morphemes.get("root")
        if not current_form: # If root is None
            return segmented_word if '~' not in segmented_word and parsed_morphemes.get("root") == segmented_word else ""

        # 1. Apply DERIVATIONAL suffixes first
        for suffix in parsed_morphemes.get("suffixes_derivational", []):
            current_form += suffix

        # 2. Apply Reduplication
        redup_marker = parsed_morphemes.get("redup_marker")
        redup_variant = parsed_morphemes.get("redup_variant") # Will be None if not "rs" type or if variant is empty
        
        if redup_marker:
            current_form = self._apply_reduplication_reconstruction(current_form, redup_marker, redup_variant)

        # 3. Apply POSSESSIVE and PARTICLE suffixes AFTER reduplication
        for suffix in parsed_morphemes.get("suffixes_possessive", []):
            current_form += suffix
            
        for suffix in parsed_morphemes.get("suffixes_particle", []):
            current_form += suffix
        
        # Placeholder for subsequent steps (prefixes)
        for prefix_morpheme in reversed(parsed_morphemes.get("prefixes", [])):
            current_form = self._apply_forward_morphophonemics(prefix_morpheme, current_form)

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

    def _apply_forward_morphophonemics(self, prefix_canonical_form: str, base_word: str) -> str:
        """
        Applies forward morphophonemic rules for a given prefix and base word.
        Example: prefix_canonical_form="meN-", base_word="pukul" -> "memukul"
                 prefix_canonical_form="ber-", base_word="ajar" -> "belajar"
        """
        if prefix_canonical_form == "meN" and base_word.startswith("per"):
            return "mem" + base_word
            
        rule_details = self.rules.get_rule_details(prefix_canonical_form)

        if not rule_details:
            # Simple prefix like 'di-', 'ke-', 'se-' or unknown prefix
            # For 'di-', 'ke-', 'se-', the canonical form itself is the surface form.
            # If prefix_canonical_form includes a hyphen (e.g., "di-"), remove it.
            # However, parser provides "di", "ke".
            # The rules.json for simple prefixes has "form": "di", "canonical": "di".
            # So, prefix_canonical_form here would be "di".
            return prefix_canonical_form + base_word

        allomorphs = rule_details.get("allomorphs")
        if not allomorphs: # Should have a default allomorph if it's a complex prefix
            return rule_details.get("form", prefix_canonical_form) + base_word

        # --- Start of specific handling for peN- prefix for monosyllabic roots ---
        if prefix_canonical_form == "peN":
            for allomorph_rule_check in allomorphs: 
                if allomorph_rule_check.get("is_monosyllabic_root"):
                    if self._is_monosyllabic_heuristic(base_word):
                        surface_form = allomorph_rule_check.get("surface") 
                        # print(f"DEBUG reconstruct peN-: Matched monosyllabic rule '{surface_form}' for base '{base_word}'.")
                        return surface_form + base_word 
            # If monosyllabic rule for peN- didn't match and return, proceed to other allomorphs below.
        # --- End of specific handling for peN- prefix ---

        if prefix_canonical_form == "peN" and base_word == "tulis":
            print(f"DEBUG peN~tulis: Entering main loop. Allomorphs for peN: {allomorphs}")

        # Iterate through allomorphs to find the matching one
        for allomorph_rule in allomorphs:
            # If peN- and this is the monosyllabic rule, skip it as it was handled in the pre-pass.
            if prefix_canonical_form == "peN" and allomorph_rule.get("is_monosyllabic_root"):
                if base_word == "tulis": print("DEBUG peN~tulis: Skipping monosyllabic rule in main loop as expected.")
                continue

            surface_form = allomorph_rule.get("surface")
            if not surface_form:
                continue # Malformed rule

            # Condition checks
            conditions_met = 0
            expected_conditions = 0
            
            # 1. Monosyllabic root condition
            if allomorph_rule.get("is_monosyllabic_root"):
                expected_conditions += 1
                if self._is_monosyllabic_heuristic(base_word):
                    conditions_met += 1
                else:
                    continue # This allomorph doesn't apply
            
            
            # 2. Root starting character condition(s)
            # This condition checks if the base_word starts with a character that this allomorph is specific to.
            # The affix_rules.json uses "condition_root_starts_with" for this kind of phonological conditioning.
            # Previous code was mistakenly using "next_char_is" here.
            condition_to_check = allomorph_rule.get("condition_root_starts_with") # Using the correct key
            if condition_to_check: 
                expected_conditions += 1
                if any(base_word.startswith(char) for char in condition_to_check): 
                    conditions_met += 1
                else:
                    if prefix_canonical_form == "peN" and base_word == "tulis":
                        print(f"DEBUG peN~tulis: Allomorph {surface_form} skipped, condition_root_starts_with {condition_to_check} not met by '{base_word}'.")
                    continue 
            
            # 3. Exact root condition 
            condition_exact_root = allomorph_rule.get("condition_exact_root") 
            if condition_exact_root:
                expected_conditions += 1
                if base_word in condition_exact_root:
                    conditions_met += 1
                else:
                    if prefix_canonical_form == "peN" and base_word == "tulis":
                         print(f"DEBUG peN~tulis: Allomorph {surface_form} skipped, condition_exact_root {condition_exact_root} not met by '{base_word}'.")
                    continue 

            if expected_conditions > 0 and conditions_met != expected_conditions:
                if prefix_canonical_form == "peN" and base_word == "tulis": 
                    print(f"DEBUG peN~tulis: Skipped allomorph {surface_form} due to overall condition mismatch. Expected: {expected_conditions}, Met: {conditions_met}")
                continue
            
            if prefix_canonical_form == "peN" and base_word == "tulis": 
                print(f"DEBUG peN~tulis: Matched allomorph {surface_form}. Details: {allomorph_rule}")
            
            temp_base_word = base_word
            
            char_elided_from_root = allomorph_rule.get("reconstruct_root_initial") 
            elision_type = allomorph_rule.get("elision")

            if elision_type and isinstance(char_elided_from_root, str): 
                if temp_base_word.startswith(char_elided_from_root):
                    temp_base_word = temp_base_word[len(char_elided_from_root):]
                    if prefix_canonical_form == "peN" and base_word == "tulis": 
                        print(f"DEBUG peN~tulis: Elision applied for '{char_elided_from_root}'. Temp_base_word now: '{temp_base_word}'")
                elif prefix_canonical_form == "peN" and base_word == "tulis": 
                     print(f"DEBUG peN~tulis: Elision active for {surface_form}, but base_word '{temp_base_word}' does not start with elision char '{char_elided_from_root}'. No elision performed.")
            elif prefix_canonical_form == "peN" and base_word == "tulis": 
                 print(f"DEBUG peN~tulis: No elision applied for {surface_form}. elision_type: {elision_type}, char_elided_spec: {char_elided_from_root}")
            elif elision_type == "vowel_sound_meng": 
                pass

            return surface_form + temp_base_word

        default_surface = prefix_canonical_form.replace('N', '') 
        if default_surface.endswith('-'): default_surface = default_surface[:-1] 
        
        if prefix_canonical_form == "peN" and base_word == "tulis": 
            print(f"DEBUG peN~tulis: No allomorph matched for '{base_word}'. Falling back to default_surface '{default_surface}'. Output: {default_surface + base_word}")
        return default_surface + base_word 
