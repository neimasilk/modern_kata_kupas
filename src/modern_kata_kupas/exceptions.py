# src/modern_kata_kupas/exceptions.py
"""
Modul untuk custom exceptions yang digunakan dalam library ModernKataKupas.
"""

class ModernKataKupasError(Exception):
    """Kelas dasar untuk semua exception di ModernKataKupas."""
    pass

class DictionaryError(ModernKataKupasError):
    """Exception terkait dengan operasi kamus (misalnya, file tidak ditemukan)."""
    pass

class RuleError(ModernKataKupasError):
    """Exception terkait dengan pemuatan atau aplikasi aturan morfologi."""
    pass

class WordNotInDictionaryError(DictionaryError):
    """Exception ketika sebuah kata tidak ditemukan di kamus dan diperlukan."""
    def __init__(self, word, message=None):
        self.word = word
        if message is None:
            message = f"Kata '{word}' tidak ditemukan dalam kamus."
        super().__init__(message)

class InvalidAffixError(ModernKataKupasError):
    """Exception ketika afiks yang diberikan tidak valid atau tidak dikenal."""
    pass

class ReconstructionError(ModernKataKupasError):
    """Exception yang terjadi selama proses rekonstruksi kata."""
    pass

class SeparationError(ModernKataKupasError):
    """Exception yang terjadi selama proses pemisahan kata."""
    pass

# Contoh bagaimana exception ini bisa di-raise (untuk dokumentasi/tes):
# if __name__ == '__main__':
#     try:
#         raise WordNotInDictionaryError("katatidakada")
#     except WordNotInDictionaryError as e:
#         print(f"Caught an exception: {e}")
# 
#     try:
#         raise RuleError("Format aturan salah pada baris 5.")
#     except RuleError as e:
#         print(f"Caught an exception: {e}")