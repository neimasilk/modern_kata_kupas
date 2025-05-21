# src/modern_kata_kupas/__init__.py
"""
ModernKataKupas Library

Sebuah library Python modern untuk stemming kata dalam Bahasa Indonesia,
terinspirasi oleh PySastrawi namun dengan fokus pada modularitas, kemudahan
pemeliharaan, dan potensi perluasan.
"""

__version__ = "0.0.1"  # Versi awal

# Impor kelas dan fungsi utama agar mudah diakses
from .dictionary_manager import RootWordDictionary
from .separator import Separator
from .reconstructor import Reconstructor
from .rules import MorphologicalRules
from .exceptions import (
    ModernKataKupasError,
    DictionaryError,
    RuleError,
    WordNotInDictionaryError,
    InvalidAffixError,
    ReconstructionError,
    SeparationError
)
from .utils import normalize_word, is_vowel, is_consonant

# TODO: Mungkin ada kelas Fassade utama di sini nanti, misal `Stemmer`
# yang mengkoordinasikan Separator, Reconstructor, Dictionary, dan Rules.

__all__ = [
    "RootWordDictionary",
    "Separator",
    "Reconstructor",
    "MorphologicalRules",
    "ModernKataKupasError",
    "DictionaryError",
    "RuleError",
    "WordNotInDictionaryError",
    "InvalidAffixError",
    "ReconstructionError",
    "SeparationError",
    "normalize_word",
    "is_vowel",
    "is_consonant",
    "__version__"
]

# Pesan selamat datang atau inisialisasi logging bisa ditambahkan di sini jika perlu
# print("ModernKataKupas library initialized.")