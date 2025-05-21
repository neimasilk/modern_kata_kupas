class DictionaryManager:
    def __init__(self, dictionary_path: str = None, initial_words: Optional[List[str]] = None):
        """
        Inisialisasi DictionaryManager.
        Args:
            dictionary_path (str, optional): Path ke file kamus. Defaults to None.
            initial_words (Optional[List[str]], optional): Daftar kata awal. Defaults to None.
        """
        self.dictionary_path = dictionary_path
        self.words: Set[str] = set()  # Inisialisasi self.words di awal
        self.newly_added_words: Set[str] = set()
        self.removed_words: Set[str] = set()
        self.default_dictionary_path = os.path.join(
            os.path.dirname(__file__), "data", "kata_dasar.txt"
        )

        if dictionary_path:
            self.words.update(self._load_dictionary(dictionary_path))
        elif initial_words is not None:
            self.words.update(initial_words)

    def _load_dictionary(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self._kata_dasar = {line.strip().lower() for line in file}
        except FileNotFoundError:
            raise ValueError(f"File kamus tidak ditemukan: {self.file_path}")
        except Exception as e:
            raise RuntimeError(f"Gagal memuat kamus: {str(e)}")

    def _load_dictionary(self) -> None:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self._kata_dasar = {line.strip() for line in f}
        except FileNotFoundError:
            raise ValueError(f"File kamus tidak ditemukan: {self.file_path}")
        except Exception as e:
            raise RuntimeError(f"Gagal memuat kamus: {str(e)}")

    def __init__(self, dictionary_path="data/kata_dasar.txt"):
        """
        Inisialisasi kamus kata dasar

        Args:
            dictionary_path (str): Path ke file kamus kata dasar
        """
        self.file_path = dictionary_path
        self._kata_dasar = set()
        self._load_dictionary()

    def _load_dictionary(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self._kata_dasar = {line.strip().lower() for line in file}
        except FileNotFoundError:
            raise ValueError(f"File kamus tidak ditemukan: {self.file_path}")
        except Exception as e:
            raise RuntimeError(f"Gagal memuat kamus: {str(e)}")

    def is_kata_dasar(self, kata):
        """
        Cek apakah kata merupakan kata dasar

        Args:
            kata (str): Kata yang akan dicek

        Returns:
            bool: True jika kata dasar, False jika bukan
        """
        return kata.lower() in self._kata_dasar
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
            print(f"File {file_path} tidak ditemukan, kamus kosong")
            self.words = set()