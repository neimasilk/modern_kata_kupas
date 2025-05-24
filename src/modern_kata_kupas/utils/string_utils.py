# src/modern_kata_kupas/utils/string_utils.py
"""
String utility functions for ModernKataKupas.
"""

# normalize_word has been removed from this file.
# Please use TextNormalizer from modern_kata_kupas.normalizer

def is_vowel(char: str) -> bool:
    """
    Checks if a single character is a vowel (a, e, i, o, u).

    The check is case-insensitive. If the input is not a single character string,
    it returns False.

    Args:
        char (str): The character to check. Expected to be a single character.

    Returns:
        bool: True if the character is a vowel, False otherwise (including if
              the input is not a single character string).
    """
    if not isinstance(char, str) or len(char) != 1:
        return False
    # return normalize_word(char) in 'aiueo' # Original line
    return char.lower() in 'aiueo' # Use simple lower() for this internal utility

def is_consonant(char: str) -> bool:
    """
    Checks if a single character is a consonant.

    A character is considered a consonant if it is an alphabet letter (a-z, case-insensitive)
    and not a vowel. If the input is not a single character string, or not an
    alphabetic character, it returns False.

    Args:
        char (str): The character to check. Expected to be a single character.

    Returns:
        bool: True if the character is a consonant, False otherwise (including if
              the input is not a single alphabetic character).
    """
    # normalized_char = normalize_word(char) # Original line
    normalized_char = char.lower() # Use simple lower() for this internal utility
    return len(normalized_char) == 1 and 'a' <= normalized_char <= 'z' and not is_vowel(normalized_char)