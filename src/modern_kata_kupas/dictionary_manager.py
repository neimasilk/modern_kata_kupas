# src/modern_kata_kupas/dictionary_manager.py
import os
import logging # Added import
from typing import Set, Optional, Iterable
from .exceptions import (
    DictionaryFileNotFoundError,
    DictionaryLoadingError
)
from .normalizer import TextNormalizer # Changed to relative import

class DictionaryManager:
    """
    Manages Indonesian root word dictionaries and loanword lists.

    Responsible for loading, storing, and providing access to sets of
    normalized root words (`kata_dasar`) and loanwords. It supports loading
    from default packaged files or custom external files. All words are
    normalized (e.g., lowercased) before storage and lookup.

    Attributes:
        kata_dasar_set (set[str]): A set of normalized Indonesian root words.
        loanwords_set (set[str]): A set of normalized loanwords.
        normalizer (TextNormalizer): An instance of `TextNormalizer` used for
            normalizing words before they are added to the sets or checked
            for existence.
    """
    DEFAULT_DICT_PACKAGE_PATH = "modern_kata_kupas.data" # Corrected path as per task
    DEFAULT_DICT_FILENAME = "kata_dasar.txt"
    DEFAULT_LOANWORD_FILENAME = "loanwords.txt"

    def __init__(self, dictionary_path: Optional[str] = None, loanword_list_path: Optional[str] = None):
        """Initializes the DictionaryManager and loads dictionaries.

        Loads root words and loanwords from specified file paths or from
        default packaged files if paths are not provided. Words are normalized
        (e.g., lowercased, whitespace stripped) before being added to the
        internal sets.

        Args:
            dictionary_path (Optional[str]): Path to an external root word
                dictionary file (one word per line, UTF-8 encoded). If None,
                the default packaged dictionary is loaded. Defaults to None.
            loanword_list_path (Optional[str]): Path to an external loanword list
                file (one word per line, UTF-8 encoded). If None, the default
                packaged loanword list is loaded. Defaults to None.
                
        Raises:
            DictionaryFileNotFoundError: If a specified `dictionary_path` or
                `loanword_list_path` points to a file that is not found or is
                not a file. Also raised if default files cannot be located and
                no custom path is given.
            DictionaryLoadingError: If there's an error during the loading or
                parsing of dictionary or loanword files (e.g., IO errors,
                issues with `importlib.resources` if default files are missing
                from the package).
        """
        self.kata_dasar_set: Set[str] = set()
        self.loanwords_set: Set[str] = set() # Renamed from self.loanwords to self.loanwords_set
        self.normalizer = TextNormalizer() # Instantiate TextNormalizer

        if dictionary_path:
            self._load_from_file_path(dictionary_path, is_loanword_list=False)
        else:
            self._load_default_packaged_dictionary()

        if loanword_list_path:
            self._load_from_file_path(loanword_list_path, is_loanword_list=True)
        else:
            self._load_default_loanword_list()

    # _normalize_word method removed, will use self.normalizer.normalize_word()
        
    def add_word(self, word: str, is_loanword: bool = False):
        """
        Adds a new word to the appropriate dictionary set after normalization.

        The word is normalized (e.g., lowercased, stripped of leading/trailing
        whitespace) before being added. If the normalized form of the word is
        empty, it is not added to either set.

        Args:
            word (str): The word to add to one of the dictionary sets.
            is_loanword (bool, optional): If True, adds the word to the loanwords
                set. Otherwise, adds to the root words (`kata_dasar`) set.
                Defaults to False.

        Example:
            >>> dm = DictionaryManager() # Assumes default dict loads
            >>> dm.add_word("   TesT   ")
            >>> dm.is_kata_dasar("test")
            True
            >>> dm.add_word("  LoAnWoRd!  ", is_loanword=True)
            >>> dm.is_loanword("loanword")
            True
        """
        normalized_word = self.normalizer.normalize_word(word) # Use TextNormalizer
        if normalized_word:
            if is_loanword:
                self.loanwords_set.add(normalized_word)
            else:
                self.kata_dasar_set.add(normalized_word)

    def get_kata_dasar_count(self) -> int:
        """
        Gets the current number of unique root words in the dictionary.
        
        Returns:
            int: The total count of loaded and normalized root words.
        """
        return len(self.kata_dasar_set)

    def get_loanword_count(self) -> int:
        """
        Gets the current number of unique loanwords in the list.
        
        Returns:
            int: The total count of loaded and normalized loanwords.
        """
        return len(self.loanwords_set)
        
    def _load_words_from_iterable(self, word_iterable: Iterable[str], is_loanword_list: bool = False):
        """
        Loads words from an iterable into the appropriate set, normalizing them.
        Skips empty words after normalization.
        """
        target_set = self.loanwords_set if is_loanword_list else self.kata_dasar_set
        for line in word_iterable:
            normalized_word = self.normalizer.normalize_word(line) # Use TextNormalizer
            if normalized_word: 
                target_set.add(normalized_word)
                
    def is_kata_dasar(self, kata: str) -> bool:
        """
        Checks if a given word is present in the loaded root word dictionary.

        The word is normalized before checking. The check is effectively
        case-insensitive due to this normalization.
        
        Args:
            kata (str): The word to check for existence in the root word dictionary.
            
        Returns:
            bool: True if the normalized form of `kata` exists in the root word
                set, False otherwise.

        Example:
            >>> dm = DictionaryManager(dictionary_path="path/to/your/dict.txt")
            >>> # Assuming "contoh" is in your dict.txt
            >>> dm.is_kata_dasar("Contoh")
            True
            >>> dm.is_kata_dasar("tidakada")
            False
        """
        normalized_kata = self.normalizer.normalize_word(kata) # Use TextNormalizer
        is_present = normalized_kata in self.kata_dasar_set
        return is_present

    def is_loanword(self, word: str) -> bool:
        """
        Checks if a given word is present in the loaded loanword list.

        The word is normalized before checking. The check is effectively
        case-insensitive due to this normalization.
        
        Args:
            word (str): The word to check for existence in the loanword list.
            
        Returns:
            bool: True if the normalized form of `word` exists in the loanword
                set, False otherwise.
        """
        normalized_word = self.normalizer.normalize_word(word) # Use TextNormalizer
        is_present = normalized_word in self.loanwords_set
        return is_present
        
    def _load_default_packaged_dictionary(self):
        """Memuat kamus default yang dikemas dengan library."""
        try:
            import importlib.resources
            # Use files() for Python 3.9+ to avoid DeprecationWarning
            if hasattr(importlib.resources, 'files'):
                file_content = importlib.resources.files(self.DEFAULT_DICT_PACKAGE_PATH).joinpath(self.DEFAULT_DICT_FILENAME).read_text(encoding='utf-8')
            else:
                # Fallback for Python 3.8
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
            # Use files() for Python 3.9+ to avoid DeprecationWarning
            if hasattr(importlib.resources, 'files'):
                file_content = importlib.resources.files(self.DEFAULT_DICT_PACKAGE_PATH).joinpath(self.DEFAULT_LOANWORD_FILENAME).read_text(encoding='utf-8')
            else:
                # Fallback for Python 3.8
                file_content = importlib.resources.read_text(
                    self.DEFAULT_DICT_PACKAGE_PATH,
                    self.DEFAULT_LOANWORD_FILENAME,
                    encoding='utf-8'
                )
            self._load_words_from_iterable(file_content.splitlines(), is_loanword_list=True)
            logging.info(f"DictionaryManager: Successfully loaded {len(self.loanwords_set)} loanwords from default list.")
        except FileNotFoundError:
            # This is not a critical error if the default loanword file doesn't exist,
            # as it's an optional feature. The loanwords_set will remain empty.
            logging.warning(f"DictionaryManager: Default loanword file '{self.DEFAULT_LOANWORD_FILENAME}' not found. Loanword feature will be limited.")
        except Exception as e:
            # Log other errors but don't raise, to allow main dictionary to still work.
            logging.error(f"DictionaryManager: Error loading default loanword list: {e}", exc_info=True)
            
    def _load_from_file_path(self, file_path: str, is_loanword_list: bool = False):
        """Loads dictionary or loanword list from a given file path."""
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            entity_type = "Loanword list" if is_loanword_list else "Dictionary"
            raise DictionaryFileNotFoundError(f"{entity_type} file not found at path: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self._load_words_from_iterable(f, is_loanword_list=is_loanword_list)
            if is_loanword_list:
                 logging.info(f"DictionaryManager: Successfully loaded {len(self.loanwords_set)} loanwords from '{file_path}'.")
            else: # For regular dictionary
                 logging.info(f"DictionaryManager: Successfully loaded {len(self.kata_dasar_set)} kata dasar from '{file_path}'.")
        except IOError as e:
            entity_type = "loanword list" if is_loanword_list else "dictionary"
            raise DictionaryLoadingError(f"Error reading {entity_type} file {file_path}: {e}") from e
        except Exception as e:
            entity_type = "loanword list" if is_loanword_list else "dictionary"
            raise DictionaryLoadingError(f"Unexpected error loading {entity_type} {file_path}: {e}") from e