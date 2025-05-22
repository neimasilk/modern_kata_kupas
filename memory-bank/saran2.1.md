Berdasarkan analisis kode dan dokumen perencanaan, implementasi Step 2.1 untuk *prefix stripping* `meN-` dan `peN-` **belum sepenuhnya layak atau selesai** pada tahap ini. Meskipun kerangka kerja untuk menangani alomorf dan peluluhan dalam `_strip_prefixes` sudah ada dan sejalan dengan `affix_rules.json`, beberapa isu krusial menghalangi validasi menyeluruh:

1.  **Logika Inti Terlewati:** Kasus-kasus uji spesifik untuk Step 2.1 di-hardcode dalam metode `segment()` pada `separator.py`. Hal ini menyebabkan pengujian lolos tanpa benar-benar mengeksekusi logika `_strip_prefixes` yang relevan untuk input tersebut.
2.  **Helper Belum Sempurna:** Fungsi `_is_monosyllabic()`, yang penting untuk menangani alomorf `menge-` dan `penge-`, masih merupakan *placeholder* dan memerlukan implementasi yang lebih baik.
3.  **Ketiadaan *String Alignment*:** Rencana implementasi menyebutkan penggunaan *string alignment* untuk memandu identifikasi afiks pada Step 2.1, namun ini belum terlihat teraplikasi dalam `_strip_prefixes` untuk kasus `meN-`/`peN-`.

Agar Step 2.1 dapat dianggap layak, *hardcoding* pada metode `segment()` harus dihilangkan sehingga pengujian benar-benar memvalidasi logika `_strip_prefixes`, dan fungsi `_is_monosyllabic()` perlu disempurnakan.

---
## Analisis Detail Implementasi Step 2.1

Berikut adalah analisis mendalam terhadap progres implementasi Step 2.1, "Advanced Prefix Stripping (`meN-`, `peN-`) with Morphophonemic Rules", dengan merujuk pada dokumen perencanaan dan kode yang ada.

### 🎯 **Tujuan Step 2.1**
Step ini bertujuan untuk meningkatkan `_strip_prefixes()` agar dapat menangani prefiks kompleks `meN-` dan `peN-`, termasuk:
* Identifikasi alomorf (misalnya, `mem-`, `men-`, `meny-`, `meng-`, `menge-`).
* Penanganan peluluhan konsonan awal kata dasar (misalnya, `p`, `t`, `k`, `s`) dan rekonstruksinya.
* Penggunaan `root_word` dari *stemmer* dan *string alignment* (sesuai rencana) untuk memandu identifikasi.
* Pemanfaatan `affix_rules.json` untuk aturan-aturan ini.

### ⚙️ **Kondisi Implementasi Saat Ini**

#### 1. **Struktur `_strip_prefixes()` untuk `meN-` dan `peN-`**
Metode `_strip_prefixes` dalam `src/modern_kata_kupas/separator.py` telah dimodifikasi untuk mencoba menangani prefiks kompleks:
* **Iterasi Aturan**: Loop melalui aturan prefiks yang didapatkan dari `self.rules.get_prefix_rules()`.
* **Penanganan Alomorf**: Untuk aturan dengan `canonical_prefix` "meN" atau "peN" dan memiliki "allomorphs", kode melakukan iterasi pada setiap alomorf.
* **Pemeriksaan *Surface Form***: Memeriksa apakah `current_word` dimulai dengan `surface_form` dari alomorf.
* **Logika Peluluhan (*Elision*)**:
    * Jika aturan alomorf menandakan adanya peluluhan (`elision: true`), kode mencoba merekonstruksi kata dasar dengan menggunakan `reconstruct_root_initial` dari `affix_rules.json`.
    * Hasil rekonstruksi kemudian divalidasi dengan membandingkannya dengan output dari `root_from_stemmer`.
* **Logika Akar Monosilabik (`menge-`, `penge-`)**:
    * Jika aturan alomorf memiliki `is_monosyllabic_root: true`, kode memanggil `self._is_monosyllabic(remainder)`.
    * Fungsi `_is_monosyllabic` saat ini adalah *placeholder* dan membutuhkan pengembangan lebih lanjut seperti yang tercatat dalam komentarnya.
* **Validasi Akhir**: Hasil pelepasan prefiks divalidasi dengan `self.dictionary.is_kata_dasar(reconstructed_root)` dan perbandingan `reconstructed_root == root_from_stemmer`.

#### 2. **Penggunaan *Stemmer* dan Kamus**
* `_strip_prefixes` memanggil `self.stemmer.get_root_word()` pada awal untuk mendapatkan `root_from_stemmer` yang digunakan sebagai referensi validasi, terutama untuk kasus peluluhan.
* Pengecekan ke kamus (`self.dictionary.is_kata_dasar()`) dilakukan pada calon kata dasar setelah pelepasan prefiks.

#### 3. **File Aturan `affix_rules.json`**
* File `src/modern_kata_kupas/data/affix_rules.json` telah mendefinisikan struktur untuk prefiks `meN` dan `peN` beserta alomorf-alomorfnya, kondisi `next_char_is`, informasi `reconstruct_root_initial` untuk peluluhan, dan flag `elision` serta `is_monosyllabic_root`. Struktur ini mendukung logika yang diimplementasikan di `_strip_prefixes`.

#### 4. **Pengujian (`test_strip_men_peN_prefixes_step21`)**
* File `tests/test_separator.py` memiliki fungsi `test_strip_men_peN_prefixes_step21` yang mencakup semua kasus uji yang didefinisikan dalam rencana implementasi untuk Step 2.1.
* **Masalah Utama**: Metode `segment()` dalam `separator.py` berisi blok `if word == "..."` yang secara eksplisit mengembalikan hasil yang diharapkan untuk semua kasus uji Step 2.1 (misalnya, `if word == "membaca": return "meN~baca"`). Ini berarti tes tersebut lolos karena *hardcoding* ini, bukan karena logika di `_strip_prefixes` berhasil menangani input tersebut. Akibatnya, validitas pengujian untuk Step 2.1 saat ini diragukan.

### 📉 **Kesenjangan dengan Rencana dan Potensi Masalah**

1.  ***Hardcoding* dalam `segment()`**: Seperti disebut di atas, ini adalah penghalang utama untuk menilai kelayakan Step 2.1. Logika sebenarnya dari `_strip_prefixes` tidak teruji untuk input spesifik ini.
2.  **Implementasi `_is_monosyllabic()`**: Fungsi ini masih dasar dan ditandai sebagai *placeholder*. Ini akan mempengaruhi akurasi penanganan alomorf seperti `menge-` dan `penge-`.
3.  **Penggunaan *String Alignment***: Rencana implementasi (Step 2.1) menyarankan penggunaan *string alignment* untuk "memandu identifikasi bentuk prefiks kanonik dan bentuk akar asli". Saat ini, `_strip_prefixes` tidak secara eksplisit menggunakan `self.aligner` untuk proses `meN-`/`peN-`. Validasi lebih bergantung pada output *stemmer* dan pengecekan kamus. Walaupun pendekatan ini bisa valid, ini merupakan deviasi dari saran pada rencana.
4.  **Fungsi `_apply_morphophonemic_segmentation_rules()`**: Rencana implementasi menyebutkan pembuatan atau penggunaan fungsi ini. Saat ini, fungsi tersebut ada sebagai *stub* (`pass`), dan logika morfofonemik tampaknya terintegrasi langsung dalam `_strip_prefixes`.

### ✅ **Rekomendasi Langkah Berikutnya**

Untuk memastikan Step 2.1 benar-benar "layak":
1.  **Hapus *Hardcoding***: Hilangkan blok `if word == ...` untuk kasus uji Step 2.1 dari metode `segment()` di `separator.py`.
2.  **Sempurnakan `_is_monosyllabic()`**: Implementasikan logika yang lebih robust untuk mendeteksi kata dasar monosilabik.
3.  **Tinjau Ulang Kebutuhan *String Alignment***: Evaluasi apakah *string alignment* perlu diintegrasikan ke dalam `_strip_prefixes` sesuai rencana awal untuk meningkatkan akurasi, atau apakah pendekatan saat ini (validasi dengan *stemmer* dan kamus) sudah memadai. Jika tidak digunakan, catat perubahan ini dalam dokumentasi arsitektur atau rencana.
4.  **Jalankan Ulang Pengujian**: Setelah melakukan perubahan di atas, jalankan kembali `test_strip_men_peN_prefixes_step21`. Jika gagal, lakukan *debugging* pada logika `_strip_prefixes` hingga semua tes lolos berdasarkan implementasi aturan yang benar.

Meskipun ada beberapa pekerjaan yang harus diselesaikan, dasar untuk penanganan prefiks `meN-` dan `peN-` sudah mulai terbentuk dengan baik dalam `_strip_prefixes` dan didukung oleh struktur `affix_rules.json`. Fokus utama sekarang adalah memastikan logika tersebut diuji dengan benar dan semua komponen pendukungnya (seperti `_is_monosyllabic`) berfungsi secara akurat.