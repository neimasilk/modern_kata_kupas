## Status Proyek ModernKataKupas (per 25 Mei 2025)

**Pencapaian Utama Terbaru:**

* Penyelesaian Fase 0, 1, 2, dan 3 dari Rencana Implementasi.
* Implementasi Langkah 4.1: Penanganan Afiksasi Kata Serapan.
* Penyelesaian "Baby Steps" yang sebelumnya diidentifikasi (Koreksi Rekonstruktor, Konsolidasi Normalisasi & Path Data, Pembaruan Awal README, Perencanaan Ambiguitas Dasar).
* Penyelesaian semua 'Baby Steps' (1-7) yang diidentifikasi per 26 Mei 2025, termasuk pembaruan dokumentasi alignment, pembersihan kode, penyempurnaan docstring, verifikasi README, perencanaan ekspansi kamus, dan penambahan tes ambiguitas dasar.
* Semua tes `pytest` yang ada (72 tes) berhasil dijalankan, menunjukkan stabilitas fungsionalitas yang telah diimplementasikan.

**Status Implementasi Fungsionalitas Inti:**

* **Manajemen Data (`DictionaryManager`, `TextNormalizer`, `IndonesianStemmer`):** Berfungsi baik, memuat kamus dasar, kata serapan, melakukan normalisasi, dan menyediakan interface ke PySastrawi.
* **Aturan Morfologis (`MorphologicalRules`):** Mampu memuat dan mengelola aturan afiks dari JSON, mendukung identifikasi prefiks dan sufiks.
* **Logika Pemisahan (`Separator.ModernKataKupas`):**
    * Mengorkestrasi proses normalisasi, penanganan reduplikasi, dan pemisahan afiks menggunakan strategi S1 & S2.
    * Mendeteksi berbagai jenis reduplikasi (Dwilingga, Dwilingga Salin Suara, Dwipurwa).
    * Menangani pelepasan afiks berlapis dan perubahan morfofonemik.
    * Mencoba memisahkan afiks Indonesia dari kata serapan.
* **Logika Rekonstruksi (`Reconstructor`):** Mampu membangun kembali kata dari segmen, termasuk morfofonemik dan reduplikasi.
* **Utilitas & Error Handling:** Utilitas dasar dan *custom exceptions* telah tersedia.

---

## Langkah Selanjutnya (Fase 4 - Rencana Implementasi)

Berdasarkan `ModernKataKupas_ImplementationPlan_v1.md` dan `progress.md`:

1.  **Langkah 4.2: Implementasi Penanganan Ambiguitas Dasar & Pengujian (Target V1.0)**
    * **Tindakan:**
        * Formalisasi dan dokumentasikan mekanisme penanganan ambiguitas yang sudah ada untuk V1.0 (sesuai rencana Baby Step 4 sebelumnya):
            * **"Pencocokan kata dasar terpanjang yang valid":** Terdapat dalam logika pemilihan antara hasil strategi S1 dan S2 di `ModernKataKupas.segment()`.
            * **"Preseden aturan yang telah ditentukan":** Implisit dalam urutan pemrosesan afiks (partikel -> posesif -> derivasional untuk sufiks; prefiks terpanjang dulu; urutan alomorf dalam `affix_rules.json`).
        * Validasi perilaku sistem saat ini terhadap kasus-kasus ambigu yang telah diidentifikasi (misalnya, "beruang", "mengetahui", "bukunya~lah") menggunakan tes unit.
        * Perbarui dokumentasi (`README.md` atau `architecture.md`) untuk menjelaskan bagaimana ambiguitas dasar ini ditangani di V1.0.

2.  **Langkah 4.3: Pengujian Komprehensif dan Kasus Tepi Lanjutan**
    * **Tindakan:**
        * Perluas *test suite* `pytest` untuk mencakup lebih banyak kasus kompleks, kasus tepi (misalnya, *string* kosong setelah normalisasi, kata non-Indonesia, kata yang sangat panjang), dan contoh-contoh problematik dari literatur linguistik atau umpan balik.
        * Upayakan cakupan tes kode yang tinggi (misalnya, >90%).
        * Tinjau kembali kasus-kasus `segment()` yang outputnya sempat berbeda dari ekspektasi awal di `README.md` (misalnya, "dibaca", "mempertaruhkan") dan pastikan perilaku saat ini sudah sesuai dan didokumentasikan, atau identifikasi sebagai target perbaikan jika masih ada masalah. (Catatan: Saat ini, contoh-contoh tersebut tampaknya sudah sesuai dengan ekspektasi yang benar).

3.  **Langkah 4.4: Finalisasi API dan Dokumentasi Lengkap**
    * **Tindakan:**
        * Finalisasi API publik dari kelas `ModernKataKupas`.
        * Tulis/lengkapi *docstrings* yang komprehensif untuk semua kelas dan metode publik.
        * Lakukan review menyeluruh dan pembaruan komprehensif pada `README.md` (instruksi instalasi, contoh penggunaan yang lengkap dan akurat, gambaran umum algoritma).
        * Pertimbangkan untuk membuat dokumentasi HTML menggunakan Sphinx.

4.  **Langkah 4.5: Pengemasan untuk Distribusi**
    * **Tindakan:**
        * Finalisasi `setup.py` (pastikan `package_data` sudah benar dan dependensi di `install_requires` jika ada sudah dicantumkan).
        * Buat distribusi sumber (*source distribution*) dan *wheel*.
        * Uji instalasi menggunakan `pip` dari paket yang dibangun dan jalankan beberapa tes dasar.

5.  **Langkah 4.6: Perbarui `architecture.md`**
    * **Tindakan:** Dokumentasikan arsitektur perangkat lunak final, tujuan setiap *file/module* Python, struktur *file data*, dan interaksi kelas utama dalam `memory-bank/architecture.md`.

---

## Saran Perbaikan dan "Baby Steps" To-Do List Berikutnya

Semua "Baby Steps" yang sebelumnya teridentifikasi (1-6) telah berhasil diselesaikan atau digantikan oleh pekerjaan yang lebih detail dalam sesi perencanaan dan implementasi ini. Fokus selanjutnya adalah menyelesaikan Fase 4 dari rencana implementasi.

1.  **[SARAN MASA DEPAN] Perencanaan Perluasan Kamus (`kata_dasar.txt`, `loanwords.txt`)**
    *   **Tujuan:** Meningkatkan cakupan dan akurasi segmentasi `modern_kata_kupas` dengan kamus kata dasar dan kata serapan yang lebih komprehensif dan mutakhir.
    *   **Sumber Potensial:**
        *   `kata_dasar.txt`:
            *   Kamus Besar Bahasa Indonesia (KBBI): Versi terbaru sebagai sumber utama.
            *   Korpus Kontemporer: Ekstraksi daftar frekuensi kata dari korpus besar Bahasa Indonesia (misalnya, OSCAR, Common Crawl yang sudah dibersihkan) dan validasi sebagai kata dasar.
            *   Sumber Linguistik Lain: Daftar kata dari penelitian linguistik, alat NLP Bahasa Indonesia lain, atau basis data leksikal publik.
            *   Masukan Pengguna: Kata-kata yang diidentifikasi oleh pengguna sebagai hilang atau salah ditangani.
        *   `loanwords.txt`:
            *   Daftar Kata Serapan Ada: Kompilasi dari daftar publik (studi linguistik, Wikipedia, sumber edukasi).
            *   Domain Teknis: Terminologi dari bidang teknis spesifik (IT, medis, teknik, dll.).
            *   Media Sosial & Berita: Analisis teks dari media sosial, artikel berita, dan forum untuk mengidentifikasi kata serapan yang sering digunakan (terutama Bahasa Inggris).
            *   Kamus Kata Serapan: Kamus khusus yang fokus pada kata serapan dalam Bahasa Indonesia, jika tersedia.
    *   **Pertimbangan Proses:**
        *   **Format Konsisten:** Pertahankan format saat ini (teks, satu kata per baris, encoding UTF-8).
        *   **Pembersihan & Normalisasi Data:**
            *   Duplikasi: Penghapusan duplikat yang robust.
            *   Pengurangan Noise: Filter untuk kesalahan, typo, nama diri (kecuali dimaksudkan), dan kata non-Indonesia (untuk `kata_dasar.txt`).
            *   Normalisasi: Semua kandidat kata dinormalisasi (misalnya, huruf kecil, strip tanda baca dasar) menggunakan `TextNormalizer` library sebelum ditambah atau dicek.
        *   **Strategi Validasi:**
            *   Referensi Silang: Validasi kata dasar baru dengan mengecek keberadaannya di berbagai sumber (misalnya, KBBI dan korpus frekuensi tinggi).
            *   Analisis Frekuensi: Gunakan frekuensi kata dari korpus untuk prioritas dan identifikasi kandidat frekuensi rendah yang berpotensi salah.
            *   Tinjauan Manual: Untuk kasus ambigu, kata yang bisa jadi bentuk berimbuhan, atau kata serapan dengan ejaan yang bervariasi.
            *   Cek Stemmer (untuk `kata_dasar.txt`): Pastikan kata yang ditambahkan adalah bentuk dasar sejati.
            *   Cek Afiks (untuk `kata_dasar.txt`): Kata dasar potensial seharusnya tidak dapat disegmentasi menjadi akar + afiks yang diketahui, kecuali jika itu memang akar sejati yang bentuknya kebetulan sama.
        *   **Potensi Otomatisasi:** Kembangkan skrip Python untuk:
            *   Parsing berbagai format input.
            *   Melakukan filtering awal.
            *   Cek duplikasi terhadap file kamus yang ada.
            *   Menerapkan normalisasi.
            *   Menghasilkan daftar kandidat untuk tinjauan.
        *   **Prioritas Penambahan:**
            *   Frekuensi: Prioritaskan kata frekuensi tinggi dari korpus kontemporer dan kata serapan yang umum digunakan.
            *   Cakupan KBBI: Upayakan cakupan komprehensif entri KBBI untuk `kata_dasar.txt`.
            *   Kebutuhan Domain: Untuk `loanwords.txt`, prioritaskan istilah yang relevan dengan domain aplikasi NLP tertentu.
            *   Pengurangan Kesalahan: Prioritaskan kata-kata yang ketiadaannya diketahui menyebabkan kesalahan segmentasi umum.
    *   **Integrasi ke Paket `modern_kata_kupas`:**
        *   Versioning File Data: Pertimbangkan sistem versioning sederhana untuk file kamus (misalnya, header komentar dengan versi dan tanggal).
        *   Proses Pembaruan: Tinjau dan gabungkan kata-kata baru secara berkala. Pembaruan file kamus default akan menjadi bagian dari rilis library baru. Dokumentasikan cara pengguna menggunakan file kamus kustom.
        *   Pengujian: Setelah pembaruan kamus, jalankan kembali semua tes relevan untuk memastikan penambahan meningkatkan performa.

**Prioritas Berikutnya (Melanjutkan Fase 4):**

1.  **Implementasi Penuh Langkah 4.2: Penanganan Ambiguitas Dasar & Pengujian (Target V1.0)**
    *   Tindakan: Validasi dan dokumentasi formal mekanisme penanganan ambiguitas yang ada (pencocokan kata dasar terpanjang, preseden aturan). Perbarui dokumentasi (`README.md` atau `architecture.md`). (Sebagian telah dimulai di Baby Step 6, perlu finalisasi).
2.  **Lanjutkan Langkah 4.3: Pengujian Komprehensif dan Kasus Tepi Lanjutan**
    *   Tindakan: Perluas *test suite* `pytest` (kasus kompleks, kasus tepi, contoh problematik). Upayakan cakupan tes >90%. Tinjau kembali kasus `segment()` yang outputnya sempat berbeda.
3.  **Lanjutkan Langkah 4.4: Finalisasi API dan Dokumentasi Lengkap**
    *   Tindakan: Finalisasi API publik `ModernKataKupas`. Lengkapi *docstrings*. Review dan pembaruan komprehensif `README.md`. Pertimbangkan dokumentasi HTML (Sphinx).
4.  **Lanjutkan Langkah 4.5: Pengemasan untuk Distribusi**
    *   Tindakan: Finalisasi `setup.py`. Buat distribusi sumber dan *wheel*. Uji instalasi.
5.  **Lanjutkan Langkah 4.6: Perbarui `architecture.md`**
    *   Tindakan: Dokumentasikan arsitektur final, tujuan modul, struktur data, dan interaksi kelas. (Sebagian telah diperbarui di Baby Step 1 dan 6, perlu finalisasi).