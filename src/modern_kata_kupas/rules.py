import json
import os
import importlib.resources # Added import
import logging # Added import
from typing import List, Dict, Any, Tuple, Optional, Union # Pastikan Optional atau Union diimpor

# Konstanta untuk path file default menggunakan importlib.resources
DEFAULT_RULES_PACKAGE_PATH = "modern_kata_kupas.data"
DEFAULT_RULES_FILENAME = "affix_rules.json"

# Definisikan RuleError di sini jika belum ada global
class RuleError(Exception):
    """Custom exception for errors during rule loading or processing."""
    pass

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
    Manages morphological rules for Indonesian word segmentation and reconstruction.

    This class loads, parses, and provides access to affix rules (prefixes, suffixes,
    infixes) and their associated morphophonemic changes from a JSON file.
    It organizes rules for efficient lookup and application during the
    segmentation and reconstruction processes.

    Attributes:
        prefix_rules (Dict[str, List[Dict[str, Any]]]): A dictionary storing prefix rules,
            typically keyed by canonical prefix forms. Each value is a list of rule details.
        suffix_rules (Dict[str, List[Dict[str, Any]]]): A dictionary storing suffix rules,
            typically keyed by the suffix form (e.g., "-kan"). Each value is a list of rule details.
        infix_rules (Dict[str, List[Dict[str, Any]]]): A dictionary storing infix rules (if any).
        all_rules (Dict[str, Any]): The raw JSON structure loaded from the rules file.
    """
    def __init__(self, rules_file_path: str = None):
        """
        Initializes the MorphologicalRules engine by loading rules from a JSON file.

        If `rules_file_path` is not provided, it attempts to load default rules
        packaged with the library. If the specified file is empty or contains
        invalid JSON, rules will be empty (for default load) or an error raised
        (for explicit path).

        Args:
            rules_file_path (str, optional): Path to a custom JSON file containing
                morphological rules. Defaults to None, which triggers loading of
                default packaged rules.

        Raises:
            FileNotFoundError: If `rules_file_path` is specified but the file
                               does not exist.
            RuleError: If the JSON file specified by `rules_file_path` is invalid
                       or if there's an unexpected error during rule processing from
                       an explicitly provided file.
        """
        self.rules_file_path_arg = rules_file_path # Simpan argumen asli untuk referensi
        
        # Inisialisasi default ke aturan kosong
        self.all_rules: Dict[str, Any] = {"prefixes": [], "suffixes": []}
        self.prefix_rules: Dict[str, List[Dict[str, Any]]] = {}
        self.suffix_rules: Dict[str, List[Dict[str, Any]]] = {}
        self.infix_rules: Dict[str, List[Dict[str, Any]]] = {}

        self.is_default_load = not bool(rules_file_path) # True jika path tidak diberikan

        try:
            if self.is_default_load:
                # Muat dari paket menggunakan importlib.resources
                logging.info(f"MorphologicalRules: Loading default rules from package: {DEFAULT_RULES_PACKAGE_PATH}/{DEFAULT_RULES_FILENAME}")
                file_content = importlib.resources.read_text(
                    DEFAULT_RULES_PACKAGE_PATH,
                    DEFAULT_RULES_FILENAME,
                    encoding='utf-8'
                )
                self._parse_rules_from_content(file_content, f"package:{DEFAULT_RULES_PACKAGE_PATH}/{DEFAULT_RULES_FILENAME}")
            else:
                # Muat dari file path yang diberikan
                logging.info(f"MorphologicalRules: Loading rules from explicit path: {rules_file_path}")
                if not os.path.exists(rules_file_path):
                    raise FileNotFoundError(f"File aturan yang ditentukan secara eksplisit tidak ditemukan: {rules_file_path}")
                with open(rules_file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                self._parse_rules_from_content(file_content, rules_file_path)

        except FileNotFoundError as e:
            # Jika file default dari paket tidak ditemukan (seharusnya tidak terjadi jika setup benar)
            # atau file eksplisit tidak ditemukan.
            if self.is_default_load:
                 logging.warning(f"File aturan default dari paket tidak ditemukan. Menggunakan aturan kosong. Error: {e}")
            else: # File eksplisit tidak ditemukan, ini adalah error.
                raise
        except json.JSONDecodeError as e:
            source_description = f"paket {DEFAULT_RULES_PACKAGE_PATH}/{DEFAULT_RULES_FILENAME}" if self.is_default_load else rules_file_path
            # Jika file (default atau eksplisit) ada tapi JSON-nya salah.
            # Untuk file default yang rusak, kita bisa memilih untuk warning + aturan kosong.
            # Untuk file eksplisit yang rusak, kita harus raise error.
            if self.is_default_load:
                logging.warning(f"File aturan default dari {source_description} rusak atau tidak dapat diurai. Menggunakan aturan kosong. Detail: {e}")
            else:
                raise RuleError(f"Format JSON tidak valid dalam file: {rules_file_path}. Detail: {e}") from e
        except Exception as e: # Menangkap error lain
            source_description = f"paket {DEFAULT_RULES_PACKAGE_PATH}/{DEFAULT_RULES_FILENAME}" if self.is_default_load else rules_file_path
            if self.is_default_load:
                logging.warning(f"Error tak terduga saat memuat aturan default dari {source_description}. Menggunakan aturan kosong. Detail: {e}")
            else:
                raise RuleError(f"Error saat memuat atau memproses aturan dari {rules_file_path}: {str(e)}") from e


    def _parse_rules_from_content(self, file_content: str, source_description: str):
        """
        Mem-parse konten string aturan (JSON) dan menginisialisasi struktur aturan.
        Dipanggil setelah file content dibaca baik dari paket atau file path.
        """
        if not file_content.strip(): # Periksa apakah file kosong atau hanya berisi spasi putih
            logging.info(f"MorphologicalRules: Konten aturan dari '{source_description}' kosong. Menggunakan aturan kosong.")
            self.all_rules = {"prefixes": [], "suffixes": []} # Sudah diinisialisasi, tapi untuk kejelasan
            self.prefix_rules = {}
            self.suffix_rules = {}
            self.infix_rules = {}
            return

        loaded_json = json.loads(file_content) # Bisa memunculkan JSONDecodeError
        
        self.all_rules = loaded_json
        self.prefix_rules = {}
        self.suffix_rules = {}
        self.infix_rules = {}

        # Proses suffix rules
        # processed_suffix_rules = {} # This was a temporary variable, directly use self.suffix_rules
        raw_suffixes = self.all_rules.get("suffixes", [])
        if isinstance(raw_suffixes, list):
            for rule in raw_suffixes:
                    key = rule.get("form")
                    if key:
                        if key not in self.suffix_rules: # Menggunakan self.suffix_rules langsung
                            self.suffix_rules[key] = []
                        self.suffix_rules[key].append(rule)
        elif isinstance(raw_suffixes, dict): # Asumsi format lama jika berupa dict (Corrected Indentation)
            self.suffix_rules = raw_suffixes # Harus dipastikan formatnya sesuai

        # Proses prefix rules
        # processed_prefix_rules = {} # This was a temporary variable, directly use self.prefix_rules
        raw_prefixes = self.all_rules.get("prefixes", [])
        if isinstance(raw_prefixes, list):
            for rule in raw_prefixes:
                key = rule.get("canonical")
                if not key:
                    key = rule.get("form") or rule.get("surface")
                if key:
                    if key not in self.prefix_rules: # Menggunakan self.prefix_rules langsung
                        self.prefix_rules[key] = []
                    self.prefix_rules[key].append(rule)
        elif isinstance(raw_prefixes, dict): # Corrected Indentation
            self.prefix_rules = raw_prefixes # Harus dipastikan formatnya sesuai
            
        # Anda bisa menambahkan pemuatan untuk infiks jika ada
            # raw_infixes = self.all_rules.get("infixes", [])
            # ... (proses serupa untuk infiks) ...

    def get_matching_suffix_rules(self, word: str) -> List[Dict[str, Any]]:
        """
        Retrieves all suffix rules that match the end of the given word.

        The rules are returned sorted by the length of the suffix pattern in descending
        order to prioritize longer matches (e.g., "-kannya" before "-nya").
        Each returned rule dictionary includes an 'original_pattern' key for reference.

        Args:
            word (str): The word to check for matching suffixes.

        Returns:
            List[Dict[str, Any]]: A list of rule dictionaries for all matching suffixes.
                                  Each dictionary contains details of a suffix rule,
                                  plus an 'original_pattern' key indicating the matched suffix form.
                                  Returns an empty list if no suffixes match.
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
        Retrieves all prefix rules that match the beginning of the given word.

        The rules are returned sorted by the length of the prefix pattern in descending
        order to prioritize longer matches (e.g., "memper-" before "meN-").
        Each returned rule dictionary includes an 'original_pattern' key for reference.

        Args:
            word (str): The word to check for matching prefixes.

        Returns:
            List[Dict[str, Any]]: A list of rule dictionaries for all matching prefixes.
                                  Each dictionary contains details of a prefix rule,
                                  plus an 'original_pattern' key indicating the matched prefix form.
                                  Returns an empty list if no prefixes match.
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
        Checks if a given string is a valid canonical prefix form.

        A canonical prefix form is a key in the `self.prefix_rules` dictionary,
        representing a standardized form of a prefix (e.g., "meN", "di").

        Args:
            prefix (str): The canonical prefix string to check (e.g., "meN", "di", "ber").

        Returns:
            bool: True if the string is a valid canonical prefix form present in the
                  loaded rules, False otherwise.
        """
        # self.prefix_rules is now keyed by canonical forms (e.g., "meN", "di").
        # Each value is a list of rule_detail_dicts (usually one dict for canonical keys).
        return prefix in self.prefix_rules
        
    # --- PERBAIKAN UTAMA DI SINI ---
    def get_suffix_type(self, suffix_form: str) -> Optional[str]:
        """
        Gets the type of a given suffix form (e.g., "-lah", "-an").

        Suffix types can include "particle", "possessive", "suffix_derivational", etc.,
        as defined in the morphological rules file.

        Args:
            suffix_form (str): The suffix form whose type is to be determined (e.g., "-kan").

        Returns:
            Optional[str]: The type of the suffix (e.g., "suffix_derivational") if found,
                           otherwise None.
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
        Gets the type of a given prefix form (e.g., "meN-", "di-").

        Prefix types are defined in the morphological rules file (e.g., "prefix_derivational").
        This method checks against the canonical prefix forms.

        Args:
            prefix_form (str): The canonical prefix form whose type is to be determined
                               (e.g., "meN", "di").

        Returns:
            Optional[str]: The type of the prefix if found, otherwise None.
        """
        if prefix_form in self.prefix_rules:
            rules_for_prefix = self.prefix_rules[prefix_form]
            if rules_for_prefix:
                rule_detail = rules_for_prefix[0] # Assumes one primary rule dict per canonical form
                return rule_detail.get("type")
        return None

    # Metode lain yang mungkin berguna
    def is_suffix(self, form: str) -> bool:
        """
        Checks if a given string is a valid suffix form.

        A suffix form is a key in the `self.suffix_rules` dictionary (e.g., "-an", "-lah").

        Args:
            form (str): The suffix form string to check (e.g., "-an", "-lah").

        Returns:
            bool: True if the string is a valid suffix form present in the loaded rules,
                  False otherwise.
        """
        # self.suffix_rules adalah Dict[str_form, List[Dict_rule_details]]
        # Contoh: {"-an": [{...}], "-lah": [{...}]}
        return form in self.suffix_rules

    def get_all_prefix_forms(self) -> List[str]:
        """
        Retrieves a list of all unique surface forms of prefixes from the loaded rules.

        This includes simple forms (e.g., "di-") and all allomorphs
        (e.g., "me", "mem", "men", "meny", "meng", "menge" for "meN-").

        Returns:
            List[str]: A list of all unique prefix surface forms.
        """
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
        """
        Gets the canonical form of a given prefix surface form.

        For example, given "mem", it should return "meN" if "meN-" is the
        canonical prefix and "mem" is one of its allomorphs.

        Args:
            surface_form (str): The surface form of the prefix (e.g., "mem", "di-").

        Returns:
            Optional[str]: The canonical form of the prefix (e.g., "meN") if found,
                           otherwise None.
        """
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
        Reverses morphophonemic changes to restore an initial root character that might have been elided.

        This is used during prefix stripping. For example, if "mem" (surface form of "meN-")
        was stripped leaving "ukul", this method would identify that "p" was elided
        and return "pukul".

        Args:
            surface_stripped_prefix (str): The surface form of the prefix that was stripped
                                           (e.g., "mem").
            canonical_prefix (str): The canonical form of the stripped prefix (e.g., "meN").
            stem_after_strip (str): The remaining stem after the prefix was stripped
                                    (e.g., "ukul").

        Returns:
            str: The stem with the initial character restored if an elision rule applies.
                 Returns the `stem_after_strip` unchanged if no applicable elision rule
                 is found for the given prefix combination.
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
        """
        Returns the dictionary of all loaded prefix rules.

        The dictionary is typically keyed by canonical prefix forms.

        Returns:
            Dict[str, List[Dict[str, Any]]]: The raw dictionary of prefix rules.
        """
        return self.prefix_rules

    def get_suffix_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Returns the dictionary of all loaded suffix rules.

        The dictionary is typically keyed by suffix forms (e.g., "-kan").

        Returns:
            Dict[str, List[Dict[str, Any]]]: The raw dictionary of suffix rules.
        """
        return self.suffix_rules

# Contoh penggunaan (opsional, untuk pengujian cepat)
if __name__ == '__main__':
    # Pastikan file affix_rules.json ada di modern_kata_kupas/data/affix_rules.json
    # Untuk menjalankan dari root direktori proyek: python -m src.modern_kata_kupas.rules
    
    # Default loading (dari paket)
    print("Menguji pemuatan aturan default dari paket...")
    try:
        rules_manager_default = MorphologicalRules()
        print(f"Berhasil memuat {len(rules_manager_default.get_all_prefix_forms())} bentuk prefiks (default).")
        print(f"Tipe sufiks '-lah' (default): {rules_manager_default.get_suffix_type('-lah')}")
    except Exception as e:
        print(f"Error saat memuat aturan default: {e}")

    # Membuat file aturan dummy untuk pengujian pemuatan dari path eksplisit
    dummy_rules_content = {
        "prefixes": [
            {"form": "tes-", "canonical": "tes-", "type": "test_prefix_type", "allomorphs": []}
        ],
        "suffixes": [
            {"form": "-tes", "type": "test_suffix_type", "conditions": []}
        ]
    }
    dummy_rules_path = "dummy_test_rules.json"
    with open(dummy_rules_path, 'w', encoding='utf-8') as f:
        json.dump(dummy_rules_content, f)

    print(f"\nMenguji pemuatan aturan dari path eksplisit: {dummy_rules_path}")
    try:
        rules_manager_explicit = MorphologicalRules(rules_file_path=dummy_rules_path)
        print(f"Berhasil memuat {len(rules_manager_explicit.get_all_prefix_forms())} bentuk prefiks (eksplisit).")
        print(f"Tipe sufiks '-tes' (eksplisit): {rules_manager_explicit.get_suffix_type('-tes')}")
    except Exception as e:
        print(f"Error saat memuat aturan dari path eksplisit: {e}")
    finally:
        if os.path.exists(dummy_rules_path):
            os.remove(dummy_rules_path) # Bersihkan file dummy

    # Contoh penggunaan lain tetap di sini jika diperlukan,
    # misalnya untuk menguji get_suffix_type dengan aturan default jika berhasil dimuat
    if 'rules_manager_default' in locals() and rules_manager_default:
        rules_manager = rules_manager_default # Gunakan aturan default untuk sisa tes
    elif 'rules_manager_explicit' in locals() and rules_manager_explicit:
        rules_manager = rules_manager_explicit # Fallback ke aturan eksplisit jika default gagal
    else:
        print("\nTidak ada manajer aturan yang berhasil diinisialisasi untuk tes lebih lanjut.")
        exit()
        
    print("\nMelanjutkan dengan tes get_suffix_type (menggunakan manajer yang berhasil dimuat):")
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