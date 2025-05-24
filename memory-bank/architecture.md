# Arsitektur modern-kata-kupas

Dokumen ini menjelaskan arsitektur dan komponen utama dari library `modern-kata-kupas`.

## Komponen Utama

### DictionaryManager

Bertanggung jawab untuk memuat dan mengelola kamus kata dasar bahasa Indonesia. Mendukung pemuatan dari file eksternal atau kamus default yang dikemas dalam library.

### StemmerInterface

Kelas ini berfungsi sebagai wrapper untuk library stemming bahasa Indonesia, saat ini mengintegrasikan PySastrawi. Tujuannya adalah menyediakan antarmuka yang konsisten dan sederhana untuk mendapatkan kata dasar dari sebuah kata, mengabstraksi detail implementasi dari library stemming yang mendasarinya. Metode utamanya adalah `get_root_word` yang mengambil string kata dan mengembalikan kata dasarnya.

### Normalizer

The `utils` directory contains helper modules. One such utility is `utils/alignment.py`, which implements the Needleman-Wunsch algorithm for string alignment. However, it's important to note that this explicit string alignment is not actively used in the core V1.0 segmentation logic within `Separator.py`. For V1.0, a heuristic approach based on direct rule application and dictionary lookups was found to be sufficient for common cases. The string alignment utility exists for potential future exploration in handling more complex or ambiguous scenarios.

### Separator

Modul utama (`separator.py`) yang bertanggung jawab untuk memisahkan kata berimbuhan menjadi kata dasar dan afiksnya. Ini mengkoordinasikan penggunaan komponen lain seperti normalizer, dictionary, rules, dan stemmer.

## Penanganan Ambiguitas Dasar (V1.0)

Versi 1.0 dari `ModernKataKupas` memiliki mekanisme heuristik dasar untuk menangani beberapa kasus ambiguitas, meskipun tidak secara eksplisit dirancang untuk menyelesaikan semua jenis ambiguitas secara mendalam. Penanganan ini lebih merupakan hasil dari interaksi aturan yang ada dan prioritas dalam proses segmentasi.

Berikut adalah analisis bagaimana kata-kata ambigu "beruang" dan "mengetahui" ditangani oleh sistem V1.0, berdasarkan pengujian dengan kamus yang ada (yang mungkin tidak mencakup semua akar kata potensial seperti "uang", "ruang", atau "tahu" dalam setiap skenario pengujian).

### Kasus: "beruang"

*   **Output Aktual (V1.0 dengan kamus uji saat ini):** `beruang`
*   **Analisis Heuristik:**
    1.  **Normalisasi:** Kata "beruang" dinormalisasi menjadi "beruang".
    2.  **Pengecekan Kata Dasar:** Jika "beruang" ada dalam kamus sebagai kata dasar, maka akan dikembalikan apa adanya.
    3.  **Penanganan Reduplikasi:** Tidak ada pola reduplikasi yang terdeteksi. `word_to_process` menjadi "beruang".
    4.  **Strategi Segmentasi (S1: Prefiks dulu, S2: Sufiks dulu):**
        *   **Pelepasan Prefiks (`_strip_prefixes`):**
            *   Aturan untuk prefiks "ber-" akan dicoba. Jika "uang" ada dalam kamus (`kata_dasar_set`), maka "ber~uang" akan menjadi kandidat kuat.
            *   Aturan untuk prefiks "be-" (jika ada dan relevan, misal untuk akar yang dimulai dengan 'r' seperti "ruang") juga bisa dicoba. Jika "ruang" ada dalam kamus, "be~ruang" bisa menjadi kandidat.
        *   **Pelepasan Sufiks (`_strip_suffixes`):** Tidak ada sufiks yang jelas pada "beruang".
    5.  **Pemilihan Hasil Terbaik:**
        *   Jika kedua strategi (S1 dan S2) dijalankan, dan salah satunya menghasilkan segmen yang valid dimana stemnya adalah kata dasar yang dikenal (misalnya, "uang" setelah "ber-" dilepas, atau "ruang" setelah "be-" dilepas), segmen tersebut akan dipilih.
        *   **Dalam kasus pengujian saat ini (Baby Step 6), kata "uang" dan "ruang" tidak dapat ditambahkan secara reliabel ke `tests/data/test_kata_dasar.txt`. Akibatnya, `is_kata_dasar("uang")` dan `is_kata_dasar("ruang")` akan mengembalikan `False`.**
        *   Karena tidak ada akar kata yang valid ("uang" atau "ruang") yang ditemukan setelah mencoba melepaskan prefiks "ber-" atau "be-", kedua strategi segmentasi (S1 dan S2) gagal menghasilkan dekomposisi yang valid menjadi afiks + akar kata dikenal.
        *   Ketika tidak ada segmentasi valid yang ditemukan, dan kata itu sendiri ("beruang") tidak teridentifikasi sebagai kata dasar dalam kamus yang terbatas, sistem akan mengembalikan kata yang sudah dinormalisasi sebagai output akhir. Inilah mengapa outputnya adalah "beruang".
    *   **Prioritas Heuristik:**
        *   **Keberadaan dalam Kamus:** Validitas sebuah akar kata setelah pelepasan afiks sangat bergantung pada keberadaannya dalam `kata_dasar_set`.
        *   **Aturan Prefiks:** Aturan prefiks "ber-" (dan alomorfnya jika ada) akan dicocokkan. Jika `affix_rules.json` mendefinisikan "ber-" sebagai bentuk yang valid dan "be-" sebagai alomorf hanya untuk kondisi tertentu (misalnya, bertemu akar "kerja" menjadi "bekerja"), maka "ber~uang" akan lebih diprioritaskan daripada "be~ruang" jika "uang" adalah akar yang valid.

### Kasus: "mengetahui"

*   **Output Aktual (V1.0 dengan kamus uji saat ini):** `mengetahui`
*   **Analisis Heuristik:**
    1.  **Normalisasi:** "mengetahui" -> "mengetahui".
    2.  **Pengecekan Kata Dasar:** Jika "mengetahui" ada dalam kamus, akan dikembalikan.
    3.  **Penanganan Reduplikasi:** Tidak ada. `word_to_process` menjadi "mengetahui".
    4.  **Strategi Segmentasi (S1 dan S2):**
        *   **Pelepasan Sufiks (`_strip_suffixes`):**
            *   Sufiks "-i" akan dicoba dilepaskan, menghasilkan "mengetahu".
        *   **Pelepasan Prefiks (`_strip_prefixes` pada "mengetahu" atau "mengetahui"):**
            *   Aturan untuk prefiks "meN-" akan dicoba. Alomorf "meng-" mungkin cocok dengan "mengetahui" (jika "etahui" dianggap calon stem) atau "menge-" dengan "mengetahui" (jika "tahui" dianggap calon stem).
            *   Jika "-i" sudah dilepas menjadi "mengetahu", maka "meN-" (dengan alomorf "meng-" atau "menge-") akan dicoba pada "mengetahu".
                *   Jika "tahu" adalah kata dasar yang dikenal: `meN~` + `tahu` akan menjadi `mengetahui` (setelah `reverse_morphophonemics` pada "tahu" dari "etahui" jika "meng-" + "etahui" diproses, atau "menge-" + "tahui").
                *   Jika "ketahui" adalah kata dasar yang dikenal: `meN~` + `ketahui` bisa menjadi `mengetahui`.
    5.  **Pemilihan Hasil Terbaik:**
        *   Segmentasi yang paling mungkin dan valid berdasarkan aturan dan kamus adalah `meN~tahu~i`. Ini memerlukan "tahu" sebagai kata dasar yang dikenal.
        *   **Dalam kasus pengujian saat ini (Baby Step 6), kata "tahu" tidak dapat ditambahkan secara reliabel ke `tests/data/test_kata_dasar.txt`. Akibatnya, `is_kata_dasar("tahu")` akan mengembalikan `False`.**
        *   Karena akar kata "tahu" tidak ditemukan dalam kamus uji, proses pelepasan afiks "meN-" dan "-i" tidak dapat divalidasi sepenuhnya ke akar yang dikenal.
        *   Strategi S1 (prefiks dulu) mungkin mencoba `meN-` dari `mengetahui`, menyisakan `etahui`. Jika `etahui` bukan KD, dan pembalikan morfofonemiknya ke `ketahui` atau `tahui` juga bukan KD, maka path ini tidak menghasilkan stem valid.
        *   Strategi S2 (sufiks dulu) akan melepas `-i` menjadi `mengetahu`. Kemudian prefiks `meN-` dicoba pada `mengetahu`. Jika `tahu` tidak dikenal sebagai KD, maka path ini juga tidak menghasilkan stem valid.
        *   Ketika tidak ada dekomposisi menjadi afiks + akar kata dikenal yang ditemukan, dan "mengetahui" itu sendiri bukan kata dasar, sistem mengembalikan kata yang sudah dinormalisasi.
    *   **Prioritas Heuristik:**
        *   **Validitas Kata Dasar:** Kunci utama adalah pengenalan "tahu" sebagai kata dasar.
        *   **Urutan Pelepasan Afiks:** Urutan pelepasan sufiks (seperti "-i") dan prefiks (seperti "meN-") serta pemeriksaan kamus pada setiap langkah sangat menentukan.
        *   **Aturan Alomorf `meN-`:** Aturan untuk "menge-" (jika kata dasar satu suku kata) atau "meng-" (untuk vokal atau k-) akan dievaluasi.

Secara umum, untuk V1.0, jika sebuah kata ambigu tidak dapat dipecah menjadi kombinasi afiks dan akar kata *yang dikenal dalam kamus saat ini*, maka kata tersebut cenderung dikembalikan dalam bentuk normalisasinya. Kemampuan untuk menangani ambiguitas akan sangat bergantung pada kelengkapan kamus dan kecanggihan aturan pemrioritasan.

Metode kunci dalam modul ini meliputi:

- `segment()`: Metode publik utama untuk memulai proses segmentasi.
- `_strip_suffixes()`: Metode helper yang bertanggung jawab untuk memisahkan sufiks dari kata. Saat ini diimplementasikan untuk menangani sufiks infleksional (partikel dan posesif) serta sufiks derivasional dasar (`-kan`, `-i`, `-an`) sesuai dengan Step 1.4 dan Step 1.5. Logika pelepasan sufiks ini mengikuti urutan tertentu untuk memastikan pelepasan yang benar.
- `_strip_prefixes()`: Metode helper yang bertanggung jawab untuk memisahkan prefiks sederhana (`di-`, `ke-`, `se-`) dari kata sesuai dengan Step 1.6. Metode ini berinteraksi dengan `MorphologicalRules` untuk mendapatkan dan menerapkan aturan prefiks.

### Reconstructor

(Deskripsi akan ditambahkan nanti)

### Rules

(Deskripsi akan ditambahkan nanti)

### Utils

(Deskripsi akan ditambahkan nanti)