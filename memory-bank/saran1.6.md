Baik, saya telah menganalisis output \`pytest\` Anda. Terdapat dua kegagalan utama:

1.  **`test_strip_basic_prefixes`**: Gagal karena `mkk._strip_prefixes("dibaca")` mengembalikan `('dibaca', [])` padahal seharusnya `('baca', ['di'])`.
2.  **`test_strip_combined_affixes`**: Gagal karena `mkk.segment("dimakanlah")` mengembalikan `'dimakanlah'` padahal seharusnya `'di~makan~lah'`.

Pesan *stdout* yang paling menonjol dan muncul di kedua kegagalan adalah:
`Placeholder: MorphologicalRules initialized without specific rules file.`

Ini adalah akar masalahnya. Kelas `ModernKataKupas` saat diinisialisasi dalam tes tidak memuat file `affix_rules.json` yang berisi aturan-aturan prefiks. Akibatnya, `self.rules` di dalam `ModernKataKupas` tidak memiliki aturan yang diperlukan, sehingga `_strip_prefixes` tidak dapat melepaskan prefiks apa pun.

Mari kita perbaiki ini dengan memastikan `ModernKataKupas` memuat file aturan saat inisialisasi.

**Langkah-langkah Perbaikan:**

1.  **Modifikasi `ModernKataKupas.__init__` di `src/modern_kata_kupas/separator.py`**:
    Kita akan mengubah konstruktor untuk memuat `affix_rules.json` menggunakan `importlib.resources`, mirip dengan cara `DictionaryManager` memuat kamus default. Ini memastikan bahwa file aturan dapat ditemukan terlepas dari bagaimana paket diinstal atau dijalankan.

2.  **Perbarui `setup.py`**:
    File `setup.py` saat ini hanya menyertakan file `*.txt` dalam `package_data` untuk `modern_kata_kupas.data`. Ini perlu diperbarui untuk juga menyertakan file `*.json`.

Berikut adalah modifikasi yang diusulkan:

**1. Modifikasi `src/modern_kata_kupas/separator.py`**

```python
# src/modern_kata_kupas/separator.py
"""
Modul untuk memisahkan kata berimbuhan menjadi kata dasar dan afiksnya.
"""
import os # Tambahkan ini jika belum ada
import importlib.resources # Tambahkan ini

from .normalizer import TextNormalizer
from .dictionary_manager import DictionaryManager
from .rules import MorphologicalRules
from .stemmer_interface import IndonesianStemmer
from .utils.alignment import align

MIN_STEM_LENGTH_FOR_POSSESSIVE = 3 # Panjang minimal kata dasar untuk pemisahan sufiks posesif

# Path untuk data default dalam paket
DEFAULT_DATA_PACKAGE_PATH = "modern_kata_kupas.data"
DEFAULT_RULES_FILENAME = "affix_rules.json"

class ModernKataKupas:
    """
    Kelas utama untuk proses pemisahan kata berimbuhan.
    """
    MIN_STEM_LENGTH_FOR_POSSESSIVE = 3 
    MIN_STEM_LENGTH_FOR_DERIVATIONAL_SUFFIX_STRIPPING = 4 
    MIN_STEM_LENGTH_FOR_PARTICLE = 3 

    def __init__(self, dictionary_path: str = None, rules_file_path: str = None): # Modifikasi __init__
        """
        Inisialisasi ModernKataKupas dengan dependensi yang diperlukan.

        Args:
            dictionary_path (str, optional): Path ke file kamus khusus. 
                                            Jika None, kamus default akan dimuat.
            rules_file_path (str, optional): Path ke file aturan khusus. 
                                           Jika None, file aturan default akan dimuat.
        """
        self.normalizer = TextNormalizer()
        self.dictionary = DictionaryManager(dictionary_path=dictionary_path)
        self.stemmer = IndonesianStemmer()
        self.aligner = align

        if rules_file_path:
            self.rules = MorphologicalRules(rules_path=rules_file_path)
        else:
            try:
                # Menggunakan importlib.resources untuk memuat file aturan default dari paket
                # Ini mengharuskan __init__.py ada di dalam direktori 'data' agar bisa dianggap sebagai paket
                # atau path yang benar ke resource
                
                # Pastikan direktori 'data' memiliki file __init__.py agar bisa diakses sebagai package
                # Jika tidak, kita bisa menggunakan path relatif dari file ini
                # Untuk konsistensi dengan DictionaryManager, kita akan mencoba memuatnya sebagai resource paket.

                # Cara 1: Jika 'modern_kata_kupas.data' adalah sebuah paket (memiliki __init__.py)
                # Coba untuk mendapatkan path ke file rules menggunakan importlib.resources
                # Ini lebih aman jika file tersebut berada di dalam package yang terinstal
                with importlib.resources.path(DEFAULT_DATA_PACKAGE_PATH, DEFAULT_RULES_FILENAME) as default_rules_path:
                    self.rules = MorphologicalRules(rules_path=str(default_rules_path))
            except (FileNotFoundError, TypeError, ModuleNotFoundError) as e:
                # Fallback jika importlib.resources.path gagal atau jika DEFAULT_DATA_PACKAGE_PATH bukan package
                # Ini bisa terjadi jika struktur direktori tidak tepat atau file tidak ada.
                # Coba path relatif dari direktori src/modern_kata_kupas
                print(f"Warning: Could not load rules via importlib.resources ({e}). Trying relative path.")
                base_dir = os.path.dirname(os.path.abspath(__file__))
                default_rules_path_rel = os.path.join(base_dir, "data", DEFAULT_RULES_FILENAME)
                if os.path.exists(default_rules_path_rel):
                    self.rules = MorphologicalRules(rules_path=default_rules_path_rel)
                else:
                    # Jika semua gagal, inisialisasi dengan placeholder rules
                    print(f"Error: Default rules file '{DEFAULT_RULES_FILENAME}' not found at expected locations. Initializing with placeholder rules.")
                    self.rules = MorphologicalRules() # Akan mencetak pesan placeholder dari MorphologicalRules

    def segment(self, word: str) -> str:
        normalized_word = self.normalizer.normalize_word(word)
        # Hapus print debug jika tidak diperlukan lagi
        # if word == "dimakanlah" or word == "kesekolah": 
        #     print(f"DEBUG: segment() called with '{word}'")

        # Strategi 1: Prefiks dulu, baru sufiks
        stem_after_prefixes, stripped_prefix_list = self._strip_prefixes(normalized_word)
        # if word == "dimakanlah" or word == "kesekolah":
        #     print(f"DEBUG_STRAT1: stem_after_prefixes='{stem_after_prefixes}', stripped_prefix_list={stripped_prefix_list}")

        final_stem_strat1, stripped_suffix_list_strat1 = self._strip_suffixes(stem_after_prefixes)
        # if word == "dimakanlah" or word == "kesekolah":
        #     print(f"DEBUG_STRAT1: final_stem='{final_stem_strat1}', stripped_suffix_list={stripped_suffix_list_strat1}")
            # print(f"DEBUG_STRAT1: Checking dictionary for '{final_stem_strat1}'...")
            # print(f"DEBUG_KS: Is '{final_stem_strat1}' in self.dictionary.kata_dasar_set? { final_stem_strat1 in self.dictionary.kata_dasar_set }")

        is_strat1_valid_root = self.dictionary.is_kata_dasar(final_stem_strat1)
        # if word == "dimakanlah" or word == "kesekolah":
        #     print(f"DEBUG_STRAT1: is_kata_dasar('{final_stem_strat1}') is {is_strat1_valid_root}")

        if is_strat1_valid_root:
            parts = []
            if stripped_prefix_list: 
                parts.extend(stripped_prefix_list)
            parts.append(final_stem_strat1)
            if stripped_suffix_list_strat1: 
                parts.extend(stripped_suffix_list_strat1)
            
            if not stripped_prefix_list and not stripped_suffix_list_strat1: # Hanya jika kata dasar tanpa afiks
                return final_stem_strat1 
            return '~'.join(parts)
        
        # if word == "dimakanlah" or word == "kesekolah":
        #     print(f"DEBUG: Strat1 failed for '{final_stem_strat1}'. Trying Strat2.")
        
        # Strategi 2: Sufiks dulu, baru prefiks (Fallback)
        stem_after_suffixes, stripped_suffix_list_strat2 = self._strip_suffixes(normalized_word)
        # if word == "dimakanlah" or word == "kesekolah":
        #     print(f"DEBUG_STRAT2: stem_after_suffixes='{stem_after_suffixes}', stripped_suffix_list={stripped_suffix_list_strat2}")

        final_stem_strat2, stripped_prefix_list_strat2 = self._strip_prefixes(stem_after_suffixes)
        # if word == "dimakanlah" or word == "kesekolah":
        #     print(f"DEBUG_STRAT2: final_stem='{final_stem_strat2}', stripped_prefix_list={stripped_prefix_list_strat2}")
            # print(f"DEBUG_STRAT2: Checking dictionary for '{final_stem_strat2}'...")
        
        is_strat2_valid_root = self.dictionary.is_kata_dasar(final_stem_strat2)
        # if word == "dimakanlah" or word == "kesekolah":
        #         print(f"DEBUG_STRAT2: is_kata_dasar('{final_stem_strat2}') is {is_strat2_valid_root}")

        if is_strat2_valid_root:
            parts = []
            if stripped_prefix_list_strat2:
                parts.extend(stripped_prefix_list_strat2)
            parts.append(final_stem_strat2)
            if stripped_suffix_list_strat2:
                parts.extend(stripped_suffix_list_strat2)
            
            if not stripped_prefix_list_strat2 and not stripped_suffix_list_strat2: # Hanya jika kata dasar tanpa afiks
                    return final_stem_strat2
            return '~'.join(parts)
        
        # if word == "dimakanlah" or word == "kesekolah":
        #     print(f"DEBUG: Both strats failed. Fallback for '{normalized_word}'.")
        
        # Fallback: Jika kedua strategi gagal, kembalikan kata yang sudah dinormalisasi
        # Ini akan terjadi jika kata tersebut adalah kata dasar atau tidak dapat disegmentasi oleh aturan saat ini.
        return normalized_word


    def _handle_reduplication(self, word: str) -> str:
        """
        Helper method to handle reduplication (stub).
        """
        # pass # Stub implementation - Komentari atau hapus jika tidak digunakan
        return word # Untuk saat ini kembalikan kata aslinya


    def _strip_suffixes(self, word: str) -> tuple[str, list[str]]:
        current_word = str(word) 
        stripped_suffixes_in_stripping_order = []

        particles = ['kah', 'lah', 'pun']
        
        # Strip partikel
        original_word_before_particle_check = current_word
        for particle_sfx in particles:
            if current_word.endswith(particle_sfx):
                remainder = current_word[:-len(particle_sfx)]
                if len(remainder) >= self.MIN_STEM_LENGTH_FOR_PARTICLE:
                    # Logika untuk mencegah pelepasan salah (misal "sekolah" -> "seko")
                    is_original_root = self.dictionary.is_kata_dasar(original_word_before_particle_check)
                    is_remainder_root = self.dictionary.is_kata_dasar(remainder)
                    
                    # Izinkan pelepasan jika:
                    # 1. Sisa kata adalah root ("ada" dari "adalah")
                    # 2. Atau, kata asli bukan root (jadi pelepasan tidak merusak root yang sudah ada)
                    # 3. Atau, keduanya adalah root (misalnya "adalah" -> "ada")
                    if is_remainder_root or not is_original_root or (is_original_root and is_remainder_root):
                        # Pengecualian spesifik (opsional, jika ada kasus sulit)
                        if current_word == "adalah" and remainder == "ada" and particle_sfx == "lah":
                             current_word = remainder
                             stripped_suffixes_in_stripping_order.append(particle_sfx)
                             break # Hanya satu partikel yang dilepas
                        elif not (is_original_root and not is_remainder_root) : # General case
                             current_word = remainder
                             stripped_suffixes_in_stripping_order.append(particle_sfx)
                             break # Hanya satu partikel yang dilepas
        
        # Strip Posesif
        possessives = ['ku', 'mu', 'nya']
        word_before_possessives = current_word
        for poss_sfx in possessives:
            if word_before_possessives.endswith(poss_sfx) and \
               len(word_before_possessives[:-len(poss_sfx)]) >= self.MIN_STEM_LENGTH_FOR_POSSESSIVE:
                current_word = word_before_possessives[:-len(poss_sfx)]
                stripped_suffixes_in_stripping_order.append(poss_sfx)
                break # Hanya satu posesif yang dilepas

        # Strip Derivasional
        derivational_suffixes = ['kan', 'i', 'an']
        word_before_derivational = current_word
        for deriv_sfx in derivational_suffixes:
            if word_before_derivational.endswith(deriv_sfx):
                remainder = word_before_derivational[:-len(deriv_sfx)]
                if len(remainder) >= self.MIN_STEM_LENGTH_FOR_DERIVATIONAL_SUFFIX_STRIPPING:
                    current_word = remainder
                    stripped_suffixes_in_stripping_order.append(deriv_sfx)
                    break # Hanya satu sufiks derivasional yang dilepas

        return current_word, list(reversed(stripped_suffixes_in_stripping_order))


    def _strip_prefixes(self, word: str) -> tuple[str, list[str]]:
        current_word = str(word)
        stripped_prefixes_output = []

        # Pastikan self.rules diinisialisasi dengan benar dan memiliki aturan
        if not hasattr(self.rules, 'get_prefix_rules') or not callable(self.rules.get_prefix_rules):
             # Ini seharusnya tidak terjadi jika __init__ berjalan dengan benar
            print("Error: self.rules.get_prefix_rules is not available.")
            return current_word, stripped_prefixes_output

        prefix_rules = self.rules.get_prefix_rules()
        if not prefix_rules and (word.startswith("di") or word.startswith("ke") or word.startswith("se")):
            # Jika aturan kosong tapi kita tahu ada potensi prefiks dari tes yang gagal
            # ini menunjukkan masalah pemuatan aturan.
            # Pesan ini hanya untuk debug jika masalah berlanjut.
            print(f"Warning: Prefix rules are empty. Word: {word}")


        for rule in prefix_rules:
            prefix_form = rule.get("form")
            canonical_form = rule.get("canonical", prefix_form)

            if prefix_form and current_word.startswith(prefix_form):
                potential_root = current_word[len(prefix_form):]
                
                # Untuk Langkah 1.6, validasi utama akan dilakukan di metode segment()
                # setelah _strip_suffixes juga. Di sini kita hanya melakukan pelepasan.
                current_word = potential_root
                stripped_prefixes_output.append(canonical_form)
                
                # Untuk Langkah 1.6 (prefiks sederhana, non-morfofonemik, tidak berlapis),
                # kita biasanya hanya melepas satu prefiks dari jenis ini.
                break 

        return current_word, stripped_prefixes_output

    def _apply_morphophonemic_segmentation_rules(self, word: str) -> str:
        """
        Helper method to apply morphophonemic segmentation rules (stub).
        """
        # pass # Stub implementation
        return word # Kembalikan kata asli untuk saat ini
```

**Penjelasan Perubahan di `ModernKataKupas.__init__`:**

  * Menggunakan `importlib.resources.path(DEFAULT_DATA_PACKAGE_PATH, DEFAULT_RULES_FILENAME)` untuk mendapatkan path ke `affix_rules.json` yang berada di dalam paket. Ini adalah cara yang lebih robust.
  * Menambahkan fallback ke path relatif jika `importlib.resources` gagal, dan akhirnya ke inisialisasi `MorphologicalRules()` tanpa argumen jika file tetap tidak ditemukan (yang akan mencetak pesan placeholder dari `MorphologicalRules`).
  * Parameter `rules_file_path` pada `__init__` tetap ada untuk memungkinkan pengguna menyediakan file aturan kustom jika diperlukan.
  * Saya juga menyederhanakan logika di `segment()` dan `_strip_suffixes()` sedikit berdasarkan observasi dari *trace* dan untuk lebih fokus pada masalah utama yaitu pemuatan aturan. Logika di `_strip_suffixes` diperbarui agar lebih mirip dengan implementasi sebelumnya yang berhasil melewati tes sufiks.

**2. Modifikasi `setup.py`**

```python
from setuptools import setup, find_packages

setup(
    name='modern_kata_kupas',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data={
        'modern_kata_kupas.data': ['*.txt', '*.json'], # Tambahkan '*.json'
    },
    install_requires=[
        'PySastrawi', # Pastikan ini ada jika belum
        # dependensi Anda, jika ada
    ],
    # ... (sisa konfigurasi setup.py Anda)
)
```

**Penjelasan Perubahan di `setup.py`:**

  * Pada `package_data`, `'modern_kata_kupas.data': ['*.txt']` diubah menjadi `'modern_kata_kupas.data': ['*.txt', '*.json']`. Ini akan memastikan bahwa file `affix_rules.json` (dan file JSON lainnya di direktori tersebut) disertakan saat paket dibuat dan diinstal.
  * Saya juga menambahkan `PySastrawi` ke `install_requires` untuk memastikan dependensi tersebut terinstal, karena kelas `IndonesianStemmer` Anda menggunakannya.

**3. Tambahkan `__init__.py` ke `src/modern_kata_kupas/data/` (Jika Belum Ada)**

Agar `importlib.resources` dapat menganggap `modern_kata_kupas.data` sebagai sebuah *package resource*, direktori `src/modern_kata_kupas/data/` sebaiknya berisi file `__init__.py` (bisa kosong).

```
src/
└── modern_kata_kupas/
    ├── __init__.py
    ├── data/
    │   ├── __init__.py  <-- Tambahkan file ini (kosong)
    │   ├── affix_rules.json
    │   └── kata_dasar.txt
    ├── dictionary_manager.py
    ├── ... (file lainnya)
```

**Setelah melakukan perubahan ini:**

1.  Pastikan file `src/modern_kata_kupas/data/__init__.py` ada (bisa kosong).
2.  Jika Anda menginstal paket secara lokal untuk pengembangan (misalnya dengan `pip install -e .`), Anda mungkin perlu menjalankan ulang instalasi tersebut agar perubahan pada `setup.py` (terutama `package_data`) diterapkan dengan benar.
3.  Jalankan `pytest` lagi.

Dengan perubahan ini, `ModernKataKupas` seharusnya dapat menemukan dan memuat `affix_rules.json` dengan benar, yang akan mengatasi pesan `Placeholder: MorphologicalRules initialized without specific rules file.` dan memungkinkan tes prefiks berjalan sesuai harapan.