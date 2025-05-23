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
    DEFAULT_DICT_PACKAGE_PATH = "src.modern_kata_kupas.data" # Corrected path
    DEFAULT_DICT_FILENAME = "kata_dasar.txt"
    DEFAULT_LOANWORD_FILENAME = "loanwords.txt"

    def __init__(self, dictionary_path: Optional[str] = None, loanword_list_path: Optional[str] = None):
        """
        Inisialisasi DictionaryManager dan memuat kamus kata dasar serta daftar kata serapan.
        
        Args:
            dictionary_path: Path opsional ke file kamus eksternal.
                Jika tidak disediakan, akan mencoba memuat kamus default.
            loanword_list_path: Path opsional ke file daftar kata serapan eksternal.
                Jika tidak disediakan, akan mencoba memuat daftar default.
                
        Raises:
            DictionaryFileNotFoundError: Jika file kamus atau kata serapan tidak ditemukan.
            DictionaryLoadingError: Jika terjadi kesalahan saat memuat file.
        """
        self.kata_dasar_set: Set[str] = set()
        self.loanwords_set: Set[str] = set() # Renamed from self.loanwords to self.loanwords_set

        if dictionary_path:
            self._load_from_file_path(dictionary_path, is_loanword_list=False)
        else:
            self._load_default_packaged_dictionary()

        if loanword_list_path:
            self._load_from_file_path(loanword_list_path, is_loanword_list=True)
        else:
            self._load_default_loanword_list()

    def _normalize_word(self, word: str) -> str:
        """Normalizes a word by stripping whitespace and converting to lowercase."""
        if not isinstance(word, str):
            return "" 
        return word.strip().lower()
        
    def add_word(self, word: str, is_loanword: bool = False):
        """
        Adds a new word to the appropriate set (kata_dasar_set or loanwords_set)
        after normalizing it. Skips empty words after normalization.
        """
        normalized_word = self._normalize_word(word)
        if normalized_word:
            if is_loanword:
                self.loanwords_set.add(normalized_word)
            else:
                self.kata_dasar_set.add(normalized_word)

    def get_kata_dasar_count(self) -> int:
        """
        Mengembalikan jumlah kata dasar dalam kamus.
        
        Returns:
            int: Jumlah kata dasar yang telah dimuat.
        """
        return len(self.kata_dasar_set)

    def get_loanword_count(self) -> int:
        """
        Mengembalikan jumlah kata serapan dalam daftar.
        
        Returns:
            int: Jumlah kata serapan yang telah dimuat.
        """
        return len(self.loanwords_set)
        
    def _load_words_from_iterable(self, word_iterable: Iterable[str], is_loanword_list: bool = False):
        """
        Loads words from an iterable into the appropriate set, normalizing them.
        Skips empty words after normalization.
        """
        target_set = self.loanwords_set if is_loanword_list else self.kata_dasar_set
        for line in word_iterable:
            normalized_word = self._normalize_word(line)
            if normalized_word: 
                target_set.add(normalized_word)
                
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
        # print(f"DictionaryManager: Checking KD '{kata}' (normalized: '{normalized_kata}'), found: {is_present}") 
        return is_present

    def is_loanword(self, word: str) -> bool:
        """
        Memeriksa apakah suatu kata ada dalam daftar kata serapan.
        
        Args:
            word: Kata yang akan diperiksa.
            
        Returns:
            bool: True jika kata ada dalam daftar (case-insensitive), False jika tidak.
        """
        normalized_word = self._normalize_word(word)
        is_present = normalized_word in self.loanwords_set
        # print(f"DictionaryManager: Checking Loanword '{word}' (normalized: '{normalized_word}'), found: {is_present}")
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
            self._load_words_from_iterable(file_content.splitlines(), is_loanword_list=False)
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

    def _load_default_loanword_list(self):
        """Memuat daftar kata serapan default yang dikemas dengan library."""
        try:
            import importlib.resources
            file_content = importlib.resources.read_text(
                self.DEFAULT_DICT_PACKAGE_PATH,
                self.DEFAULT_LOANWORD_FILENAME,
                encoding='utf-8'
            )
            self._load_words_from_iterable(file_content.splitlines(), is_loanword_list=True)
            print(f"DictionaryManager: Successfully loaded {len(self.loanwords_set)} loanwords from default list.")
        except FileNotFoundError:
            # This is not a critical error if the default loanword file doesn't exist,
            # as it's an optional feature. The loanwords_set will remain empty.
            print(f"DictionaryManager: Default loanword file '{self.DEFAULT_LOANWORD_FILENAME}' not found. Loanword feature will be limited.")
        except Exception as e:
            # Log other errors but don't raise, to allow main dictionary to still work.
            print(f"DictionaryManager: Error loading default loanword list: {e}")
            
    def _load_from_file_path(self, file_path: str, is_loanword_list: bool = False):
        """Loads dictionary or loanword list from a given file path."""
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            entity_type = "Loanword list" if is_loanword_list else "Dictionary"
            raise DictionaryFileNotFoundError(f"{entity_type} file not found at path: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self._load_words_from_iterable(f, is_loanword_list=is_loanword_list)
            if is_loanword_list:
                 print(f"DictionaryManager: Successfully loaded {len(self.loanwords_set)} loanwords from '{file_path}'.")
        except IOError as e:
            entity_type = "loanword list" if is_loanword_list else "dictionary"
            raise DictionaryLoadingError(f"Error reading {entity_type} file {file_path}: {e}") from e
        except Exception as e:
            entity_type = "loanword list" if is_loanword_list else "dictionary"
            raise DictionaryLoadingError(f"Unexpected error loading {entity_type} {file_path}: {e}") from e