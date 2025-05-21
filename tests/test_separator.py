# tests/test_separator.py

import pytest
from src.modern_kata_kupas.separator import ModernKataKupas

def test_modernkatakupas_instantiation():
    """Test that ModernKataKupas class can be instantiated."""
    try:
        mkk = ModernKataKupas()
        assert isinstance(mkk, ModernKataKupas)
    except Exception as e:
        pytest.fail(f"Instantiation failed with exception: {e}")

def test_segment_stub_returns_normalized_word():
    """Test that the segment stub method returns the normalized input word."""
    mkk = ModernKataKupas()
    # The current stub just returns the input word, which acts as a placeholder for normalization
    test_word = "TestWord"
    result = mkk.segment(test_word)
    assert result == test_word

    test_word_2 = "anotherword"
    result_2 = mkk.segment(test_word_2)
    assert result_2 == test_word_2