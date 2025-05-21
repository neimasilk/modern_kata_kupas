# tests/test_dictionary_manager.py
import pytest
import os
from modern_kata_kupas.dictionary_manager import DictionaryManager
from modern_kata_kupas.exceptions import (
    DictionaryFileNotFoundError,
    DictionaryLoadingError
)

def test_dictionary_manager_initialization():
    """Tests basic initialization of DictionaryManager."""
    manager = DictionaryManager(dictionary_path=EMPTY_DICT_PATH)
    assert manager.get_kata_dasar_count() == 0
    assert isinstance(manager.kata_dasar_set, set)

def test_normalize_word():
    """Tests the _normalize_word method."""
    manager = DictionaryManager() # Perlu instance untuk memanggil metode (meski bisa statis)
    assert manager._normalize_word("  Kata Contoh  ") == "kata contoh"
    assert manager._normalize_word("SEMUA BESAR") == "semua besar"
    assert manager._normalize_word("sudahkecil") == "sudahkecil"
    assert manager._normalize_word("") == ""
    assert manager._normalize_word("   ") == ""
    assert manager._normalize_word(123) == "" # Test non-string input

def test_load_words_from_iterable():
    """Tests the _load_words_from_iterable method."""
    manager = DictionaryManager(dictionary_path=EMPTY_DICT_PATH)
    sample_words = [
        "apel", "  Jeruk  ", "PISANG", "", "   ", "mangga", "apel" # "apel" duplikat
    ]
    manager._load_words_from_iterable(sample_words)

    expected_set = {"apel", "jeruk", "pisang", "mangga"}
    assert manager.kata_dasar_set == expected_set # Bisa akses langsung untuk tes metode internal ini
    assert manager.get_kata_dasar_count() == 4

    # Cek juga dengan is_kata_dasar
    assert manager.is_kata_dasar("Apel")
    assert not manager.is_kata_dasar("anggur")

    # Tes dengan iterable kosong
    manager_empty = DictionaryManager(dictionary_path=EMPTY_DICT_PATH)
    manager_empty._load_words_from_iterable([])
    assert manager_empty.get_kata_dasar_count() == 0

# Path ke file kamus sampel untuk tes
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SAMPLE_DICT_PATH = os.path.join(TEST_DATA_DIR, "test_kata_dasar_sample.txt")
EMPTY_DICT_PATH = os.path.join(TEST_DATA_DIR, "empty_dict.txt")

# Fixture untuk membuat file kamus sampel jika belum ada
@pytest.fixture(scope="module", autouse=True)
def create_sample_dict_file():
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    content = "Alpha\n  bravo  \nCHARLIE\ndelta\n"
    with open(SAMPLE_DICT_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    yield


def test_load_from_valid_external_path():
    """Tests loading dictionary from a valid external file path."""
    manager = DictionaryManager(dictionary_path=SAMPLE_DICT_PATH)
    assert manager.get_kata_dasar_count() == 4
    assert manager.is_kata_dasar("alpha")
    assert manager.is_kata_dasar("BRAVO")
    assert manager.is_kata_dasar("  charlie  ")
    assert manager.is_kata_dasar("delta")
    assert not manager.is_kata_dasar("echo")


def test_load_from_non_existent_external_path():
    """Tests that DictionaryFileNotFoundError is raised for a non-existent path."""
    non_existent_path = os.path.join(TEST_DATA_DIR, "file_yang_tidak_ada.txt")
    with pytest.raises(DictionaryFileNotFoundError) as exc_info:
        DictionaryManager(dictionary_path=non_existent_path)
    assert non_existent_path in str(exc_info.value)


def test_load_from_directory_path_instead_of_file():
    """Tests that DictionaryFileNotFoundError is raised for a directory path."""
    with pytest.raises(DictionaryFileNotFoundError):
        DictionaryManager(dictionary_path=TEST_DATA_DIR)
        
def test_load_default_packaged_dictionary_successfully():
    """Tests successful loading of the default packaged dictionary."""
    try:
        manager = DictionaryManager() # Tanpa argumen path
        assert manager.get_kata_dasar_count() > 0
        # Verifikasi beberapa kata dari src/modern_kata_kupas/data/kata_dasar.txt
        assert manager.is_kata_dasar("makan") # Ganti dengan kata yang ada
        assert manager.is_kata_dasar("MINUM") # Tes normalisasi
    except (DictionaryFileNotFoundError, DictionaryLoadingError) as e:
        pytest.fail(f"Default dictionary loading failed. Check setup. Error: {e}")