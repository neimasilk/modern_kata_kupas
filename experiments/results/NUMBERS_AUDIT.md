# Audit Angka Naskah — 23 Sep 2026

Memetakan setiap angka di abstrak dan Bab 4–5 `memory-bank/paper-draft.md` ke sumbernya, lalu
membandingkannya dengan hasil jalankan-ulang dari HEAD.

**Sumber kebenaran baru:**
- `python experiments/paper_numbers.py` → `experiments/results/paper_numbers.json` (+ `paper_predictions.csv`)
- `python experiments/downstream_significance.py` → `experiments/results/downstream_significance.json`

Semua angka intrinsik di bawah dihitung terhadap gold **buatan LLM yang belum divalidasi manusia**,
jadi masih sementara (lihat `data/annotation/README.md`).

## A. Temuan penyebab ketidakcocokan

1. **Gold berubah setelah angka dikutip.** 70,00% (252/360) dihitung pada `gold_standard_v3.csv` versi commit
   `e73cd72`. Commit `9dceaa9` (13 Apr 2026) meregenerasi berkas itu: 82 kata diganti, 5 label reduplikasi diubah,
   dan jumlah baris menjadi 362. Dengan kode HEAD, versi lama tetap menghasilkan 70,00%, sedangkan versi sekarang 64,92% (235/362).
2. **Duplikat.** Versi sekarang punya 8 kata ganda (mis. *makanan* muncul sebagai `suffix_an` **dan** `suffix_kan`).
   Evaluasi baru memakai 354 kata unik.
3. **Dua angka "utama" di dalam naskah sendiri.** Abstrak menulis 70,00% dan κ 0,70 (`statistical_results_v2.json`),
   §5.1 menulis 66,94% dan κ 0,6688 (`statistical_results.json`, run lebih lama).
4. **Bug `experiments/evaluate.py`** (sudah diperbaiki, dengan tes `tests/test_eval_metrics.py`):
   - `parse_segmentation` tidak pernah memecah string (`seg == seg.strip('~')` hampir selalu benar), sehingga
     metrik morfem/stem/afiks sebenarnya membandingkan string utuh.
   - Kata yang tidak tersegmentasi dilewati (`continue`), sehingga P/R terlalu tinggi.
   - Penyebut akurasi prefiks/sufiks salah (`1 if gold else 1`) ditambah efek butir sebelumnya, sehingga `prefix_accuracy` dan `suffix_accuracy` = 1,0.
   - `metrics_v3.json` (73,30%, 191 kata) dihitung pada `gold_standard_v2.csv` (191 kata) dengan kode lama.
     `gold_standard.csv` (v1) bahkan tidak punya segmentasi (`gold == word` di semua 191 baris).
5. **Cohen's κ tidak bermakna.** `statistical_tests.py` menghitung κ dengan setiap string segmentasi sebagai
   kategori, sehingga peluang kesepakatan acak ≈ 0 dan κ ≈ akurasi (0,6994 vs 0,7000). Ini **bukan** kesepakatan
   antar-anotator. Hapus dari naskah. κ antar-anotator yang sungguhan baru bisa dihitung setelah anotasi manusia
   (`experiments/annotation_agreement.py`).
6. **McNemar "vs baseline" trivial.** Baselinenya "tidak menyegmentasi", yang hanya benar pada 5 dari 354 kata.
   Uji ini hanya membuktikan sistem lebih baik daripada tidak melakukan apa-apa. Boleh tetap dilaporkan, tetapi jangan
   diframing sebagai "significant improvement over baseline".
7. **Morfessor** (`morfessor_comparison.py`): dilatih pada `kata_dasar.txt` (daftar kata dasar tanpa imbuhan)
   **ditambah 360 kata uji** (kebocoran data uji), dan dinilai dengan exact match terhadap bentuk kanonik
   (`meN~...`) yang tidak mungkin dihasilkan segmenter permukaan. Hasilnya 13,33% di JSON, sedangkan naskah menulis 14,17%.

## B. Tabel angka

| Lokasi naskah | Angka di naskah | Sumber lama | Angka baru (HEAD) | Status |
|---|---|---|---|---|
| Abstrak, §4.1.1 | 360 kata, 21 kategori | gold v3 lama | 362 baris / **354 kata unik**, 21 kategori | GANTI |
| §4.1.1 | "DeepSeek API with manual validation", "cross-checked against KBBI" | — | 171 DeepSeek (validasi = DeepSeek yang melihat prediksi sistem) + 191 "existing" tanpa jejak validasi; **0 validasi manusia** | HAPUS KLAIM |
| Abstrak | 70,00% [65,00; 74,44] | statistical_results_v2.json | **64,41% (228/354) [59,32; 69,49]** | GANTI |
| §5.1 | 66,94% (241/360) [62,22; 71,67] | statistical_results.json | idem 64,41% | GANTI |
| Abstrak, §5.1 | κ 0,70 / 0,6688 | statistical_tests.py | — (tidak bermakna, lihat A.5) | HAPUS |
| Abstrak, §5.1 | McNemar p<0,001, χ²=232,04 | idem | exact McNemar vs no-split: b=224, c=1, p≈8·10⁻⁶⁶ | GANTI + ubah framing |
| — (baru) | — | — | Morfem P/R/F1 (multiset, semua kata): 84,61 / 68,21 / **75,53** | TAMBAH |
| — (baru) | — | — | Akurasi stem 71,19%; prefiks 69,83%; sufiks 66,03% | TAMBAH |
| §5.4, abstrak | MKK 70,00% vs Morfessor 14,17% (+55,83) | morfessor_comparison.json (13,33%!) | Evaluasi batas morfem, 307 kata non-reduplikasi: **MKK F1 85,10 [81,26; 88,51]** vs **Morfessor (tipe) F1 78,06 [75,19; 80,73]**, Morfessor (token) 63,13. Exact-boundary match 73,94% vs 51,47%, McNemar p≈2·10⁻⁹ | GANTI TOTAL |
| §5.4 | tabel agreement 46/206/5/103 | — | tidak cocok dengan JSON (43/209/5/103); tidak dipakai lagi | HAPUS |
| §5.4 | speed 32 vs 2.503 w/s | JSON 51,9 vs 2.818,8 | MKK ±67 kata/detik (bergantung mesin) | GANTI / hilangkan |
| §5.4 (baru) | — | — | Subset tanpa meN-/peN- (188 kata): MKK F1 88,3 vs Morfessor 81,9 (uji robustness konvensi) | TAMBAH |
| Abstrak, §5.5 | "100% coverage" | wikipedia_eval.json | = tidak ada crash; **bukan metrik kualitas** | HAPUS |
| §5.5 | 500 sentences | JSON: total_sentences = 1 | 504 baris teks, 11.021 token, 2.631 tipe | GANTI |
| §5.5 | 35,12% tersegmentasi | JSON | 35,12% (924/2.631) | OK |
| §5.5 | OOV 47,47% | definisi: kata utuh tak ada di kamus + heuristik afiks | **OOV akar**: 27,25% (717/2.631), yaitu akar hasil MKK tidak ada di kamus kata dasar/serapan | GANTI + definisikan |
| §5.5 | 24,4 dan 39 w/s (dua angka berbeda) | JSON 39,1 | satu angka saja, sebutkan mesin | GANTI |
| §5.6 | tabel per kategori | statistical_results.json (run lama) | lihat `paper_numbers.json → intrinsic.per_category`. Perubahan besar: compound_reduplication 65% → **0/20** (label diregenerasi April); reduplication_phonetic 0% → 77,78%; reduplication_partial 11% → 55,56% | GANTI |
| §5.6 | "11 of 21 significant above random" | ci_lower > 0,5 | "random" 50% tidak bermakna untuk segmentasi; hapus framing ini | HAPUS |
| §5.7.1 | ablation 6,28% … 66,94% | tidak cocok dengan `ablation_results.json` (7,33% … 76,96%, N=191 gold v2) | perlu dijalankan ulang pada gold final | TANDAI / JALANKAN ULANG |
| §5.7.2 | distribusi error 27/17/6/1 | errors_v3.csv (gold 191) | perlu dijalankan ulang pada gold final | TANDAI |
| §5.2, §5.3 | vocab 9.650 / 8.628 / 7.374; alignment 41,7% | tokenization_comparison_real_bpe.json | cocok dengan JSON; **tetapi** korpus sintetis (afiksasi acak) dan alignment hanya pada 24 sampel | OK angka, lemah metodologi |
| §5.8 | +0,60 acc / +2,20 F1 | text_classification_eval.json | lihat bagian C | GANTI |
| §4.6 | 93 test cases | — | 146 tes: 109 library + 37 evaluasi (Sep 2026) | GANTI |

## C. Downstream (SmSA)

Diisi dari `experiments/results/downstream_significance.json` setelah eksperimen selesai (lihat bagian bawah berkas ini).
