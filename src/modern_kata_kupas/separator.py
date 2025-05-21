# src/modern_kata_kupas/separator.py
"""
Modul untuk memisahkan kata berimbuhan menjadi kata dasar dan afiksnya.
"""

from .normalizer import TextNormalizer
from .dictionary_manager import DictionaryManager
from .rules import MorphologicalRules
from .stemmer_interface import IndonesianStemmer
from .utils.alignment import align

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
                 # Check if the remaining word is at least 3 characters long (a common rule)
                # For basic suffixes, we strip if the word is long enough. Dictionary check will be done later.
                if len(current_word) > len(particle):
                     current_word = current_word[:-len(particle)]
                     stripped_suffixes.append(particle)
                     # Assuming only one particle can be attached at the end for now
                     break

        # 2. Strip possessives (-ku, -mu, -nya)
        possessives = ['ku', 'mu', 'nya']
        for possessive in possessives:
            if current_word.endswith(possessive):
                 # Check if the remaining word is at least 3 characters long
                 # For basic suffixes, we strip if the word is long enough. Dictionary check will be done later.
                 if len(current_word) > len(possessive):
                     current_word = current_word[:-len(possessive)]
                     stripped_suffixes.append(possessive)
                     # Assuming only one possessive can be attached at the end for now
                     break

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