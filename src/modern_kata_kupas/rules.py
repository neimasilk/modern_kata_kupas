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
                                   Jika None, akan menggunakan path default.
                                   Jika file kosong atau JSON tidak valid, akan diinisialisasi dengan aturan kosong
                                   (kecuali jika file eksplisit tidak ditemukan, maka FileNotFoundError).
        """
        self.rules_file_path_arg = rules_file_path # Simpan argumen asli untuk referensi
        resolved_path = rules_file_path or AFFIX_RULES_PATH

        # Inisialisasi default ke aturan kosong
        self.all_rules: Dict[str, Any] = {"prefixes": [], "suffixes": []}
        self.prefix_rules: Dict[str, List[Dict[str, Any]]] = {}
        self.suffix_rules: Dict[str, List[Dict[str, Any]]] = {}
        self.infix_rules: Dict[str, List[Dict[str, Any]]] = {} # Jika ada aturan infiks

        # Path yang akan digunakan oleh _load_rules
        self.rules_file_path = resolved_path

        if rules_file_path:  # Path file aturan diberikan secara eksplisit
            if not os.path.exists(rules_file_path):
                raise FileNotFoundError(f"File aturan yang ditentukan secara eksplisit tidak ditemukan: {rules_file_path}")
            # File eksplisit ada, coba muat
            try:
                self._load_rules()
            except RuleError as e:
                # Jika file eksplisit ada tetapi kosong atau formatnya salah,
                # _load_rules seharusnya sudah menangani kasus file kosong dengan benar.
                # Jika RuleError muncul di sini, berarti file tidak kosong tapi formatnya salah.
                # Untuk konsistensi dengan bagaimana _load_rules menangani file kosong (menjadi aturan kosong),
                # kita bisa memilih untuk membiarkan aturan tetap kosong atau memunculkan error.
                # Saat ini, jika _load_rules memunculkan RuleError (misalnya, JSON tidak valid), kita biarkan error itu muncul.
                # Test mengharapkan aturan kosong jika file *kosong* secara eksplisit diberikan.
                # _load_rules yang dimodifikasi akan memastikan self.all_rules kosong jika file-nya kosong.
                # Jika file tidak kosong tapi JSON-nya salah, RuleError akan dimunculkan oleh _load_rules.
                raise # Biarkan RuleError (mis. dari JSONDecodeError yang dibungkus) muncul
            # FileNotFoundError dari _load_rules (misalnya karena race condition setelah os.path.exists) akan muncul juga.

        else:  # Tidak ada path file aturan eksplisit, gunakan default
            if os.path.exists(resolved_path): # File default ada
                try:
                    self._load_rules()
                except RuleError as e:
                    # File default ada tapi formatnya salah (dan tidak kosong).
                    # Bisa pilih untuk memunculkan error atau lanjut dengan aturan kosong + warning.
                    # Untuk sekarang, kita buat lebih permisif untuk file default yang rusak: log warning, gunakan aturan kosong.
                    print(f"PERINGATAN: File aturan default {resolved_path} ada tetapi rusak atau tidak dapat diurai. Menggunakan aturan kosong. Detail: {e}")
                    # Aturan sudah diinisialisasi kosong, jadi tidak perlu tindakan lebih lanjut.
            # else: File default (AFFIX_RULES_PATH) tidak ada.
            #       Lanjutkan dengan aturan kosong yang sudah diinisialisasi. Tidak ada error/warning.

    def _load_rules(self) -> None:
        """
        Memuat aturan morfologi dari file JSON.
        Mengelompokkan aturan berdasarkan tipe (prefix, suffix, infix).
        Jika file kosong, akan menginisialisasi aturan sebagai kosong.
        """
        try:
            with open(self.rules_file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
                if not file_content.strip(): # Periksa apakah file kosong atau hanya berisi spasi putih
                    # Jika file kosong, pastikan semua struktur aturan direset ke kondisi kosong
                    self.all_rules = {"prefixes": [], "suffixes": []}
                    self.prefix_rules = {}
                    self.suffix_rules = {}
                    self.infix_rules = {} # Pastikan ini juga direset jika digunakan
                    return # Berhasil "memuat" aturan kosong dari file kosong

                # File tidak kosong, coba parse JSON
                loaded_json = json.loads(file_content)
            
            # Reset/Inisialisasi ulang dictionary aturan sebelum memuat dari JSON yang berhasil diparsing
            # Ini penting jika _load_rules dipanggil lagi atau untuk kejelasan state.
            self.all_rules = loaded_json
            self.prefix_rules = {}
            self.suffix_rules = {}
            self.infix_rules = {} # Pastikan ini juga direset jika digunakan

            # Proses suffix rules
            processed_suffix_rules = {}
            raw_suffixes = self.all_rules.get("suffixes", [])
            if isinstance(raw_suffixes, list):
                for rule in raw_suffixes:
                    key = rule.get("form")
                    if key:
                        if key not in processed_suffix_rules:
                            processed_suffix_rules[key] = []
                        processed_suffix_rules[key].append(rule)
            elif isinstance(raw_suffixes, dict): # Asumsi format lama jika berupa dict
                processed_suffix_rules = raw_suffixes
            self.suffix_rules = processed_suffix_rules

            # Proses prefix rules
            processed_prefix_rules = {}
            raw_prefixes = self.all_rules.get("prefixes", [])
            if isinstance(raw_prefixes, list):
                for rule in raw_prefixes:
                    # Use canonical form as the key for self.prefix_rules.
                    # This simplifies lookup later.
                    key = rule.get("canonical") 
                    if not key: # Fallback if "canonical" is somehow missing, though it shouldn't be for prefixes.
                        key = rule.get("form") or rule.get("surface")

                    if key:
                        # Each key should map to a list containing ONE rule dictionary for that canonical/form.
                        # If affix_rules.json has multiple entries for the exact same canonical form (undesirable),
                        # this would overwrite. Assuming unique canonical forms for top-level prefix rules.
                        # The value should be the rule dict itself, not a list containing it, if keys are canonical.
                        # Or, if we expect multiple distinct rule objects for the *same* canonical form (e.g. meN defined twice),
                        # then a list is needed. Assuming one definition per canonical prefix.
                        # For consistency with how Reconstructor expects to find the rule (one dict per canonical form):
                        # self.prefix_rules[key] = rule # Store the rule dict directly.
                        
                        # Re-evaluation: The Reconstructor looks for a list of rule dicts.
                        # _apply_forward_morphophonemics now iterates .items() and then uses rule_list_for_form[0]
                        # The original _load_rules created a list: processed_prefix_rules[key].append(rule)
                        # Let's stick to storing a list of rules, even if it's usually a list with one item
                        # when keyed by canonical form.
                        if key not in processed_prefix_rules:
                            processed_prefix_rules[key] = []
                        processed_prefix_rules[key].append(rule)
            elif isinstance(raw_prefixes, dict): # Asumsi format lama jika berupa dict
                # This path for old format might need adjustment if keys are not canonical.
                # For now, assume it is also keyed by canonical form if it's a dict.
                processed_prefix_rules = raw_prefixes
            self.prefix_rules = processed_prefix_rules
            
            # Anda bisa menambahkan pemuatan untuk infiks jika ada
            # raw_infixes = self.all_rules.get("infixes", [])
            # ... (proses serupa untuk infiks) ...

        except FileNotFoundError:
            # Biarkan __init__ yang memutuskan bagaimana menangani ini berdasarkan apakah path default atau eksplisit
            raise
        except json.JSONDecodeError as e:
            # File tidak kosong, tetapi bukan JSON yang valid.
            # Definisikan RuleError jika belum ada, atau gunakan Exception bawaan.
            # class RuleError(Exception): pass (perlu didefinisikan di level modul)
            raise RuleError(f"Format JSON tidak valid dalam file: {self.rules_file_path}. Detail: {e}")
        except Exception as e: # Menangkap error lain yang mungkin terjadi saat pemrosesan aturan
            # Lebih baik lebih spesifik jika memungkinkan, tapi ini sebagai fallback.
            raise RuleError(f"Error saat memuat atau memproses aturan dari {self.rules_file_path}: {str(e)}")

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
        Memeriksa apakah sebuah string adalah prefiks yang valid berdasarkan BENTUK KANONIK.
        Contoh: is_prefix("meN") akan True jika "meN" adalah bentuk kanonik dari salah satu aturan prefiks,
        dan "meN" akan menjadi kunci di self.prefix_rules.
        
        Args:
            prefix (str): String bentuk kanonik prefiks yang akan diperiksa (misalnya, "meN", "di", "ber").
            
        Returns:
            bool: True jika string adalah bentuk kanonik prefiks yang valid dan ada sebagai kunci, False jika tidak.
        """
        # self.prefix_rules is now keyed by canonical forms (e.g., "meN", "di").
        # Each value is a list of rule_detail_dicts (usually one dict for canonical keys).
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
        """
        Memeriksa apakah sebuah string adalah sufiks yang valid berdasarkan BENTUK FORM.
        Contoh: is_suffix("-an") akan True jika "-an" adalah kunci di self.suffix_rules.

        Args:
            form (str): Bentuk sufiks yang akan diperiksa (misalnya, "-an", "-lah").

        Returns:
            bool: True jika string adalah bentuk sufiks yang valid, False jika tidak.
        """
        # self.suffix_rules adalah Dict[str_form, List[Dict_rule_details]]
        # Contoh: {"-an": [{...}], "-lah": [{...}]}
        return form in self.suffix_rules

    def get_all_prefix_forms(self) -> List[str]:
        """Mengembalikan daftar semua bentuk permukaan (surface forms) dari prefiks."""
        all_forms = set()
        for canon_rules_list in self.prefix_rules.values():
            for rule_details in canon_rules_list:
                # Untuk aturan prefiks sederhana yang mungkin hanya punya "form"
                if "form" in rule_details and isinstance(rule_details["form"], str):
                    all_forms.add(rule_details["form"])
                # Untuk aturan prefiks kompleks dengan "allomorphs"
                if "allomorphs" in rule_details and isinstance(rule_details["allomorphs"], list):
                    for allomorph_rule in rule_details["allomorphs"]:
                        if "surface" in allomorph_rule and isinstance(allomorph_rule["surface"], str):
                            all_forms.add(allomorph_rule["surface"])
        return list(all_forms)

    def get_canonical_prefix_form(self, surface_form: str) -> Optional[str]:
        """Mendapatkan bentuk kanonik dari sebuah surface_form prefiks."""
        for canonical, rules_list in self.prefix_rules.items():
            for rule_details in rules_list:
                if rule_details.get("form") == surface_form:
                    return canonical
                if "allomorphs" in rule_details:
                    for allomorph in rule_details["allomorphs"]:
                        if allomorph.get("surface") == surface_form:
                            return canonical
        return None

    def reverse_morphophonemics(self, surface_stripped_prefix: str, canonical_prefix: str, stem_after_strip: str) -> str:
        """
        Mencoba membalikkan perubahan morfofonemik untuk mengembalikan karakter root awal yang mungkin telah luluh (elided).
        Contoh: surface_stripped_prefix="mem", canonical_prefix="meN", stem_after_strip="ukul" -> "pukul"
        """
        if not canonical_prefix or not surface_stripped_prefix:
            return stem_after_strip # Tidak bisa melakukan apa-apa tanpa info prefiks

        rules_for_canonical = self.prefix_rules.get(canonical_prefix)
        if not rules_for_canonical:
            return stem_after_strip

        # Asumsi ada satu detail aturan utama per bentuk kanonik dalam list
        actual_rule_details = rules_for_canonical[0]
        allomorphs = actual_rule_details.get("allomorphs")

        if not allomorphs:
            return stem_after_strip # Tidak ada alomorf, tidak ada peluluhan yang perlu dibalik

        for allomorph_rule in allomorphs:
            if allomorph_rule.get("surface") == surface_stripped_prefix:
                # Kita menemukan aturan alomorf yang cocok dengan prefiks permukaan yang dilepas
                char_to_restore = allomorph_rule.get("reconstruct_root_initial")
                was_elision = allomorph_rule.get("elision", False)

                if char_to_restore and was_elision:
                    # Jika aturan ini melibatkan peluluhan dan ada karakter untuk direstorasi,
                    # maka tambahkan karakter tersebut ke awal stem_after_strip.
                    # Tidak perlu memeriksa apakah stem_after_strip sudah dimulai dengan char_to_restore,
                    # karena diasumsikan stem_after_strip adalah hasil *setelah* peluluhan.
                    return char_to_restore + stem_after_strip
                else:
                    # Alomorf cocok, tetapi tidak ada peluluhan yang perlu dibalik menurut aturan ini.
                    return stem_after_strip
        
        # Jika surface_stripped_prefix tidak cocok dengan alomorf yang diketahui yang memiliki aturan peluluhan,
        # kembalikan stem apa adanya.
        return stem_after_strip

    def get_prefix_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Mendapatkan semua aturan prefiks."""
        return self.prefix_rules

    def get_suffix_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Mendapatkan semua aturan sufiks."""
        return self.suffix_rules

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