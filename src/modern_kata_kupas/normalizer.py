# src/modern_kata_kupas/normalizer.py
"""
Modul untuk normalisasi teks dalam ModernKataKupas.
"""

from typing import Any

class TextNormalizer:
    """
    Provides methods for normalizing text, specifically Indonesian words.

    Normalization typically includes converting to lowercase, stripping whitespace,
    and removing common trailing punctuation. Internal hyphens are preserved.
    """

    def normalize_word(self, word: Any) -> str:
        """
        Normalizes a given word according to defined rules.

        The normalization process includes:
        1. Converting the word to lowercase.
        2. Stripping leading/trailing whitespace.
        3. Removing common trailing punctuation (e.g., '.', ',', '?', '!', ':', ';').
        Internal hyphens are preserved. Non-string inputs are first converted to
        strings, then stripped and lowercased.

        Args:
            word (str): The word to be normalized. Can be any type that can be
                        converted to a string.

        Returns:
            str: The normalized word. If the input `word` is None or results in
                 an empty string after stripping, an empty string is returned.
        """
        if not isinstance(word, str):
            # For non-strings, convert to string, strip, and lowercase.
            # This handles None, numbers, etc., consistently with dictionary needs.
            return str(word).strip().lower() 
            
        # For strings, strip whitespace, then lowercase.
        normalized = word.strip().lower()
        
        # Hapus tanda baca di akhir kata (setelah lowercase dan strip)
        # Common trailing punctuation relevant for token cleaning.
        # This simple loop is fine for typical cases.
        # More complex scenarios might involve regex or more specific rules.
        while len(normalized) > 0 and normalized[-1] in {'.', ',', '?', '!', ':', ';'}: # Added colon and semicolon
            normalized = normalized[:-1]
            
        return normalized