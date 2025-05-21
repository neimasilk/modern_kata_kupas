# tests/test_normalizer.py
"""
Unit tests untuk modul normalizer.
"""

import pytest
from modern_kata_kupas.normalizer import TextNormalizer

def test_normalize_word():
    """Tes metode normalize_word dari TextNormalizer."""
    normalizer = TextNormalizer()
    
    # Tes huruf kapital
    assert normalizer.normalize_word("BESAR") == "besar"
    assert normalizer.normalize_word("KeCiL") == "kecil"
    
    # Tes tanda baca di akhir kata
    assert normalizer.normalize_word("kata.") == "kata"
    assert normalizer.normalize_word("kalimat,") == "kalimat"
    assert normalizer.normalize_word("pertanyaan?") == "pertanyaan"
    assert normalizer.normalize_word("seru!") == "seru"
    
    # Tes tanda hubung internal
    assert normalizer.normalize_word("kata-kata") == "kata-kata"
    assert normalizer.normalize_word("multi-tahap") == "multi-tahap"
    
    # Tes input non-string
    assert normalizer.normalize_word(123) == "123"
    assert normalizer.normalize_word(None) == "none"