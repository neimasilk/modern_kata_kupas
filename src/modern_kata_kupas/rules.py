# src/modern_kata_kupas/rules.py
"""
Modul untuk mengelola aturan morfologi dan fonologi.

Aturan ini akan digunakan oleh Separator dan Reconstructor.
Contoh aturan:
- Penghilangan prefiks: "meng-" + "gambar" -> "gambar" (aturan: "meng-" -> "g")
- Perubahan fonologis: "meN-" + "sapu" -> "menyapu" (aturan: "N" bertemu "s" -> "ny")
- Aturan untuk sufiks, infiks, konfiks.
"""

from abc import ABC, abstractmethod

class Rule(ABC):
    """
    Base class untuk semua aturan morfologis
    """
    
    @abstractmethod
    def apply(self, word: str) -> str:
        """
        Menerapkan aturan pada kata input
        
        Args:
            word (str): Kata input
            
        Returns:
            str: Hasil setelah aturan diterapkan
        """
        pass


class RemoveSuffixRule(Rule):
    """
    Contoh implementasi aturan untuk menghapus suffix
    """
    
    def __init__(self, suffixes: list[str]):
        self.suffixes = suffixes
    
    def apply(self, word: str) -> str:
        """
        Mencoba menghapus suffix dari kata
        
        Args:
            word (str): Kata input
            
        Returns:
            str: Kata tanpa suffix jika ditemukan, kata asli jika tidak
        """
        for suffix in self.suffixes:
            if word.endswith(suffix):
                return word[:word.rfind(suffix)]
        return word

# Placeholder untuk kelas atau fungsi terkait aturan
# Ini bisa berupa kelas RuleLoader, RuleApplier, atau struktur data untuk aturan

DEFAULT_RULES_PATH = "path/to/default_rules.json" # atau .yaml

class MorphologicalRules:
    """
    Kelas untuk memuat dan mengelola aturan morfologi.
    """
    def __init__(self, rules_path=None):
        """
        Inisialisasi MorphologicalRules.

        Args:
            rules_path (str, optional): Path ke file aturan. 
                                        Jika None, aturan default mungkin akan dimuat 
                                        atau sistem akan menunggu aturan dimuat secara eksplisit.
        """
        self.rules = {}
        if rules_path:
            self.load_rules(rules_path)
        else:
            # Mungkin memuat aturan default bawaan atau membiarkannya kosong
            print("Placeholder: MorphologicalRules initialized without specific rules file.")

    def load_rules(self, file_path: str):
        """
        Memuat aturan dari file JSON.
        Struktur aturan harus mengikuti format:
        {
            "prefixes": [
                {"form": "meng-", "removes": "k", "adds_if_next_vowel": "ng"},
                {"form": "me-", "allomorphs": ["mem-", "men-", "meny-", "meng-", "menge-"]}
            ],
            "suffixes": [
                {"form": "-kan"},
                {"form": "-i"}
            ],
            "phonological": [
                {"pattern": "N-p", "replacement": "m-p"}, # meN- + pukul -> memukul
                {"pattern": "N-s", "replacement": "ny-s"} # meN- + sapu -> menyapu
            ]
        }
        """
        import json
        from typing import Dict, List
        
        REQUIRED_SECTIONS = ['prefixes', 'suffixes']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_rules = json.load(f)
                
                # Validasi struktur dasar
                if not isinstance(loaded_rules, dict):
                    raise ValueError("File aturan harus berupa dictionary")
                    
                for section in REQUIRED_SECTIONS:
                    if section not in loaded_rules:
                        raise ValueError(f"Bagian {section} harus ada dalam file aturan")
                    if not isinstance(loaded_rules[section], list):
                        raise ValueError(f"Bagian {section} harus berupa list")
                
                self.rules = loaded_rules
                print(f"Berhasil memuat aturan dari {file_path}")
                
        except json.JSONDecodeError as e:
            raise ValueError(f"File aturan bukan JSON yang valid: {e}")
        except Exception as e:
            raise ValueError(f"Gagal memuat aturan dari {file_path}: {e}")

    def get_prefix_rules(self):
        """
        Mengembalikan daftar aturan prefiks.
        """
        return self.rules.get("prefixes", [])

    def get_suffix_rules(self):
        """
        Mengembalikan daftar aturan sufiks.
        """
        return self.rules.get("suffixes", [])

    # Metode lain untuk mendapatkan tipe aturan spesifik (infiks, fonologis, dll.)

# Contoh penggunaan (bisa dihapus atau dikomentari nanti)
if __name__ == '__main__':
    # Asumsikan ada file dummy_rules.json
    # with open("dummy_rules.json", "w") as f:
    #     import json
    #     json.dump({"info": "dummy rules"}, f)

    # rule_manager = MorphologicalRules("dummy_rules.json")
    rule_manager_default = MorphologicalRules()
    print(f"Aturan prefiks (default): {rule_manager_default.get_prefix_rules()}")
    # os.remove("dummy_rules.json") # cleanup