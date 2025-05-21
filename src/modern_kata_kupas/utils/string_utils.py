# src/modern_kata_kupas/utils/string_utils.py
"""
String utility functions for ModernKataKupas.
"""

def normalize_word(word: str) -> str:
    """
    Menormalisasi kata ke format standar (misalnya, huruf kecil).

    Args:
        word (str): Kata yang akan dinormalisasi.

    Returns:
        str: Kata yang sudah dinormalisasi.
    """
    if not isinstance(word, str):
        print(f"Peringatan: Input untuk normalisasi bukan string: {type(word)}")
        return str(word).lower()
    return word.lower()

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
    return normalize_word(char) in 'aiueo'

def is_consonant(char: str) -> bool:
    """
    Memeriksa apakah sebuah karakter adalah huruf konsonan.

    Args:
        char (str): Karakter tunggal untuk diperiksa.

    Returns:
        bool: True jika konsonan, False jika tidak.
    """
    normalized_char = normalize_word(char)
    return len(normalized_char) == 1 and 'a' <= normalized_char <= 'z' and not is_vowel(normalized_char)