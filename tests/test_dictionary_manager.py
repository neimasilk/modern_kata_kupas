import pytest
from src.modern_kata_kupas.dictionary_manager import RootWordDictionary

class TestRootWordDictionary:
    def test_contains_existing_word(self):
        """Test untuk memverifikasi kata yang ada dalam kamus"""
        dictionary = RootWordDictionary("data/kata_dasar.txt")
        assert dictionary.contains("kata") is True
    
    def test_contains_non_existing_word(self):
        """Test untuk memverifikasi kata yang tidak ada dalam kamus"""
        dictionary = RootWordDictionary("data/kata_dasar.txt")
        assert dictionary.contains("xyz") is False
    
    def test_add_word(self):
        """Test untuk menambahkan kata baru ke kamus"""
        dictionary = RootWordDictionary("data/kata_dasar.txt")
        dictionary.add_word("baru")
        assert dictionary.contains("baru") is True
    
    def test_load_from_file(self):
        """Test untuk memuat kamus dari file"""
        dictionary = RootWordDictionary("data/kata_dasar.txt")
        assert len(dictionary.words) > 0