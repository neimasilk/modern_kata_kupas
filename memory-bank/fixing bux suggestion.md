Baik, saya sudah membaca log pytest Anda dan konteks dari file-file di memory-bank.
Masalah utama yang menyebabkan semua 4 error saat pytest mengumpulkan tes adalah TypeError pada file src/modern_kata_kupas/rules.py di baris 173.
Detail Masalah:
Errornya adalah:
E TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
Ini terjadi pada definisi fungsi get_suffix_type di dalam kelas MorphologicalRules:

Python


# src\modern_kata_kupas\rules.py:173
def get_suffix_type(self, suffix_form: str) -> str | None:


Penggunaan str | None untuk type hinting (menunjukkan bahwa fungsi bisa mengembalikan string atau None) adalah fitur yang diperkenalkan di Python 3.10. Log Anda menunjukkan bahwa Anda menggunakan Python 3.9.0. Oleh karena itu, Python 3.9 tidak mengenali sintaks | untuk type union dengan NoneType.
Saran Solusi Mendetail:
Untuk mengatasi masalah ini, Anda perlu mengubah cara Anda mendefinisikan type hint agar kompatibel dengan Python 3.9. Anda dapat menggunakan modul typing dan mengganti str | None dengan Optional[str] atau Union[str, None].
Berikut adalah langkah-langkah untuk memperbaikinya:
Buka file src/modern_kata_kupas/rules.py.
Tambahkan import yang diperlukan dari modul typing di bagian atas file, jika belum ada:
Python
from typing import Optional, Union # Anda bisa memilih salah satu atau keduanya

Jika Anda sudah memiliki import lain dari typing, cukup tambahkan Optional atau Union ke daftar import tersebut.
Ubah baris 173 (definisi fungsi get_suffix_type) menjadi salah satu dari berikut ini:
Menggunakan Optional[str] (lebih disarankan untuk kasus ini):
Python
def get_suffix_type(self, suffix_form: str) -> Optional[str]:
```Optional[str]` secara semantik sama dengan `Union[str, None]`.



Menggunakan Union[str, None]:
Python
def get_suffix_type(self, suffix_form: str) -> Union[str, None]:


Contoh Perbaikan pada src/modern_kata_kupas/rules.py:

Python


# Di bagian atas file src/modern_kata_kupas/rules.py
from typing import List, Dict, Any, Tuple, Optional # Tambahkan Optional di sini jika belum ada

# ... (kode lainnya)

class MorphologicalRules:
    # ... (metode lainnya)

    # Ubah baris ini
    # def get_suffix_type(self, suffix_form: str) -> str | None:
    # Menjadi:
    def get_suffix_type(self, suffix_form: str) -> Optional[str]:
        # Implementasi fungsi Anda
        # ...
        # Contoh:
        if suffix_form in self.suffix_rules: # Asumsi self.suffix_rules ada
            return self.suffix_rules[suffix_form].get("type") # Sesuaikan dengan struktur data Anda
        return None


Mengapa ini akan menyelesaikan masalah:
Dengan menggunakan typing.Optional atau typing.Union, Anda menggunakan sintaks type hinting yang didukung oleh Python 3.9. Ini akan memungkinkan pytest untuk mengumpulkan (collect) tes Anda dengan benar tanpa memunculkan TypeError saat mengimpor modul rules.py. Karena semua 4 error yang Anda lihat berasal dari masalah yang sama pada saat impor MorphologicalRules, perbaikan tunggal ini seharusnya menyelesaikan keempatnya.
Langkah Berikutnya:
Terapkan perubahan di atas pada file src/modern_kata_kupas/rules.py.
Jalankan kembali pytest.
Jika setelah perbaikan ini masih ada error, silakan berikan log terbaru. Namun, saya cukup yakin ini akan menyelesaikan masalah TypeError yang Anda hadapi saat ini.
---


Tentu, saya akan memeriksa kembali kode yang relevan dan menyajikan saran perbaikan dalam format Canvas.

Berikut adalah saran perbaikan untuk file src/modern\_kata\_kupas/rules.py agar kompatibel dengan Python 3.9 dan menyelesaikan TypeError yang Anda alami.

Perbaikan rules.py  
May 24, 10:11 AM

**Penjelasan Perbaikan dan Saran Tambahan:**

1. **Type Hinting untuk Python \< 3.10:**  
   * Seperti yang dibahas sebelumnya, str | None telah diubah menjadi Optional\[str\] pada fungsi get\_suffix\_type (dan juga saya tambahkan contoh untuk get\_prefix\_type).  
   * Pastikan Anda memiliki from typing import Optional (atau Union) di bagian atas file.  
2. **Pemuatan Aturan (\_load\_rules):**  
   * Saya menambahkan penanganan error yang lebih baik menggunakan try-except untuk FileNotFoundError dan json.JSONDecodeError.  
   * Saya membuat asumsi tentang struktur file affix\_rules.json. Jika struktur Anda berbeda (misalnya, bagaimana "suffixes" atau "prefixes" disimpan dan bagaimana setiap aturan didefinisikan di dalamnya), logika dalam \_load\_rules dan cara self.suffix\_rules serta self.prefix\_rules diisi mungkin perlu disesuaikan.  
   * Saya menambahkan penanganan kasus di mana nilai untuk kunci afiks (misalnya, raw\_suffixes\[suffix\_key\]) mungkin berupa dict tunggal, bukan list dari dict. Kode sekarang mengubahnya menjadi list berisi satu dict agar konsisten.  
3. **Logika get\_suffix\_type dan get\_prefix\_type:**  
   * Fungsi ini sekarang mengambil suffix\_form (misalnya, "-lah") sebagai argumen.  
   * Ia mencari suffix\_form ini sebagai kunci dalam self.suffix\_rules.  
   * Jika ditemukan, ia mengambil aturan pertama dari list aturan yang terkait (diasumsikan semua aturan untuk bentuk sufiks yang sama memiliki tipe yang sama atau tipe dari aturan pertama sudah cukup representatif).  
   * Ia kemudian mengembalikan nilai dari kunci "type" dari detail aturan tersebut. Menggunakan .get("type") lebih aman karena akan mengembalikan None jika kunci "type" tidak ada, daripada menyebabkan KeyError.  
   * Jika suffix\_form tidak ditemukan sebagai kunci, ia mengembalikan None.  
4. **Path ke File Aturan (AFFIX\_RULES\_PATH):**  
   * Saya memperbaiki cara BASE\_DIR dan AFFIX\_RULES\_PATH didefinisikan agar lebih robust, dengan asumsi file rules.py berada di src/modern\_kata\_kupas/.  
   * Blok if \_\_name\_\_ \== '\_\_main\_\_': juga disesuaikan untuk mencoba menemukan file affix\_rules.json dengan benar saat skrip dijalankan langsung, baik dari direktori src/modern\_kata\_kupas/ maupun dari root direktori proyek.  
5. **Struktur Data Aturan (self.suffix\_rules, self.prefix\_rules):**  
   * Saya mengasumsikan self.suffix\_rules (dan self.prefix\_rules) adalah sebuah dictionary di mana *kunci* adalah bentuk afiks (misalnya, "-an", "meng-") dan *nilai* adalah **list dari dictionary**, di mana setiap dictionary berisi detail satu aturan spesifik untuk afiks tersebut (misalnya, \[{ "form": "-an", "type": "DS", "allomorphs": \[...\], ...}, ...\]).  
   * Jika struktur data Anda berbeda, misalnya jika nilai adalah dictionary tunggal, maka akses seperti rules\_for\_suffix\[0\] perlu disesuaikan. Logika pemuatan di \_load\_rules sudah mencoba menangani ini dengan mengubah dict tunggal menjadi list berisi satu dict.  
6. **Metode get\_matching\_suffix\_rules dan get\_matching\_prefix\_rules:**  
   * Saya menambahkan implementasi contoh untuk metode ini. Metode ini berguna untuk mendapatkan *semua* aturan yang mungkin cocok dengan akhir atau awal kata.  
   * Kunci-kunci afiks diurutkan berdasarkan panjangnya secara menurun. Ini penting agar afiks yang lebih panjang (misalnya, "-kannya") dicocokkan sebelum yang lebih pendek (misalnya, "-nya" atau "-an"), yang seringkali merupakan perilaku yang diinginkan dalam proses stemming.  
   * Setiap aturan yang cocok dikembalikan sebagai dictionary yang menyertakan pola asli (original\_pattern) untuk referensi.  
7. **Kelas Rule, RemoveSuffixRule, RemovePrefixRule:**  
   * Saya menyertakan kembali definisi kelas-kelas ini dari konteks yang Anda berikan sebelumnya untuk kelengkapan, meskipun error utama tidak ada di sini.

**Langkah Selanjutnya:**

1. **Sesuaikan Struktur Data:** Verifikasi bahwa struktur affix\_rules.json Anda sesuai dengan asumsi yang dibuat dalam kode, terutama bagaimana daftar sufiks/prefiks dan detail masing-masing aturan (termasuk field "type") disimpan. Jika berbeda, sesuaikan logika dalam \_load\_rules dan get\_suffix\_type/get\_prefix\_type.  
2. **Uji Kode:** Jalankan kembali pytest. Error TypeError yang disebabkan oleh str | None seharusnya sudah teratasi.  
3. **Uji Fungsionalitas:** Jika pytest berjalan, uji fungsionalitas MorphologicalRules secara lebih mendalam, terutama metode get\_suffix\_type, get\_prefix\_type, dan metode pencocokan aturan, untuk memastikan mereka bekerja sesuai harapan dengan data aturan Anda. Blok if \_\_name\_\_ \== '\_\_main\_\_': menyediakan contoh pengujian dasar.

Semoga ini membantu Anda memperbaiki masalah dan melanjutkan pengembangan proyek\!



---

# src/modern_kata_kupas/rules.py

import json
import os
from typing import List, Dict, Any, Tuple, Optional, Union # Pastikan Optional atau Union diimpor

# Konstanta untuk path file, bisa disesuaikan jika struktur direktori berbeda
# Diasumsikan file ini berada di src/modern_kata_kupas/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AFFIX_RULES_PATH = os.path.join(BASE_DIR, "data", "affix_rules.json")

class Rule:
    """
    Kelas dasar untuk semua aturan morfologi.
    """
    def __init__(self, pattern: str, replacement: str = "", condition: Optional[str] = None):
        self.pattern = pattern
        self.replacement = replacement
        self.condition = condition

    def apply(self, word: str) -> str:
        """
        Menerapkan aturan ke sebuah kata.
        Metode ini harus di-override oleh subclass.
        """
        raise NotImplementedError("Subclass harus mengimplementasikan metode apply.")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(pattern='{self.pattern}', replacement='{self.replacement}', condition='{self.condition}')"

class RemoveSuffixRule(Rule):
    """
    Aturan untuk menghapus sufiks.
    """
    def apply(self, word: str) -> str:
        if word.endswith(self.pattern):
            # Logika kondisi bisa ditambahkan di sini jika self.condition tidak None
            return word[:-len(self.pattern)]
        return word

class RemovePrefixRule(Rule): # Contoh jika ada aturan prefix
    """
    Aturan untuk menghapus prefiks.
    """
    def apply(self, word: str) -> str:
        if word.startswith(self.pattern):
            # Logika kondisi bisa ditambahkan di sini jika self.condition tidak None
            return word[len(self.pattern):]
        return word


class MorphologicalRules:
    """
    Mengelola dan menerapkan aturan-aturan morfologi untuk stemming.
    """
    def __init__(self, rules_file_path: str = AFFIX_RULES_PATH):
        """
        Inisialisasi dengan memuat aturan dari file JSON.

        Args:
            rules_file_path (str): Path ke file JSON yang berisi aturan afiks.
        """
        self.rules_file_path = rules_file_path
        self.prefix_rules: Dict[str, List[Dict[str, Any]]] = {}
        self.suffix_rules: Dict[str, List[Dict[str, Any]]] = {}
        self.infix_rules: Dict[str, List[Dict[str, Any]]] = {} # Jika ada aturan infiks
        self.all_rules: Dict[str, Any] = {} # Untuk menyimpan semua aturan mentah jika diperlukan
        
        self._load_rules()

    def _load_rules(self) -> None:
        """
        Memuat aturan morfologi dari file JSON.
        Mengelompokkan aturan berdasarkan tipe (prefix, suffix, infix).
        """
        try:
            with open(self.rules_file_path, 'r', encoding='utf-8') as f:
                self.all_rules = json.load(f)
            
            # Mengelompokkan aturan
            # Struktur affix_rules.json diasumsikan memiliki kunci seperti "prefixes", "suffixes"
            # dan di dalamnya ada daftar aturan.
            # Contoh: {"suffixes": {"-lah": [{"form": "-lah", "type": "P", ...}]}}
            
            raw_suffixes = self.all_rules.get("suffixes", {})
            for suffix_key, rules_list in raw_suffixes.items():
                # Pastikan rules_list adalah list
                if isinstance(rules_list, list):
                    self.suffix_rules[suffix_key] = rules_list
                elif isinstance(rules_list, dict): # Jika formatnya { "-lah": { "form": "-lah", ...}}
                    self.suffix_rules[suffix_key] = [rules_list] # Ubah menjadi list berisi satu dict
                else:
                    print(f"Peringatan: Format tidak dikenal untuk sufiks '{suffix_key}' dalam file aturan.")


            raw_prefixes = self.all_rules.get("prefixes", {})
            for prefix_key, rules_list in raw_prefixes.items():
                if isinstance(rules_list, list):
                    self.prefix_rules[prefix_key] = rules_list
                elif isinstance(rules_list, dict):
                    self.prefix_rules[prefix_key] = [rules_list]
                else:
                    print(f"Peringatan: Format tidak dikenal untuk prefiks '{prefix_key}' dalam file aturan.")
            
            # Anda bisa menambahkan pemuatan untuk infiks jika ada
            # raw_infixes = self.all_rules.get("infixes", {})
            # ...

        except FileNotFoundError:
            print(f"Error: File aturan tidak ditemukan di {self.rules_file_path}")
            # Anda bisa melempar exception khusus di sini jika diperlukan
            # raise RulesFileNotFoundError(f"File aturan tidak ditemukan di {self.rules_file_path}")
        except json.JSONDecodeError:
            print(f"Error: Gagal mendekode JSON dari file aturan di {self.rules_file_path}")
            # raise InvalidRulesFormatError(f"Format JSON tidak valid di {self.rules_file_path}")
        except Exception as e:
            print(f"Error tidak terduga saat memuat aturan: {e}")
            # raise

    def get_matching_suffix_rules(self, word: str) -> List[Dict[str, Any]]:
        """
        Mendapatkan semua aturan sufiks yang cocok dengan akhir kata.
        Aturan dikembalikan dalam urutan yang mungkin relevan (misalnya, yang lebih panjang dulu).
        """
        matched_rules = []
        # Urutkan kunci sufiks berdasarkan panjangnya secara menurun
        # agar sufiks yang lebih panjang (misal "-kannya") dicek sebelum yang lebih pendek (misal "-nya")
        sorted_suffix_keys = sorted(self.suffix_rules.keys(), key=len, reverse=True)

        for suffix_pattern in sorted_suffix_keys:
            if word.endswith(suffix_pattern):
                # self.suffix_rules[suffix_pattern] adalah list dari dict aturan
                for rule_detail in self.suffix_rules[suffix_pattern]:
                    # Tambahkan pattern asli ke detail aturan untuk referensi mudah
                    rule_with_pattern = rule_detail.copy()
                    rule_with_pattern['original_pattern'] = suffix_pattern 
                    matched_rules.append(rule_with_pattern)
        return matched_rules

    def get_matching_prefix_rules(self, word: str) -> List[Dict[str, Any]]:
        """
        Mendapatkan semua aturan prefiks yang cocok dengan awal kata.
        """
        matched_rules = []
        sorted_prefix_keys = sorted(self.prefix_rules.keys(), key=len, reverse=True)

        for prefix_pattern in sorted_prefix_keys:
            if word.startswith(prefix_pattern):
                for rule_detail in self.prefix_rules[prefix_pattern]:
                    rule_with_pattern = rule_detail.copy()
                    rule_with_pattern['original_pattern'] = prefix_pattern
                    matched_rules.append(rule_with_pattern)
        return matched_rules
        
    # --- PERBAIKAN UTAMA DI SINI ---
    def get_suffix_type(self, suffix_form: str) -> Optional[str]:
        """
        Mendapatkan tipe dari sebuah bentuk sufiks (misalnya, "-lah", "-an", "-i").
        Tipe bisa berupa Partikel (P), Derivasi (DS), atau Infleksi (IS).

        Args:
            suffix_form (str): Bentuk sufiks yang ingin dicari tipenya.

        Returns:
            Optional[str]: Tipe sufiks jika ditemukan (misalnya "P", "DS", "IS"), 
                           atau None jika sufiks tidak ditemukan dalam aturan.
        """
        # self.suffix_rules adalah Dict[str, List[Dict[str, Any]]]
        # Contoh: {"-lah": [{"form": "-lah", "type": "P", ...}, ...], ...}
        
        # Cari sufiks dalam kunci-kunci self.suffix_rules
        if suffix_form in self.suffix_rules:
            # Ambil list aturan untuk sufiks tersebut
            rules_for_suffix = self.suffix_rules[suffix_form]
            if rules_for_suffix: # Pastikan list tidak kosong
                # Ambil tipe dari aturan pertama (asumsi semua aturan untuk sufiks yang sama memiliki tipe yang sama,
                # atau ambil tipe dari aturan yang paling spesifik jika ada logika tambahan)
                # Setiap elemen dalam rules_for_suffix adalah dict yang berisi detail aturan, termasuk 'type'.
                # Contoh: {"form": "-lah", "type": "P", "description": "Partikel -lah"}
                rule_detail = rules_for_suffix[0] # Ambil aturan pertama sebagai representatif
                return rule_detail.get("type") # Menggunakan .get() untuk keamanan jika 'type' tidak ada
        
        # Jika sufiks tidak ditemukan sebagai kunci utama, mungkin perlu iterasi
        # Ini mungkin tidak diperlukan jika struktur suffix_rules sudah {suffix_form: [details]}
        # Namun, jika struktur berbeda, logika pencarian mungkin perlu disesuaikan.
        # Contoh iterasi jika struktur lebih kompleks:
        # for key, rules_list in self.suffix_rules.items():
        #     for rule_detail in rules_list:
        #         if rule_detail.get("form") == suffix_form:
        #             return rule_detail.get("type")
            
        return None # Kembalikan None jika sufiks atau tipenya tidak ditemukan

    def get_prefix_type(self, prefix_form: str) -> Optional[str]:
        """
        Mendapatkan tipe dari sebuah bentuk prefiks.
        (Mirip dengan get_suffix_type)
        """
        if prefix_form in self.prefix_rules:
            rules_for_prefix = self.prefix_rules[prefix_form]
            if rules_for_prefix:
                rule_detail = rules_for_prefix[0]
                return rule_detail.get("type")
        return None

    # Metode lain yang mungkin berguna
    def is_suffix(self, form: str) -> bool:
        """Cek apakah sebuah form adalah sufiks yang diketahui."""
        return form in self.suffix_rules

    def is_prefix(self, form: str) -> bool:
        """Cek apakah sebuah form adalah prefiks yang diketahui."""
        return form in self.prefix_rules

# Contoh penggunaan (opsional, untuk pengujian cepat)
if __name__ == '__main__':
    # Pastikan file affix_rules.json ada di src/modern_kata_kupas/data/affix_rules.json
    # atau sesuaikan path di bawah ini.
    # Untuk menjalankan dari root direktori proyek: python -m src.modern_kata_kupas.rules
    
    # Membuat path yang benar jika dijalankan dari root proyek
    project_root = os.path.dirname(os.path.dirname(BASE_DIR)) # Naik dua level dari src/modern_kata_kupas
    test_rules_file = os.path.join(project_root, "src", "modern_kata_kupas", "data", "affix_rules.json")

    if not os.path.exists(test_rules_file):
        print(f"File aturan tidak ditemukan untuk pengujian: {test_rules_file}")
        # Jika dijalankan langsung dari direktori src/modern_kata_kupas/
        # maka AFFIX_RULES_PATH seharusnya sudah benar.
        # Coba gunakan AFFIX_RULES_PATH jika test_rules_file tidak ada
        if os.path.exists(AFFIX_RULES_PATH):
            test_rules_file = AFFIX_RULES_PATH
        else:
            print("Tidak dapat menemukan file aturan untuk pengujian.")
            exit()
            
    print(f"Menggunakan file aturan: {test_rules_file}")
    rules_manager = MorphologicalRules(rules_file_path=test_rules_file)

    # Test get_suffix_type
    print(f"Tipe sufiks '-lah': {rules_manager.get_suffix_type('-lah')}")
    print(f"Tipe sufiks '-an': {rules_manager.get_suffix_type('-an')}")
    print(f"Tipe sufiks '-i': {rules_manager.get_suffix_type('-i')}")
    print(f"Tipe sufiks '-kan': {rules_manager.get_suffix_type('-kan')}")
    print(f"Tipe sufiks '-nya': {rules_manager.get_suffix_type('-nya')}")
    print(f"Tipe sufiks tidak ada '-xyz': {rules_manager.get_suffix_type('-xyz')}")

    # Test get_prefix_type
    print(f"Tipe prefiks 'meng-': {rules_manager.get_prefix_type('meng-')}")
    print(f"Tipe prefiks 'di-': {rules_manager.get_prefix_type('di-')}")
    print(f"Tipe prefiks 'ber-': {rules_manager.get_prefix_type('ber-')}")
    print(f"Tipe prefiks tidak ada 'xyz-': {rules_manager.get_prefix_type('xyz-')}")

    # Test matching rules
    word_test_suffix = "makanan"
    print(f"Aturan sufiks yang cocok untuk '{word_test_suffix}': {rules_manager.get_matching_suffix_rules(word_test_suffix)}")
    
    word_test_suffix_complex = "memberikannya"
    print(f"Aturan sufiks yang cocok untuk '{word_test_suffix_complex}': {rules_manager.get_matching_suffix_rules(word_test_suffix_complex)}")

    word_test_prefix = "mengambil"
    print(f"Aturan prefiks yang cocok untuk '{word_test_prefix}': {rules_manager.get_matching_prefix_rules(word_test_prefix)}")
