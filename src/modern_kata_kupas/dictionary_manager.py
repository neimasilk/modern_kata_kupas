# src/modern_kata_kupas/dictionary_manager.py
import os
from typing import Set, Optional, Iterable
from .exceptions import (
    DictionaryFileNotFoundError,
    DictionaryLoadingError
)

class DictionaryManager:
    """
    Kelas untuk mengelola kamus kata dasar bahasa Indonesia.
    
    Attributes:
        kata_dasar_set: Set yang berisi kata-kata dasar yang telah dinormalisasi.
    """
    DEFAULT_DICT_PACKAGE_PATH = "modern_kata_kupas.data"
    DEFAULT_DICT_FILENAME = "kata_dasar.txt"

    def __init__(self, dictionary_path: Optional[str] = None):
        """
        Inisialisasi DictionaryManager dan memuat kamus.
        
        Args:
            dictionary_path: Path opsional ke file kamus eksternal.
                Jika tidak disediakan, akan mencoba memuat kamus default.
                
        Raises:
            DictionaryFileNotFoundError: Jika file kamus tidak ditemukan.
            DictionaryLoadingError: Jika terjadi kesalahan saat memuat kamus.
        """
        self.kata_dasar_set: Set[str] = set()

        if dictionary_path:
            self._load_from_file_path(dictionary_path)
        else:
            self._load_default_packaged_dictionary()

    def _normalize_word(self, word: str) -> str:
        """Normalizes a word by stripping whitespace and converting to lowercase."""
        if not isinstance(word, str):
            return "" # Atau raise TypeError, tapi untuk normalisasi internal, "" lebih aman
        return word.strip().lower()
        
    def add_word(self, word: str):
        """
        Adds a new word to the dictionary set after normalizing it.
        Skips empty words after normalization.
        """
        normalized_word = self._normalize_word(word)
        if normalized_word: # Hanya tambahkan jika kata tidak kosong setelah normalisasi
            self.kata_dasar_set.add(normalized_word)

    def get_kata_dasar_count(self) -> int:
        """
        Mengembalikan jumlah kata dasar dalam kamus.
        
        Returns:
            int: Jumlah kata dasar yang telah dimuat.
        """
        return len(self.kata_dasar_set)
        
    def _load_words_from_iterable(self, word_iterable: Iterable[str]):
        """
        Loads words from an iterable into the kata_dasar_set, normalizing them.
        Skips empty words after normalization.
        """
        for line in word_iterable:
            normalized_word = self._normalize_word(line)
            if normalized_word: # Hanya tambahkan jika kata tidak kosong setelah normalisasi
                self.kata_dasar_set.add(normalized_word)
                
    def is_kata_dasar(self, kata: str) -> bool:
        """
        Memeriksa apakah suatu kata ada dalam kamus yang telah dimuat.
        
        Args:
            kata: Kata yang akan diperiksa.
            
        Returns:
            bool: True jika kata ada dalam kamus (case-insensitive), False jika tidak.
        """
        normalized_kata = self._normalize_word(kata)
        is_present = normalized_kata in self.kata_dasar_set
        print(f"DictionaryManager: Checking '{kata}' (normalized: '{normalized_kata}'), found: {is_present}") # Add logging
        return is_present
        
    def _load_default_packaged_dictionary(self):
        """Memuat kamus default yang dikemas dengan library."""
        try:
            import importlib.resources
            file_content = importlib.resources.read_text(
                self.DEFAULT_DICT_PACKAGE_PATH,
                self.DEFAULT_DICT_FILENAME,
                encoding='utf-8'
            )
            self._load_words_from_iterable(file_content.splitlines())
        except FileNotFoundError as e:
            raise DictionaryFileNotFoundError(
                f"Kamus default '{self.DEFAULT_DICT_FILENAME}' "
                f"tidak ditemukan dalam paket '{self.DEFAULT_DICT_PACKAGE_PATH}'. "
                f"Periksa instalasi dan 'package_data' di setup.py."
            ) from e
        except ModuleNotFoundError as e:
            raise DictionaryLoadingError(
                f"Paket kamus default '{self.DEFAULT_DICT_PACKAGE_PATH}' tidak ditemukan. "
                f"Pastikan library terinstal dengan benar. Error: {e}"
            ) from e
        except Exception as e:
            raise DictionaryLoadingError(
                f"Error tak terduga saat memuat kamus default: {e}"
            ) from e
            
    def _load_from_file_path(self, file_path: str):
        """Loads dictionary from a given file path."""
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            raise DictionaryFileNotFoundError(f"Dictionary file not found at path: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self._load_words_from_iterable(f)
        except IOError as e:
            raise DictionaryLoadingError(f"Error reading dictionary file {file_path}: {e}") from e
        except Exception as e:
            raise DictionaryLoadingError(f"Unexpected error loading dictionary {file_path}: {e}") from e