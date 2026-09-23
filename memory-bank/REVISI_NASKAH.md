# Revisi Naskah — bahan untuk penulis pertama (23 Sep 2026)

Dokumen ini berisi **teks pengganti siap tempel (bahasa Inggris)** untuk `memory-bank/paper-draft.md`,
berdasarkan angka yang dihasilkan ulang dari HEAD. Setiap angka punya sumber:

| Sumber | Perintah |
|---|---|
| `experiments/results/paper_numbers.json` | `python experiments/paper_numbers.py` |
| `experiments/results/downstream_significance.json` | `python experiments/downstream_significance.py` |
| Rincian ketidakcocokan lama | `experiments/results/NUMBERS_AUDIT.md` |
| Referensi | `memory-bank/REFERENCES_AUDIT.md` |

**Dua jalur.** Teks di bawah ditulis untuk kondisi **sekarang** (gold belum divalidasi manusia): klaim dilemahkan
dan keterbatasannya dinyatakan terang. Setelah anotasi manusia (`data/annotation/`) selesai, jalankan ulang kedua
skrip di atas, ganti angka, dan laporkan κ antar-anotator yang sesungguhnya. Itu akan memperkuat paper secara signifikan.
Saran: **jangan kirim ke venue sebelum anotasi manusia selesai**. Reviewer yang teliti akan menolak gold standard
buatan LLM sebagai satu-satunya bukti.

---

## 1. Abstract (ganti paragraf 2–4)

> We evaluate ModernKataKupas on a test set of 354 unique Indonesian words spanning 21 morphological categories.
> The reference segmentations were generated with an LLM (DeepSeek) and have not yet been validated by human
> annotators; all intrinsic results should therefore be read as provisional. Against this reference, the system
> reaches 64.4% exact-match word accuracy (95% bootstrap CI 59.3–69.5%) and a morpheme-level F1 of 75.5%.
> To compare with an unsupervised baseline on equal terms, we map canonical output to surface morpheme boundaries
> and train Morfessor Baseline on 330k tokens of running Indonesian text. ModernKataKupas obtains a boundary F1
> of 85.1 (95% CI 81.3–88.5) versus 78.1 (75.2–80.7) for Morfessor, and a higher rate of fully correct
> segmentations (73.9% vs 51.5%; exact McNemar p < 10⁻⁸). On a sample of Indonesian Wikipedia text
> (2,631 word types), 35.1% of types are segmented, and for 27.3% the recovered root is not in the root lexicon.
> Performance is high on regular affixation (possessives, di-, ber-, per-an, ke-an: 86–100%) and low on
> peN-an confixes, prefix stacking and reduplicated compounds.

(Hapus kalimat Cohen's Kappa, "McNemar ... over baseline", "100% coverage", "70.00% vs 14.17%", dan
"validated ... alternative". Angka downstream: lihat bagian 6.)

## 2. §1.4 Contributions

- Butir 2: ganti "Creation of a manually validated gold standard" →
  "A 354-word LLM-generated test set covering 21 morphological categories, released together with a blind
  annotation package for human validation (Section 4.1.1)."
- Butir 3: hapus "Cohen's Kappa". Ganti menjadi "bootstrap confidence intervals and exact McNemar tests".

## 3. §4.1.1 Gold Standard (ganti paragraf + tabel atribut)

> The test set combines 191 words from an earlier in-house list and 171 words generated with the DeepSeek API
> using category-specific prompts. Where the generated label disagreed with the system output, DeepSeek was
> asked to adjudicate. Because the adjudication prompt included the system prediction, this procedure may bias
> the reference toward the system. No human validation has been performed yet. After removing 8 duplicate entries,
> the set contains 354 unique words. We release a blind annotation package (words only, randomised order,
> guidelines) so that two native speakers can annotate independently; inter-annotator agreement will be
> reported as Cohen's κ over morpheme-boundary decisions.

| Attribute | Value |
|---|---|
| Unique words | 354 (362 rows, 8 duplicates) |
| Categories | 21 |
| Label source | 191 legacy list, 171 DeepSeek-generated |
| Validation | LLM adjudication only; **human validation pending** |

Tabel jumlah per kategori: ambil dari `paper_numbers.json → intrinsic.per_category.*.n`.

## 4. §4.2 Evaluation Metrics (ganti daftar)

1. **Word accuracy**: exact match of the canonical segmentation, with 95% percentile bootstrap CI (10,000 resamples).
2. **Morpheme P/R/F1**: multiset overlap of canonical morphemes, micro-averaged over all words
   (unsegmented outputs included).
3. **Boundary P/R/F1**: canonical output is mapped deterministically to surface boundaries
   (convention: the nasal of meN-/peN- belongs to the prefix; an elided root-initial k/p/t/s leaves the
   remainder as the root, e.g. *menulis* → men|ulis). Items with reduplication, or whose surface form cannot be
   derived from the reference morphemes, are excluded (47 of 354).
4. **Significance**: exact McNemar test on paired per-word correctness; paired bootstrap for metric differences.

(Hapus Cohen's Kappa.)

## 5. §5.1 dan §5.4 (ganti isi)

**§5.1 Overall performance (N = 354)**

| Metric | Score | 95% CI |
|---|---|---|
| Word accuracy | 64.41% (228/354) | 59.32–69.49 |
| Morpheme precision / recall / F1 | 84.61 / 68.21 / 75.53 | – |
| Stem accuracy | 71.19% | – |
| Unsegmented outputs | 76 words | – |

Kalimat pembanding "no segmentation" boleh dipertahankan dengan framing jujur:
"A trivial no-segmentation baseline is correct on 1.4% of items."

**§5.4 Comparison with Morfessor (ganti seluruh subbagian)**

> Morfessor produces surface segments, whereas our reference is canonical (meN~per~baik~i), so exact match
> against canonical forms is not a meaningful comparison. We therefore evaluate both systems on surface
> morpheme boundaries (Section 4.2). Morfessor Baseline (Virpioja et al., 2013) was trained with default
> parameters on 329,551 tokens (17,759 types) of running text: our Wikipedia sample plus the SmSA training
> texts. Test words were not added to the training data (143 of the test words occur naturally in the corpus).
> We report the token-count and type-count training variants.

| System (N = 307) | Boundary P | Boundary R | Boundary F1 [95% CI] | Fully correct |
|---|---|---|---|---|
| **ModernKataKupas** | 97.7 | 75.4 | **85.1** [81.3, 88.5] | 73.9% |
| Morfessor (types) | 71.9 | 85.4 | 78.1 [75.2, 80.7] | 51.5% |
| Morfessor (tokens) | 74.5 | 54.8 | 63.1 [59.4, 67.0] | 35.5% |
| No segmentation | – | 0.0 | 0.0 | 1.6% |

> ModernKataKupas is more precise (97.7 vs 71.9; only 7 of 307 words receive a spurious boundary), while
> Morfessor-types has higher recall. Morfessor tends to split loanword roots (*meng|in|ter|pre|tasi|kan*), whereas
> ModernKataKupas' errors are mostly omissions: 59 of the 307 words are left unsegmented, typically when the root
> is missing from its lexicon. A further 17 predictions contain a reduplication analysis that cannot be mapped to
> the surface (e.g. *memasak* → masak~rp); these are scored as unsegmented. The difference in fully correct segmentations is significant
> (exact McNemar, b = 102, c = 33, p = 2.2×10⁻⁹). Because the nasal-prefix convention could favour the rule-based
> system, we also evaluate the 188 items without meN-/peN-. The ranking is unchanged (F1 88.3 vs 81.9).

(Hapus tabel agreement 46/206/5/103, klaim "+55.83%", dan kalimat "Morfessor ... cannot capture" yang terlalu kuat.)

## 6. §5.8 Downstream (SmSA)

Lihat bagian **Downstream** di akhir dokumen ini (diisi dari `downstream_significance.json`).

## 7. §5.5 Wikipedia (ganti tabel + poin diskusi 1 & 3)

| Metric | Value |
|---|---|
| Text | 504 lines, 11,021 tokens, 2,631 word types |
| Types segmented | 924 (35.1%) |
| Root OOV (recovered root not in root/loanword lexicon) | 717 (27.3%) |

> Segmentation rate is not accuracy: whether the 924 segmentations are correct has not been measured.
> A random sample of 200 types is included in the annotation package for this purpose.

Hapus "100% coverage" dan klaim "many OOV words are still correctly segmented", yang tidak diukur.

## 8. §5.6, §5.7

- §5.6: ganti tabel dengan `paper_numbers.json → intrinsic.per_category`. Hapus framing "significantly above random
  (lower CI > 50%)". Catat bahwa *compound_reduplication* 0/20 terutama karena label LLM yang tidak wajar
  (mis. *anak-cucu-cicit* → `anak~ulg~cucu~ulg~cicit`). Ini justru argumen untuk validasi manusia.
- §5.7 (ablation, error analysis): angka di naskah tidak cocok dengan berkas mana pun. **Jalankan ulang setelah gold
  final**, atau hapus subbagian ini dari versi yang dikirim.

## 9. Lain-lain

- §4.6: "pytest with 93 test cases" → 146 tests. "100% mypy type-safe" perlu dicek ulang sebelum diklaim.
- §4.7 Reproducibility: ganti perintah dengan dua skrip di atas.
- §5.2/5.3: korpus 10.000 kata **sintetis** (afiksasi acak) dan alignment BPE hanya pada 24 sampel. Nyatakan
  sebagai keterbatasan, atau ulangi pada teks nyata.
- Referensi: ikuti `REFERENCES_AUDIT.md` (6 koreksi, 6 sitasi hilang, Swasono 2016 hapus, tambah Morfessor 2.0 & IndoNLU).
- **Lisensi kamus:** README Sastrawi menyebut kamus kata dasarnya berasal dari Kateglo (CC-BY-NC-SA 3.0), sedangkan
  paket ini MIT dan menyertakan `kata_dasar.txt`. Perlu dicek sebelum klaim "open-source, MIT" dan pendaftaran HKI.
