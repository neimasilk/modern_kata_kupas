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
        # Implementasi awal untuk memeriksa kata dasar
        if self.dictionary and self.dictionary.contains(word):
            return word, []
            
        # Logika untuk memeriksa prefiks
        prefixes = ["me-", "di-", "ter-", "ke-", "pe-", "se-"]
        for prefix in prefixes:
            if word.startswith(prefix[0:-1]):  # Hapus tanda '-' dari prefiks
                possible_root = word[len(prefix)-1:]
                if self.dictionary and self.dictionary.contains(possible_root):
                    return possible_root, [prefix]
        
        # Logika untuk memeriksa sufiks
        suffixes = ["-kan", "-i", "-an", "-nya"]
        for suffix in suffixes:
            if word.endswith(suffix[1:]):  # Hapus tanda '-' dari sufiks
                possible_root = word[:-len(suffix)+1]
                if self.dictionary and self.dictionary.contains(possible_root):
                    return possible_root, [suffix]
        
        # Logika untuk memeriksa konfiks (prefiks + sufiks)
        for prefix in prefixes:
            for suffix in suffixes:
                if word.startswith(prefix[0:-1]) and word.endswith(suffix[1:]):
                    possible_root = word[len(prefix)-1:-len(suffix)+1]
                    if self.dictionary and self.dictionary.contains(possible_root):
                        return possible_root, [prefix, suffix]
                    
        # Jika tidak ditemukan afiks, kembalikan kata asli
        return word, []

# Contoh penggunaan (bisa dihapus atau dikomentari nanti)
if __name__ == '__main__':
    sep = Separator()
    result = sep.separate("mencoba")
    print(f"Hasil separasi 'mencoba': {result}")