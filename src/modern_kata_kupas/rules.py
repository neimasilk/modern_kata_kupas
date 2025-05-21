# src/modern_kata_kupas/rules.py
"""
Modul untuk mengelola aturan morfologi dan fonologi.

Aturan ini akan digunakan oleh Separator dan Reconstructor.
Contoh aturan:
- Penghilangan prefiks: "meng-" + "gambar" -> "gambar" (aturan: "meng-" -> "g")
- Perubahan fonologis: "meN-" + "sapu" -> "menyapu" (aturan: "N" bertemu "s" -> "ny")
- Aturan untuk sufiks, infiks, konfiks.
"""

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
        Memuat aturan dari file (misalnya JSON atau YAML).
        Struktur aturan perlu didefinisikan dengan jelas.
        Contoh:
        {
            "prefixes": [
                {"form": "meng-", "removes": "k", "adds_if_next_vowel": "ng"},
                {"form": "me-", "allomorphs": ["mem-", "men-", "meny-", "meng-", "menge-"]}
            ],
            "suffixes": [
                {"form": "-kan"},
                {"form": "-i"}
            ],
            "fonologis": [
                {"pattern": "N-p", "replacement": "m-p"}, # meN- + pukul -> memukul
                {"pattern": "N-s", "replacement": "ny-s"} # meN- + sapu -> menyapu
            ]
        }
        """
        # Placeholder untuk logika pemuatan aturan
        # Ini akan melibatkan pembacaan file dan parsing kontennya
        try:
            # Contoh jika menggunakan JSON
            # import json
            # with open(file_path, 'r') as f:
            #     self.rules = json.load(f)
            print(f"Placeholder: Loading rules from {file_path}")
            # Untuk sekarang, set aturan dummy
            self.rules = {
                "info": f"Rules loaded from {file_path} (placeholder)",
                "prefixes": [],
                "suffixes": []
            }
        except Exception as e:
            print(f"Error loading rules from {file_path}: {e}")
            # Mungkin melempar custom exception di sini
            self.rules = {}

    def get_prefix_rules(self):
        """
        Mengembalikan aturan yang berkaitan dengan prefiks.
        """
        return self.rules.get("prefixes", [])

    def get_suffix_rules(self):
        """
        Mengembalikan aturan yang berkaitan dengan sufiks.
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