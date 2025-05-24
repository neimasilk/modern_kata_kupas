# src/modern_kata_kupas/normalizer.py
"""
Modul untuk normalisasi teks dalam ModernKataKupas.
"""

class TextNormalizer:
    """
    Kelas untuk menormalisasi kata-kata.
    """

    def normalize_word(self, word: str) -> str:
        """
        Menormalisasi kata dengan:
        - Mengubah ke huruf kecil
        - Menghapus tanda baca di akhir kata
        - Mempertahankan tanda hubung internal

        Args:
            word (str): Kata yang akan dinormalisasi

        Returns:
            str: Kata yang sudah dinormalisasi
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