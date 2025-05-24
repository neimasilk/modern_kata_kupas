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
    def __init__(self, rules_file_path: str = None):
        """
        Inisialisasi objek MorphologicalRules.

        Args:
            rules_file_path (str): Path ke file JSON yang berisi aturan morfologis.
        """
        self.rules_file_path = rules_file_path or AFFIX_RULES_PATH
        self.prefix_rules: Dict[str, List[Dict[str, Any]]] = {}
        self.suffix_rules: Dict[str, List[Dict[str, Any]]] = {}
        self.infix_rules: Dict[str, List[Dict[str, Any]]] = {} # Jika ada aturan infiks
        self.all_rules: Dict[str, Any] = {} # Untuk menyimpan semua aturan mentah jika diperlukan
        
        # Jika rules_file_path diberikan secara eksplisit, file harus ada
        if rules_file_path and not os.path.exists(rules_file_path):
            raise FileNotFoundError(f"File aturan tidak ditemukan: {rules_file_path}")
            
        try:
            self._load_rules()
        except FileNotFoundError:
            # Hanya gunakan dictionary kosong jika menggunakan path default
            if not rules_file_path:
                self.all_rules = {"prefixes": [], "suffixes": []}
                self.prefix_rules = {}
                self.suffix_rules = {}
            else:
                raise
        except Exception as e:
            raise e

    def _load_rules(self) -> None:
        """
        Memuat aturan morfologi dari file JSON.
        Mengelompokkan aturan berdasarkan tipe (prefix, suffix, infix).
        """
        try:
            with open(self.rules_file_path, 'r', encoding='utf-8') as f:
                self.all_rules = json.load(f)

            # Inisialisasi dictionary untuk menyimpan aturan yang sudah diproses
            processed_suffix_rules = {}
            processed_prefix_rules = {}

            # Proses suffix rules
            raw_suffixes = self.all_rules.get("suffixes", [])
            if isinstance(raw_suffixes, list):
                for rule in raw_suffixes:
                    key = rule.get("form")
                    if key:
                        if key not in processed_suffix_rules:
                            processed_suffix_rules[key] = []
                        processed_suffix_rules[key].append(rule)
            elif isinstance(raw_suffixes, dict):
                processed_suffix_rules = raw_suffixes

            # Proses prefix rules
            raw_prefixes = self.all_rules.get("prefixes", [])
            if isinstance(raw_prefixes, list):
                for rule in raw_prefixes:
                    key = rule.get("form") or rule.get("canonical")
                    if key:
                        if key not in processed_prefix_rules:
                            processed_prefix_rules[key] = []
                        processed_prefix_rules[key].append(rule)
            elif isinstance(raw_prefixes, dict):
                processed_prefix_rules = raw_prefixes

            # Assign ke instance variables
            self.suffix_rules = processed_suffix_rules
            self.prefix_rules = processed_prefix_rules
            
            # Anda bisa menambahkan pemuatan untuk infiks jika ada
            # raw_infixes = self.all_rules.get("infixes", {})
            # ...

        except FileNotFoundError:
            raise FileNotFoundError(f"File aturan tidak ditemukan: {self.rules_file_path}")
        except json.JSONDecodeError:
            raise RuleError(f"Format JSON tidak valid dalam file: {self.rules_file_path}")
        except Exception as e:
            raise RuleError(f"Error saat memuat aturan: {str(e)}")

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

    def is_prefix(self, prefix: str) -> bool:
        """
        Memeriksa apakah sebuah string adalah prefiks yang valid.
        
        Args:
            prefix (str): String yang akan diperiksa.
            
        Returns:
            bool: True jika string adalah prefiks yang valid, False jika tidak.
        """
        return prefix in self.prefix_rules
        
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