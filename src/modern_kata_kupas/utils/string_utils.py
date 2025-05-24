# src/modern_kata_kupas/utils/string_utils.py
"""
String utility functions for ModernKataKupas.
"""

# normalize_word has been removed from this file.
# Please use TextNormalizer from modern_kata_kupas.normalizer

def is_vowel(char: str) -> bool:
    """
    Memeriksa apakah sebuah karakter adalah huruf vokal (a, e, i, o, u).

    Args:
        char (str): Karakter tunggal untuk diperiksa.

    Returns:
        bool: True jika vokal, False jika tidak.
    """
    if not isinstance(char, str) or len(char) != 1:
        return False
    # return normalize_word(char) in 'aiueo' # Original line
    return char.lower() in 'aiueo' # Use simple lower() for this internal utility

def is_consonant(char: str) -> bool:
    """
    Memeriksa apakah sebuah karakter adalah huruf konsonan.

    Args:
        char (str): Karakter tunggal untuk diperiksa.

    Returns:
        bool: True jika konsonan, False jika tidak.
    """
    # normalized_char = normalize_word(char) # Original line
    normalized_char = char.lower() # Use simple lower() for this internal utility
    return len(normalized_char) == 1 and 'a' <= normalized_char <= 'z' and not is_vowel(normalized_char)