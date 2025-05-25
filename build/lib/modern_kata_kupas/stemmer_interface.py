# src/modern_kata_kupas/stemmer_interface.py
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

class IndonesianStemmer:
    """
    A wrapper class for the PySastrawi Indonesian language stemmer.

    This class provides a consistent interface to the underlying Sastrawi stemmer,
    encapsulating its initialization and usage. It is used to obtain the root
    form of Indonesian words.

    Attributes:
        _stemmer: An instance of the Sastrawi stemmer.
    """
    def __init__(self):
        """
        Initializes the IndonesianStemmer by creating an instance of the Sastrawi stemmer.
        """
        factory = StemmerFactory()
        self._stemmer = factory.create_stemmer()

    def get_root_word(self, word: str) -> str:
        """
        Gets the root form of an Indonesian word using the PySastrawi stemmer.

        Args:
            word (str): The word to be stemmed.

        Returns:
            str: The stemmed (root) form of the input word.
        """
        return self._stemmer.stem(word)