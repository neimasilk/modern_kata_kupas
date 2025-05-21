# src/modern_kata_kupas/separator.py
"""
Modul untuk memisahkan kata berimbuhan menjadi kata dasar dan afiksnya.
"""

class Separator:
    """
    Kelas utama untuk proses pemisahan kata.
    """
    def __init__(self, dictionary=None, rules=None):
        """
        Inisialisasi Separator.

        Args:
            dictionary: Objek kamus kata dasar.
            rules: Objek aturan morfologi.
        """
        self.dictionary = dictionary
        self.rules = rules
        # Placeholder untuk logika inisialisasi lebih lanjut

    def separate(self, word: str) -> tuple:
        """
        Memisahkan kata berimbuhan.

        Args:
            word (str): Kata yang akan dipisahkan.

        Returns:
            tuple: Berisi (kata_dasar, list_afiks_ditemukan) atau (kata_asli, []) jika tidak ada perubahan.
                   Contoh: ("makan", ["me-", "-an"]) untuk "makanan"
                           ("baca", ["mem-"]) untuk "membaca"
        """
        # Placeholder untuk logika pemisahan
        # Ini akan menjadi implementasi inti dari algoritma pemisahan
        # Untuk saat ini, kembalikan kata asli
        print(f"Placeholder: Separating word '{word}'")
        return word, []

# Contoh penggunaan (bisa dihapus atau dikomentari nanti)
if __name__ == '__main__':
    sep = Separator()
    result = sep.separate("mencoba")
    print(f"Hasil separasi 'mencoba': {result}")