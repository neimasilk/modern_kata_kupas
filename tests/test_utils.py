# tests/test_utils.py
"""
Unit tests untuk modul utilitas.
"""

import pytest
from modern_kata_kupas import utils
# from modern_kata_kupas.exceptions import ModernKataKupasError # Jika utils melempar error custom

def test_normalize_word():
    """Tes fungsi normalize_word."""
    assert utils.normalize_word("BesAR") == "besar"
    assert utils.normalize_word("kecil") == "kecil"
    assert utils.normalize_word("DENGAN SPASI") == "dengan spasi"
    assert utils.normalize_word("") == ""
    assert utils.normalize_word("AngKa123") == "angka123"
    # Tes dengan input non-string (sesuai implementasi di utils.py)
    assert utils.normalize_word(123) == "123"
    assert utils.normalize_word(None) == "none" # Tergantung bagaimana None dikonversi ke str

def test_is_vowel():
    """Tes fungsi is_vowel."""
    vowels = 'aiueoAIUEO'
    non_vowels = 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ123!@#'
    for char in vowels:
        assert utils.is_vowel(char), f"'{char}' seharusnya vokal"
    for char in non_vowels:
        assert not utils.is_vowel(char), f"'{char}' seharusnya bukan vokal"
    assert not utils.is_vowel("") # String kosong
    assert not utils.is_vowel("aa") # String lebih dari satu karakter

def test_is_consonant():
    """Tes fungsi is_consonant."""
    consonants = 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ'
    non_consonants = 'aiueoAIUEO123!@#'
    for char in consonants:
        assert utils.is_consonant(char), f"'{char}' seharusnya konsonan"
    for char in non_consonants:
        assert not utils.is_consonant(char), f"'{char}' seharusnya bukan konsonan"
    assert not utils.is_consonant("") # String kosong
    assert not utils.is_consonant("bb") # String lebih dari satu karakter

# Jika ada fungsi utilitas lain, tambahkan tesnya di sini
# Contoh:
# def test_some_other_util_function():
#     assert utils.some_other_util_function(input) == expected_output