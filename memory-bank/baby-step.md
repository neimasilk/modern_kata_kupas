# Baby Steps To-Do List untuk ModernKataKupas (V1.0 Sprint Berikutnya)

Daftar ini berisi tugas-tugas kecil dan konkret yang perlu diselesaikan untuk memajukan proyek ModernKataKupas menuju rilis V1.0, berdasarkan ulasan kode dan status per 25 Mei 2025.

## 1. Utilitas Penyelarasan String (`utils.alignment.py`)

**Keputusan (25 Mei 2025):** Untuk V1.0, integrasi penuh `utils.alignment.py` ke dalam logika inti `Separator.py` akan **ditunda**. Pendekatan saat ini yang menggunakan `startswith`/`endswith` dan aturan morfofonemik dinilai memadai untuk V1.0, dengan pertimbangan alignment akan dieksplorasi pada versi mendatang.

* **Baby Step 1: Pembaruan Dokumentasi Terkait Keputusan Alignment**
    * **Tujuan:** Memastikan semua dokumentasi proyek konsisten dengan keputusan untuk tidak mengintegrasikan alignment eksplisit di V1.0.
    * **Aktivitas:**
        1.  Identifikasi semua dokumen yang menyebutkan penggunaan alignment untuk pemisahan afiks inti (PRD FR3.3, Rencana Implementasi Langkah 0.5 & 2.1, Draf Paper Bab 3.3.4, `architecture.md`).
        2.  Perbarui bagian-bagian relevan untuk mencerminkan bahwa alignment eksplisit tidak digunakan dalam proses segmentasi inti V1.0. Jelaskan secara singkat justifikasinya (misalnya, "Untuk V1.0, pendekatan heuristik berbasis aturan dan pemotongan langsung dinilai memadai berdasarkan pengujian awal. Pertimbangan integrasi alignment string untuk peningkatan lebih lanjut pada kasus kompleks akan dieksplorasi pada versi mendatang.").
        3.  Pastikan `utils/alignment.py` dan tesnya (`tests/utils/test_alignment.py`) tetap ada di codebase sebagai utilitas yang mungkin berguna di masa depan atau untuk analisis lain, tetapi tidak dipanggil oleh `Separator.py`.
    * **Status:** `TODO`

## 2. Refinement Kode dan Dokumentasi

* **Baby Step 2: Pembersihan Kode dari Pernyataan Debug**
    * **Tujuan:** Kode produksi bersih dari `print()` yang tidak perlu.
    * **Aktivitas:** Cari semua `print()` di `src/modern_kata_kupas`, hapus atau ganti dengan logging.
    * **File Terkait:** `separator.py`, `reconstructor.py`, dan file lain di `src`.
    * **Status:** `TODO`

* **Baby Step 3: Penyempurnaan Docstrings**
    * **Tujuan:** Meningkatkan kejelasan dokumentasi internal kode.
    * **Aktivitas:** Tinjau dan lengkapi *docstrings* (ringkasan, parameter, nilai kembalian, exceptions) di modul utama.
    * **File Terkait:** `separator.py`, `reconstructor.py`, `rules.py`, `dictionary_manager.py`, `normalizer.py`.
    * **Status:** `TODO`

* **Baby Step 4: Verifikasi dan Sinkronisasi `README.md`**
    * **Tujuan:** Memastikan `README.md` akurat dan sinkron dengan kode V1.0.
    * **Aktivitas:** Jalankan `verify_segment_examples.py`, analisis perbedaan, perbarui `README.md` atau kode jika perlu, tinjau manual.
    * **File Terkait:** `README.md`, `verify_segment_examples.py`.
    * **Status:** `TODO`

## 3. Pengembangan Kamus

* **Baby Step 5: Perencanaan Perluasan Kamus**
    * **Tujuan:** Membuat strategi awal untuk memperluas `kata_dasar.txt` dan `loanwords.txt`.
    * **Aktivitas:** Identifikasi sumber data, pertimbangkan format dan pembersihan, evaluasi otomatisasi (opsional), prioritaskan untuk rilis. (PRD FR3.1 adalah target penting).
    * **File Terkait:** `src/modern_kata_kupas/data/kata_dasar.txt`, `src/modern_kata_kupas/data/loanwords.txt`.
    * **Status:** `TODO`

## 4. Penyelesaian Langkah 4.2 (Penanganan Ambiguitas Dasar)

* **Baby Step 6: Pengujian Spesifik untuk Kasus Ambiguitas**
    * **Tujuan:** Memvalidasi dan mendokumentasikan penanganan kasus ambiguitas di V1.0.
    * **Aktivitas:** Identifikasi kata ambigu, buat *test case* di `test_separator.py` berdasarkan heuristik saat ini, dokumentasikan perilaku V1.0.
    * **File Terkait:** `test_separator.py`, `README.md` atau `architecture.md`.
    * **Status:** `TODO`

---
Penanggung Jawab Utama untuk Baby Steps ini: [Nama PIC/Tim]
Target Penyelesaian Sprint: [Tanggal Target Sprint]