# tests/test_exceptions.py
"""
Unit tests untuk custom exceptions.
"""

import pytest
from modern_kata_kupas import exceptions

def test_modern_kata_kupas_error():
    """Tes ModernKataKupasError dasar."""
    with pytest.raises(exceptions.ModernKataKupasError):
        raise exceptions.ModernKataKupasError("Generic MKK error")

def test_dictionary_error():
    """Tes DictionaryError."""
    with pytest.raises(exceptions.DictionaryError):
        raise exceptions.DictionaryError("Dictionary-related error")

def test_rule_error():
    """Tes RuleError."""
    with pytest.raises(exceptions.RuleError):
        raise exceptions.RuleError("Rule-related error")

def test_word_not_in_dictionary_error():
    """Tes WordNotInDictionaryError."""
    word = "katatidakada"
    with pytest.raises(exceptions.WordNotInDictionaryError) as excinfo:
        raise exceptions.WordNotInDictionaryError(word)
    assert excinfo.value.word == word
    assert str(excinfo.value) == f"Kata '{word}' tidak ditemukan dalam kamus."

def test_word_not_in_dictionary_error_custom_message():
    """Tes WordNotInDictionaryError dengan pesan custom."""
    word = "katatidakada"
    message = "Pesan error khusus."
    with pytest.raises(exceptions.WordNotInDictionaryError) as excinfo:
        raise exceptions.WordNotInDictionaryError(word, message=message)
    assert excinfo.value.word == word
    assert str(excinfo.value) == message

def test_invalid_affix_error():
    """Tes InvalidAffixError."""
    with pytest.raises(exceptions.InvalidAffixError):
        raise exceptions.InvalidAffixError("Invalid affix provided")

def test_dictionary_file_not_found_error():
    """Tes DictionaryFileNotFoundError."""
    with pytest.raises(exceptions.DictionaryFileNotFoundError) as exc_info:
        raise exceptions.DictionaryFileNotFoundError("Tes file tidak ditemukan")
    assert "Tes file tidak ditemukan" in str(exc_info.value)
    assert isinstance(exc_info.value, FileNotFoundError) # Cek inheritance

def test_dictionary_loading_error():
    """Tes DictionaryLoadingError."""
    with pytest.raises(exceptions.DictionaryLoadingError) as exc_info:
        raise exceptions.DictionaryLoadingError("Tes error loading")
    assert "Tes error loading" in str(exc_info.value)

def test_reconstruction_error():
    """Tes ReconstructionError."""
    with pytest.raises(exceptions.ReconstructionError):
        raise exceptions.ReconstructionError("Error during reconstruction")

def test_separation_error():
    """Tes SeparationError."""
    with pytest.raises(exceptions.SeparationError):
        raise exceptions.SeparationError("Error during separation")

# Memastikan hierarki exception benar
def test_exception_hierarchy():
    """Tes hierarki warisan exception."""
    assert issubclass(exceptions.DictionaryError, exceptions.ModernKataKupasError)
    assert issubclass(exceptions.RuleError, exceptions.ModernKataKupasError)
    assert issubclass(exceptions.WordNotInDictionaryError, exceptions.DictionaryError)
    assert issubclass(exceptions.InvalidAffixError, exceptions.ModernKataKupasError)
    assert issubclass(exceptions.ReconstructionError, exceptions.ModernKataKupasError)
    assert issubclass(exceptions.SeparationError, exceptions.ModernKataKupasError)