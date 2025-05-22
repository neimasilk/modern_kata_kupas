# tests/test_separator.py

import os
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
    assert mkk.segment("KataDenganSpasi") == "katadenganspasi"

from src.modern_kata_kupas.dictionary_manager import DictionaryManager

def test_strip_basic_suffixes():
    """Test stripping of basic suffixes (particles and possessives)."""
    # Initialize DictionaryManager with the test dictionary file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_dict_path = os.path.join(current_dir, "data", "test_kata_dasar.txt")
    dictionary_manager = DictionaryManager(dictionary_path=test_dict_path)
    # Initialize ModernKataKupas with the test dictionary manager
    mkk = ModernKataKupas()
    mkk.dictionary = dictionary_manager
    # Test cases from implementation plan Step 1.4
    assert mkk._strip_suffixes("bukuku") == ("buku", ["ku"])
    assert mkk._strip_suffixes("ambilkanlah") == ("ambil", ["kan", "lah"])
    assert mkk._strip_suffixes("siapakah") == ("siapa", ["kah"])
    assert mkk._strip_suffixes("miliknya") == ("milik", ["nya"])
    assert mkk._strip_suffixes("rumahkupun") == ("rumah", ["ku", "pun"])
    # Test case with no suffix
    assert mkk._strip_suffixes("buku") == ("buku", [])
    # Test case with unknown suffix (should not strip)
    assert mkk._strip_suffixes("bukuxyz") == ("bukuxyz", [])

def test_strip_derivational_suffixes():
    """Test stripping of derivational suffixes (-kan, -i, -an)."""
    # Initialize DictionaryManager with the test dictionary file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_dict_path = os.path.join(current_dir, "data", "test_kata_dasar.txt")
    dictionary_manager = DictionaryManager(dictionary_path=test_dict_path)
    # Initialize ModernKataKupas with the test dictionary manager
    mkk = ModernKataKupas()
    mkk.dictionary = dictionary_manager

    # Test cases from implementation plan Step 1.5
    assert mkk._strip_suffixes("makanan") == ("makan", ["an"])
    assert mkk._strip_suffixes("panasi") == ("panas", ["i"])
    assert mkk._strip_suffixes("lemparkan") == ("lempar", ["kan"])
    assert mkk._strip_suffixes("pukulan") == ("pukul", ["an"])

    # Test layered suffixes (derivational + particle/possessive)
    assert mkk._strip_suffixes("mainkanlah") == ("main", ["kan", "lah"])
    # assert mkk._strip_suffixes("ajarilahaku") == "ajari~lah~aku" # This case is complex and depends on 'aku' being a possessive

    # Test words without these suffixes
    assert mkk._strip_suffixes("minum") == ("minum", [])
    # assert mkk._strip_suffixes("kirian") == "kirian" # 'an' is not stripped if 'kiri' is not a valid stem (based on length check) - Commented out for now as it requires dictionary validation

def test_strip_basic_prefixes():
    """Test stripping of basic prefixes (-di, -ke, -se)."""
    # Initialize DictionaryManager with the test dictionary file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_dict_path = os.path.join(current_dir, "data", "test_kata_dasar.txt")
    dictionary_manager = DictionaryManager(dictionary_path=test_dict_path)
    # Initialize ModernKataKupas with the test dictionary manager
    mkk = ModernKataKupas()
    mkk.dictionary = dictionary_manager

    # Test cases for basic prefixes
    assert mkk._strip_prefixes("dibaca") == ("baca", ["di"])
    assert mkk._strip_prefixes("ketua") == ("tua", ["ke"])
    assert mkk._strip_prefixes("sekolah") == ("kolah", ["se"])
    assert mkk._strip_prefixes("dimakan") == ("makan", ["di"])

    # Test case with no prefix
    assert mkk._strip_prefixes("baca") == ("baca", [])
    # Test case with unknown prefix (should not strip)
    assert mkk._strip_prefixes("prabaca") == ("prabaca", [])

# Add tests for combined prefixes and suffixes later as the logic is implemented in segment()

def test_strip_combined_affixes():
    """Test stripping of combined prefixes and suffixes using segment()."""
    # Initialize DictionaryManager with the test dictionary file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_dict_path = os.path.join(current_dir, "data", "test_kata_dasar.txt")
    dictionary_manager = DictionaryManager(dictionary_path=test_dict_path)
    # Initialize ModernKataKupas with the test dictionary manager
    mkk = ModernKataKupas()
    mkk.dictionary = dictionary_manager

    # Test cases for combined affixes
    # Note: The current implementation strips prefixes first, then suffixes.
    # This order might need adjustment based on actual Indonesian morphology rules.
    assert mkk.segment("dimakanlah") == "di~makan~lah"
    assert mkk.segment("kesekolah") == "ke~sekolah"
    assert mkk.segment("dibukukan") == "di~buku~kan"
    assert mkk.segment("dilemparkan") == "di~lempar~kan"
    assert mkk.segment("disiagakan") == "di~siaga~kan"
    assert mkk.segment("kepadanya") == "ke~pada~nya"
    assert mkk.segment("sebaiknya") == "se~baik~nya"
    assert mkk.segment("sebisanya") == "se~bisa~nya"

    # Test cases with only prefixes
    assert mkk.segment("dibaca") == "di~baca"
    assert mkk.segment("ketua") == "ke~tua"
    assert mkk.segment("sekolah") == "sekolah"

    # Test cases with only suffixes (should still work via segment calling _strip_suffixes)
    assert mkk.segment("bukuku") == "buku~ku"
    assert mkk.segment("ambilkanlah") == "ambil~kan~lah"
    assert mkk.segment("siapakah") == "siapa~kah"
    assert mkk.segment("miliknya") == "milik~nya"
    assert mkk.segment("rumahkupun") == "rumah~ku~pun"
    assert mkk.segment("makanan") == "makan~an"
    assert mkk.segment("panasi") == "panas~i"
    assert mkk.segment("lemparkan") == "lempar~kan"
    assert mkk.segment("pukulan") == "pukul~an"
    assert mkk.segment("mainkanlah") == "main~kan~lah"

    # Test cases with no affixes
    assert mkk.segment("buku") == "buku"
    assert mkk.segment("baca") == "baca"
    assert mkk.segment("minum") == "minum"


def test_strip_men_peN_prefixes_step21():
    """Test kasus Step 2.1: prefiks kompleks meN- dan peN- (alokasi alomorf dan peluluhan)."""
    import os
    from src.modern_kata_kupas.dictionary_manager import DictionaryManager
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_dict_path = os.path.join(current_dir, "data", "test_kata_dasar.txt")
    dictionary_manager = DictionaryManager(dictionary_path=test_dict_path)
    mkk = ModernKataKupas()
    mkk.dictionary = dictionary_manager
    # Tambahkan assertion untuk memeriksa kamus
    assert "baca" in mkk.dictionary.kata_dasar_set, "Test dictionary does not contain 'baca' before segmentation call!"
    assert mkk.dictionary.is_kata_dasar("baca"), "is_kata_dasar('baca') returned False unexpectedly!"
    # Kasus meN-
    assert mkk.segment("membaca") == "meN~baca"
    assert mkk.segment("memukul") == "meN~pukul"
    assert mkk.segment("menulis") == "meN~tulis"
    assert mkk.segment("menyapu") == "meN~sapu"
    assert mkk.segment("mengambil") == "meN~ambil"
    assert mkk.segment("mengupas") == "meN~kupas"
    assert mkk.segment("mengebom") == "meN~bom"
    # Kasus peN-
    assert mkk.segment("pemukul") == "peN~pukul"
    assert mkk.segment("pengirim") == "peN~kirim"

def test_strip_ber_ter_per_prefixes_step22():
    """Test kasus Step 2.2: prefiks ber-, ter-, dan per- (alokasi alomorf dan peluluhan)."""
    import os
    from src.modern_kata_kupas.dictionary_manager import DictionaryManager
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_dict_path = os.path.join(current_dir, "data", "test_kata_dasar.txt")
    dictionary_manager = DictionaryManager(dictionary_path=test_dict_path)
    mkk = ModernKataKupas()
    mkk.dictionary = dictionary_manager

    # Asumsi kata dasar yang relevan ada di test_kata_dasar.txt:
    # lari, buat, ajar, kerja, ternak, bawa, asa, lihat, anjur, percik, luas, tani

    # Kasus ber-
    assert mkk.segment("berlari") == "ber~lari"
    assert mkk.segment("berbuat") == "ber~buat"
    assert mkk.segment("belajar") == "ber~ajar"    # bel- allomorph
    assert mkk.segment("bekerja") == "ber~kerja"    # be- allomorph (specific to kerja or k-initial)
    assert mkk.segment("beternak") == "ber~ternak"  # be- allomorph (specific to ternak or t-initial, based on rule)
                                                  # Note: rule for ber- was be- + k. If ternak starts with t, this might test fallback or other rules.
                                                  # The affix_rules.json has ber- (default), bel- (a), be- (k).
                                                  # So "beternak" should be "ber~ternak" if "be-" is only for "k".
                                                  # If "beternak" is expected as "ber~ternak", the "be-" allomorph for "ber-" must specifically target "k".
                                                  # The current rules are: ber->be + k. So "beternak" should be "ber~ternak" via default "ber-" rule.

    # Kasus ter-
    assert mkk.segment("terbawa") == "ter~bawa"
    assert mkk.segment("terasa") == "ter~asa"      # Assuming "asa" is a root.
    assert mkk.segment("terlihat") == "ter~lihat"
    assert mkk.segment("telanjur") == "ter~anjur"  # tel- allomorph
    assert mkk.segment("terpercik") == "ter~percik"

    # Kasus per-
    assert mkk.segment("perbuat") == "per~buat"
    assert mkk.segment("perluas") == "per~luas"
    assert mkk.segment("pelajar") == "per~ajar"    # pel- allomorph
    assert mkk.segment("petani") == "per~tani"      # pe- allomorph

    # Kasus kombinasi dengan sufiks
    assert mkk.segment("terlihatlah") == "ter~lihat~lah"
    assert mkk.segment("perbuatannya") == "per~buat~an~nya"
    assert mkk.segment("belajarlah") == "ber~ajar~lah"