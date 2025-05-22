Baik, mari kita rancang implementasi untuk **Step 2.1: Advanced Prefix Stripping (`meN-`, `peN-`) with Morphophonemic Rules** dengan detail dan jelas.

Langkah ini krusial karena mengenalkan logika untuk menangani perubahan bentuk kata yang lebih kompleks akibat afiksasi.

**Referensi Utama:**
* `ModernKataKupas_ImplementationPlan_v1.md` (untuk definisi Step 2.1)
* `memory-bank/paper-draft.md` (Chapter 3.2, untuk contoh struktur aturan `meN-`)
* File `src/modern_kata_kupas/separator.py` dan `src/modern_kata_kupas/data/affix_rules.json`.

---

### Tahap A: Pembaruan Definisi Aturan (`src/modern_kata_kupas/data/affix_rules.json`)

Anda perlu memperluas file `affix_rules.json` untuk mendefinisikan aturan `meN-` dan `peN-` beserta semua alomorf dan kondisi morfofonemiknya.

**Contoh Struktur untuk `meN-` (dan serupa untuk `peN-`):**

```json
{
  "prefixes": [
    // ... aturan prefiks sederhana yang sudah ada (di-, ke-, se-)
    {
      "canonical": "meN", // Bentuk kanonikal dari prefiks
      "type": "prefix_derivational_complex", // Tipe baru untuk membedakan jika perlu
      "allomorphs": [
        {
          "surface": "mem", // Bentuk permukaan yang muncul di kata
          "next_char_is": ["b", "f", "v", "p"], // Karakter awal dari kata dasar SETELAH 'mem' dilepas (jika tidak luluh) ATAU karakter luluh itu sendiri
          "reconstruct_root_initial": { // Apa yang harus direkonstruksi di awal kata dasar
            "p": "p" // Jika next_char_is 'p', maka 'p' luluh, rekonstruksi jadi 'p' + sisa_kata
            // "f": null, // Jika 'f', tidak ada peluluhan, hanya kondisi
          },
          "elision": true // Menandakan ada potensi peluluhan
        },
        {
          "surface": "men",
          "next_char_is": ["d", "c", "j", "z", "t"],
          "reconstruct_root_initial": {
            "t": "t"
          },
          "elision": true
        },
        {
          "surface": "meny",
          "next_char_is": ["s"], // Khusus untuk 's' yang luluh menjadi 'ny'
          "reconstruct_root_initial": {
            "s": "s"
          },
          "elision": true
        },
        {
          "surface": "meng",
          "next_char_is": ["g", "h", "q", "a", "i", "u", "e", "o", "k"],
          "reconstruct_root_initial": {
            "k": "k"
          },
          "elision": true
        },
        {
          "surface": "me",
          "next_char_is": ["l", "m", "n", "r", "w", "y", "ng", "ny"], // Tidak ada peluluhan
          "reconstruct_root_initial": null, // Atau tidak ada field ini
          "elision": false
        },
        {
          "surface": "menge",
          "is_monosyllabic_root": true, // Kondisi khusus untuk akar kata satu suku kata
          "reconstruct_root_initial": null,
          "elision": false
        }
      ]
    }
    // ... Tambahkan aturan untuk "peN-" dengan struktur serupa ...
    // (pem-, pen-, peny-, peng-, pe-, penge-)
  ],
  "suffixes": [
    // ... aturan sufiks yang sudah ada
  ]
}
```

**Penjelasan Field Baru/Penting:**
* `"canonical"`: Bentuk dasar prefiks yang akan disimpan jika berhasil dipisahkan (misal, "meN").
* `"allomorphs"`: Array objek, masing-masing mendefinisikan satu variasi bentuk prefiks.
* `"surface"`: Bentuk prefiks yang terlihat di kata (misal, "mem").
* `"next_char_is"`: Array karakter. Karakter pertama dari sisa kata (setelah `surface` dihilangkan) harus salah satu dari ini. Untuk kasus peluluhan, ini adalah karakter yang luluh.
* `"reconstruct_root_initial"`: Objek yang memetakan karakter dari `next_char_is` (yang luluh) ke karakter yang harus direkonstruksi di awal kata dasar. Jika `null` atau tidak ada, berarti tidak ada peluluhan atau karakter awal akar tidak berubah. Ini juga bisa string tunggal jika hanya ada satu kemungkinan rekonstruksi untuk `surface` form tersebut.
* `"elision"`: Boolean, menandakan apakah alomorf ini melibatkan peluluhan.
* `"is_monosyllabic_root"`: Boolean, kondisi khusus untuk alomorf seperti "menge-" yang biasanya melekat pada akar kata bersuku kata satu (misal, "bom" -> "mengebom").

**Tugas Anda untuk Tahap A:**
1.  Salin dan adaptasi struktur di atas ke dalam file `src/modern_kata_kupas/data/affix_rules.json`.
2.  Lengkapi aturan untuk semua alomorf `meN-` dan `peN-` sesuai kaidah morfologi bahasa Indonesia. Perhatikan variasi seperti `meN-` + `f` -> `memf` (tidak luluh), `meN-` + `v` -> `memv` (tidak luluh). `peN-` juga memiliki perilaku serupa (`pemf-`, `pemv-`).

---

### Tahap B: Modifikasi `_strip_prefixes()` di `src/modern_kata_kupas/separator.py`

Metode ini akan menjadi jauh lebih kompleks.

```python
# src/modern_kata_kupas/separator.py

# ... (import dan __init__ tetap sama)

    def _is_monosyllabic(self, word: str) -> bool:
        """
        Helper sederhana untuk mengecek apakah sebuah kata (calon akar) monosilabik.
        Ini adalah placeholder, Anda mungkin memerlukan logika yang lebih baik
        atau daftar kata dasar monosilabik.
        """
        if not word:
            return False
        # Logika deteksi suku kata bisa kompleks. Untuk awal:
        # Anggap saja jika pendek dan ada di kamus, atau jika hanya punya satu vokal.
        # Ini perlu disempurnakan. Contoh: 'bom', 'cat', 'las'.
        vowels = "aiueo"
        vowel_count = sum(1 for char in word if char in vowels)
        # Kasar: jika jumlah vokal = 1 dan ada di kamus ATAU sangat pendek
        if vowel_count == 1 and (len(word) <= 3 or self.dictionary.is_kata_dasar(word)):
            return True
        # Ini hanya contoh kasar, perlu analisis lebih lanjut atau daftar kata monosilabik.
        # Untuk kasus seperti "tes", "kon" (dari "rekonstruksi"), "bor"
        # Mungkin lebih baik jika aturan "menge-" hanya berlaku jika sisanya adalah kata dasar yang diketahui monosilabik.
        if self.dictionary.is_kata_dasar(word):
            # Jika kata ada di kamus, baru cek suku katanya (logika bisa rumit)
            # Untuk sekarang, kita asumsikan jika kata ada di kamus dan jumlah vokal=1, itu monosilabik.
             return vowel_count == 1
        return False # Default

    def _strip_prefixes(self, original_word_for_prefix_stripping: str) -> tuple[str, list[str]]:
        current_word = str(original_word_for_prefix_stripping)
        stripped_prefixes_output = []

        # Dapatkan kata dasar dari stemmer SEBELUM iterasi prefiks. Ini penting untuk validasi.
        # original_word_for_prefix_stripping adalah kata yang masuk ke _strip_prefixes,
        # bisa jadi sudah tanpa sufiks, atau kata asli jika _strip_prefixes dipanggil pertama.
        # Untuk perbandingan yang lebih konsisten, mungkin lebih baik menggunakan kata asli (sebelum sufiks juga)
        # Namun, mari kita coba dengan kata yang masuk saat ini.
        # root_from_stemmer = self.stemmer.get_root_word(original_word_for_prefix_stripping)

        # Loop ini mungkin perlu dijalankan beberapa kali jika ada prefiks berlapis,
        # tapi untuk meN- dan peN-, biasanya mereka adalah lapisan terluar dari prefiks kompleks.
        # Untuk Step 2.1, kita fokus pada satu lapisan meN- atau peN-.

        prefix_rules_all = self.rules.get_prefix_rules()

        for rule_group in prefix_rules_all:
            canonical_prefix = rule_group.get("canonical")
            
            # Tangani prefiks sederhana (dari Langkah 1.6)
            if "allomorphs" not in rule_group: 
                simple_prefix_form = rule_group.get("form")
                if simple_prefix_form and current_word.startswith(simple_prefix_form):
                    potential_root = current_word[len(simple_prefix_form):]
                    # Validasi sederhana: jika sisa kata ada di kamus, atau jika kata dasar dari stemmer cocok
                    # Ini adalah logika dari Langkah 1.6, pastikan tetap berfungsi atau diintegrasikan.
                    # Untuk saat ini, kita asumsikan jika ini dipanggil, validasi dilakukan di `segment`
                    # atau kita harus memvalidasinya di sini.
                    # if self.dictionary.is_kata_dasar(potential_root): # Validasi dasar
                    stripped_prefixes_output.append(canonical_prefix)
                    current_word = potential_root
                    # Prefiks sederhana biasanya tidak berlapis dengan meN-/peN- sebagai inner.
                    # Jika satu ditemukan, lanjutkan ke loop berikutnya atau keluar.
                    # Ini akan bergantung pada strategi segmentasi keseluruhan.
                    # Untuk sekarang, jika prefiks sederhana cocok, kita anggap selesai untuk iterasi ini.
                    # return current_word, stripped_prefixes_output # KEMBALIKAN SEGERA JIKA PREFIKS SEDERHANA COCOK DAN VALID
                                                                  # ATAU tandai dan lanjutkan untuk melihat apakah ada yang lebih kompleks cocok
                    # Untuk Step 2.1, kita prioritaskan aturan kompleks jika ada.
                    # Jadi, mungkin loop ini harus diubah urutannya atau cara penanganannya.
                    # Mari kita lanjutkan ke aturan kompleks di bawah ini.
                    # Jika aturan sederhana ditemukan, kita bisa menyimpannya sebagai kandidat.
                    pass # Akan ditangani oleh logika di `segment` jika tidak ada aturan kompleks yang cocok


            # Tangani prefiks kompleks (meN-, peN-)
            if "allomorphs" in rule_group and (canonical_prefix == "meN" or canonical_prefix == "peN"):
                for allomorph_rule in rule_group["allomorphs"]:
                    surface_form = allomorph_rule.get("surface")
                    
                    if current_word.startswith(surface_form):
                        remainder = current_word[len(surface_form):]
                        if not remainder: # Jika setelah dipotong tidak ada sisa (misal "me")
                            continue

                        reconstructed_root_candidate = remainder # Default jika tidak ada peluluhan
                        
                        # 1. Cek Kondisi dan Rekonstruksi Akar (jika ada peluluhan)
                        elision_handled = False
                        if allomorph_rule.get("elision"):
                            # Cek kondisi next_char_is dan reconstruct_root_initial
                            # Ini adalah bagian yang paling rumit
                            next_char_original = remainder[0] if remainder else '' # Karakter setelah prefiks (sebelum rekonstruksi)
                            
                            # Validasi kondisi next_char_is dari aturan JSON
                            valid_next_chars_for_allomorph = allomorph_rule.get("next_char_is", [])
                            
                            char_to_reconstruct = None
                            if allomorph_rule.get("reconstruct_root_initial"):
                                # Jika 's' luluh jadi 'meny', remainder akan mulai dengan vokal, next_char_is harusnya ['s']
                                # Jika 'p' luluh jadi 'mem', remainder akan mulai dengan vokal, next_char_is harusnya ['p']
                                # Logika ini perlu hati-hati: 'next_char_is' di aturan JSON harus merujuk pada KARAKTER ASLI AKAR KATA
                                # yang menyebabkan alomorf tersebut, BUKAN karakter pertama dari 'remainder'.

                                # Misal: "memukul", surface="mem", remainder="ukul"
                                # Aturan untuk "mem" yang luluh dari "p": {"surface": "mem", "next_char_is": ["p"], "reconstruct_root_initial": {"p":"p"}}
                                # Disini kita harus mencocokkan 'p' (dari next_char_is) dengan sesuatu.
                                # Cara terbaik adalah: coba rekonstruksi, lalu validasi dengan kamus/stemmer.

                                # Iterasi melalui kemungkinan rekonstruksi
                                possible_reconstructions = allomorph_rule.get("reconstruct_root_initial")
                                found_match_for_elision = False
                                if possible_reconstructions: # Ini adalah objek seperti {"p": "p", "t": "t"}
                                    for original_char, reconstructed_char_val in possible_reconstructions.items():
                                        # `original_char` adalah karakter yang luluh (misal 'p')
                                        # `reconstructed_char_val` adalah karakter yang muncul di awal root (misal 'p')
                                        # Apakah `original_char` ada di `valid_next_chars_for_allomorph`? Ya, seharusnya.
                                        
                                        # Coba rekonstruksi:
                                        temp_reconstructed_root = reconstructed_char_val + remainder
                                        # Validasi apakah temp_reconstructed_root ini kata dasar
                                        if self.dictionary.is_kata_dasar(temp_reconstructed_root):
                                            # Juga, bandingkan dengan stemmer dari kata ASLI
                                            # original_word_for_prefix_stripping adalah input ke _strip_prefixes
                                            root_from_stemmer = self.stemmer.get_root_word(original_word_for_prefix_stripping)
                                            if temp_reconstructed_root == root_from_stemmer:
                                                reconstructed_root_candidate = temp_reconstructed_root
                                                elision_handled = True
                                                found_match_for_elision = True
                                                break # Rekonstruksi berhasil dan tervalidasi
                                    if not found_match_for_elision:
                                        continue # Alomorf ini tidak cocok karena rekonstruksi gagal divalidasi
                                else: # Tidak ada aturan reconstruct_root_initial, berarti tidak ada peluluhan yg perlu direkonstruksi untuk alomorf ini
                                     pass # lanjut ke validasi non-elision di bawah
                                
                            else: # Tidak ada `elision: true` atau tidak ada `reconstruct_root_initial`
                                elision_handled = True # Anggap saja tidak ada elision yang perlu ditangani
                                # Validasi next_char_is jika tidak ada elision (misal "me" + "lari")
                                if valid_next_chars_for_allomorph and (not remainder or remainder[0] not in valid_next_chars_for_allomorph):
                                    continue # Karakter berikutnya tidak cocok dengan kondisi

                        elif allomorph_rule.get("is_monosyllabic_root"):
                            if not self._is_monosyllabic(remainder) or not self.dictionary.is_kata_dasar(remainder):
                                continue # Bukan akar monosilabik yang valid
                            elision_handled = True # Tidak ada elision, hanya kondisi monosilabik
                        
                        else: # Tidak ada elision, tidak ada monosyllabic, ini adalah kasus "me" + l,m,n,r,w,y...
                            if not self.dictionary.is_kata_dasar(remainder): # Cek apakah sisanya kata dasar
                                continue
                            # Bandingkan dengan stemmer
                            root_from_stemmer = self.stemmer.get_root_word(original_word_for_prefix_stripping)
                            if remainder != root_from_stemmer:
                                continue
                            elision_handled = True

                        # Jika lolos dari semua pemeriksaan kondisi dan rekonstruksi (jika ada)
                        if elision_handled:
                            # Validasi final: apakah reconstructed_root_candidate (atau remainder jika tidak ada elision) adalah kata dasar?
                            if self.dictionary.is_kata_dasar(reconstructed_root_candidate):
                                # Validasi dengan stemmer terhadap kata *asli* yang masuk ke _strip_prefixes
                                root_from_stemmer_final_check = self.stemmer.get_root_word(original_word_for_prefix_stripping)
                                if reconstructed_root_candidate == root_from_stemmer_final_check:
                                    stripped_prefixes_output.append(canonical_prefix)
                                    current_word = reconstructed_root_candidate
                                    # Setelah menemukan prefiks meN-/peN- yang valid, kita biasanya berhenti
                                    # karena jarang ada prefiks lain setelah meN-/peN- (kecuali kasus sangat spesifik)
                                    return current_word, stripped_prefixes_output 
                                else:
                                    # Log jika stemmer tidak cocok, bisa jadi masalah di kamus stemmer atau aturan kita
                                    print(f"Debug: For '{original_word_for_prefix_stripping}', rule produced '{reconstructed_root_candidate}', stemmer produced '{root_from_stemmer_final_check}'")
                            # else:
                                # print(f"Debug: '{reconstructed_root_candidate}' not in dictionary for word '{original_word_for_prefix_stripping}' via surface '{surface_form}'")

        # Jika tidak ada aturan meN-/peN- yang cocok, coba lagi dengan aturan prefiks sederhana (jika ada)
        # Ini adalah fallback jika aturan kompleks tidak menghasilkan apa-apa
        for rule_group in prefix_rules_all:
            if "allomorphs" not in rule_group: # Aturan prefiks sederhana
                simple_prefix_form = rule_group.get("form")
                canonical_simple = rule_group.get("canonical")
                if simple_prefix_form and original_word_for_prefix_stripping.startswith(simple_prefix_form): # Cek kata asli yg masuk
                    potential_root_simple = original_word_for_prefix_stripping[len(simple_prefix_form):]
                    if self.dictionary.is_kata_dasar(potential_root_simple):
                        # Validasi dengan stemmer
                        root_from_stemmer_simple = self.stemmer.get_root_word(original_word_for_prefix_stripping)
                        if potential_root_simple == root_from_stemmer_simple :
                            # Hanya tambahkan jika belum ada prefiks kompleks yang lebih baik
                            if not stripped_prefixes_output:
                                stripped_prefixes_output.append(canonical_simple)
                                current_word = potential_root_simple
                                return current_word, stripped_prefixes_output
        
        return current_word, stripped_prefixes_output # Kembalikan hasil (mungkin tidak berubah jika tidak ada yang cocok)

    # ... (sisa kelas ModernKataKupas, termasuk segment() dan _strip_suffixes())
```

**Penjelasan Perubahan di `_strip_prefixes()`:**
1.  **Prioritas Aturan**: Idealnya, aturan yang lebih spesifik (seperti alomorf `meN-`/`peN-`) harus diuji terlebih dahulu sebelum aturan prefiks sederhana (`di-`, `ke-`, `se-`) jika ada potensi tumpang tindih (meskipun jarang untuk prefiks-prefiks ini). Struktur loop di atas mencoba menangani ini dengan memproses aturan kompleks terlebih dahulu dan bisa langsung `return` jika berhasil.
2.  **Iterasi Alomorf**: Loop internal ditambahkan untuk mencoba setiap `surface_form` dari alomorf yang didefinisikan di JSON.
3.  **Logika Kondisi & Rekonstruksi (`elision_handled`)**:
    * Jika alomorf melibatkan peluluhan (`"elision": true`), ia akan mencoba merekonstruksi karakter awal akar kata menggunakan `"reconstruct_root_initial"`. `temp_reconstructed_root` kemudian divalidasi terhadap kamus (`self.dictionary.is_kata_dasar()`) DAN output stemmer (`self.stemmer.get_root_word()`) dari kata *asli sebelum semua stripping*. Ini penting untuk memastikan rekonstruksi benar.
    * Jika alomorf memiliki kondisi `"is_monosyllabic_root": true` (seperti "menge-"), maka `remainder` harus divalidasi sebagai akar monosilabik (menggunakan helper `_is_monosyllabic` dan kamus).
    * Jika tidak ada elision dan bukan monosilabik (kasus "me-" + l,m,n,r,w,y), `remainder` langsung divalidasi terhadap kamus dan stemmer.
4.  **Validasi Kunci**: Kombinasi dari:
    * Mencocokkan `surface_form`.
    * Memenuhi kondisi khusus (`next_char_is`, `is_monosyllabic_root`).
    * Menghasilkan `reconstructed_root_candidate` (atau `remainder`) yang **ada di kamus** DAN **sesuai dengan output stemmer untuk kata input asli**.
5.  **Penyimpanan Prefiks**: Jika semua validasi berhasil, `canonical_prefix` (misalnya "meN") disimpan, dan `current_word` diperbarui menjadi `reconstructed_root_candidate`.
6.  **Helper `_is_monosyllabic()`**: Anda perlu helper ini. Implementasi awal bisa sederhana, namun mungkin perlu disempurnakan (misalnya dengan daftar kata dasar monosilabik yang diketahui atau analisis suku kata yang lebih canggih).
7.  **Penggunaan String Alignment**: Sesuai rencana implementasi, string alignment (`self.aligner`) dapat digunakan sebagai panduan tambahan, terutama jika ada ambiguitas atau jika output stemmer tidak selalu sempurna. Misalnya, setelah mendapatkan `reconstructed_root_candidate`, Anda bisa align kata asli dengan `surface_form + reconstructed_root_candidate` untuk melihat seberapa baik cocoknya. Untuk saat ini, kode di atas lebih mengandalkan kamus dan stemmer.

---

### Tahap C: Penyesuaian `segment()` di `src/modern_kata_kupas/separator.py`

Logika dua strategi di `segment()` (prefiks dulu baru sufiks, atau sebaliknya) sebagian besar masih bisa relevan. Pastikan bahwa `final_stem` yang dihasilkan dari kedua strategi tersebut divalidasi dengan benar terhadap `self.dictionary.is_kata_dasar()`.
Karena `_strip_prefixes` sekarang lebih canggih, `stem_after_prefixes` yang dihasilkannya harus merupakan akar kata yang lebih akurat jika prefiks `meN-`/`peN-` berhasil dilepas.

---

### Tahap D: Pembuatan Kasus Uji (`tests/test_separator.py`)

Tambahkan metode tes baru atau perluas yang sudah ada untuk mencakup semua skenario dari rencana implementasi untuk Step 2.1.

```python
# tests/test_separator.py

# ... (pytest, os, ModernKataKupas import)

# Pastikan mkk di-inisialisasi dengan benar dalam tes Anda, termasuk dictionary
# Anda mungkin memerlukan fixture untuk ini jika belum ada

def test_segment_advanced_men_pen_prefixes(mkk_instance_with_test_dict_and_rules): # Asumsi fixture ini ada
    """Tes segmentasi dengan prefiks meN- dan peN- yang kompleks."""
    # Pastikan kata dasar ada di tests/data/test_kata_dasar.txt
    # Contoh: "baca", "pukul", "tulis", "sapu", "ambil", "kupas", "bom", "kirim"

    # Kasus meN-
    assert mkk_instance_with_test_dict_and_rules.segment("membaca") == "meN~baca"
    assert mkk_instance_with_test_dict_and_rules.segment("memukul") == "meN~pukul"
    assert mkk_instance_with_test_dict_and_rules.segment("menulis") == "meN~tulis"
    assert mkk_instance_with_test_dict_and_rules.segment("menyapu") == "meN~sapu" # Membutuhkan 's' -> 's' di reconstruct_root_initial untuk 'meny'
    assert mkk_instance_with_test_dict_and_rules.segment("mengambil") == "meN~ambil" # 'a' vokal
    assert mkk_instance_with_test_dict_and_rules.segment("mengupas") == "meN~kupas" # Membutuhkan 'k' -> 'k' di reconstruct_root_initial untuk 'meng'
    assert mkk_instance_with_test_dict_and_rules.segment("mengebom") == "meN~bom" # Membutuhkan 'bom' sebagai monosylabic root

    # Kasus peN- (Pastikan kata dasar ada di kamus tes)
    # Contoh: "pukul", "kirim", "sapu", "ajar" (untuk pengajar), "bom" (untuk pengebom)
    assert mkk_instance_with_test_dict_and_rules.segment("pemukul") == "peN~pukul"
    assert mkk_instance_with_test_dict_and_rules.segment("pengirim") == "peN~kirim" # 'k' luluh, 'i' vokal
    # assert mkk_instance_with_test_dict_and_rules.segment("penyapu") == "peN~sapu"
    # assert mkk_instance_with_test_dict_and_rules.segment("pengajar") == "peN~ajar"
    # assert mkk_instance_with_test_dict_and_rules.segment("pengebom") == "peN~bom"

    # Kasus non-elision (misal "me" + l,m,n,r,w,y)
    # Pastikan "lari", "masak" ada di kamus tes
    assert mkk_instance_with_test_dict_and_rules.segment("melarang") == "meN~larang" # jika larang ada di kamus
    assert mkk_instance_with_test_dict_and_rules.segment("memasak") == "meN~masak" # jika memasak ada di kamus dan 'm' adalah kondisi untuk 'me'

    # Kata yang tidak seharusnya diproses oleh aturan meN-/peN- jika tidak cocok
    assert mkk_instance_with_test_dict_and_rules.segment("dimakan") == "di~makan" # Harus tetap menggunakan aturan 'di'
    assert mkk_instance_with_test_dict_and_rules.segment("perbacaan") == "per~baca~an" # Akan diurus di step berikutnya
```

**Tugas Anda untuk Tahap D:**
1.  Buat fixture `mkk_instance_with_test_dict_and_rules` yang menginisialisasi `ModernKataKupas` dengan kamus tes DAN file `affix_rules.json` yang sudah diperbarui.
2.  Tambahkan kata-kata dasar yang diperlukan (`baca`, `pukul`, `tulis`, `sapu`, `ambil`, `kupas`, `bom`, `kirim`, `larang`, `masak`, `ajar`, dll.) ke dalam `tests/data/test_kata_dasar.txt`.
3.  Implementasikan tes di atas.

---

**Saran Tambahan:**
* **Debugging**: Gunakan banyak `print()` atau logging selama pengembangan `_strip_prefixes` untuk melacak bagaimana keputusan dibuat, kata apa yang sedang diproses, kandidat akar apa yang dihasilkan, dan output stemmer.
* **Modularitas**: Jika `_strip_prefixes` menjadi terlalu besar, pecah logikanya menjadi beberapa metode helper privat (misalnya, satu khusus untuk menangani aturan elision, satu untuk kondisi monosilabik, dll.). Rencana implementasi menyarankan `_apply_morphophonemic_segmentation_rules()`, ini bisa menjadi kandidat metode helper tersebut.
* **Urutan Aturan dalam JSON**: Cara Anda menyusun aturan dalam `affix_rules.json` dan cara `_strip_prefixes` mengiterasinya bisa memengaruhi hasil jika ada ambiguitas. Alomorf yang lebih panjang atau lebih spesifik (misal, "meny-", "menge-") sebaiknya dipertimbangkan sebelum yang lebih umum (misal, "me-").

Ini adalah langkah yang cukup signifikan. Fokus pada satu jenis peluluhan atau satu alomorf pada satu waktu, uji secara menyeluruh, baru lanjutkan ke berikutnya.