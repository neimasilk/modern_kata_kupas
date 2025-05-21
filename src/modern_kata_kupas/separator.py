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

        # Check if word_after_prefixes is a root word
        print(f"Segment: After prefixes, word='{word_after_prefixes}', is_kata_dasar={self.dictionary.is_kata_dasar(word_after_prefixes)}") # Add logging
        if self.dictionary.is_kata_dasar(word_after_prefixes):
            # If yes, likely no suffixes need to be stripped
            final_word = word_after_prefixes
            stripped_suffixes = [] # No suffixes stripped from this root word
        else:
            # Strip suffixes only if word_after_prefixes is not a known root word
            word_after_suffixes, stripped_suffixes = self._strip_suffixes(word_after_prefixes)
            final_word = word_after_suffixes

        # 5. Apply morphophonemic rules (stub)
        # final_word = self._apply_morphophonemic_segmentation_rules(word_after_suffixes)
        # final_word = word_after_suffixes # Placeholder - This line is now handled by the if/else block

        # Combine prefixes, root, and suffixes
        # Assuming the desired format is prefix1~prefix2~...~word~suffix1~suffix2~...
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

    def _strip_suffixes(self, word: str) -> str:
        """
        Helper method to strip suffixes (particles and possessives).
        Strips particles (-kah, -lah, -pun) first, then possessives (-ku, -mu, -nya).

        Args:
            word (str): The word to strip suffixes from.

        Returns:
            str: The word after stripping suffixes.
        """
        current_word = word
        stripped_suffixes = []
        print(f"_strip_suffixes: Processing word='{word}'") # Add logging

        # 1. Strip particles (-kah, -lah, -pun)
        particles = ['kah', 'lah', 'pun']
        for particle in particles:
            if current_word.endswith(particle):
                potential_root = current_word[:-len(particle)]
                # Add check for dictionary lookup before stripping the particle
                is_root_in_dict = self.dictionary.is_kata_dasar(potential_root) # Capture the result
                print(f"Checking particle suffix '{particle}': potential_root='{potential_root}', is_kata_dasar='{is_root_in_dict}'") # Add logging
                if is_root_in_dict:
                    current_word = potential_root
                    stripped_suffixes.insert(0, particle) # Changed to insert(0, ...) for correct output order
                    # Do not break here, continue to check for possessives and derivational suffixes
                # If potential_root is not a root word, do not strip this particle

        # 2. Strip possessives (-ku, -mu, -nya)
        possessives = ['ku', 'mu', 'nya']
        for possessive in possessives:
            if current_word.endswith(possessive):
                potential_root = current_word[:-len(possessive)]
                # Add check for minimum stem length and dictionary lookup before stripping
                if len(potential_root) >= MIN_STEM_LENGTH_FOR_POSSESSIVE:
                    is_root_in_dict = self.dictionary.is_kata_dasar(potential_root) # Capture the result
                    print(f"Checking possessive suffix '{possessive}': potential_root='{potential_root}', is_kata_dasar='{is_root_in_dict}'") # Add logging
                    if is_root_in_dict:
                        current_word = potential_root
                        stripped_suffixes.insert(0, possessive) # Changed to insert(0, ...) for correct output order
                        # Do not break here, continue to check for derivational suffixes

        # 3. Strip derivational suffixes (-kan, -i, -an)
        derivational_suffixes = ['kan', 'i', 'an'] # Perhatikan 'i' bisa ambigu dengan akhir kata dasar
        # temp_word_before_derivational = current_word # Simpan keadaan sebelum strip derivational - not needed for this logic

        MIN_STEM_LENGTH_FOR_DERIVATIONAL_SUFFIX_STRIPPING = 2 # Define constant here or at class level

        for deriv_suffix in derivational_suffixes:
            if current_word.endswith(deriv_suffix):
                potential_root = current_word[:-len(deriv_suffix)]
                # Add check for minimum stem length and dictionary lookup before stripping
                if len(potential_root) >= MIN_STEM_LENGTH_FOR_DERIVATIONAL_SUFFIX_STRIPPING and self.dictionary.is_kata_dasar(potential_root):
                     current_word = potential_root
                     stripped_suffixes.insert(0, deriv_suffix)
                     # Do not break here, continue to check for other derivational suffixes (though unlikely in this set) or the end of the loop

        # Return the remaining word and the list of stripped suffixes
        return current_word, stripped_suffixes

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
                # Check if the potential root is a valid root word before stripping the prefix
                if self.dictionary.is_kata_dasar(potential_root):
                    current_word = potential_root
                    stripped_prefixes.append(prefix)
                    break # Assuming only one basic prefix at the beginning
                # If potential_root is not a root word, do not strip this prefix
                # Continue to the next prefix if needed (though the break prevents this for now)

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