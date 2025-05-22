Tentu, mari kita bahas saran yang lengkap dan mendetail untuk menyelesaikan Langkah 1.6 dari rencana implementasi Anda (`ModernKataKupas_ImplementationPlan_v1.md`).

**Tujuan Langkah 1.6:** Implementasi pelepasan prefiks dasar (`di-`, `ke-`, `se-`) yang non-morfofonemik, dengan menggunakan `AffixRuleRepository`.

Berikut adalah langkah-langkah mendetail yang disarankan:

**1. Persiapan dan Pemahaman Aturan Afiks (AffixRuleRepository)**

* **Tinjau Struktur `AffixRuleRepository` (Langkah 0.4)**:
    * Pastikan Anda memahami bagaimana `AffixRuleRepository` (yang diimplementasikan sebagai kelas `MorphologicalRules` di `src/modern_kata_kupas/rules.py`) memuat dan menyediakan aturan.
    * Rencana implementasi Langkah 0.4 memberikan contoh struktur JSON untuk `affix_rules.json`. Contohnya adalah:
        ```json
        {
          "prefixes": {
            "di-": {"canonical": "di", "type": "prefix_derivational", "surface_forms": ["di"]},
            "ke-": {"canonical": "ke", "type": "prefix_derivational", "surface_forms": ["ke"]},
            "meN-": { ... }
          },
          "suffixes": { ... }
        }
        ```
    * Namun, kelas `MorphologicalRules` Anda saat ini tampaknya mengharapkan format yang sedikit berbeda saat memuat aturan dari file JSON, yaitu daftar kamus (list of dictionaries) di bawah kunci `"prefixes"` dan `"suffixes"`:
        ```python
        # src/modern_kata_kupas/rules.py - MorphologicalRules.load_rules
        # ...
        # if not isinstance(loaded_rules[section], list):
        #     raise ValueError(f"Bagian {section} harus berupa list")
        # ...
        ```
        Contoh di `test_rules.py` juga menggunakan format ini:
        ```python
        # tests/test_rules.py - dummy_rules_file fixture
        rules_content = {
            "prefixes": [
                {"form": "meN-", "allomorphs": [...]},
                {"form": "di-"}
            ],
            # ...
        }
        ```
    * **Keputusan**: Pilih salah satu format dan pastikan konsisten antara file `affix_rules.json` (yang akan Anda buat atau perbarui) dan cara `MorphologicalRules` mem-parsingnya. Untuk prefiks sederhana seperti `di-`, `ke-`, `se-`, Anda mungkin hanya memerlukan `form` (bentuk permukaan) dan `canonical` (bentuk kanonik).

* **Buat atau Perbarui `affix_rules.json`**:
    * Buat file `affix_rules.json` di direktori `src/modern_kata_kupas/data/` (sesuai rencana Langkah 0.4).
    * Isi file ini dengan aturan untuk prefiks `di-`, `ke-`, dan `se-`. Mengikuti format yang diharapkan oleh `MorphologicalRules.py` (list of dictionaries):
        ```json
        {
          "prefixes": [
            {
              "form": "di",
              "canonical": "di",
              "type": "prefix_derivational"
              // Anda bisa menambahkan "surface_forms": ["di"] jika diperlukan,
              // namun untuk prefiks sederhana ini, 'form' mungkin cukup.
            },
            {
              "form": "ke",
              "canonical": "ke",
              "type": "prefix_derivational"
            },
            {
              "form": "se",
              "canonical": "se",
              "type": "prefix_derivational"
            }
            // Tambahkan aturan prefiks lain dari Langkah 0.4 jika belum ada,
            // misalnya contoh untuk meN- (meskipun ini akan digunakan di Langkah 2.1)
          ],
          "suffixes": [
            // Definisikan juga aturan sufiks dari Langkah 0.4 dan 1.5 di sini
            // jika Anda ingin semua aturan terpusat.
            // Contoh:
            // { "form": "kan", "canonical": "kan", "type": "suffix_derivational" },
            // { "form": "lah", "canonical": "lah", "type": "particle" }
          ]
        }
        ```
    * Pastikan `MorphologicalRules` diinisialisasi untuk memuat file ini. Jika Anda belum menentukan path file aturan saat inisialisasi `MorphologicalRules` di `ModernKataKupas.__init__`, Anda perlu melakukannya, atau pastikan `MorphologicalRules` memiliki path default ke `src/modern_kata_kupas/data/affix_rules.json`.
        ```python
        # src/modern_kata_kupas/separator.py
        # class ModernKataKupas:
        #     def __init__(self):
        #         # ...
        #         # Pastikan rules_path_actual menunjuk ke file affix_rules.json Anda
        #         rules_path_actual = "src/modern_kata_kupas/data/affix_rules.json" # atau path yang sesuai
        #         self.rules = MorphologicalRules(rules_path_actual)
        #         # ...
        ```
        Perhatikan bahwa `MorphologicalRules` saat ini mencetak pesan placeholder jika tidak ada path yang diberikan.

**2. Refaktor Metode `_strip_prefixes` di `separator.py`**

* Ubah implementasi `_strip_prefixes` untuk menggunakan aturan yang dimuat oleh `self.rules`.
    ```python
    # src/modern_kata_kupas/separator.py

    def _strip_prefixes(self, word: str) -> tuple[str, list[str]]:
        current_word = str(word) # Pastikan bekerja dengan string
        stripped_prefixes_output = [] # Akan menyimpan bentuk kanonik prefiks

        # Dapatkan aturan prefiks dari AffixRuleRepository
        prefix_rules = self.rules.get_prefix_rules() # Asumsi ini mengembalikan list of dicts

        # Untuk Langkah 1.6, kita fokus pada prefiks sederhana non-morfofonemik
        # yang tidak berlapis-lapis (hanya satu prefiks di awal).
        # Iterasi melalui aturan prefiks yang relevan (misalnya, di-, ke-, se-)
        for rule in prefix_rules:
            # Asumsikan 'form' adalah bentuk permukaan yang dicari, dan 'canonical' adalah yang disimpan
            prefix_form = rule.get("form") # Misalnya "di", "ke", "se"
            canonical_form = rule.get("canonical", prefix_form) # Default ke form jika canonical tidak ada

            if prefix_form and current_word.startswith(prefix_form):
                # Periksa apakah ini prefiks yang diinginkan untuk Langkah 1.6 (di, ke, se)
                # Ini bisa dibuat lebih dinamis, tapi untuk awal, filter sederhana bisa digunakan
                # Atau, pastikan `get_prefix_rules()` hanya mengembalikan yang relevan jika memungkinkan,
                # atau tambahkan properti 'type' atau 'complexity' pada aturan.
                # Untuk sekarang, asumsikan semua prefix_form dari aturan adalah kandidat.

                potential_root = current_word[len(prefix_form):]
                
                # Validasi apakah potential_root adalah kata dasar atau bisa diproses lebih lanjut
                # Untuk Langkah 1.6, validasi utama akan dilakukan di metode segment() setelah _strip_suffixes juga.
                # Di sini kita hanya melakukan pelepasan.

                current_word = potential_root
                stripped_prefixes_output.append(canonical_form) # Simpan bentuk kanonik
                
                # Untuk Langkah 1.6 (prefiks sederhana, non-morfofonemik, tidak berlapis),
                # kita biasanya hanya melepas satu prefiks dari jenis ini.
                break # Hentikan setelah prefiks pertama yang cocok dilepas

        return current_word, stripped_prefixes_output
    ```

**3. Tinjau dan Perbarui Pengujian di `test_separator.py`**

* **Kata Dasar untuk Pengujian**:
    * Tambahkan kata `sana` dan `buah` ke dalam file `tests/data/test_kata_dasar.txt` jika Anda mengharapkannya menjadi kata dasar yang valid setelah pelepasan prefiks `ke-` dan `se-`.
        ```text
        // tests/data/test_kata_dasar.txt
        // ... (kata-kata yang sudah ada)
        sana
        buah
        ```
    * Jika `kesana` atau `sebuah` adalah kata dasar utuh dalam kamus Anda (dan tidak seharusnya disegmentasi), maka pengujiannya harus mencerminkan hal tersebut (misalnya, `mkk.segment("kesana") == "kesana"`). Berdasarkan rencana, tampaknya `ke~sana` dan `se~buah` adalah hasil yang diharapkan, yang menyiratkan `sana` dan `buah` adalah kata dasar.

* **Pengujian Unit untuk `_strip_prefixes`**:
    * Pastikan pengujian unit untuk `_strip_prefixes` (yaitu `test_strip_basic_prefixes`) masih valid setelah refaktorisasi. Anda mungkin perlu menyesuaikan ekspektasi jika bentuk kanonik prefiks berbeda dari bentuk permukaannya (meskipun untuk `di-`, `ke-`, `se-`, biasanya sama).
        ```python
        # tests/test_separator.py
        def test_strip_basic_prefixes(self): # Ganti self dengan mkk_instance jika menggunakan fixture
            # ... (setup mkk instance dengan dictionary dan rules yang dimuat)
            mkk = ModernKataKupas() # Pastikan dictionary dan rules dimuat dengan benar
            # Contoh: mkk.rules.load_rules("path/to/your/affix_rules.json") jika belum di __init__
            #         atau pastikan __init__ mkk memuatnya.

            assert mkk._strip_prefixes("dibaca") == ("baca", ["di"]) # Asumsi kanoniknya "di"
            assert mkk._strip_prefixes("ketua") == ("tua", ["ke"])   # Asumsi kanoniknya "ke"
            assert mkk._strip_prefixes("sekolah") == ("kolah", ["se"]) # Asumsi kanoniknya "se"
            assert mkk._strip_prefixes("dimakan") == ("makan", ["di"])

            # Tambahkan pengujian untuk kesana dan sebuah jika relevan dengan kata dasar Anda
            if mkk.dictionary.is_kata_dasar("sana"): # Cek apakah "sana" ada di kamus tes
                 assert mkk._strip_prefixes("kesana") == ("sana", ["ke"])
            if mkk.dictionary.is_kata_dasar("buah"): # Cek apakah "buah" ada di kamus tes
                 assert mkk._strip_prefixes("sebuah") == ("buah", ["se"])

            assert mkk._strip_prefixes("baca") == ("baca", [])
            assert mkk._strip_prefixes("prabaca") == ("prabaca", []) # Tidak ada aturan "pra"
        ```

* **Pengujian Integrasi dalam `segment()`**:
    * Pastikan pengujian dalam `test_strip_combined_affixes` (yang memanggil `mkk.segment()`) masih mencakup kasus-kasus yang relevan untuk Langkah 1.6 dan memberikan hasil yang benar.
        ```python
        # tests/test_separator.py
        def test_strip_combined_affixes(self): # Ganti self dengan mkk_instance jika menggunakan fixture
            mkk = ModernKataKupas() # Pastikan dictionary dan rules dimuat dengan benar

            # Kasus dari rencana implementasi Langkah 1.6
            assert mkk.segment("dibaca") == "di~baca"
            # Untuk kesana dan sebuah, tergantung pada ketersediaan kata dasar
            if mkk.dictionary.is_kata_dasar("sana"):
                assert mkk.segment("kesana") == "ke~sana"
            else:
                # Jika "sana" tidak ada, dan "kesana" juga tidak, mungkin hasilnya "kesana" (tidak disegmentasi)
                # atau perilaku lain sesuai logika fallback Anda.
                # Untuk saat ini, asumsikan "sana" akan ada jika tes ini ingin berhasil.
                pass # Tambahkan assertion yang sesuai jika "sana" tidak ada

            if mkk.dictionary.is_kata_dasar("buah"):
                assert mkk.segment("sebuah") == "se~buah"
            else:
                pass # Tambahkan assertion yang sesuai jika "buah" tidak ada
            
            assert mkk.segment("dimakanan") == "di~makan~an" # Ini sudah dicakup oleh "dimakanlah" atau "dibukukan"

            # Verifikasi ulang kasus lain yang melibatkan prefiks ini:
            assert mkk.segment("dimakanlah") == "di~makan~lah"
            assert mkk.segment("kesekolah") == "ke~sekolah" # Membutuhkan "sekolah" atau "kolah" sebagai dasar
                                                          # Dictionary tes Anda punya "kolah"
                                                          # Logika segment() Anda akan mencoba:
                                                          # 1. ke + sekolah -> _strip_prefixes("kesekolah") -> ("sekolah", ["ke"])
                                                          #    _strip_suffixes("sekolah") -> ("sekolah", []) -> final_stem="sekolah"
                                                          #    Apakah "sekolah" ada di kamus? Jika tidak, strategi 1 gagal.
                                                          # 2. _strip_suffixes("kesekolah") -> ("kesekolah", [])
                                                          #    _strip_prefixes("kesekolah") -> ("sekolah", ["ke"]) -> final_stem="sekolah"
                                                          #    Jika "sekolah" tidak di kamus, maka hasil akhirnya "kesekolah".
                                                          # Jika "kolah" yang ada di kamus, maka segmentasi "kesekolah" 
                                                          # dengan aturan saat ini mungkin tidak menghasilkan "ke~se~kolah"
                                                          # kecuali jika "sekolah" di-stem menjadi "kolah" atau
                                                          # "se-" adalah prefiks yang bisa dilepas dari "sekolah" untuk menghasilkan "kolah".
                                                          # Ini menyoroti pentingnya urutan dan validasi pada tiap langkah.
                                                          # Untuk Langkah 1.6, fokus pada "ke~[kata dasar]" jika "[kata dasar]" ada.
                                                          # Jadi, jika "sekolah" adalah kata dasar, "ke~sekolah". Jika "sana" kd, "ke~sana".
    ```

**4. Verifikasi Urutan Pemrosesan dalam `segment()`**

* Rencana menyebutkan: "*This highlights the need for a clear processing order: Suffixes first, then Prefixes for simple cases*."
* Metode `segment()` Anda saat ini sudah memiliki dua strategi:
    1.  Prefiks dulu, baru sufiks.
    2.  Jika gagal, sufiks dulu, baru prefiks.
* Ini adalah pendekatan yang masuk akal untuk eksplorasi. Untuk prefiks dan sufiks sederhana (non-morfofonemik dan tidak banyak lapisan), urutan mungkin tidak terlalu krusial selama kata dasar akhir divalidasi. Namun, untuk kasus yang lebih kompleks nanti, urutan yang lebih tetap berdasarkan prinsip linguistik mungkin diperlukan.
* Untuk Langkah 1.6, pastikan strategi ini menghasilkan segmentasi yang benar untuk kasus uji yang diberikan. Misalnya, untuk `dimakanan`:
    * **Strategi 1 (P->S)**: `dimakanan` -> `_strip_prefixes` -> `makanan`, `["di"]`. `_strip_suffixes("makanan")` -> `makan`, `["an"]`. `final_stem = "makan"`. Valid. Hasil: `di~makan~an`.
    * Ini tampaknya bekerja dengan baik untuk contoh ini.

**5. Jalankan Semua Pengujian**

* Setelah melakukan perubahan, jalankan seluruh suite pengujian Anda (`pytest`) untuk memastikan tidak ada regresi pada fungsionalitas yang sudah ada (terutama Langkah 1.4 dan 1.5).

**Contoh Tambahan Pertimbangan untuk `kesekolah`:**

Jika kamus tes Anda memiliki `kolah` tetapi tidak `sekolah`:
* `_strip_prefixes("kesekolah")` akan menghasilkan `("sekolah", ["ke"])`.
* Kemudian, jika `sekolah` tidak ada di kamus, `segment` akan mencoba strategi fallback atau mengembalikan `kesekolah`.
* Jika Anda ingin `kesekolah` disegmentasi menjadi `ke~se~kolah` (dengan asumsi `se-` adalah prefiks lain dan `kolah` adalah kata dasar), ini memerlukan logika pelepasan prefiks yang lebih canggih (mungkin berlapis atau iteratif) yang mungkin di luar cakupan Langkah 1.6 (yang berfokus pada prefiks sederhana tunggal di awal).

Untuk Langkah 1.6, target utamanya adalah `di~[root]`, `ke~[root]`, `se~[root]` dimana `[root]` adalah kata dasar yang valid.

Setelah menyelesaikan poin-poin ini, Anda akan memiliki implementasi Langkah 1.6 yang lebih sesuai dengan rencana dan prinsip Vibe Coding, terutama dalam hal eksternalisasi aturan.