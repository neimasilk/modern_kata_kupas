# Arsitektur modern-kata-kupas

Dokumen ini menjelaskan arsitektur dan komponen utama dari library `modern-kata-kupas`.

## Komponen Utama

### DictionaryManager

Bertanggung jawab untuk memuat dan mengelola kamus kata dasar bahasa Indonesia. Mendukung pemuatan dari file eksternal atau kamus default yang dikemas dalam library.

### StemmerInterface

Kelas ini berfungsi sebagai wrapper untuk library stemming bahasa Indonesia, saat ini mengintegrasikan PySastrawi. Tujuannya adalah menyediakan antarmuka yang konsisten dan sederhana untuk mendapatkan kata dasar dari sebuah kata, mengabstraksi detail implementasi dari library stemming yang mendasarinya. Metode utamanya adalah `get_root_word` yang mengambil string kata dan mengembalikan kata dasarnya.

### Normalizer

(Deskripsi akan ditambahkan nanti)

### Separator

Modul utama (`separator.py`) yang bertanggung jawab untuk memisahkan kata berimbuhan menjadi kata dasar dan afiksnya. Ini mengkoordinasikan penggunaan komponen lain seperti normalizer, dictionary, rules, dan stemmer.

Metode kunci dalam modul ini meliputi:

- `segment()`: Metode publik utama untuk memulai proses segmentasi.
- `_strip_suffixes()`: Metode helper yang bertanggung jawab untuk memisahkan sufiks dari kata. Saat ini diimplementasikan untuk menangani sufiks infleksional (partikel dan posesif) serta sufiks derivasional dasar (`-kan`, `-i`, `-an`) sesuai dengan Step 1.4 dan Step 1.5. Logika pelepasan sufiks ini mengikuti urutan tertentu untuk memastikan pelepasan yang benar.

### Reconstructor

(Deskripsi akan ditambahkan nanti)

### Rules

(Deskripsi akan ditambahkan nanti)

### Utils

(Deskripsi akan ditambahkan nanti)