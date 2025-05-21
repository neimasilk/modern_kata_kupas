# tests/test_separator.py
"""
Unit tests untuk Separator.
"""

import pytest
from modern_kata_kupas.separator import Separator
from modern_kata_kupas.dictionary_manager import RootWordDictionary # Mungkin diperlukan nanti
from modern_kata_kupas.rules import MorphologicalRules # Mungkin diperlukan nanti

# Setup dasar untuk tes (bisa diperluas)
@pytest.fixture
def dummy_dictionary():
    # Buat dictionary dummy untuk tes
    dic = RootWordDictionary() # Asumsi ada file kata dasar dummy atau cara inisialisasi lain
    dic.add_word("makan")
    dic.add_word("coba")
    dic.add_word("baca")
    return dic

@pytest.fixture
def dummy_rules():
    # Buat rules dummy untuk tes
    rules = MorphologicalRules() # Asumsi ada file aturan dummy atau cara inisialisasi lain
    # Tambahkan beberapa aturan dummy jika perlu
    return rules

@pytest.fixture
def separator_instance(dummy_dictionary, dummy_rules):
    return Separator(dictionary=dummy_dictionary, rules=dummy_rules)

def test_separator_init(separator_instance):
    """Tes inisialisasi Separator."""
    assert separator_instance is not None
    assert separator_instance.dictionary is not None
    assert separator_instance.rules is not None

def test_separate_simple_word(separator_instance):
    """Tes pemisahan kata sederhana yang tidak berimbuhan (placeholder)."""
    word = "makan"
    # Saat ini, implementasi placeholder mengembalikan kata asli
    root, affixes = separator_instance.separate(word)
    assert root == word
    assert affixes == []

# Tambahkan lebih banyak tes di sini seiring pengembangan Separator
# Contoh:
# def test_separate_with_prefix(separator_instance):
#     word = "memakan"
#     # Harapan setelah implementasi:
#     # root, affixes = separator_instance.separate(word)
#     # assert root == "makan"
#     # assert affixes == ["me-"]
#     pass

# def test_separate_with_suffix(separator_instance):
#     # ...
#     pass

# def test_separate_with_confix(separator_instance):
#     # ...
#     pass