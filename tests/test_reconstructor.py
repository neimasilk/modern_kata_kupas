# tests/test_reconstructor.py
"""
Unit tests untuk Reconstructor.
"""

import pytest
from modern_kata_kupas.reconstructor import Reconstructor
from modern_kata_kupas.rules import MorphologicalRules # Mungkin diperlukan nanti
from modern_kata_kupas.dictionary_manager import DictionaryManager # Added import
from modern_kata_kupas.stemmer_interface import IndonesianStemmer # Added
from modern_kata_kupas import ModernKataKupas # For integration tests
from modern_kata_kupas.exceptions import DictionaryFileNotFoundError, RuleError

@pytest.fixture
def dummy_rules_recon():
    """Provides a MorphologicalRules instance for Reconstructor tests."""
    return MorphologicalRules() # Assumes default loading

@pytest.fixture
def dummy_dict_mgr_recon():
    """Provides a DictionaryManager instance for Reconstructor tests."""
    return DictionaryManager() # Assumes default loading

@pytest.fixture
def dummy_stemmer_recon(): # Added fixture for stemmer
    """Provides an IndonesianStemmer instance for Reconstructor tests.""" # Added
    return IndonesianStemmer() # Added

@pytest.fixture
def reconstructor_instance(dummy_rules_recon, dummy_dict_mgr_recon, dummy_stemmer_recon): # Added stemmer
    # Create a DictionaryManager instance.
    # This might require a path to a dummy dictionary or allowing it to use default.
    # For simplicity, let's assume it can initialize with default or None.
    # dictionary_manager = DictionaryManager()
    return Reconstructor(rules=dummy_rules_recon, dictionary_manager=dummy_dict_mgr_recon, stemmer=dummy_stemmer_recon) # Pass stemmer

def test_reconstructor_init(reconstructor_instance):
    """Tes inisialisasi Reconstructor."""
    assert reconstructor_instance is not None
    assert reconstructor_instance.rules is not None

def test_reconstruct_simple_word_no_affixes(reconstructor_instance):
    """Tes rekonstruksi kata dasar tanpa afiks (placeholder)."""
    segmented_word = "makan"
    # Reconstructor.reconstruct expects a single segmented string.
    reconstructed = reconstructor_instance.reconstruct(segmented_word)
    assert reconstructed == segmented_word

def test_reconstruct_with_simple_prefix(reconstructor_instance):
    """Tes rekonstruksi dengan prefiks sederhana (placeholder)."""
    segmented_word = "meN~coba" # Using segmented string format
    expected_reconstruction = "mencoba" # Expected output
    # Reconstructor.reconstruct expects a single segmented string.
    reconstructed = reconstructor_instance.reconstruct(segmented_word)
    # Perbarui assertion ini setelah implementasi Reconstructor lebih baik
    # Untuk placeholder saat ini, mungkin hasilnya "mencoba" atau "men-coba"
    # tergantung logika placeholder di reconstructor.py
    # print(f"Hasil reconstruct placeholder: {reconstructed}")
    assert reconstructed == expected_reconstruction # Ganti dengan assertion yang lebih spesifik

# Tambahkan lebih banyak tes di sini seiring pengembangan Reconstructor
# Contoh:
# def test_reconstruct_with_suffix(reconstructor_instance):
#     root_word = "makan"
#     affixes = ["-an"]
#     # Harapan: "makanan"
#     reconstructed = reconstructor_instance.reconstruct(root_word, affixes)
#     assert reconstructed == "makanan"
#
# def test_reconstruct_with_confix(reconstructor_instance):
#     root_word = "adil"
#     affixes = ["ke-", "-an"]
#     # Harapan: "keadilan"
#     reconstructed = reconstructor_instance.reconstruct(root_word, affixes)
#     assert reconstructed == "keadilan"

import unittest
from src.modern_kata_kupas.separator import ModernKataKupas # Main class for .reconstruct()
# from src.modern_kata_kupas.reconstructor import Reconstructor # Directly test Reconstructor if needed
# from src.modern_kata_kupas.rules import MorphologicalRules
# from src.modern_kata_kupas.dictionary_manager import DictionaryManager

class TestWordReconstruction(unittest.TestCase):
    def setUp(self):
        """Set up the ModernKataKupas instance for test methods."""
        self.mkk = ModernKataKupas()
        # The ModernKataKupas instance self.mkk will have its own Reconstructor,
        # DictionaryManager, and MorphologicalRules initialized.
        # Ensure that the default dictionary and rules are sufficient for these tests.
        # Specifically, roots like 'las', 'cat', 'bom', 'ajar', 'tani', 'lebar', 'adil', 'bangun', 'juang', 'timbang', 'hasil'
        # and all other roots used in assertions must be in `kata_dasar.txt`.
        # Also, affix rules in `affix_rules.json` must support the morphophonemic changes tested.

    def test_basic_reconstruction(self):
        self.assertEqual(self.mkk.reconstruct("makan"), "makan")
        self.assertEqual(self.mkk.reconstruct("di~baca"), "dibaca")
        self.assertEqual(self.mkk.reconstruct("makan~an"), "makanan")
        self.assertEqual(self.mkk.reconstruct("minum~lah"), "minumlah")
        self.assertEqual(self.mkk.reconstruct("buku~nya"), "bukunya")

    def test_prefixes_with_morphophonemics(self):
        self.assertEqual(self.mkk.reconstruct("meN~pukul"), "memukul")
        self.assertEqual(self.mkk.reconstruct("meN~tulis"), "menulis")
        self.assertEqual(self.mkk.reconstruct("meN~sapu"), "menyapu")
        self.assertEqual(self.mkk.reconstruct("meN~goreng"), "menggoreng")
        self.assertEqual(self.mkk.reconstruct("meN~bom"), "mengebom")   # Monosyllabic
        self.assertEqual(self.mkk.reconstruct("meN~cat"), "mengecat") # Monosyllabic
        # Based on `affix_rules.json` for `meN-`: `{"surface": "me", "condition_root_starts_with": ["l", "m", "n", "r", "w", "y"], "elision": "none"}`.
        # Thus, "meN~las" -> "melas"
        self.assertEqual(self.mkk.reconstruct("meN~las"), "melas") 
        self.assertEqual(self.mkk.reconstruct("peN~pukul"), "pemukul")
        self.assertEqual(self.mkk.reconstruct("peN~tulis"), "penulis")
        self.assertEqual(self.mkk.reconstruct("peN~sapu"), "penyapu")
        self.assertEqual(self.mkk.reconstruct("peN~bom"), "pengebom")
        self.assertEqual(self.mkk.reconstruct("ber~ajar"), "belajar")
        # Assuming 'per~tani~an' is the segmented form for 'pertanian'
        # `parse_segmented_string` will give: root="tani", prefixes=["per"], suffixes_derivational=["an"]
        # `reconstruct` order: root + deriv_suffix -> "tanian"
        # Then redup (none)
        # Then poss/part suffixes (none)
        # Then prefix: per + tanian -> pertanian
        self.assertEqual(self.mkk.reconstruct("per~tani~an"), "pertanian")
        self.assertEqual(self.mkk.reconstruct("per~lebar"), "perlebar") # No morphophonemic change

    def test_reduplication_reconstruction(self):
        self.assertEqual(self.mkk.reconstruct("buku~ulg"), "buku-buku")
        # anak~ulg~nya -> root="anak", redup_marker="ulg", suffixes_possessive=["nya"]
        # Order: root -> "anak"
        # Derivational (none)
        # Reduplication: "anak" -> "anak-anak"
        # Possessive/Particle: "anak-anak" + "nya" -> "anak-anaknya"
        self.assertEqual(self.mkk.reconstruct("anak~ulg~nya"), "anak-anaknya")
        # mobil~ulg~an -> root="mobil", redup_marker="ulg", suffixes_derivational=["an"]
        # Order: root -> "mobil"
        # Derivational: "mobil" + "an" -> "mobilan"
        # Reduplication: "mobilan" -> "mobilan-mobilan" (This is the expected behavior with current order)
        # However, the task description for "mobil-mobilan" implies the root is "mobil", then "ulg", then "an".
        # This means "an" is a suffix on the reduplicated form, not on the base before reduplication.
        # The `_handle_reduplication` in `separator.py` for "mobil-mobilan" returns:
        # base_form="mobil", redup_marker="ulg", direct_redup_suffixes=["an"]
        # The `segment()` method assembles this as "mobil~ulg~an".
        # `parse_segmented_string`: root="mobil", redup_marker="ulg", suffixes_derivational=["an"]
        # With the new logic, "an" after "ulg" should be handled by "suffixes_after_reduplication"
        # mobil~ulg~an:
        # parse: root="mobil", redup_marker="ulg", suffixes_after_reduplication=["an"]
        # reconstruct: current_form="mobil"
        # deriv (standard): none
        # redup: _apply_reduplication_reconstruction("mobil", "ulg", None) -> "mobil-mobil"
        # suffixes_after_redup: current_form = "mobil-mobil" + "an" -> "mobil-mobilan"
        # poss/part: none
        # prefixes: none
        # Result: "mobil-mobilan"
        self.assertEqual(self.mkk.reconstruct("mobil~ulg~an"), "mobil-mobilan")
        self.assertEqual(self.mkk.reconstruct("rumah~ulg~an"), "rumah-rumahan")
        # Assuming "i" is a derivational suffix, it will be categorized as suffixes_after_reduplication
        self.assertEqual(self.mkk.reconstruct("motor~ulg~i"), "motor-motori") 

        self.assertEqual(self.mkk.reconstruct("laki~rp"), "lelaki")
        self.assertEqual(self.mkk.reconstruct("tua~rp~ku"), "tetuaku") # "ku" is possessive, applies after redup
        self.assertEqual(self.mkk.reconstruct("sayur~rs(~mayur)"), "sayur-mayur")
        
        # bolak~rs(~balik)~an
        # parse: root="bolak", redup_marker="rs", redup_variant="~balik", suffixes_after_reduplication=["an"]
        # reconstruct: current_form="bolak"
        # deriv (standard): none
        # redup: _apply_reduplication_reconstruction("bolak", "rs", "~balik") -> "bolak-balik"
        # suffixes_after_redup: current_form = "bolak-balik" + "an" -> "bolak-balikan"
        # poss/part: none
        # prefixes: none
        # Result: "bolak-balikan"
        self.assertEqual(self.mkk.reconstruct("bolak~rs(~balik)~an"), "bolak-balikan")

    def test_layered_affixes(self):
        self.assertEqual(self.mkk.reconstruct("ke~adil~an"), "keadilan") # "an" is standard derivational here
        self.assertEqual(self.mkk.reconstruct("peN~bangun~an"), "pembangunan")
        # meN~per~juang~kan
        # parse: root="juang", prefixes=["meN-", "per-"], suffixes_derivational=["kan"]
        # reconstruct: current_form = "juang"
        # deriv: current_form = "juangkan"
        # redup: none
        # poss/part: none
        # prefix (per-): _apply_forward_morphophonemics("per", "juangkan") -> "perjuangkan" (assuming "per-" is simple)
        # prefix (meN-): _apply_forward_morphophonemics("meN", "perjuangkan") -> "memperjuangkan"
        self.assertEqual(self.mkk.reconstruct("meN~per~juang~kan"), "memperjuangkan")
        self.assertEqual(self.mkk.reconstruct("di~per~timbang~kan~lah"), "dipertimbangkanlah")
        self.assertEqual(self.mkk.reconstruct("ke~ber~hasil~an~nya"), "keberhasilannya")

    def test_idempotency_segment_reconstruct(self):
        words_to_test = [
            "makanan", "memperjuangkannya", "buku-bukunya", "lelaki",
            "sayur-mayur", "dibacakan", "keadilan", "pembangunan",
            "terpercaya", "menulis", "menyapu", "mengambil",
            "pengeboman", "pelajar",
            "mobil-mobilan", # Should now work with the new logic
            "bolak-balikan", # Should now work with the new logic
            "rumah-rumahan",  # Added for completeness
            # New complex words for idempotency test (V1.0 context)
            "mempertanggungjawabkan",
            "dipersemakmurkan",
            "sebaik-baiknya",   # V1.0 segments to sebaik~ulg~nya
            "keberlangsungan",
            "mengomunikasikan",
            "ketidakadilan",
        ]
        
        for word in words_to_test:
            with self.subTest(word=word):
                normalized = self.mkk.normalizer.normalize_word(word)
                segmented = self.mkk.segment(word)
                reconstructed = self.mkk.reconstruct(segmented)
                # if word == "sebaik-baiknya": # Debug print (keeping commented for now)
                #     print(f"DEBUG: word='{word}', norm='{normalized}', recon='{reconstructed}'")
                #     print(f"DEBUG: repr(norm)='{repr(normalized)}', repr(recon)='{repr(reconstructed)}'")
                #     print(f"DEBUG: type(norm)={type(normalized)}, type(recon)={type(reconstructed)}")
                #     print(f"DEBUG: norm == recon? {normalized == reconstructed}")
                #     print(f"DEBUG: str(norm) == str(recon)? {str(normalized) == str(reconstructed)}")
                self.assertEqual(str(reconstructed), str(normalized), f"Failed for word: {word} (segmented: {segmented}, reconstructed: {reconstructed}, expected: {normalized})")

if __name__ == '__main__':
    unittest.main()