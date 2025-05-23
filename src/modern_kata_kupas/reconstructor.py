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

        parts = segmented_word.split('~')
        
        if segmented_word == "sayur~rs(~mayur)":
            print(f"DEBUG_SAYUR: Input to parse_segmented_string: '{segmented_word}'")
            print(f"DEBUG_SAYUR: parts: {parts}")
            
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
            if part.startswith("rs(") and part.endswith(")"):
                result["redup_marker"] = "rs"
                variant = part[3:-1]
                if variant: 
                    result["redup_variant"] = variant
                # else: # Invalid "rs()" - variant is empty, handled by None default
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
                actual_variant = variant 
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
            # Fallback for simple prefixes if they were structured with 'form' instead of 'allomorphs'
            # or if a complex prefix rule is missing allomorphs (error in rules.json).
            # This also handles cases where the canonical form is the direct surface form.
            return rule_details.get("form", prefix_canonical_form) + base_word

        # Iterate through allomorphs to find the matching one
        for allomorph_rule in allomorphs:
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
            # The separator rules use "next_char_is" (array). For reconstruction, this means the base_word should start with one of these characters.
            condition_next_char_is = allomorph_rule.get("next_char_is") # List of chars (e.g., ["k", "t", "s", "p"])
            if condition_next_char_is:
                expected_conditions += 1
                if any(base_word.startswith(char) for char in condition_next_char_is):
                    conditions_met += 1
                else:
                    # If the rule specifies characters the root MUST start with, and it doesn't, this allomorph doesn't apply.
                    # However, some allomorphs (like default "me-" for "meN-") might not have "next_char_is".
                    # These should only be skipped if "next_char_is" is present and the condition is not met.
                    continue 
            
            # 3. Exact root condition (e.g., for "ber-" + "ajar" -> "belajar")
            # Separator rules use "condition_root_is": ["ajar"]
            condition_exact_root = allomorph_rule.get("condition_exact_root") # List of exact roots
            if condition_exact_root:
                expected_conditions += 1
                if base_word in condition_exact_root:
                    conditions_met += 1
                else:
                    continue # This allomorph doesn't apply

            # If there were specific conditions, and not all were met, skip this allomorph
            if expected_conditions > 0 and conditions_met != expected_conditions:
                continue
            
            # If expected_conditions is 0, this is a default/fallback allomorph for this prefix.
            # Or if all specific conditions were met.

            # At this point, this allomorph applies.
            temp_base_word = base_word
            
            # Elision logic:
            # Separator rule example for "meN-" + "pukul" (stemming "memukul"):
            # "surface": "mem", "next_char_is": ["b","f","p","v"], "elision": true, "reconstruct_root_initial": "p"
            # For forward "meN-" + "pukul":
            # Allomorph should be like: {"surface": "mem", "condition_root_starts_with": ["p"], "elide_root_initial": "p"}
            # Or {"surface": "mem", "condition_root_starts_with": ["p"], "elision_details": {"elide_char": "p"}}
            
            # Let's assume forward rules use "elide_chars_from_root": "p" or ["p", "t", "s", "k"]
            # or simply "elision_active_on_root_initial": "p"
            
            # Based on prompt: "elision == "consonant"" AND "reconstruct_root_initial" is a string AND temp_base_word.startswith(reconstruct_root_initial)
            # The key "reconstruct_root_initial" is from separator's perspective (char to add back).
            # For forward, this is the char to elide.
            
            elides_char = allomorph_rule.get("elide_char_from_root") # e.g., "p" for meN- + pukul -> memukul
                                                                  # e.g., "r" for ber- + -ajar -> belajar (if 'r' from 'ber' is elided) - this is complex.
                                                                  # The "ber-" + "ajar" -> "belajar" is usually a specific rule {"surface": "bel", "condition_exact_root": ["ajar"]}
                                                                  # where "bel" is the surface form and "ajar" is the root. No elision on "ajar" itself.

            # More direct: use a key like `elide_root_initial_if_starts_with`: "p"
            # Or the separator's `reconstruct_root_initial` IS the char that was elided.
            char_elided_from_root = allomorph_rule.get("reconstruct_root_initial") # This is from separator perspective.

            # Simplified elision check based on Sastrawi rules using boolean `true`.
            elision_type = allomorph_rule.get("elision")
            if elision_type and isinstance(char_elided_from_root, str): # Handles `elision: true`
                if temp_base_word.startswith(char_elided_from_root):
                    temp_base_word = temp_base_word[len(char_elided_from_root):]
            elif elision_type == "vowel_sound_meng": # for meN- + e.g. undur -> mengundur
                # This case typically means `meng-` is used and no change to root.
                # The surface form "meng" already handles it.
                pass


            # Special handling for "menge-" if base_word is monosyllabic (already checked by is_monosyllabic_root condition)
            # The surface_form "menge" would be chosen by the conditions.

            return surface_form + temp_base_word

        # Fallback: If no allomorph rule was explicitly matched (e.g. default case for a prefix like "meN-" -> "me-")
        # This should ideally be the last allomorph in the rules list with no specific conditions.
        # If rules are not comprehensive, this is a safety net.
        # The prompt implies rules should be comprehensive. The `get_rule_details` returns the whole group,
        # including the canonical form itself, which might serve as a fallback if no allomorphs are listed.
        # However, complex prefixes *always* have allomorphs.
        # If "di-" was fetched, `allomorphs` would be None.
        # This part of code is reached if `allomorphs` is not None, but loop finishes.
        # This indicates an incomplete rule set for a complex prefix.
        # A robust default would be to use the prefix's canonical form (minus any markers like 'N')
        # or a predefined default surface form.
        # For "meN-", a very basic fallback could be "me" + base_word.
        # For "ber-", it's "ber-" + base_word.
        # For "per-", it's "per-" + base_word.
        # The simplest general fallback if rules are incomplete:
        default_surface = prefix_canonical_form.replace('N', '') # Crude fallback for meN-, peN-
        if default_surface.endswith('-'): default_surface = default_surface[:-1] # remove trailing hyphen
        
        return default_surface + base_word # Fallback, potentially incorrect if rules are not exhaustive
