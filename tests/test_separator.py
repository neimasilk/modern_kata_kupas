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
    # The segment method should now return the normalized word
    assert mkk.segment("TestWord.") == "testword"
    assert mkk.segment("anotherWORD") == "anotherword"
    assert mkk.segment("KataDenganSpasi") == "katadenganspasi" # Assuming normalizer handles spaces or removes them

def test_strip_basic_suffixes():
    """Test stripping of basic suffixes (particles and possessives)."""
    mkk = ModernKataKupas()
    # Test cases from implementation plan Step 1.4
    assert mkk._strip_suffixes("bukuku") == "buku~ku"
    assert mkk._strip_suffixes("ambilkanlah") == "ambilkan~lah"
    assert mkk._strip_suffixes("siapakah") == "siapa~kah"
    assert mkk._strip_suffixes("miliknya") == "milik~nya"
    assert mkk._strip_suffixes("rumahkupun") == "rumah~ku~pun"
    # Test case with no suffix
    assert mkk._strip_suffixes("buku") == "buku"
    # Test case with unknown suffix (should not strip)
    assert mkk._strip_suffixes("bukuxyz") == "bukuxyz"