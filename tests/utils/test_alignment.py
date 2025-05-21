# tests/utils/test_alignment.py
"""
Unit tests untuk modul alignment.py
"""

import pytest
from modern_kata_kupas.utils.alignment import align

def test_align_simple_match():
    """Tes penyelarasan dengan kecocokan sederhana."""
    seq1 = "apple"
    seq2 = "apply"
    a1, a2, alignment = align(seq1, seq2)
    assert a1 == "apple"
    assert a2 == "apply"
    assert alignment.count("|") == 4  # 4 karakter cocok
    assert alignment.count(".") == 1  # 1 karakter tidak cocok

def test_align_with_insertion():
    """Tes penyelarasan dengan operasi penyisipan."""
    seq1 = "apple"
    seq2 = "apples"
    a1, a2, alignment = align(seq1, seq2)
    assert a1 == "apple-"
    assert a2 == "apples"
    assert alignment.count(" ") == 1  # 1 gap

def test_align_with_deletion():
    """Tes penyelarasan dengan operasi penghapusan."""
    seq1 = "apples"
    seq2 = "apple"
    a1, a2, alignment = align(seq1, seq2)
    assert a1 == "apples"
    assert a2 == "apple-"
    assert alignment.count(" ") == 1  # 1 gap

def test_align_with_substitution():
    """Tes penyelarasan dengan operasi substitusi."""
    seq1 = "apple"
    seq2 = "apricot"
    a1, a2, alignment = align(seq1, seq2)
    assert alignment.count(".") >= 3  # minimal 3 substitusi

@pytest.mark.parametrize("seq1,seq2,expected_matches", [
    ("", "", 0),  # Kasus kosong
    ("a", "a", 1),  # Kasus 1 karakter cocok
    ("a", "b", 0),  # Kasus 1 karakter tidak cocok
])
def test_align_edge_cases(seq1, seq2, expected_matches):
    """Tes kasus-kasus edge penyelarasan."""
    _, _, alignment = align(seq1, seq2)
    assert alignment.count("|") == expected_matches