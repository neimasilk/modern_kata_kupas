import pytest
import pytest
from src.modern_kata_kupas.dictionary_manager import DictionaryManager

class TestDictionaryManager:
    def test_is_kata_dasar_true(self):
        """Test untuk memverifikasi kata dasar yang valid"""
        dictionary = DictionaryManager("tests/data/test_kata_dasar.txt")
        assert dictionary.is_kata_dasar("testkata1") is True
    
    def test_is_kata_dasar_false(self):
        """Test untuk memverifikasi kata bukan dasar"""
        dictionary = DictionaryManager("tests/data/test_kata_dasar.txt")
        assert dictionary.is_kata_dasar("invalidkata") is False
    
    def test_file_not_found_error(self):
        """Test handling file tidak ditemukan"""
        with pytest.raises(ValueError):
            DictionaryManager("invalid_path.txt")
    
    def test_load_dictionary_error(self, mocker):
        """Test handling error saat memuat kamus"""
        mocker.patch("builtins.open", side_effect=Exception("Simulated error"))
        with pytest.raises(RuntimeError):
            DictionaryManager("tests/data/test_kata_dasar.txt")