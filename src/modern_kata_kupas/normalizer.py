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
            return str(word).lower()
            
        normalized = word.lower()
        # Hapus tanda baca di akhir kata
        while len(normalized) > 0 and normalized[-1] in {'.', ',', '?', '!'}:
            normalized = normalized[:-1]
            
        return normalized