# src/modern_kata_kupas/exceptions.py
"""
Modul untuk custom exceptions yang digunakan dalam library ModernKataKupas.
"""

from typing import Optional

class ModernKataKupasError(Exception):
    """Kelas dasar untuk semua exception di ModernKataKupas."""
    pass

class DictionaryOperationError(Exception): # Renamed from DictionaryError
    """Base class for general dictionary operation related errors."""
    pass

class DictionaryFileNotFoundError(DictionaryOperationError, FileNotFoundError): # Inherits from renamed
    """Raised when a dictionary or loanword file cannot be found at the specified path."""
    pass

class DictionaryLoadingError(DictionaryOperationError): # Inherits from renamed
    """Raised for errors encountered during the loading or parsing of dictionary files."""
    pass

class DictionaryError(ModernKataKupasError): # This is the library-specific one
    """Exception raised for errors specific to dictionary operations within ModernKataKupas.
    
    This could include issues like failing to load a required dictionary or
    problems accessing dictionary data.
    """
    pass

class RuleError(ModernKataKupasError):
    """Exception raised for errors related to loading or applying morphological rules.

    This could include issues with rule file format, or inconsistencies found
    during rule processing.
    """
    pass

class WordNotInDictionaryError(DictionaryError): # Inherits from the MKK-specific DictionaryError
    """Exception raised when a word required for an operation is not found in the dictionary.
    
    Attributes:
        word (str): The word that was not found.
    """
    def __init__(self, word: str, message: Optional[str] = None):
        """
        Initializes the WordNotInDictionaryError.

        Args:
            word (str): The word that was not found in the dictionary.
            message (str, optional): A custom message for the exception. If None,
                                     a default message is generated. Defaults to None.
        """
        self.word = word
        if message is None:
            message = f"Kata '{word}' tidak ditemukan dalam kamus."
        super().__init__(message)

class InvalidAffixError(ModernKataKupasError):
    """Exception raised when an affix is invalid, unknown, or used incorrectly."""
    pass

class ReconstructionError(ModernKataKupasError):
    """Exception raised during the word reconstruction process.

    This indicates an issue in reassembling a word from its morphemes, potentially
    due to inconsistent segmentation or rule application problems.
    """
    pass

class SeparationError(ModernKataKupasError):
    """Exception raised during the word separation (segmentation) process.

    This indicates an issue in breaking down a word into its morphemes,
    possibly due to complex or ambiguous structures not handled by current rules.
    """
    pass

# Contoh bagaimana exception ini bisa di-raise (untuk dokumentasi/tes):
# if __name__ == '__main__':
#     try:
#         raise WordNotInDictionaryError("katatidakada")
#     except WordNotInDictionaryError as e:
#         print(f"Caught an exception: {e}")
# 
#     try:
#         raise RuleError("Format aturan salah pada baris 5.")
#     except RuleError as e:
#         print(f"Caught an exception: {e}")