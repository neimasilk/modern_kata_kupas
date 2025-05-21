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
    MIN_STEM_LENGTH_FOR_POSSESSIVE = 2 # Define minimum stem length for possessive stripping
    MIN_STEM_LENGTH_FOR_DERIVATIONAL_SUFFIX_STRIPPING = 3 # Define minimum stem length for derivational suffix stripping
    def __init__(self):
        """
        Inisialisasi ModernKataKupas dengan dependensi yang diperlukan.
        """
        # Initialize dependencies (stubs for now)
        # self.normalizer = TextNormalizer()
        # self.dictionary = RootWordDictionary()
        # self.rules = AffixRuleRepository()
        # self.stemmer = IndonesianStemmer()
        # self.aligner = alignment_function # Placeholder for the function/callable
        
        # Initialize dependencies
        self.normalizer = TextNormalizer()
        self.dictionary = DictionaryManager()
        self.rules = MorphologicalRules()
        self.stemmer = IndonesianStemmer()
        self.aligner = align

    def segment(self, word: str) -> str:
        normalized_word = self.normalizer.normalize_word(word)

        # Langkah 1: Coba lepaskan prefiks terlebih dahulu
        stem_after_prefixes, stripped_prefix_list = self._strip_prefixes(normalized_word)

        # Langkah 2: Coba lepaskan sufiks dari hasil pelepasan prefiks
        final_stem, stripped_suffix_list = self._strip_suffixes(stem_after_prefixes)

        # Langkah 3: Validasi
        # Hanya gabungkan jika final_stem adalah kata dasar yang valid
        if self.dictionary.is_kata_dasar(final_stem):
            parts = []
            if stripped_prefix_list:
                parts.extend(stripped_prefix_list)
            parts.append(final_stem)
            if stripped_suffix_list:
                parts.extend(stripped_suffix_list)

            if not stripped_prefix_list and not stripped_suffix_list:
                return final_stem
            return '~'.join(parts)
        else:
            # Coba alternatif: lepaskan sufiks dulu baru prefiks
            stem_after_suffixes, stripped_suffix_list = self._strip_suffixes(normalized_word)
            final_stem, stripped_prefix_list = self._strip_prefixes(stem_after_suffixes)
            
            if self.dictionary.is_kata_dasar(final_stem):
                parts = []
                if stripped_prefix_list:
                    parts.extend(stripped_prefix_list)
                parts.append(final_stem)
                if stripped_suffix_list:
                    parts.extend(stripped_suffix_list)
                return '~'.join(parts)
            
            # Jika kedua pendekatan gagal, kembalikan kata yang dinormalisasi
            if self.dictionary.is_kata_dasar(normalized_word):
                return normalized_word
            return normalized_word
        """
        Memisahkan kata berimbuhan menjadi kata dasar dan afiksnya.

        Args:
            word (str): Kata yang akan dipisahkan.

        Returns:
            str: Kata setelah proses segmentasi (saat ini hanya pelepasan afiks dasar).
        """
        # 1. Normalisasi kata
        normalized_word = self.normalizer.normalize_word(word)

        # 2. Handle reduplikasi (stub)
        # word_after_reduplication = self._handle_reduplication(normalized_word)
        word_after_reduplication = normalized_word # Placeholder

        # 3. Strip prefixes
        word_after_prefixes, stripped_prefixes = self._strip_prefixes(word_after_reduplication)

        # 4. Strip suffixes
        # Note: The order of stripping prefixes and suffixes can be complex
        # For now, we apply suffixes after prefixes. This might need refinement.

        # word_after_reduplication = self._handle_reduplication(normalized_word) # Untuk nanti
        current_processing_word = normalized_word

        # Langkah 1: Coba lepaskan sufiks terlebih dahulu
        stem_after_suffixes, stripped_suffix_list = self._strip_suffixes(current_processing_word)

        # Langkah 2: Coba lepaskan prefiks dari hasil pelepasan sufiks
        final_stem, stripped_prefix_list = self._strip_prefixes(stem_after_suffixes)

        # Langkah 3: Validasi
        # Hanya gabungkan jika final_stem adalah kata dasar yang valid
        if self.dictionary.is_kata_dasar(final_stem):
            parts = []
            if stripped_prefix_list:
                parts.extend(stripped_prefix_list)
            parts.append(final_stem)
            if stripped_suffix_list: # stripped_suffix_list sudah dalam urutan yang benar dari _strip_suffixes (misal: [kan, lah])
                parts.extend(stripped_suffix_list)

            if not stripped_prefix_list and not stripped_suffix_list: # Tidak ada afiks yang dilepas
                 return final_stem # Kembalikan kata dasar jika memang itu inputnya
            return '~'.join(parts)
        else:
            # Jika setelah semua pelepasan, tidak menghasilkan kata dasar yang valid,
            # kembalikan kata yang sudah dinormalisasi (atau kata asli jika normalisasi tidak menghasilkan apa-apa).
            # Perilaku fallback ini mungkin perlu dipertimbangkan lebih lanjut sesuai kebutuhan.
            # Untuk sekarang, jika normalisasi adalah kata dasar, kembalikan itu.
            if self.dictionary.is_kata_dasar(normalized_word):
                return normalized_word
            # Jika kata input yang dinormalisasi juga bukan kata dasar, dan segmentasi gagal,
            # tes mungkin mengharapkan kata asli yang dinormalisasi dikembalikan.
            # Untuk "dimakanlah", jika gagal total, apakah "dimakanlah" atau "di~makan~lah" yang diharapkan?
            # Tes "dimakanlah" == "di~makan~lah" berarti segmentasi HARUS berhasil.
            # Jika final_stem tidak valid, berarti ada yang salah dalam logika _strip_suffixes atau _strip_prefixes
            # atau kata tersebut memang tidak bisa disegmentasi dengan aturan saat ini.
            # Untuk tujuan tes, kita asumsikan jika tidak valid, maka tidak ada segmen.
            # Namun, jika input awal adalah kata dasar, itu harus dikembalikan.
            return normalized_word # Fallback sementara
        parts = []
        if stripped_prefixes:
            parts.extend(stripped_prefixes)
        parts.append(final_word)
        if stripped_suffixes:
            parts.extend(stripped_suffixes)

        return '~'.join(parts)

    def _handle_reduplication(self, word: str) -> str:
        """
        Helper method to handle reduplication (stub).
        """
        pass # Stub implementation

    def _strip_suffixes(self, word: str) -> tuple[str, list[str]]:
        current_word = str(word) # Pastikan bekerja dengan string
        stripped_suffixes_in_stripping_order = []

        # Partikel: -kah, -lah, -pun
        particles = ['kah', 'lah', 'pun']
        for particle_sfx in particles:
            if current_word.endswith(particle_sfx):
                current_word = current_word[:-len(particle_sfx)]
                stripped_suffixes_in_stripping_order.append(particle_sfx)
                break

        # Posesif: -ku, -mu, -nya
        possessives = ['ku', 'mu', 'nya']
        word_before_possessives = current_word
        for poss_sfx in possessives:
            if word_before_possessives.endswith(poss_sfx) and \
               len(word_before_possessives[:-len(poss_sfx)]) >= self.MIN_STEM_LENGTH_FOR_POSSESSIVE:
                current_word = word_before_possessives[:-len(poss_sfx)]
                stripped_suffixes_in_stripping_order.append(poss_sfx)
                break

        # Derivasional: -kan, -i, -an
        derivational_suffixes = ['kan', 'i', 'an']
        word_before_derivational = current_word
        for deriv_sfx in derivational_suffixes:
            if word_before_derivational.endswith(deriv_sfx):
                remainder = word_before_derivational[:-len(deriv_sfx)]
                if len(remainder) >= self.MIN_STEM_LENGTH_FOR_DERIVATIONAL_SUFFIX_STRIPPING:
                    current_word = remainder
                    stripped_suffixes_in_stripping_order.append(deriv_sfx)
                    break

        return current_word, list(reversed(stripped_suffixes_in_stripping_order))
        """
        Helper method to strip suffixes (particles, possessives, derivational).
        Strips particles, then possessives, then derivational suffixes iteratively.
        Does NOT validate against the dictionary at each step.

        Args:
            word (str): The word to strip suffixes from.

        Returns:
            tuple[str, list[str]]: The word after stripping suffixes and a list of stripped suffixes.
        """
        current_word = str(word)
        stripped_suffixes_in_stripping_order = []

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

    def _strip_prefixes(self, word: str) -> str:
        """
        Helper method to strip basic prefixes (-di, -ke, -se).

        Args:
            word (str): The word to strip prefixes from.

        Returns:
            str: The word after stripping prefixes.
        """
        current_word = word
        stripped_prefixes = []

        # Strip basic prefixes (-di, -ke, -se)
        prefixes = ['di', 'ke', 'se']
        for prefix in prefixes:
            if current_word.startswith(prefix):
                potential_root = current_word[len(prefix):]
                # Strip the prefix if found. Dictionary validation happens in segment().
                current_word = potential_root
                stripped_prefixes.append(prefix)
                break # Assuming only one basic prefix at the beginning


        # Return the remaining word and the list of stripped prefixes
        return current_word, stripped_prefixes

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