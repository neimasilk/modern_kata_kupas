# ModernKataKupas — instruksi untuk Claude Code

Library Python segmentasi morfologi bahasa Indonesia (PyPI `modern-kata-kupas`, MIT). Kode di `src/modern_kata_kupas/`,
tes di `tests/`, eksperimen paper di `experiments/`, dokumen proyek dan draf paper di `memory-bank/`.

## Baca dulu
- **`REVIEW_2026-09-23.md`**: temuan review + tabel status perbaikan. Mulai dari sini.
- Angka naskah HANYA dari `experiments/paper_numbers.py` dan `experiments/downstream_significance.py` (lihat `experiments/results/NUMBERS_AUDIT.md`).

## Aturan
- Tes: `python -m pytest -q` (baseline 23 Sep 2026 sore: 146 passed; `experiments/test_deepseek.py` sudah diganti nama agar tak memanggil API). Jangan commit kalau tes merah.
- Perubahan pada metrik/evaluasi: test-first, dan catat perintah yang menghasilkan setiap angka yang dikutip naskah.
- Jangan mengarang angka atau mendeskripsikan isi referensi yang belum diperoleh. Setiap referensi harus punya DOI/URL resmi.
- Gold standard: AI tidak boleh mengisi atau memvalidasi label; itu pekerjaan anotator manusia.
- Naskah jurnal kini dipimpin rekan (Amien penulis kedua). Perbaikan di sini = menyiapkan bukti dan angka yang benar.
