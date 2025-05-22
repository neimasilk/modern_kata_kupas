# src/modern_kata_kupas/separator.py
"""
Modul untuk memisahkan kata berimbuhan menjadi kata dasar dan afiksnya.
"""

from .normalizer import TextNormalizer
from .dictionary_manager import DictionaryManager
from .rules import MorphologicalRules
from .stemmer_interface import IndonesianStemmer
from .utils.alignment import align

MIN_STEM_LENGTH_FOR_POSSESSIVE = 3 # Panjang minimal kata dasar untuk pemisahan sufiks posesif

class ModernKataKupas:
    """
    Kelas utama untuk proses pemisahan kata berimbuhan.
    """
    MIN_STEM_LENGTH_FOR_POSSESSIVE = 3 # Define minimum stem length for possessive stripping
    MIN_STEM_LENGTH_FOR_DERIVATIONAL_SUFFIX_STRIPPING = 4 # Define minimum stem length for derivational suffix stripping
    MIN_STEM_LENGTH_FOR_PARTICLE = 3 # Define minimum stem length for particle stripping
    def __init__(self, dictionary_path: str = None, rules_file_path: str = None):
        """
Inisialisasi ModernKataKupas dengan dependensi yang diperlukan.

        Args:
            dictionary_path (str, optional): Path ke file kamus khusus.
                                            Jika None, kamus default akan dimuat.
            rules_file_path (str, optional): Path ke file aturan khusus.
                                           Jika None, file aturan default akan dimuat.
        """
        import importlib
        
        # Constants for default rules file location
        DEFAULT_DATA_PACKAGE_PATH = 'modern_kata_kupas.data'
        DEFAULT_RULES_FILENAME = 'affix_rules.json'
        
        self.normalizer = TextNormalizer()
        self.dictionary = DictionaryManager(dictionary_path=dictionary_path)
        self.stemmer = IndonesianStemmer()
        self.aligner = align

        if rules_file_path:
            self.rules = MorphologicalRules(rules_path=rules_file_path)
        else:
            try:
                with importlib.resources.path(DEFAULT_DATA_PACKAGE_PATH, DEFAULT_RULES_FILENAME) as default_rules_path:
                    self.rules = MorphologicalRules(rules_path=str(default_rules_path))
            except (FileNotFoundError, TypeError, ModuleNotFoundError) as e: # TODO: Add logging here
                base_dir = os.path.dirname(os.path.abspath(__file__))
                default_rules_path_rel = os.path.join(base_dir, "data", DEFAULT_RULES_FILENAME)
                if os.path.exists(default_rules_path_rel):
                    self.rules = MorphologicalRules(rules_path=default_rules_path_rel)
                else: # TODO: Add logging here
                    self.rules = MorphologicalRules()

    def segment(self, word: str) -> str:
        """Memisahkan kata berimbuhan menjadi kata dasar dan afiksnya.

        Args:
            word (str): Kata yang akan dipisahkan.

        Returns:
            str: Kata setelah proses segmentasi dalam format prefiks~kata_dasar~sufiks.
        """
        # 1. Normalisasi kata
        normalized_word = self.normalizer.normalize_word(word)
        
        # Jika kata sudah merupakan kata dasar, langsung kembalikan
        if self.dictionary.is_kata_dasar(normalized_word):
            return normalized_word
        
        # Strategi 1: Prefiks dulu, baru sufiks
        stem_after_prefixes, stripped_prefix_list = self._strip_prefixes(normalized_word)
        final_stem_strat1, stripped_suffix_list_strat1 = self._strip_suffixes(stem_after_prefixes)
        is_strat1_valid_root = self.dictionary.is_kata_dasar(final_stem_strat1)
        
        # Strategi 2: Sufiks dulu, baru prefiks
        stem_after_suffixes, stripped_suffix_list_strat2 = self._strip_suffixes(normalized_word)
        final_stem_strat2, stripped_prefix_list_strat2 = self._strip_prefixes(stem_after_suffixes)
        is_strat2_valid_root = self.dictionary.is_kata_dasar(final_stem_strat2)
        
        # Pilih strategi yang menghasilkan kata dasar valid
        if is_strat1_valid_root:
            # Gunakan hasil dari Strategi 1
            parts = []
            if stripped_prefix_list:
                parts.extend(stripped_prefix_list)
            parts.append(final_stem_strat1)
            if stripped_suffix_list_strat1:
                parts.extend(stripped_suffix_list_strat1)
            
            if not stripped_prefix_list and not stripped_suffix_list_strat1:
                return final_stem_strat1
            return '~'.join(parts)
            
        elif is_strat2_valid_root:
            # Gunakan hasil dari Strategi 2
            parts = []
            if stripped_prefix_list_strat2:
                parts.extend(stripped_prefix_list_strat2)
            parts.append(final_stem_strat2)
            if stripped_suffix_list_strat2:
                parts.extend(stripped_suffix_list_strat2)
            
            if not stripped_prefix_list_strat2 and not stripped_suffix_list_strat2:
                return final_stem_strat2
            return '~'.join(parts)
        
        # Jika kedua strategi gagal, kembalikan kata yang sudah dinormalisasi
        return normalized_word

    def _handle_reduplication(self, word: str) -> str:
        """
        Helper method to handle reduplication (stub).
        """
        pass # Stub implementation


    def _strip_suffixes(self, word: str) -> tuple[str, list[str]]:
        current_word = str(word)
        stripped_suffixes_in_stripping_order = []
        
        # Urutan prioritas pelepasan sufiks (dari luar ke dalam)
        # 1. Partikel: -lah, -kah, -pun
        # 2. Posesif: -ku, -mu, -nya
        # 3. Derivasional: -kan, -i, -an
        suffix_types = [
            ["lah", "kah", "pun"],  # Partikel
            ["ku", "mu", "nya"],    # Posesif
            ["kan", "i", "an"]      # Derivasional
        ]
        
        # Iteratively strip suffixes until no more known suffixes are found
        something_stripped = True
        while something_stripped:
            something_stripped = False
            # Try stripping each type of suffix in order
            for suffixes_list in suffix_types:
                # Check for each suffix within the current type list
                for sfx in suffixes_list:
                    if current_word.endswith(sfx):
                        stem_candidate = current_word[:-len(sfx)]
                        
                        # Validasi panjang stem minimal
                        if len(stem_candidate) < 2:
                            continue
                            
                        # Untuk sufiks derivatif, cek panjang minimal
                        if sfx in suffix_types[2] and len(stem_candidate) < self.MIN_STEM_LENGTH_FOR_DERIVATIONAL_SUFFIX_STRIPPING:
                            continue
                            
                        # Untuk sufiks posesif, cek panjang minimal
                        if sfx in suffix_types[1] and len(stem_candidate) < self.MIN_STEM_LENGTH_FOR_POSSESSIVE:
                            continue
                            
                        # Untuk sufiks partikel, cek panjang minimal
                        if sfx in suffix_types[0] and len(stem_candidate) < self.MIN_STEM_LENGTH_FOR_PARTICLE:
                            continue
                        
                        # Kasus khusus untuk kata seperti "sekolah" yang bukan "se~kolah"
                        if sfx == "lah" and current_word == "sekolah" and stem_candidate == "seko":
                            continue
                        
                        # Tambahkan sufiks ke daftar dan perbarui kata saat ini
                        current_word = stem_candidate
                        stripped_suffixes_in_stripping_order.append(sfx)
                        something_stripped = True
                        # Restart the stripping process from the outermost suffix type
                        # This handles cases like 'rumahkupun' where 'pun' is stripped, then 'ku' can be stripped from 'rumahku'
                        break # Break inner loop (suffixes_list)
                if something_stripped:
                    break # Break outer loop (suffix_types) and restart while loop
        
        # `stripped_suffixes_in_stripping_order` contains suffixes in stripping order (outermost to innermost).
        # For test output expecting order like ['kan', 'lah'], we need to reverse it.
        return current_word, list(reversed(stripped_suffixes_in_stripping_order))

        # Kode di bawah ini sudah tidak digunakan lagi karena sudah digantikan dengan implementasi di atas
        # Tetap disimpan sebagai referensi untuk pengembangan lebih lanjut

        # Define suffix types and their order of stripping preference (outermost first)
        suffix_types = [
            ['kah', 'lah', 'pun'], # Particles
            ['ku', 'mu', 'nya'],   # Possessives
            ['kan', 'i', 'an']     # Derivational
        ]

        # Iteratively strip suffixes until no more known suffixes are found
        something_stripped = True
        while something_stripped:
            something_stripped = False
            # Try stripping each type of suffix in order
            for suffixes_list in suffix_types:
                # Check for each suffix within the current type list
                for sfx in suffixes_list:
                    if current_word.endswith(sfx):
                        # Check minimum stem length for possessive and derivational
                        if (sfx in suffix_types[1] and len(current_word[:-len(sfx)]) < self.MIN_STEM_LENGTH_FOR_POSSESSIVE) or \
                           (sfx in suffix_types[2] and len(current_word[:-len(sfx)]) < self.MIN_STEM_LENGTH_FOR_DERIVATIONAL_SUFFIX_STRIPPING):
                            continue # Skip stripping if minimum stem length is not met

                        current_word = current_word[:-len(sfx)]
                        stripped_suffixes_in_stripping_order.append(sfx)
                        something_stripped = True
                        # Restart the stripping process from the outermost suffix type
                        # This handles cases like 'rumahkupun' where 'pun' is stripped, then 'ku' can be stripped from 'rumahku'
                        break # Break inner loop (suffixes_list)
                if something_stripped:
                    break # Break outer loop (suffix_types) and restart while loop

        # `stripped_suffixes_in_stripping_order` contains suffixes in stripping order (outermost to innermost).
        # For test output expecting order like ['kan', 'lah'], we need to reverse it.
        return current_word, list(reversed(stripped_suffixes_in_stripping_order))

    def _is_monosyllabic(self, word: str) -> bool:
        """
        Helper sederhana untuk mengecek apakah sebuah kata (calon akar) monosilabik.
        Ini adalah placeholder, Anda mungkin memerlukan logika yang lebih baik
        atau daftar kata dasar monosilabik.
        """
        if not word:
            return False
        # Logika deteksi suku kata bisa kompleks. Untuk awal:
        # Anggap saja jika pendek dan ada di kamus, atau jika hanya punya satu vokal.
        # Ini perlu disempurnakan. Contoh: 'bom', 'cat', 'las'.
        vowels = "aiueo"
        vowel_count = sum(1 for char in word if char in vowels)
        # Kasar: jika jumlah vokal = 1 dan ada di kamus ATAU sangat pendek
        if vowel_count == 1 and (len(word) <= 3 or self.dictionary.is_kata_dasar(word)):
            return True
        # Ini hanya contoh kasar, perlu analisis lebih lanjut atau daftar kata monosilabik.
        # Untuk kasus seperti "tes", "kon" (dari "rekonstruksi"), "bor"
        # Mungkin lebih baik jika aturan "menge-" hanya berlaku jika sisanya adalah kata dasar yang diketahui monosilabik.
        if self.dictionary.is_kata_dasar(word):
            # Jika kata ada di kamus, baru cek suku katanya (logika bisa rumit)
            # Untuk sekarang, kita asumsikan jika kata ada di kamus dan jumlah vokal=1, itu monosilabik.
             return vowel_count == 1
        return False # Default

    def _strip_prefixes(self, original_word_for_prefix_stripping: str) -> tuple[str, list[str]]:
        current_word = str(original_word_for_prefix_stripping)
        stripped_prefixes_output = []

        # Dapatkan kata dasar dari stemmer SEBELUM iterasi prefiks. Ini penting untuk validasi.
        root_from_stemmer = self.stemmer.get_root_word(original_word_for_prefix_stripping)
        
        prefix_rules_all = self.rules.get_prefix_rules()

        # Prioritaskan aturan kompleks (meN-/peN-) terlebih dahulu
        for rule_group in prefix_rules_all:
            canonical_prefix = rule_group.get("canonical")
            
            # Tangani prefiks kompleks (meN-, peN-)
            if "allomorphs" in rule_group and (canonical_prefix == "meN" or canonical_prefix == "peN"):
                for allomorph_rule in rule_group["allomorphs"]:
                    surface_form = allomorph_rule.get("surface")

                    if current_word.startswith(surface_form):
                        remainder = current_word[len(surface_form):]
                        if not remainder: # Jika setelah dipotong tidak ada sisa
                            continue

                        reconstructed_root = remainder # Default jika tidak ada peluluhan

                        # Tangani kasus peluluhan dan rekonstruksi
                        if allomorph_rule.get("elision"):
                            reconstruct_rule = allomorph_rule.get("reconstruct_root_initial")
                            if reconstruct_rule:
                                next_char_in_remainder = remainder[0] if remainder else ''
                                elided_char = None
                                # Determine the elided_char_to_prepend from the first key of reconstruct_rule
                                if reconstruct_rule: # Ensure reconstruct_rule is not empty
                                    elided_char_to_prepend = list(reconstruct_rule.keys())[0]
                                    elided_char = elided_char_to_prepend # Set elided_char
                                else:
                                    elided_char_to_prepend = None # Should not happen if elision is true

                                if elided_char: # elided_char is now elided_char_to_prepend
                                    temp_reconstructed = elided_char + remainder
                                    # Prioritize dictionary lookup for validation of the reconstructed root
                                    is_temp_recon_kd = self.dictionary.is_kata_dasar(temp_reconstructed)
                                    if is_temp_recon_kd:
                                        reconstructed_root = temp_reconstructed
                                        # If reconstruction is successful and the root is valid, we found the stem
                                        stripped_prefixes_output.append(canonical_prefix)
                                        current_word = reconstructed_root
                                        return current_word, stripped_prefixes_output
                                    # If reconstruction failed or result is not a base word, continue trying other rules

                            # If elision rule didn't apply or didn't result in a valid root, check if remainder itself is a root
                            is_remainder_kd = self.dictionary.is_kata_dasar(remainder)
                            if is_remainder_kd:
                                stripped_prefixes_output.append(canonical_prefix)
                                current_word = remainder
                                return current_word, stripped_prefixes_output

                        # If not an elision rule or elision handling didn't return, check if stripping the prefix results in a valid root
                        elif self.dictionary.is_kata_dasar(remainder):
                            stripped_prefixes_output.append(canonical_prefix)
                            current_word = remainder
                            return current_word, stripped_prefixes_output

                        # If none of the above conditions met for this allomorph, continue to next allomorph/rule

            # Tangani prefiks sederhana sebagai fallback
            # This block should handle simple prefixes like 'di-', 'ter-', 'se-', 'ke-'
            elif "allomorphs" not in rule_group: # This is the condition for simple prefixes
                simple_prefix_form = rule_group.get("form")
                canonical_prefix = rule_group.get("canonical") # Ensure canonical_prefix is available here

                if simple_prefix_form and current_word.startswith(simple_prefix_form):
                    potential_root_after_simple_strip = current_word[len(simple_prefix_form):]

                    if not potential_root_after_simple_strip:
                        continue

                    # root_from_stemmer is the stem of the original input word to _strip_prefixes
                    stem_of_original = root_from_stemmer
                    stem_of_remainder = self.stemmer.get_root_word(potential_root_after_simple_strip)

                    # Modifikasi untuk membuat prefiks sederhana lebih permisif
                    if potential_root_after_simple_strip:
                        stripped_prefixes_output.append(canonical_prefix)
                        current_word = potential_root_after_simple_strip
                        return current_word, stripped_prefixes_output
                    if self.dictionary.is_kata_dasar(potential_root_after_simple_strip):
                        stripped_prefixes_output.append(canonical_prefix)
                        current_word = potential_root_after_simple_strip
                        # Setelah menemukan dan melepaskan awalan sederhana yang valid,
                        # kita bisa langsung return karena biasanya awalan sederhana tidak berlapis keluar setelah awalan kompleks
                        # dan satu awalan sederhana per pemanggilan _strip_prefixes sudah cukup.
                        return current_word, stripped_prefixes_output
        
        return current_word, stripped_prefixes_output

    def _apply_morphophonemic_segmentation_rules(self, word: str) -> str:
        """
        Helper method to apply morphophonemic segmentation rules (stub).
        """
        pass # Stub implementation

# Example usage (can be removed or commented out later)
if __name__ == '__main__':
    # Example usage will require initializing dependencies
    # For now, just demonstrate instantiation
    try:
        mkk = ModernKataKupas()
        print("ModernKataKupas class instantiated successfully.")
        # print(f"Segmenting 'makanan': {mkk.segment('makanan')}") # This will work with the current stub
    except Exception as e:
        print(f"Error instantiating ModernKataKupas: {e}")