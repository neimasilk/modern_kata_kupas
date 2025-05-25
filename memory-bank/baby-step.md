# Baby Steps Menuju Penyelesaian ModernKataKupas V1.0 (Lanjutan Fase 4)

Dokumen ini berisi langkah-langkah sangat detail (baby steps) untuk menyelesaikan Fase 4 dari proyek ModernKataKupas, dengan fokus pada packaging, pengujian instalasi, dan finalisasi dokumentasi. Langkah-langkah ini dirancang agar jelas dan dapat diikuti oleh junior developer.

**Asumsi Penting Sebelum Memulai:**
1.  **Tool File Editing Berfungsi:** Anda memiliki cara yang andal untuk menyimpan perubahan pada file di workspace Anda (misalnya, `setup.py`, `architecture.md`, dll.). Jika masih ada masalah dengan tool internal (`overwrite_file_with_block`), masalah tersebut harus diselesaikan terlebih dahulu.
2.  **Kode Telah Di-commit:** Semua perubahan kode terkait fungsionalitas inti V1.0 dan tes unit telah di-commit ke sistem kontrol versi Anda.
3.  **Lingkungan Pengembangan Siap:** `Python`, `pip`, `setuptools`, `wheel`, dan `virtualenv` (atau `venv`) telah terinstal dan berfungsi dengan baik di lingkungan pengembangan Anda.

---

## Tujuan Utama Fase 4 (Lanjutan):
* Menyiapkan paket distribusi ModernKataKupas V1.0.
* Memastikan paket dapat diinstal dan berfungsi dengan benar.
* Memfinalisasi semua dokumentasi proyek.

---

### Baby Step 4.5: Packaging dan Pengujian Instalasi Paket

#### Baby Step 4.5.1: Finalisasi `setup.py` dan Build Paket Awal

* **Tujuan:** Memastikan file `setup.py` sudah benar dan lengkap, kemudian membuat file distribusi paket.
* **Detail Langkah:**
    1.  **Buka file `setup.py`**: Lokasi: `setup.py` di root proyek.
    2.  **Verifikasi Konten `setup.py`**:
        * Pastikan `version='1.0.0'`.
        * Pastikan `name='modern_kata_kupas'`.
        * Pastikan `author` dan `author_email` sudah sesuai.
        * Pastikan `description` singkat dan jelas.
        * Pastikan `long_description` mengambil konten dari `README.md`.
        * Verifikasi `url` menunjuk ke repositori proyek yang benar.
        * Pastikan `packages=find_packages(where="src")` dan `package_dir={"": "src"}` sudah benar.
        * **Sangat Penting - `package_data`**: Pastikan entri `package_data` sudah benar dan mencakup semua file data yang dibutuhkan:
            ```python
            package_data={
                "modern_kata_kupas": ["data/kata_dasar.txt", "data/loanwords.txt", "data/affix_rules.json"],
            },
            ```
            Ini memastikan file-file tersebut disertakan saat paket diinstal. File-file ini berada di `src/modern_kata_kupas/data/`.
        * Verifikasi `install_requires` mencantumkan dependensi yang benar (misalnya, `PySastrawi`).
        * Pastikan `python_requires='>=3.8'` atau versi minimal yang didukung.
        * Periksa `classifiers` apakah sudah sesuai.
    3.  **Simpan file `setup.py`** jika ada perubahan.
    4.  **Buka Terminal atau Command Prompt**: Navigasi ke direktori root proyek ModernKataKupas.
    5.  **Hapus Direktori Build Lama (Jika Ada)**: Untuk memastikan build yang bersih, hapus direktori `build`, `dist`, dan `src/modern_kata_kupas.egg-info` jika sudah ada dari proses build sebelumnya.
        * Perintah (opsional, tergantung OS):
            * Linux/macOS: `rm -rf build dist src/modern_kata_kupas.egg-info`
            * Windows: `rd /s /q build dist src\modern_kata_kupas.egg-info`
    6.  **Jalankan Perintah Build Paket**:
        ```bash
        python setup.py sdist bdist_wheel
        ```
        * `sdist`: Membuat arsip source distribution (misalnya, `.tar.gz`).
        * `bdist_wheel`: Membuat distribusi wheel (format biner, lebih cepat diinstal, misalnya, `.whl`).
    7.  **Verifikasi Hasil Build**:
        * Pastikan tidak ada error selama proses build.
        * Cek apakah direktori `dist` telah dibuat di root proyek.
        * Di dalam direktori `dist`, pastikan ada dua file:
            * Satu file `.tar.gz` (misalnya, `modern_kata_kupas-1.0.0.tar.gz`).
            * Satu file `.whl` (misalnya, `modern_kata_kupas-1.0.0-py3-none-any.whl`). Nama file wheel bisa sedikit berbeda tergantung platform jika ada ekstensi C, tapi untuk proyek Python murni, biasanya `py3-none-any`).
* **Kriteria Selesai Baby Step 4.5.1**:
    * File `setup.py` telah diverifikasi dan kontennya sudah final untuk V1.0.
    * Perintah build paket berjalan sukses tanpa error.
    * Direktori `dist` berisi file `.tar.gz` dan `.whl` untuk versi 1.0.0.

#### Baby Step 4.5.1.A: Verifikasi Isi `package_data` dalam Arsip Distribusi

* **Tujuan:** Memastikan bahwa file-file data (`kata_dasar.txt`, `loanwords.txt`, `affix_rules.json`) benar-benar disertakan dalam arsip source distribution (`.tar.gz`). Ini adalah langkah verifikasi krusial.
* **Detail Langkah:**
    1.  **Navigasi ke direktori `dist`**: Buka terminal atau file explorer dan masuk ke direktori `dist` yang baru saja dibuat.
    2.  **Ekstrak File `.tar.gz`**: Ekstrak file `modern_kata_kupas-1.0.0.tar.gz` ke direktori sementara.
        * Contoh perintah di Linux/macOS:
            ```bash
            mkdir temp_sdist_check
            tar -xzvf modern_kata_kupas-1.0.0.tar.gz -C temp_sdist_check
            ```
        * Di Windows, Anda bisa menggunakan 7-Zip atau alat arsip lainnya.
    3.  **Periksa Struktur Direktori Hasil Ekstraksi**:
        * Masuk ke direktori hasil ekstraksi (misalnya, `temp_sdist_check/modern_kata_kupas-1.0.0/`).
        * Navigasi ke `src/modern_kata_kupas/data/`.
        * Pastikan ketiga file ini ada di sana: `kata_dasar.txt`, `loanwords.txt`, dan `affix_rules.json`.
    4.  **Bersihkan Direktori Sementara**: Setelah selesai memeriksa, hapus direktori sementara yang Anda buat (misalnya, `temp_sdist_check`).
* **Kriteria Selesai Baby Step 4.5.1.A**:
    * File `.tar.gz` telah diekstrak dan isinya diperiksa.
    * File `kata_dasar.txt`, `loanwords.txt`, dan `affix_rules.json` terkonfirmasi ada di dalam struktur direktori yang benar (`src/modern_kata_kupas/data/`) dalam arsip source distribution.

#### Baby Step 4.5.2: Uji Instalasi Paket Lokal di Lingkungan Virtual Bersih

* **Tujuan:** Memastikan paket yang telah di-build dapat diinstal dengan benar di lingkungan Python yang bersih dan fungsionalitas dasarnya berjalan.
* **Detail Langkah:**
    1.  **Buka Terminal atau Command Prompt Baru**.
    2.  **Buat Direktori Tes Sementara (Opsional, tapi direkomendasikan)**:
        * Buat direktori di luar direktori proyek Anda, misalnya `mkk_install_test`.
        * Navigasi ke direktori `mkk_install_test` tersebut.
    3.  **Buat Lingkungan Virtual Baru**:
        ```bash
        python -m venv .venv_mkk_test
        ```
    4.  **Aktifkan Lingkungan Virtual**:
        * Linux/macOS: `source .venv_mkk_test/bin/activate`
        * Windows: `.\.venv_mkk_test\Scripts\activate`
        * Prompt terminal Anda seharusnya berubah, menandakan lingkungan virtual aktif.
    5.  **Instal Paket Menggunakan File `.whl`**:
        * Gunakan path absolut atau relatif ke file `.whl` yang ada di direktori `dist` proyek ModernKataKupas Anda.
        * Contoh (jika Anda berada di `mkk_install_test` dan proyek Anda ada di `../modern_kata_kupas_project`):
            ```bash
            pip install ../modern_kata_kupas_project/dist/modern_kata_kupas-1.0.0-py3-none-any.whl
            ```
            (Sesuaikan nama file `.whl` jika berbeda).
    6.  **Verifikasi Instalasi**:
        * Jalankan `pip list`. Pastikan `modern-kata-kupas` (atau `modern_kata_kupas`, tergantung normalisasi nama oleh pip) muncul dalam daftar paket yang terinstal dengan versi 1.0.0.
    7.  **Uji Fungsionalitas Dasar (Smoke Test)**:
        * Buka interpreter Python: `python`
        * Di dalam interpreter Python, jalankan perintah berikut:
            ```python
            from modern_kata_kupas import ModernKataKupas
            from modern_kata_kupas.exceptions import WordNotInDictionaryError

            try:
                mkk = ModernKataKupas() # Ini akan mencoba memuat file data
                print("Objek ModernKataKupas berhasil dibuat.")

                test_word = "makanan"
                segmented_word = mkk.segment(test_word)
                print(f"Segmentasi '{test_word}': {segmented_word}")

                reconstructed_word = mkk.reconstruct(segmented_word)
                print(f"Rekonstruksi '{segmented_word}': {reconstructed_word}")

                if reconstructed_word == test_word:
                    print("Tes segmentasi dan rekonstruksi dasar BERHASIL.")
                else:
                    print("Tes segmentasi dan rekonstruksi dasar GAGAL.")

            except Exception as e:
                print(f"Terjadi error saat pengujian: {e}")
            finally:
                exit() # Keluar dari interpreter Python
            ```
    8.  **Deaktivasi Lingkungan Virtual**:
        ```bash
        deactivate
        ```
    9.  **Bersihkan (Opsional)**: Anda dapat menghapus direktori tes sementara (`mkk_install_test`) jika diinginkan.
* **Kriteria Selesai Baby Step 4.5.2**:
    * Lingkungan virtual baru berhasil dibuat dan diaktifkan.
    * Paket `modern_kata_kupas` berhasil diinstal dari file `.whl` lokal.
    * `pip list` menunjukkan paket terinstal dengan versi yang benar.
    * Smoke test di interpreter Python (membuat objek `ModernKataKupas`, melakukan segmentasi dan rekonstruksi dasar) berjalan tanpa error dan menunjukkan bahwa file data berhasil dimuat oleh paket yang terinstal.
    * Lingkungan virtual berhasil dideaktivasi.

---

### Baby Step 4.6: Finalisasi Dokumentasi

#### Baby Step 4.6.1: Update Detail Final `architecture.md`

* **Tujuan:** Memastikan dokumen arsitektur mencerminkan status final V1.0, termasuk bagaimana file data dipaketkan dan diakses.
* **Detail Langkah:**
    1.  **Buka file `memory-bank/architecture.md`**.
    2.  **Review Seluruh Konten**: Baca kembali seluruh dokumen untuk memastikan konsistensi dan akurasi dengan kode V1.0.
    3.  **Tambahkan/Update Informasi Packaging**:
        * Jelaskan secara singkat bagaimana file data (`kata_dasar.txt`, `loanwords.txt`, `affix_rules.json`) disertakan dalam paket menggunakan `package_data` di `setup.py`.
        * Jelaskan bagaimana `DictionaryManager` dan `Rules` memuat file-file ini menggunakan `pkgutil.get_data` atau mekanisme serupa untuk mengakses data dari dalam paket yang terinstal.
    4.  **Review Diagram Arsitektur (Jika Ada)**: Pastikan diagram masih relevan.
    5.  **Review Penjelasan Komponen**: Pastikan deskripsi setiap komponen (`Separator`, `Reconstructor`, `DictionaryManager`, `Normalizer`, `Rules`) sesuai dengan implementasi final.
    6.  **Review Penjelasan Alur Kerja (Workflow)**: Pastikan alur kerja segmentasi dan rekonstruksi dijelaskan dengan akurat.
    7.  **Verifikasi Penjelasan Penanganan Ambiguitas**: Pastikan strategi S1/S2 dan batasan V1.0 terkait ambiguitas (seperti kasus `berkejar-kejaran`) dijelaskan dengan jelas.
    8.  **Simpan file `architecture.md`**.
* **Kriteria Selesai Baby Step 4.6.1**:
    * File `architecture.md` telah direview secara menyeluruh.
    * Informasi mengenai packaging dan cara akses file data dari dalam paket telah ditambahkan/diperbarui.
    * Semua bagian dokumen konsisten dengan implementasi V1.0.

#### Baby Step 4.6.2: Final Review `README.md` dan Verifikasi Contoh

* **Tujuan:** Memastikan `README.md` akurat, terutama bagian instalasi dan penggunaan, serta semua contoh kode berfungsi.
* **Detail Langkah:**
    1.  **Buka file `README.md`**.
    2.  **Review Bagian Instalasi**:
        * Pastikan instruksi instalasi dari PyPI (jika direncanakan akan dirilis) atau dari source/wheel sudah jelas dan akurat. Untuk saat ini, fokus pada instalasi dari wheel lokal yang telah diuji.
        * Contoh: `pip install modern_kata_kupas` (jika sudah rilis) atau `pip install path/to/your/modern_kata_kupas-1.0.0-py3-none-any.whl`.
    3.  **Review Bagian Penggunaan (Usage)**:
        * Pastikan contoh kode untuk segmentasi dan rekonstruksi sederhana dan mudah dimengerti.
        * Pastikan contoh penggunaan `ModernKataKupas()` dengan parameter custom (misalnya, path kamus custom) juga jelas, jika fitur tersebut didukung dan didokumentasikan. (Untuk V1.0, fokus pada penggunaan default).
    4.  **Review Bagian Fitur, Batasan, dan Penanganan Ambiguitas**: Pastikan konsisten dengan implementasi V1.0 dan `architecture.md`.
    5.  **Jalankan Skrip Verifikasi Contoh (Jika Ada)**:
        * Jika Anda memiliki skrip seperti `verify_segment_examples.py`, jalankan untuk memastikan semua contoh di `README.md` masih menghasilkan output yang diharapkan dengan versi kode saat ini.
        * Perintah: `python verify_segment_examples.py` (asumsi skrip ini menggunakan paket yang sudah terinstal di lingkungan aktif, atau mengimpor dari source code lokal dengan benar). Idealnya, jalankan ini di lingkungan virtual tempat paket diinstal.
    6.  **Periksa Semua Tautan (Links)**: Pastikan semua tautan internal dan eksternal masih valid.
    7.  **Simpan file `README.md`**.
* **Kriteria Selesai Baby Step 4.6.2**:
    * File `README.md` telah direview secara menyeluruh.
    * Bagian instalasi dan penggunaan akurat dan teruji (setidaknya untuk instalasi lokal).
    * Semua contoh kode di `README.md` (termasuk yang diverifikasi oleh skrip) berfungsi dengan benar.

---

### Baby Step 4.7: Finalisasi dan Persiapan Rilis V1.0 (Opsional, tergantung keputusan rilis)

#### Baby Step 4.7.1: Update Dokumen Status dan Progress

* **Tujuan:** Memastikan semua dokumen pelacakan proyek sudah mutakhir.
* **Detail Langkah:**
    1.  **Buka file `memory-bank/status-todolist-saran.md`**.
    2.  Update status pencapaian dengan semua Baby Steps Fase 4 yang telah selesai.
    3.  Hapus atau arsipkan bagian "MASALAH KRITIS" jika sudah teratasi.
    4.  Perbarui "Saran Langkah Selanjutnya" jika ada rencana untuk Fase berikutnya atau perbaikan V1.0.x.
    5.  **Simpan file `status-todolist-saran.md`**.
    6.  **Buka file `memory-bank/progress.md`**.
    7.  Catat penyelesaian Fase 4 dan tanggalnya.
    8.  **Simpan file `progress.md`**.
* **Kriteria Selesai Baby Step 4.7.1**:
    * File `status-todolist-saran.md` dan `progress.md` telah diperbarui untuk mencerminkan penyelesaian Fase 4 (atau langkah-langkah packaging dan dokumentasi).

#### Baby Step 4.7.2: Verifikasi Akhir Semua Tes

* **Tujuan:** Memastikan semua tes unit masih lolos setelah semua perubahan dokumentasi dan packaging.
* **Detail Langkah:**
    1.  **Buka Terminal atau Command Prompt**: Navigasi ke direktori root proyek ModernKataKupas.
    2.  **Aktifkan Lingkungan Virtual Utama Pengembangan Anda** (bukan yang untuk tes instalasi, tetapi yang memiliki semua dev dependencies seperti `pytest`).
    3.  **Jalankan Semua Tes Unit**:
        ```bash
        pytest
        ```
    4.  **Verifikasi Hasil Tes**: Pastikan semua tes lolos, kecuali satu kegagalan yang diterima untuk `berkejar-kejaran` (jika belum ada solusi).
* **Kriteria Selesai Baby Step 4.7.2**:
    * `pytest` berjalan sukses dan semua tes yang diharapkan lolos telah terkonfirmasi.

#### Baby Step 4.7.3: Tagging Versi di Git (Sangat Direkomendasikan)

* **Tujuan:** Memberi penanda (tag) pada commit spesifik ini sebagai rilis V1.0.0.
* **Detail Langkah:**
    1.  **Pastikan Semua Perubahan Sudah Di-commit**: Jalankan `git status` untuk memastikan tidak ada perubahan yang belum di-commit. Commit semua file yang telah diubah (misalnya, `setup.py`, `README.md`, `architecture.md`, `status-todolist-saran.md`, `progress.md`).
    2.  **Buat Tag Git**:
        ```bash
        git tag -a v1.0.0 -m "Version 1.0.0 Release"
        ```
        * `-a v1.0.0`: Membuat annotated tag bernama `v1.0.0`.
        * `-m "Version 1.0.0 Release"`: Pesan untuk tag tersebut.
    3.  **Push Tag ke Remote Repository (Jika Menggunakan Remote)**:
        ```bash
        git push origin v1.0.0
        ```
        Atau untuk push semua tag: `git push --tags`
* **Kriteria Selesai Baby Step 4.7.3**:
    * Semua perubahan telah di-commit.
    * Tag `v1.0.0` telah dibuat secara lokal.
    * (Jika berlaku) Tag telah di-push ke remote repository.

---

Setelah semua baby steps ini selesai, ModernKataKupas V1.0 siap untuk didistribusikan atau digunakan secara internal sebagai versi stabil. Jika ada rencana untuk merilis ke PyPI, akan ada langkah-langkah tambahan terkait pendaftaran akun PyPI, pembuatan token API, dan penggunaan `twine` untuk mengunggah paket.