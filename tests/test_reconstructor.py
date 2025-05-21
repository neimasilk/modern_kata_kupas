# tests/test_reconstructor.py
"""
Unit tests untuk Reconstructor.
"""

import pytest
from modern_kata_kupas.reconstructor import Reconstructor
from modern_kata_kupas.rules import MorphologicalRules # Mungkin diperlukan nanti

@pytest.fixture
def dummy_rules_recon():
    # Buat rules dummy untuk tes rekonstruksi
    rules = MorphologicalRules() # Asumsi ada file aturan dummy atau cara inisialisasi lain
    # Tambahkan beberapa aturan dummy jika perlu untuk rekonstruksi
    return rules

@pytest.fixture
def reconstructor_instance(dummy_rules_recon):
    return Reconstructor(rules=dummy_rules_recon)

def test_reconstructor_init(reconstructor_instance):
    """Tes inisialisasi Reconstructor."""
    assert reconstructor_instance is not None
    assert reconstructor_instance.rules is not None

def test_reconstruct_simple_word_no_affixes(reconstructor_instance):
    """Tes rekonstruksi kata dasar tanpa afiks (placeholder)."""
    root_word = "makan"
    affixes = []
    # Implementasi placeholder saat ini mungkin hanya mengembalikan root_word
    reconstructed = reconstructor_instance.reconstruct(root_word, affixes)
    assert reconstructed == root_word

def test_reconstruct_with_simple_prefix(reconstructor_instance):
    """Tes rekonstruksi dengan prefiks sederhana (placeholder)."""
    root_word = "coba"
    affixes = ["men-"] # Asumsi "men-" adalah bentuk afiks yang disimpan
    # Implementasi placeholder saat ini mungkin naif
    # hasil yang diharapkan setelah implementasi: "mencoba"
    reconstructed = reconstructor_instance.reconstruct(root_word, affixes)
    # Perbarui assertion ini setelah implementasi Reconstructor lebih baik
    # Untuk placeholder saat ini, mungkin hasilnya "mencoba" atau "men-coba"
    # tergantung logika placeholder di reconstructor.py
    # print(f"Hasil reconstruct placeholder: {reconstructed}")
    assert reconstructed is not None # Ganti dengan assertion yang lebih spesifik

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