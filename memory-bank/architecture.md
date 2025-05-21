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

(Deskripsi akan ditambahkan nanti)

### Reconstructor

(Deskripsi akan ditambahkan nanti)

### Rules

(Deskripsi akan ditambahkan nanti)

### Utils

(Deskripsi akan ditambahkan nanti)