# Paket Anotasi Manusia — Gold Standard ModernKataKupas

**Status:** belum diisi. Kolom `annotator_segmentation` sengaja kosong.
Pengisian **hanya oleh anotator manusia** (penutur asli, sebaiknya berlatar linguistik).
AI tidak boleh mengisi atau memvalidasi label (aturan proyek, lihat `CLAUDE.md`).

## Berkas

| Berkas | Isi | Tujuan |
|---|---|---|
| `gold_blind.csv` | 354 kata unik dari `data/gold_standard_v3.csv`, urutan diacak (seed 20260923) | Menggantikan label LLM dengan label manusia |
| `wikipedia_blind_200.csv` | 200 kata acak dari `data/wikipedia_id_sample.txt` | Mengukur akurasi pada teks nyata (naskah saat ini hanya punya "segmentation rate") |

Berkas **tidak** memuat label DeepSeek, prediksi sistem, atau kategori. Jangan membuka
`gold_standard_v3.csv`, `paper_predictions.csv`, atau menjalankan ModernKataKupas saat menganotasi.

## Prosedur

1. Salin tiap berkas menjadi `*_A.csv` dan `*_B.csv`. Dua anotator mengisi **secara terpisah**, tanpa berdiskusi.
2. Isi `annotator_segmentation` dengan format kanonik (panduan di bawah). Isi `uncertain` = `1` bila ragu,
   lalu tulis alasannya di `annotator_notes`.
3. Hitung kesepakatan:
   ```
   python experiments/annotation_agreement.py data/annotation/gold_blind_A.csv data/annotation/gold_blind_B.csv -o data/annotation/agreement_gold.json
   ```
   Laporkan `exact_agreement` dan `boundary_kappa` di naskah (ini baru kappa antar-anotator yang sesungguhnya).
4. Adjudikasi: kedua anotator (atau anotator ketiga) membahas daftar `disagreements` dan menulis label final
   ke `gold_adjudicated.csv` (kolom `word, annotator_segmentation, annotator, method, date`).
5. Bandingkan dengan label LLM (menjadi temuan tersendiri di naskah):
   ```
   python experiments/annotation_agreement.py data/annotation/gold_adjudicated.csv data/gold_standard_v3.csv --col-b gold_segmentation
   ```
6. Setelah itu gold baru (`gold_standard_v4.csv`, dengan kolom provenance) dipakai oleh `experiments/paper_numbers.py`.

## Panduan anotasi (format kanonik)

- Pemisah morfem: `~`. Tulis dengan huruf kecil, kecuali penanda alomorf `meN` dan `peN`.
- **Prefiks nasal** ditulis kanonik: `meN`, `peN` (menulis → `meN~tulis`, pengajar → `peN~ajar`).
  Kata dasar ditulis dalam bentuk **aslinya** (luluh dikembalikan: menyapu → `meN~sapu`).
- Prefiks lain: `ber`, `ter`, `di`, `ke`, `se`, `per`. Alomorf ditulis kanonik (belajar → `ber~ajar`, bekerja → `ber~kerja`).
- Sufiks derivasional: `kan`, `i`, `an`. Partikel: `lah`, `kah`, `pun`, `tah`. Posesif/klitik: `ku`, `mu`, `nya`.
- Urutan: prefiks (luar ke dalam) ~ dasar ~ sufiks ~ partikel/klitik
  (mempertanggungjawabkannya → `meN~per~tanggung jawab~kan~nya`; tulis dasar majemuk sesuai KBBI).
- Konfiks ditulis sebagai prefiks + sufiks: kebersihan → `ke~bersih~an`.
- **Reduplikasi:** penuh `dasar~ulg` (buku-buku → `buku~ulg`), dengan afiks: berlari-lari → `ber~lari~ulg`;
  dwipurwa `dasar~rp` (lelaki → `laki~rp`); salin suara `dasar~rs(~pasangan)` (sayur-mayur → `sayur~rs(~mayur)`).
- Kata monomorfemis atau pinjaman tanpa imbuhan: tulis kata itu apa adanya (tanpa `~`).
- Kata yang **bukan kata bahasa Indonesia yang wajar** (misalnya hasil karangan LLM seperti *anak-cucu-cicit*
  berulang tidak wajar, atau salah ketik): tulis `INVALID` di `annotator_segmentation` dan jelaskan di catatan.
  Kata INVALID dikeluarkan dari evaluasi.
- Rujukan: KBBI daring (kbbi.kemdikbud.go.id) dan *Tata Bahasa Baku Bahasa Indonesia*.

Konvensi di atas meneruskan format keluaran sistem agar bisa dibandingkan. Bila anotator tidak setuju
dengan konvensinya (misalnya soal `per` pada *memper-*), catat di `annotator_notes`. Jangan diam-diam mengubah format.
