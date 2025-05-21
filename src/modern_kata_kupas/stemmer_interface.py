# src/modern_kata_kupas/stemmer_interface.py
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

class IndonesianStemmer:
    """
    Kelas wrapper untuk PySastrawi Stemmer.
    """
    def __init__(self):
        """
        Inisialisasi stemmer PySastrawi.
        """
        factory = StemmerFactory()
        self._stemmer = factory.create_stemmer()

    def get_root_word(self, word: str) -> str:
        """
        Mendapatkan kata dasar dari sebuah kata menggunakan PySastrawi.

        Args:
            word: Kata yang akan di-stem.

        Returns:
            str: Kata dasar dari kata input.
        """
        return self._stemmer.stem(word)