# Baby Steps To-Do List untuk Penyelesaian Fase 4 (V1.0)

**Tujuan Utama Fase 4:** Memfinalisasi fungsionalitas inti, melakukan pengujian komprehensif, menyelesaikan dokumentasi, dan mempersiapkan paket untuk rilis V1.0.

**Catatan untuk Developer:**
* Setiap "Baby Step" dirancang untuk menjadi tugas yang jelas dan dapat dikelola.
* Fokus pada kualitas dan kelengkapan untuk setiap langkah.
* Jika ada ketidakjelasan, segera diskusikan sebelum melanjutkan.
* Pastikan semua perubahan kode disertai dengan tes yang relevan (jika berlaku) dan semua tes berhasil dijalankan sebelum menandai langkah sebagai selesai.
* Update `memory-bank/progress.md` setelah menyelesaikan setiap "Baby Step" yang berkaitan dengan Rencana Implementasi.

---

## Bagian 1: Finalisasi Penanganan Ambiguitas Dasar (Terkait Langkah 4.2 Rencana Implementasi)

### Baby Step 4.2.1: Dokumentasi Heuristik Ambiguitas V1.0

* **Tujuan:** Mendokumentasikan dengan jelas bagaimana `ModernKataKupas` versi 1.0 saat ini menangani kasus-kasus ambiguitas morfologis dasar tanpa memerlukan perubahan kode. Fokus pada pendeskripsian perilaku *yang sudah ada*.
* **Aktivitas:**
    1.  **Identifikasi Heuristik Saat Ini:**
        * Buka file `src/modern_kata_kupas/separator.py`.
        * Pelajari kembali logika dalam metode `segment()`, khususnya bagaimana strategi S1 (`_strip_prefixes` lalu `_strip_suffixes`) dan S2 (`_strip_suffixes` lalu `_strip_prefixes`) dieksekusi dan bagaimana hasilnya dipilih jika keduanya menghasilkan segmen yang valid (misalnya, berdasarkan keberadaan kata dasar di kamus, atau jika ada preferensi implisit).
        * Perhatikan bagaimana kasus seperti "beruang" (`be-ruang` vs `ber-uang`) dan "mengetahui" (`me-N-tahu-i` vs `meng-etahui`) saat ini diproses berdasarkan kamus yang ada (`data/kata_dasar.txt`) dan aturan (`data/affix_rules.json`).
    2.  **Update `memory-bank/architecture.md`:**
        * Tambahkan sub-bagian baru (atau perbarui yang sudah ada jika relevan) bernama "Penanganan Ambiguitas Dasar (V1.0)".
        * Dalam sub-bagian ini, jelaskan secara naratif heuristik yang telah Anda identifikasi. Contoh poin yang perlu dijelaskan:
            * Bagaimana sistem memutuskan antara dua atau lebih kemungkinan segmentasi yang valid (misalnya, "Apakah ada prioritas antara hasil strategi S1 dan S2?").
            * Bagaimana keberadaan kata dasar dalam `kata_dasar.txt` mempengaruhi pilihan segmentasi.
            * Bagaimana urutan pelepasan afiks (prefiks dulu atau sufiks dulu) secara implisit dapat mempengaruhi hasil pada kata-kata tertentu.
            * Jelaskan perilaku saat ini untuk contoh konkret "beruang" dan "mengetahui", mengacu pada isi kamus pengujian jika perlu (misalnya, "Jika 'uang' ada di kamus dan 'ruang' tidak, maka 'ber-uang' akan lebih diprioritaskan jika memenuhi syarat aturan").
    3.  **Update `README.md`:**
        * Tambahkan bagian singkat (mungkin dalam "Fitur Utama" atau "Cara Kerja") yang merangkum pendekatan V1.0 terhadap ambiguitas, mengarahkan pengguna ke `architecture.md` untuk detail lebih lanjut.
        * Contoh kalimat: "Untuk V1.0, `ModernKataKupas` menggunakan pendekatan heuristik berbasis kamus dan urutan aturan untuk menangani beberapa kasus ambiguitas dasar. Detail lebih lanjut dapat ditemukan dalam dokumentasi arsitektur kami."
* **Kriteria Selesai:**
    * Sub-bagian "Penanganan Ambiguitas Dasar (V1.0)" telah ditambahkan/diperbarui di `memory-bank/architecture.md` dengan penjelasan yang jelas dan akurat mengenai heuristik yang ada.
    * `README.md` memiliki rangkuman singkat tentang penanganan ambiguitas V1.0.
    * Tidak ada perubahan kode yang dilakukan untuk langkah ini, hanya dokumentasi.
* **File Terkait untuk Diperbarui:**
    * `memory-bank/architecture.md`
    * `README.md`
* **File Terkait untuk Referensi:**
    * `src/modern_kata_kupas/separator.py`
    * `tests/test_separator.py` (terutama `TestSpecificSegmentationCases`)
    * `src/modern_kata_kupas/data/kata_dasar.txt`

---

## Bagian 2: Pengujian Komprehensif dan Kasus Tepi (Terkait Langkah 4.3 Rencana Implementasi)

### Baby Step 4.3.1: Identifikasi & Tambah Kasus Uji Morfologi Kompleks

* **Tujuan:** Meningkatkan *robustness* dan cakupan pengujian dengan menambahkan kasus-kasus kata Bahasa Indonesia yang memiliki struktur morfologis yang kompleks.
* **Aktivitas:**
    1.  **Riset Kata Kompleks:**
        * Cari atau buat daftar 5-10 kata Bahasa Indonesia yang melibatkan:
            * Afiksasi berlapis-lapis (contoh: "mempertanggungjawabkan", "dipersemakmurkan").
            * Interaksi antara reduplikasi dan afiksasi (contoh: "memerah-merah", "berkejar-kejaran", "sebaik-baiknya").
            * Konfiks yang mungkin jarang atau rumit (contoh: "keberlangsungan", "kesetiakawanan").
            * Kombinasi prefiks dan sufiks pada kata serapan yang sudah di-Indonesiakan.
    2.  **Tentukan Segmentasi yang Diharapkan:** Untuk setiap kata yang diidentifikasi, tentukan secara manual hasil segmentasi yang paling akurat menurut kaidah morfologi Bahasa Indonesia dan kemampuan yang diharapkan dari V1.0 (berdasarkan aturan dan kamus yang ada).
    3.  **Tambahkan Tes ke `tests/test_separator.py`:**
        * Buat metode tes baru dalam kelas yang sesuai (misalnya, `TestComplexCases` atau tambahkan ke `TestAffixCombinations`) untuk setiap kata kompleks.
        * Contoh:
            ```python
            def test_segment_mempertanggungjawabkan(self):
                self.assertEqual(self.separator.segment("mempertanggungjawabkan"), "meN-per-tanggung_jawab-kan") # Sesuaikan dengan output yang diharapkan
            ```
    4.  **Tambahkan Tes Idempotensi ke `tests/test_reconstructor.py`:**
        * Untuk setiap kata kompleks yang berhasil disegmentasi, pastikan `Reconstructor` dapat merekonstruksinya kembali ke bentuk semula.
        * Contoh:
            ```python
            def test_reconstruct_mempertanggungjawabkan(self):
                original_word = "mempertanggungjawabkan"
                segmented_word = "meN-per-tanggung_jawab-kan" # Hasil dari separator
                reconstructed_word = self.reconstructor.reconstruct(segmented_word)
                self.assertEqual(reconstructed_word, original_word)
            ```
    5.  **Jalankan Semua Tes:** Pastikan semua tes, termasuk yang baru ditambahkan, berhasil (`pytest`). Jika ada kegagalan pada kasus baru, analisis apakah ini bug di kode atau ekspektasi yang salah (mungkin memerlukan penyesuaian di `data/affix_rules.json` atau `data/kata_dasar.txt` jika V1.0 diharapkan menanganinya, atau catat sebagai batasan V1.0 jika di luar cakupan).
* **Kriteria Selesai:**
    * Minimal 5 kasus uji baru untuk kata-kata morfologi kompleks telah ditambahkan ke `tests/test_separator.py`.
    * Tes idempotensi yang sesuai telah ditambahkan ke `tests/test_reconstructor.py` untuk kasus-kasus baru tersebut.
    * Semua tes dalam *suite* pengujian berhasil dijalankan.
* **File Terkait untuk Diperbarui:**
    * `tests/test_separator.py`
    * `tests/test_reconstructor.py`
* **File Terkait untuk Referensi:**
    * `src/modern_kata_kupas/separator.py`
    * `src/modern_kata_kupas/reconstructor.py`
    * `src/modern_kata_kupas/data/affix_rules.json`
    * `src/modern_kata_kupas/data/kata_dasar.txt`

### Baby Step 4.3.2: Tambah Kasus Uji Tepi (Edge Cases)

* **Tujuan:** Memastikan aplikasi berperilaku secara wajar dan tidak *crash* ketika menerima input yang tidak umum atau ekstrem (kasus tepi).
* **Aktivitas:**
    1.  **Identifikasi Kasus Tepi:** Pertimbangkan input seperti:
        * String kosong: `""`
        * String hanya spasi: `"   "`
        * String hanya tanda baca: `",.!?"`
        * String dengan angka: `"kata123"`
        * Kata yang sangat pendek yang bukan kata dasar (misalnya, "a", "b" jika tidak ada di kamus).
        * Kata yang sangat panjang (misalnya, string dengan 100 karakter tanpa spasi).
        * Kata dengan karakter non-standar (misalnya, emoji, jika normalizer belum menangani ini secara eksplisit).
    2.  **Tentukan Perilaku yang Diharapkan:** Untuk setiap kasus tepi, tentukan bagaimana `ModernKataKupas` V1.0 seharusnya merespons. Contoh:
        * String kosong/spasi: Harus mengembalikan string kosong atau representasi input yang telah dinormalisasi.
        * Hanya tanda baca: Seharusnya mengembalikan input apa adanya setelah normalisasi (misalnya, jika normalizer menghapus beberapa tanda baca).
        * Kata sangat panjang/non-standar: Mungkin dikembalikan apa adanya jika tidak ada aturan atau kata dasar yang cocok. Yang penting tidak *crash*.
    3.  **Tambahkan Tes ke `tests/test_separator.py`:**
        * Buat metode tes baru dalam kelas yang sesuai (misalnya, `TestEdgeCases`) untuk setiap kasus tepi.
        * Contoh:
            ```python
            def test_segment_empty_string(self):
                self.assertEqual(self.separator.segment(""), "")

            def test_segment_only_punctuation(self):
                self.assertEqual(self.separator.segment(",.!?"), ",.!?") # Atau sesuai output normalizer
            ```
    4.  **Jalankan Semua Tes:** Pastikan semua tes, termasuk yang baru, berhasil. Jika ada *crash*, perbaiki kode agar lebih tangguh. Jika perilakunya tidak sesuai ekspektasi tapi tidak *crash*, dokumentasikan perilaku tersebut jika dianggap bisa diterima untuk V1.0, atau perbaiki jika dianggap bug.
* **Kriteria Selesai:**
    * Minimal 5 kasus uji baru untuk kasus tepi telah ditambahkan ke `tests/test_separator.py`.
    * Aplikasi tidak *crash* pada input kasus tepi tersebut.
    * Semua tes dalam *suite* pengujian berhasil dijalankan.
* **File Terkait untuk Diperbarui:**
    * `tests/test_separator.py`
* **File Terkait untuk Referensi:**
    * `src/modern_kata_kupas/separator.py`
    * `src/modern_kata_kupas/normalizer.py`

---

## Bagian 3: Finalisasi API dan Dokumentasi (Terkait Langkah 4.4 Rencana Implementasi)

### Baby Step 4.4.1: Review Final API Publik & Docstrings Inti

* **Tujuan:** Memastikan bahwa API publik dari `ModernKataKupas` dan komponen intinya jelas, konsisten, mudah digunakan, dan terdokumentasi dengan baik melalui *docstrings*. Ini penting untuk pengguna *library*.
* **Aktivitas:**
    1.  **Identifikasi API Publik:** Fokus pada kelas dan metode yang akan digunakan langsung oleh pengguna *library*:
        * `modern_kata_kupas.ModernKataKupas` (terutama metode `segment()` dan `reconstruct()`).
        * Mungkin juga metode penting dari `DictionaryManager` atau `MorphologicalRules` jika ada kasus penggunaan di mana pengguna mungkin ingin mengaksesnya secara langsung (meskipun untuk V1.0, interaksi utama mungkin hanya melalui `ModernKataKupas`).
    2.  **Review Nama Metode dan Parameter:**
        * Apakah nama metode sudah intuitif dan mencerminkan fungsinya?
        * Apakah nama parameter sudah jelas?
        * Apakah tipe data input dan output konsisten dan terdokumentasi?
        * Apakah ada parameter opsional yang berguna? Apakah nilai *default*-nya sudah sesuai?
    3.  **Review dan Lengkapi Docstrings:**
        * Untuk setiap kelas publik dan metode publik:
            * Pastikan ada *docstring*.
            * Deskripsi singkat fungsi kelas/metode.
            * Penjelasan untuk setiap parameter (`Args:`).
            * Penjelasan untuk nilai kembalian (`Returns:`).
            * Contoh penggunaan sederhana (`Example:` atau `Examples:` jika relevan dan belum ada di `README.md`).
            * Jika metode dapat memunculkan *exception* spesifik, sebutkan (`Raises:`).
        * Gunakan format *docstring* yang konsisten (misalnya, Google Style atau NumPy/SciPy style, pilih salah satu dan terapkan).
* **Kriteria Selesai:**
    * Semua metode publik di kelas `ModernKataKupas` (dan kelas inti lainnya yang dianggap publik) telah direview nama dan parameternya.
    * *Docstrings* untuk kelas dan metode publik tersebut telah dilengkapi dengan deskripsi, argumen, nilai kembalian, dan contoh (jika perlu), sesuai dengan gaya yang konsisten.
* **File Terkait untuk Diperbarui:**
    * `src/modern_kata_kupas/separator.py` (untuk kelas `ModernKataKupas`)
    * `src/modern_kata_kupas/reconstructor.py`
    * `src/modern_kata_kupas/dictionary_manager.py` (jika ada API publik)
    * `src/modern_kata_kupas/rules.py` (jika ada API publik)
* **File Terkait untuk Referensi:**
    * Panduan gaya docstring (misalnya, [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings))

### Baby Step 4.4.2: Update Komprehensif `README.md`

* **Tujuan:** Menjadikan `README.md` sebagai panduan pengguna utama yang lengkap, akurat, dan mudah dipahami untuk `ModernKataKupas` V1.0.
* **Aktivitas:**
    1.  **Bagian Instalasi:**
        * Pastikan instruksi instalasi jelas dan akurat (akan difinalisasi setelah Baby Step 4.5.1 dan 4.5.2, tapi draf bisa disiapkan). Sertakan perintah `pip install modern_kata_kupas` (atau nama paket final).
        * Sebutkan dependensi utama jika ada (misalnya, PySastrawi, versi Python yang didukung).
    2.  **Bagian Penggunaan Dasar (`Usage`):**
        * Sediakan contoh kode yang jelas untuk mengimpor dan menggunakan `ModernKataKupas.segment()`.
        * Sediakan contoh kode yang jelas untuk `ModernKataKupas.reconstruct()`.
        * Gunakan contoh kata yang beragam (sederhana, dengan afiks, dengan reduplikasi, kata serapan) yang menunjukkan kemampuan sistem. Ambil dari `verify_segment_examples.py` atau tes yang ada. Pastikan output contoh di `README.md` sesuai dengan output aktual dari kode V1.0.
    3.  **Format Output:** Jelaskan dengan jelas format string output dari `segment()` (misalnya, penggunaan `_` untuk kata dasar majemuk, `-` untuk pemisah afiks dan bentuk ulang).
    4.  **Penjelasan Fitur Utama:** Rangkum fitur-fitur utama V1.0 (misalnya, penanganan berbagai jenis afiks, reduplikasi, kata serapan dasar, normalisasi).
    5.  **Penanganan Kata OOV (Out-Of-Vocabulary):** Jelaskan bagaimana sistem menangani kata yang tidak dikenali atau tidak dapat disegmentasi (misalnya, dikembalikan apa adanya).
    6.  **Batasan (Limitations):** Sebutkan secara jujur batasan V1.0 jika ada (misalnya, penanganan ambiguitas yang masih heuristik, belum mendukung semua variasi morfologis yang sangat kompleks).
    7.  **API Singkat (Opsional):** Jika dirasa perlu, berikan ringkasan singkat metode publik utama dan fungsinya (bisa merujuk ke *docstrings* untuk detail).
    8.  **Kontribusi:** Jika terbuka untuk kontribusi, tambahkan bagian singkat cara berkontribusi.
    9.  **Lisensi:** Pastikan lisensi proyek disebutkan.
    10. **Verifikasi Contoh:** Jalankan `verify_segment_examples.py` lagi setelah memperbarui contoh di `README.md` untuk memastikan konsistensi.
* **Kriteria Selesai:**
    * `README.md` telah diperbarui secara komprehensif mencakup semua poin di atas.
    * Contoh kode di `README.md` akurat dan sesuai dengan perilaku V1.0.
    * Informasi jelas, mudah dibaca, dan terstruktur dengan baik.
* **File Terkait untuk Diperbarui:**
    * `README.md`
* **File Terkait untuk Referensi:**
    * `verify_segment_examples.py`
    * `tests/test_separator.py` (untuk contoh kasus)

---

## Bagian 4: Pengemasan untuk Distribusi (Terkait Langkah 4.5 Rencana Implementasi)

### Baby Step 4.5.1: Finalisasi `setup.py` dan Build Paket Awal

* **Tujuan:** Mempersiapkan skrip `setup.py` agar dapat membangun paket Python yang siap didistribusikan dan diinstal melalui `pip`.
* **Aktivitas:**
    1.  **Review `setup.py`:**
        * Pastikan `name` paket sudah benar (misalnya, `modern_kata_kupas`).
        * Pastikan `version` sudah sesuai untuk V1.0 (misalnya, `1.0.0`).
        * Pastikan `author`, `author_email`, `description`, `long_description` (mungkin dari `README.md`), `url` (URL GitHub repositori) sudah diisi dengan benar.
        * Verifikasi `packages=find_packages(where='src')` dan `package_dir={'': 'src'}` jika struktur proyek Anda menggunakan direktori `src`.
        * **PENTING:** Pastikan `install_requires` mencantumkan semua dependensi eksternal yang dibutuhkan, misalnya `PySastrawi>=1.2.0,<2.0.0` (tentukan rentang versi yang sesuai).
        * **PENTING:** Pastikan `package_data` sudah benar dikonfigurasi untuk menyertakan semua file data non-kode yang dibutuhkan oleh paket saat runtime, seperti `data/kata_dasar.txt`, `data/loanwords.txt`, dan `data/affix_rules.json`. Contoh:
            ```python
            package_data={
                'modern_kata_kupas': ['data/*.txt', 'data/*.json'],
            },
            ```
        * Pastikan `python_requires` sudah diset (misalnya, `>=3.8`).
        * Tambahkan `classifiers` yang sesuai (misalnya, status pengembangan, lisensi, topik).
    2.  **Build Paket:**
        * Pastikan Anda memiliki `setuptools` dan `wheel` terinstal (`pip install setuptools wheel`).
        * Dari direktori root proyek (yang berisi `setup.py`), jalankan perintah:
            ```bash
            python setup.py sdist bdist_wheel
            ```
        * Ini akan membuat direktori `dist` yang berisi file `.tar.gz` (source distribution) dan `.whl` (wheel).
* **Kriteria Selesai:**
    * `setup.py` telah direview dan semua metadata serta konfigurasi (terutama `install_requires` dan `package_data`) sudah benar.
    * Perintah `python setup.py sdist bdist_wheel` berhasil dijalankan dan menghasilkan file paket di direktori `dist`.
* **File Terkait untuk Diperbarui:**
    * `setup.py`
* **File Terkait untuk Referensi:**
    * `requirements.txt` (untuk daftar dependensi)
    * [Python Packaging User Guide](https://packaging.python.org/tutorials/packaging-projects/)

### Baby Step 4.5.2: Uji Instalasi Paket Lokal

* **Tujuan:** Memverifikasi bahwa paket yang telah di-build pada langkah sebelumnya dapat diinstal dengan benar menggunakan `pip` di lingkungan yang bersih dan fungsionalitas dasarnya berjalan.
* **Aktivitas:**
    1.  **Buat Lingkungan Virtual Baru:**
        * Buat lingkungan virtual Python baru yang bersih (misalnya, menggunakan `venv` atau `conda`).
        * Aktifkan lingkungan virtual tersebut.
    2.  **Instal Paket:**
        * Dari dalam lingkungan virtual yang aktif, instal paket menggunakan file `.whl` yang ada di direktori `dist`. Contoh:
            ```bash
            pip install dist/modern_kata_kupas-1.0.0-py3-none-any.whl # Sesuaikan nama file
            ```
    3.  **Uji Impor dan Fungsi Dasar:**
        * Buka interpreter Python atau buat skrip Python sederhana di dalam lingkungan virtual tersebut.
        * Coba impor paket: `from modern_kata_kupas import ModernKataKupas`
        * Buat instance: `mk = ModernKataKupas()`
        * Jalankan beberapa contoh segmentasi sederhana:
            ```python
            print(mk.segment("makanan"))
            print(mk.segment("berlari-lari"))
            ```
        * Verifikasi outputnya sesuai harapan.
        * Pastikan tidak ada error impor terkait file data (ini akan menguji `package_data`).
* **Kriteria Selesai:**
    * Paket berhasil diinstal menggunakan `pip` di lingkungan virtual yang bersih.
    * Paket dapat diimpor dengan sukses.
    * Fungsionalitas dasar (membuat instance dan memanggil `segment()` dengan beberapa contoh) berjalan tanpa error dan menghasilkan output yang diharapkan.
    * Tidak ada error terkait file data yang hilang.
* **File Terkait untuk Diperbarui:** (Tidak ada perubahan file kode, hanya proses pengujian)
* **File Terkait untuk Referensi:** File `.whl` dari direktori `dist`.

---

## Bagian 5: Pembaruan Dokumentasi Arsitektur Final (Terkait Langkah 4.6 Rencana Implementasi)

### Baby Step 4.6.1: Update Detail Final `architecture.md`

* **Tujuan:** Memastikan dokumen `architecture.md` secara akurat dan komprehensif mencerminkan desain final V1.0 dari `ModernKataKupas`.
* **Aktivitas:**
    1.  **Review Keseluruhan Dokumen:** Baca kembali `memory-bank/architecture.md` secara menyeluruh.
    2.  **Deskripsi Komponen:**
        * Untuk setiap modul/kelas utama (misalnya, `Separator`, `Reconstructor`, `DictionaryManager`, `MorphologicalRules`, `Normalizer`):
            * Pastikan deskripsi tanggung jawabnya sudah akurat dan sesuai dengan implementasi final V1.0.
            * Jelaskan input utama yang diterima dan output utama yang dihasilkan.
    3.  **Interaksi Antar Komponen:**
        * Perbarui diagram alur (jika ada) atau deskripsi naratif mengenai bagaimana komponen-komponen utama berinteraksi selama proses segmentasi dan rekonstruksi. Pastikan ini mencerminkan alur kerja aktual dalam kode.
    4.  **Struktur File Data:**
        * Jelaskan secara lebih detail (jika belum) struktur dan tujuan dari setiap file data:
            * `data/kata_dasar.txt`: Formatnya (satu kata per baris), sumber utama, dan bagaimana digunakan.
            * `data/loanwords.txt`: Formatnya, bagaimana digunakan dalam penanganan kata serapan.
            * `data/affix_rules.json`: Struktur JSON-nya (misalnya, kunci utama, arti setiap field dalam aturan prefiks/sufiks seperti `allomorphs`, `conditions`, `elision_rules`, `canonical_form`). Ini penting jika orang lain ingin memahami atau memodifikasi aturan.
    5.  **Keputusan Desain Penting:** Pastikan keputusan desain penting yang diambil selama pengembangan dan mempengaruhi arsitektur V1.0 sudah terdokumentasi (misalnya, keputusan untuk tidak menggunakan alignment eksplisit di V1.0, penggunaan strategi S1/S2).
    6.  **Konsistensi:** Pastikan terminologi yang digunakan konsisten di seluruh dokumen dan dengan kode serta `README.md`.
* **Kriteria Selesai:**
    * `memory-bank/architecture.md` telah diperbarui untuk secara akurat mencerminkan arsitektur final V1.0.
    * Deskripsi komponen, interaksinya, dan struktur file data sudah jelas dan detail.
    * Dokumen konsisten dan mudah dipahami.
* **File Terkait untuk Diperbarui:**
    * `memory-bank/architecture.md`
* **File Terkait untuk Referensi:**
    * Seluruh codebase di `src/modern_kata_kupas/`
    * `README.md`

---

Dengan menyelesaikan "Baby Steps" yang lebih terperinci ini, diharapkan proses penyelesaian Fase 4 menjadi lebih lancar dan hasilnya lebih berkualitas, bahkan jika dikerjakan oleh junior developer.