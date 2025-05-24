# src/modern_kata_kupas/utils/__init__.py
"""
Package initialization for utils module.
"""

from .string_utils import is_vowel, is_consonant # normalize_word removed

__all__ = [
    # "normalize_word", # Removed
    "is_vowel",
    "is_consonant"
]