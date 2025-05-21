# src/modern_kata_kupas/reconstructor.py
"""
Modul untuk merekonstruksi kata dari kata dasar dan afiksnya.
"""

class Reconstructor:
    """
    Kelas utama untuk proses rekonstruksi kata.
    """
    def __init__(self, rules=None):
        """
        Inisialisasi Reconstructor.

        Args:
            rules: Objek aturan morfologi.
        """
        self.rules = rules
        # Placeholder untuk logika inisialisasi lebih lanjut

    def reconstruct(self, root_word: str, affixes: list) -> str:
        """
        Merekonstruksi kata dari kata dasar dan daftar afiks.

        Args:
            root_word (str): Kata dasar.
            affixes (list): Daftar string afiks yang akan diterapkan.
                            Contoh: ["me-", "-kan"]

        Returns:
            str: Kata yang telah direkonstruksi.
                 Contoh: "memakan" dari ("makan", ["me-"])
                         "mempertanggungjawabkan" dari ("tanggung jawab", ["memper-", "-kan"])
        """
        # Placeholder untuk logika rekonstruksi
        # Ini akan melibatkan penerapan aturan morfologi secara terbalik atau sesuai urutan
        # Untuk saat ini, gabungkan saja secara naif (ini tidak benar secara morfologis)
        reconstructed_word = root_word
        if affixes:
            # Asumsi sederhana: prefix lalu suffix
            # Logika sebenarnya akan lebih kompleks berdasarkan tipe afiks
            for affix in affixes:
                if reconstructed_word.startswith(affix): # Ini salah, hanya contoh placeholder
                    pass # Seharusnya ada logika prefix
                elif reconstructed_word.endswith(affix): # Ini salah, hanya contoh placeholder
                    pass # Seharusnya ada logika suffix
                else:
                    # Ini adalah penyederhanaan kasar, logika sebenarnya akan lebih kompleks
                    # Misalnya, menangani infiks, konfiks, dan perubahan fonologis
                    if len(affixes) == 1 and not affix.startswith('-') and not affix.endswith('-'): # crude prefix
                        reconstructed_word = affix + reconstructed_word
                    elif len(affixes) == 1 and affix.startswith('-') and not affix.endswith('-'): # crude suffix
                        reconstructed_word = reconstructed_word + affix[1:]
                    # Perlu penanganan yang lebih baik untuk kombinasi afiks

        print(f"Placeholder: Reconstructing from '{root_word}' and affixes {affixes} -> {reconstructed_word}")
        # Kembalikan gabungan sederhana untuk placeholder
        # Logika yang benar akan jauh lebih kompleks
        temp_word = root_word
        for affix in affixes:
            if affix.endswith('-') and not affix.startswith('-'): # Prefix like "me-"
                temp_word = affix.replace('-', '') + temp_word
            elif affix.startswith('-') and not affix.endswith('-'): # Suffix like "-kan"
                temp_word = temp_word + affix.replace('-', '')
            # Perlu penanganan konfiks dan variasi lainnya

        return temp_word # Ini masih placeholder kasar

# Contoh penggunaan (bisa dihapus atau dikomentari nanti)
if __name__ == '__main__':
    recon = Reconstructor()
    result = recon.reconstruct("coba", ["men-"])
    print(f"Hasil rekonstruksi 'coba' dengan ['men-']: {result}")
    result2 = recon.reconstruct("makan", ["di-", "-kan"])
    print(f"Hasil rekonstruksi 'makan' dengan ['di-', '-kan']: {result2}")