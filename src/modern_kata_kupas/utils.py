# src/modern_kata_kupas/utils.py
"""
Modul utilitas umum untuk library ModernKataKupas.

Ini mungkin berisi fungsi helper, konstanta, atau kelas utilitas kecil
yang digunakan di berbagai bagian library.
"""

import logging

# Pengaturan logging dasar (opsional, bisa dikonfigurasi lebih lanjut)
# logger = logging.getLogger(__name__)
# logger.addHandler(logging.NullHandler()) # Agar library tidak memaksakan handler log

def normalize_word(word: str) -> str:
    """
    Menormalisasi kata ke format standar (misalnya, huruf kecil).

    Args:
        word (str): Kata yang akan dinormalisasi.

    Returns:
        str: Kata yang sudah dinormalisasi.
    """
    if not isinstance(word, str):
        # Mungkin lebih baik raise TypeError atau custom exception
        # from .exceptions import ModernKataKupasError
        # raise ModernKataKupasError("Input untuk normalisasi harus string")
        print(f"Peringatan: Input untuk normalisasi bukan string: {type(word)}")
        return str(word).lower() # Coba konversi dan lowercase
    return word.lower()

def is_vowel(char: str) -> bool:
    """
    Memeriksa apakah sebuah karakter adalah huruf vokal (a, e, i, o, u).

    Args:
        char (str): Karakter tunggal untuk diperiksa.

    Returns:
        bool: True jika vokal, False jika tidak.
    """
    return normalize_word(char) in 'aiueo'

def is_consonant(char: str) -> bool:
    """
    Memeriksa apakah sebuah karakter adalah huruf konsonan.

    Args:
        char (str): Karakter tunggal untuk diperiksa.

    Returns:
        bool: True jika konsonan, False jika tidak.
    """
    # Asumsi input adalah satu huruf alfabet
    normalized_char = normalize_word(char)
    return len(normalized_char) == 1 and 'a' <= normalized_char <= 'z' and not is_vowel(normalized_char)

# Contoh penggunaan (bisa dihapus atau dikomentari nanti)
if __name__ == '__main__':
    print(f"Normalisasi 'BesAR': {normalize_word('BesAR')}")
    print(f"'a' adalah vokal: {is_vowel('a')}")
    print(f"'E' adalah vokal: {is_vowel('E')}")
    print(f"'b' adalah vokal: {is_vowel('b')}")
    print(f"'b' adalah konsonan: {is_consonant('b')}")
    print(f"'A' adalah konsonan: {is_consonant('A')}")
    print(f"'7' adalah konsonan: {is_consonant('7')}")
    print(f"Normalisasi 123: {normalize_word(123)}")