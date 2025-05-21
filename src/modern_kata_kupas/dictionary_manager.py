class RootWordDictionary:
    def __init__(self, dictionary_path="data/kata_dasar.txt"):
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