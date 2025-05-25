# Arsitektur modern-kata-kupas

Dokumen ini menjelaskan arsitektur dan komponen utama dari library `modern-kata-kupas`.

## Komponen Utama

### Packaging and Data Access

The `modern-kata-kupas` library relies on several data files for its operation:

*   `kata_dasar.txt`: The main dictionary of Indonesian root words.
*   `loanwords.txt`: A list of common loanwords.
*   `affix_rules.json`: A JSON file containing morphological rules for prefixes, suffixes, and their morphophonemic changes.

These files are included within the installable package. This is achieved by specifying them in the `package_data` directive within the `setup.py` file:

```python
# setup.py
setup(
    # ... other setup arguments ...
    package_data={
        "modern_kata_kupas": ["data/kata_dasar.txt", "data/loanwords.txt", "data/affix_rules.json"],
    },
    # ...
)
```

#### Data Access within the Package

Components like `DictionaryManager` (for `kata_dasar.txt` and `loanwords.txt`) and `MorphologicalRules` (for `affix_rules.json`) are designed to load these data files from the package itself. This is typically done using Python's `importlib.resources` module.

For example, `DictionaryManager` uses `importlib.resources.read_text` to load the default dictionary and loanword list:

```python
# In DictionaryManager
import importlib.resources
# ...
file_content = importlib.resources.read_text(
    self.DEFAULT_DICT_PACKAGE_PATH, # e.g., "modern_kata_kupas.data"
    self.DEFAULT_DICT_FILENAME,     # e.g., "kata_dasar.txt"
    encoding='utf-8'
)
```

Similarly, `MorphologicalRules` loads `affix_rules.json` using the same mechanism. This ensures that the library functions correctly when installed, without needing direct access to the file system where the source code was originally located.

### DictionaryManager

Bertanggung jawab untuk memuat dan mengelola kamus kata dasar (`kata_dasar.txt`) dan daftar kata serapan (`loanwords.txt`) bahasa Indonesia. Mendukung pemuatan dari file eksternal atau file default yang dikemas dalam library (lihat bagian 'Packaging and Data Access'). Semua kata dinormalisasi sebelum disimpan dan diperiksa.

### StemmerInterface

Kelas ini berfungsi sebagai wrapper untuk library stemming bahasa Indonesia, saat ini mengintegrasikan PySastrawi. Tujuannya adalah menyediakan antarmuka yang konsisten dan sederhana untuk mendapatkan kata dasar dari sebuah kata, mengabstraksi detail implementasi dari library stemming yang mendasarinya. Metode utamanya adalah `get_root_word` yang mengambil string kata dan mengembalikan kata dasarnya.

### Normalizer

`Normalizer` (diimplementasikan sebagai kelas `TextNormalizer`) bertanggung jawab untuk membersihkan dan menstandarkan teks input. Ini termasuk mengubah teks menjadi huruf kecil, menghapus karakter khusus atau tanda baca yang tidak relevan, dan menangani variasi spasi. Normalisasi adalah langkah pra-pemrosesan penting sebelum segmentasi atau analisis morfologis lainnya.

### Separator

Modul utama (`separator.py`) yang bertanggung jawab untuk memisahkan kata berimbuhan menjadi kata dasar dan afiksnya. Ini mengkoordinasikan penggunaan komponen lain seperti normalizer, dictionary, rules, dan stemmer.

## Penanganan Ambiguitas Dasar (V1.0)

Versi 1.0 dari `ModernKataKupas` menggunakan pendekatan heuristik untuk menangani beberapa kasus ambiguitas morfologis. Pendekatan ini tidak dirancang untuk menyelesaikan semua jenis ambiguitas secara komprehensif, melainkan merupakan hasil dari interaksi antara urutan penerapan aturan, strategi segmentasi, dan ketersediaan kata dasar dalam kamus.

### Strategi Segmentasi Utama

Sistem menerapkan dua strategi utama untuk menemukan akar kata dan afiks:

1.  **S1 (Prefixes then Suffixes):** Mencoba melepaskan prefiks terlebih dahulu, kemudian sufiks dari sisa kata.
2.  **S2 (Suffixes then Prefixes):** Mencoba melepaskan sufiks terlebih dahulu, kemudian prefiks dari sisa kata.

### Pemilihan Hasil Segmentasi

Logika pemilihan antara hasil S1 dan S2 adalah sebagai berikut:

*   **Validitas Akar Kata:** Hasil dari sebuah strategi dianggap valid jika akar kata yang dihasilkan ditemukan dalam kamus (`kata_dasar.txt`).
*   **Prioritas:**
    1.  Jika kedua strategi (S1 dan S2) menghasilkan akar kata yang valid:
        *   Sistem akan memilih hasil yang menghasilkan **akar kata terpanjang**.
        *   Jika panjang akar kata sama, hasil dari S1 (Prefixes then Suffixes) akan lebih diprioritaskan.
    2.  Jika hanya satu strategi yang menghasilkan akar kata yang valid, hasil dari strategi tersebut akan dipilih.
    3.  Jika kedua strategi gagal menghasilkan akar kata yang valid (tidak ditemukan di kamus):
        *   Sistem akan menggunakan `word_to_process` (kata setelah penanganan reduplikasi) sebagai kandidat akar.
        *   Jika `word_to_process` ini juga tidak ada dalam kamus dan tidak ada afiks yang berhasil dilepaskan, maka kata asli yang telah dinormalisasi akan dikembalikan.

### Pengaruh Kamus (`kata_dasar.txt`)

Kamus kata dasar memainkan peran sentral. Sebuah urutan pelepasan afiks hanya dianggap berhasil jika menghasilkan stem yang terdaftar sebagai kata dasar. Kelengkapan kamus ini secara langsung mempengaruhi kemampuan sistem untuk menyelesaikan ambiguitas.

### Pengaruh Implisit dari Urutan Pelepasan Afiks

Meskipun tidak ada mekanisme eksplisit untuk memilih antara interpretasi afiks yang berbeda (misalnya, apakah "-an" pada "makanan" adalah satu sufiks atau bagian dari konfiks "ke-an"), urutan operasi internal memberikan pengaruh implisit:

*   **Pelepasan Sufiks (`_strip_suffixes`):** Sufiks dilepaskan dalam urutan prioritas:
    1.  Partikel: `-lah`, `-kah`, `-pun`
    2.  Posesif: `-ku`, `-mu`, `-nya`
    3.  Derivasional: `-kan`, `-i`, `-an`
    Proses ini iteratif; setelah satu sufiks dilepas, sistem mencoba lagi dari awal urutan prioritas pada sisa kata. Sufiks derivasional memiliki pemeriksaan tambahan: secara default, mereka hanya dilepas jika sisa stem adalah kata dasar yang dikenal (kecuali dalam konteks khusus seperti pemrosesan kluster sufiks pada kata berulang).
*   **Pelepasan Prefiks (`_strip_prefixes_detailed`):** Metode internal `_strip_prefixes_detailed` (dipanggil oleh `_strip_prefixes`) menangani pelepasan prefiks.
    *   Prefiks dicocokkan dari bentuk terpanjang ke terpendek (misalnya, "memper-" sebelum "meN-" atau "per-"). Ini membantu dalam identifikasi prefiks berlapis.
    *   Setelah sebuah prefiks dilepas, sistem memeriksa apakah sisa kata adalah kata dasar. Jika tidak, sistem juga akan mencoba membalikkan perubahan morfofonemik (misalnya, dari "tulis" menjadi "nulis" setelah "meN-" dilepas) dan memeriksa apakah bentuk asli tersebut adalah kata dasar.
    *   Proses ini bisa rekursif untuk menangani prefiks berlapis (misalnya, "dipermainkan" -> "di" + "permainkan" -> "di" + "per" + "mainkan").

Perlu dicatat bahwa penanganan reduplikasi (misalnya, "berkejar-kejaran") juga terintegrasi. Bentuk seperti ini akan diurai oleh `_handle_reduplication` (misalnya, menjadi basis "berkejar", penanda reduplikasi "ulg", dan sufiks "-an" yang menempel pada bagian kedua yang direduplikasi). Basis "berkejar" kemudian akan diproses lebih lanjut oleh strategi S1/S2.

### Contoh Kasus Ambiguitas

#### Kasus: "beruang"

*   **Kamus Referensi (`src/modern_kata_kupas/data/kata_dasar.txt`):** Tidak mengandung "uang" atau "ruang".
*   **Output Aktual (V1.0):** `beruang`
*   **Analisis Heuristik:**
    1.  **Normalisasi:** "beruang" -> "beruang".
    2.  **Cek Kata Dasar Awal:** "beruang" tidak ada di kamus.
    3.  **Reduplikasi:** Tidak ada. `word_to_process` = "beruang".
    4.  **Strategi S1 (Prefiks dulu):**
        *   `_strip_prefixes("beruang")`:
            *   Mencoba "ber-": sisa "uang". "uang" tidak ada di kamus.
            *   Mencoba "be-": sisa "ruang". "ruang" tidak ada di kamus.
            *   Tidak ada prefiks valid yang menghasilkan kata dasar dikenal. Hasil S1: tidak ada akar kata valid.
    5.  **Strategi S2 (Sufiks dulu):**
        *   `_strip_suffixes("beruang")`: Tidak ada sufiks yang cocok. Sisa "beruang".
        *   `_strip_prefixes("beruang")`: Sama seperti S1, tidak menemukan akar kata valid. Hasil S2: tidak ada akar kata valid.
    6.  **Pemilihan Hasil:** Karena S1 dan S2 gagal, dan "beruang" (sebagai `word_to_process`) tidak ada di kamus, outputnya adalah "beruang" (kata asli yang dinormalisasi).

#### Kasus: "mengetahui"

*   **Kamus Referensi (`src/modern_kata_kupas/data/kata_dasar.txt`):** Tidak mengandung "tahu" atau "ketahui".
*   **Output Aktual (V1.0):** `mengetahui`
*   **Analisis Heuristik:**
    1.  **Normalisasi:** "mengetahui" -> "mengetahui".
    2.  **Cek Kata Dasar Awal:** "mengetahui" tidak ada di kamus.
    3.  **Reduplikasi:** Tidak ada. `word_to_process` = "mengetahui".
    4.  **Strategi S1 (Prefiks dulu):**
        *   `_strip_prefixes("mengetahui")`:
            *   Mencoba "meN-" (alomorf "menge-"): sisa "tahui". "tahui" tidak ada di kamus.
            *   Mencoba "meN-" (alomorf "meng-"): sisa "etahui". "etahui" tidak ada di kamus.
            *   Tidak ada prefiks valid yang menghasilkan kata dasar dikenal. Hasil S1: tidak ada akar kata valid.
    5.  **Strategi S2 (Sufiks dulu):**
        *   `_strip_suffixes("mengetahui")`: Melepas "-i", sisa "mengetahu".
        *   `_strip_prefixes("mengetahu")`:
            *   Mencoba "meN-" (alomorf "menge-"): sisa "tahu". "tahu" tidak ada di kamus.
            *   Mencoba "meN-" (alomorf "meng-"): sisa "etahu". "etahu" tidak ada di kamus.
            *   Tidak ada prefiks valid yang menghasilkan kata dasar dikenal. Hasil S2: tidak ada akar kata valid.
    6.  **Pemilihan Hasil:** Karena S1 dan S2 gagal, dan "mengetahui" (sebagai `word_to_process`) tidak ada di kamus, outputnya adalah "mengetahui".

Secara umum, untuk V1.0, jika sebuah kata ambigu tidak dapat dipecah menjadi kombinasi afiks dan akar kata *yang dikenal dalam kamus saat ini*, maka kata tersebut cenderung dikembalikan dalam bentuk normalisasinya. Peningkatan kelengkapan kamus dan pengenalan aturan kontekstual yang lebih canggih akan diperlukan untuk penanganan ambiguitas yang lebih baik di versi mendatang.

Metode kunci dalam modul ini meliputi:

- `segment()`: Metode publik utama untuk memulai proses segmentasi.
- `_strip_suffixes()`: Metode helper yang bertanggung jawab untuk memisahkan sufiks dari kata. Saat ini diimplementasikan untuk menangani sufiks infleksional (partikel dan posesif) serta sufiks derivasional dasar (`-kan`, `-i`, `-an`) sesuai dengan Step 1.4 dan Step 1.5. Logika pelepasan sufiks ini mengikuti urutan tertentu untuk memastikan pelepasan yang benar.
- `_strip_prefixes()`: Metode helper yang bertanggung jawab untuk memisahkan prefiks sederhana (`di-`, `ke-`, `se-`) dari kata sesuai dengan Step 1.6. Metode ini berinteraksi dengan `MorphologicalRules` untuk mendapatkan dan menerapkan aturan prefiks.

### Reconstructor

`Reconstructor` bertugas untuk membangun kembali kata bahasa Indonesia dari string morfem hasil segmentasi. Kelas ini menggunakan aturan morfologi (termasuk alternasi morfofonemik) yang disediakan oleh `MorphologicalRules` dan dapat berkonsultasi dengan `DictionaryManager` untuk memvalidasi akar kata atau propertinya (misalnya, monosilabik) jika diperlukan oleh aturan rekonstruksi tertentu. Proses rekonstruksi melibatkan: penguraian string tersegmentasi, penerapan sufiks derivasional ke akar, penerapan aturan reduplikasi, penerapan sufiks pasca-reduplikasi, penerapan sufiks posesif dan partikel, dan terakhir penerapan prefiks dalam urutan terbalik dengan perubahan morfofonemik yang sesuai.

### Rules

Komponen `MorphologicalRules` bertanggung jawab untuk memuat, mem-parsing, dan menyediakan akses ke aturan afiks (prefiks, sufiks) dan perubahan morfofonemik terkait dari file konfigurasi JSON (`affix_rules.json`). Aturan-aturan ini diorganisir untuk pencarian dan penerapan yang efisien selama proses segmentasi dan rekonstruksi. Pemuatan file aturan dari dalam paket dijelaskan dalam bagian 'Packaging and Data Access'.

### Utils

Direktori `utils` berisi modul-modul pembantu. `string_utils.py` menyediakan fungsi dasar seperti `is_vowel` dan `is_consonant`. Modul `alignment.py` mengimplementasikan algoritma Needleman-Wunsch untuk penyelarasan string; fungsionalitas ini tidak digunakan secara aktif dalam logika segmentasi inti V1.0 tetapi ada untuk eksplorasi di masa depan dalam menangani kasus yang lebih kompleks atau ambigu.