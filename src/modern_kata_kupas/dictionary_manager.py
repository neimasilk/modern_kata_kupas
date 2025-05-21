from typing import Optional, List, Set
import os

class DictionaryManager:
    def __init__(self, dictionary_path: str = "data/kata_dasar.txt", initial_words: Optional[List[str]] = None):
        """
        Inisialisasi DictionaryManager.
        Args:
            dictionary_path (str): Path ke file kamus. Defaults to "data/kata_dasar.txt".
            initial_words (Optional[List[str]], optional): Daftar kata awal. Defaults to None.
        """
        self.dictionary_path = dictionary_path
        self.words: Set[str] = set()
        self.newly_added_words: Set[str] = set()
        self.removed_words: Set[str] = set()
        self.default_dictionary_path = os.path.join(
            os.path.dirname(__file__), "data", "kata_dasar.txt"
        )
        
        if dictionary_path: # Jika dictionary_path diberikan (dan initial_words tidak)
            self.load_from_file(dictionary_path)
        elif initial_words is not None:
            self.words.update(initial_words)

    

    

    def is_kata_dasar(self, kata):
        """
        Cek apakah kata merupakan kata dasar

        Args:
            kata (str): Kata yang akan dicek

        Returns:
            bool: True jika kata dasar, False jika bukan
        """
        return kata.lower() in self.words
        """
        Inisialisasi kamus kata dasar dari file teks
        
        Args:
            dictionary_path (str): Path ke file yang berisi kata dasar
        """
        self.words = set()
        self.load_from_file(dictionary_path)
    
    def contains(self, word: str) -> bool:
        """
        Mengecek apakah kata ada dalam kamus
        
        Args:
            word (str): Kata yang akan dicek
            
        Returns:
            bool: True jika kata ada dalam kamus
        """
        return word in self.words
    
    def add_word(self, word: str):
        """
        Menambahkan kata baru ke dalam kamus (in-memory)
        
        Args:
            word (str): Kata yang akan ditambahkan
        """
        self.words.add(word)
    
    def load_from_file(self, file_path: str):
        """
        Memuat/memuat ulang kamus dari file
        
        Args:
            file_path (str): Path ke file yang berisi kata dasar
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.words = {line.strip() for line in f if line.strip()}
        except FileNotFoundError:
            # Naikkan ValueError agar sesuai dengan ekspektasi tes
            raise ValueError(f"File kamus tidak ditemukan: {file_path}")
        except Exception as e:
            # Naikkan RuntimeError untuk error pemuatan lainnya, agar sesuai ekspektasi tes
            raise RuntimeError(f"Gagal memuat kamus: {str(e)}")