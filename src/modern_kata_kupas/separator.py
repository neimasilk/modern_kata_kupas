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
        (Stub implementation)

        Args:
            word (str): Kata yang akan dipisahkan.

        Returns:
            str: The normalized word (stub).
        """
        # Use the normalizer to return the normalized word
        return self.normalizer.normalize_word(word)

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

        # 1. Strip particles (-kah, -lah, -pun)
        particles = ['kah', 'lah', 'pun']
        for particle in particles:
            if current_word.endswith(particle):
                potential_root = current_word[:-len(particle)]
                # Strip the particle if found, regardless of whether the potential root is a valid root word
                current_word = potential_root
                stripped_suffixes.append(particle)
                break # Assuming only one particle can be attached at the end

        # 2. Strip possessives (-ku, -mu, -nya)
        possessives = ['ku', 'mu', 'nya']
        for possessive in possessives:
            if current_word.endswith(possessive):
                potential_root = current_word[:-len(possessive)]
                # Add check for minimum stem length before stripping
                if len(potential_root) >= MIN_STEM_LENGTH_FOR_POSSESSIVE:
                    # Strip the possessive if found, regardless of whether the potential root is a valid root word
                    current_word = potential_root
                    stripped_suffixes.append(possessive)
                    break # Assuming only one possessive can be attached at the end

        # Reconstruct the word with stripped suffixes marked (e.g., word~suffix1~suffix2)
        if stripped_suffixes:
            return current_word + '~' + '~'.join(reversed(stripped_suffixes))
        else:
            return current_word

    def _strip_prefixes(self, word: str) -> str:
        """
        Helper method to strip prefixes (stub).
        """
        pass # Stub implementation

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