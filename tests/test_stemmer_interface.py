# tests/test_stemmer_interface.py
import pytest
from modern_kata_kupas.stemmer_interface import IndonesianStemmer

def test_get_root_word_basic():
    """Tests basic stemming with common words."""
    stemmer = IndonesianStemmer()
    assert stemmer.get_root_word("makan") == "makan"
    assert stemmer.get_root_word("memakan") == "makan"
    assert stemmer.get_root_word("dimakan") == "makan"
    assert stemmer.get_root_word("termakan") == "makan"
    assert stemmer.get_root_word("makanan") == "makan"
    assert stemmer.get_root_word("mempermainkan") == "main"
    assert stemmer.get_root_word("bernyanyi") == "nyanyi"

def test_get_root_word_case_insensitivity():
    """Tests stemming with different cases."""
    stemmer = IndonesianStemmer()
    assert stemmer.get_root_word("MAKAN") == "makan"
    assert stemmer.get_root_word("MeMaKaN") == "makan"

def test_get_root_word_non_indonesian():
    """Tests stemming with non-Indonesian words (should return the word itself)."""
    stemmer = IndonesianStemmer()
    assert stemmer.get_root_word("apple") == "apple"
    assert stemmer.get_root_word("computer") == "computer"

def test_get_root_word_empty_string():
    """Tests stemming with an empty string."""
    stemmer = IndonesianStemmer()
    assert stemmer.get_root_word("") == ""

def test_get_root_word_with_punctuation():
    """Tests stemming with punctuation (PySastrawi handles this)."""
    stemmer = IndonesianStemmer()
    # PySastrawi does not remove punctuation by default, it stems the word including punctuation
    # This test verifies the expected behavior of the wrapper
    assert stemmer.get_root_word("makan,") == "makan"
    assert stemmer.get_root_word("makan.") == "makan"
    assert stemmer.get_root_word("makan!") == "makan"
    assert stemmer.get_root_word("memakan?") == "makan"

# Note: PySastrawi might have limitations or specific behaviors for complex cases.
# These tests cover basic expected functionality of the wrapper.