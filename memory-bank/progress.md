# Progress Log

This file will track the progress of the ModernKataKupas project.

## Phase 0: Project Setup and Foundational Components

- [x] Step 0.1: Project Initialization
- [x] Step 0.2: Install Core Dependencies (termasuk pembuatan modul inti, tes dasar, dan pembaruan __init__.py)
- [x] Step 0.3: Root Word Dictionary Management Module
- [x] Step 0.4: Affix Rule Repository Management Module
- [x] Step 0.5: String Alignment Utility Module (Dimulai)
- [x] Step 1.2: Stemmer Interface Module
- [x] Step 1.3: Main Separator Class Structure (`ModernKataKupas`)
- [x] Step 1.4: Basic Suffix Stripping (Particles and Possessives)
- [x] Step 1.5: Basic Derivational Suffix Stripping (`-kan`, `-i`, `-an`)
- [x] Step 1.6: Basic Prefix Stripping (Simple, Non-Morphophonemic: `di-`, `ke-`, `se-`)

## Phase 2: Advanced Morphological Processing

- [x] Step 2.1: Advanced Prefix Stripping (meN-, peN-) with Morphophonemic Rules
- [x] Step 2.2: Advanced Prefix Stripping (ber-, ter-, per-) with Morphophonemic Rules
- [x] Step 2.3: Handling Layered Prefixes and Suffixes (Confixes)

## Phase 3: Reduplication and Reconstruction

**Objective:** Implement robust handling for various reduplication types and the word reconstruction functionality.

- [x] Step 3.1: Implement Full Reduplication Logic (Dwilingga)
- [x] Step 3.2: Implement Dwilingga Salin Suara Logic
- [x] Step 3.3: Implement Dwipurwa Logic
- [x] Step 3.4: Word Reconstruction Functionality

## Phase 4: Handling Loanwords, Packaging, and Finalization

**Objective:** Enhance the segmenter to correctly handle loanwords with Indonesian affixes, finalize packaging, documentation, and testing for V1.0.

- [x] Step 4.1: Loanword Affixation Handling
- [x] Step 4.2: Documentation and Testing
    - [x] Step 4.2.1: Dokumentasi Heuristik Ambiguitas (SELESAI per 25 Mei 2024)
- [x] Step 4.3: Test Case Expansion
    - [x] Step 4.3.1: Identifikasi & Tambah Kasus Uji Morfologi Kompleks (SELESAI per 25 Mei 2024)
    - [x] Step 4.3.2: Tambah Kasus Uji Tepi (Edge Cases) (SELESAI per 25 Mei 2024)
- [x] Step 4.4: API and Documentation Review
    - [x] Step 4.4.1: Review Final API Publik & Docstrings Inti (SELESAI per 25 Mei 2024)
    - [x] Step 4.4.2: Update Komprehensif `README.md` (Iterasi Awal) (SELESAI per 25 Mei 2024)
- [x] Step 4.5: Packaging
    - [x] Step 4.5.1: Finalisasi `setup.py` dan Build Paket Awal (SELESAI per 25 Mei 2024) - `setup.py` V1.0.0 finalized, package built (`sdist`, `bdist_wheel`), `package_data` verified.
    - [x] Step 4.5.2: Uji Instalasi Paket Lokal (SELESAI per 25 Mei 2024) - Package installed from wheel in new venv, basic functionality and data access verified.
- [x] Step 4.6: Documentation Finalization
    - [x] Step 4.6.1: Update Detail Final `architecture.md` (SELESAI per 25 Mei 2024) - `architecture.md` updated for V1.0 architecture, packaging, and data access.
    - [x] Step 4.6.2: Final Review `README.md` dan Verifikasi Contoh (SELESAI per 25 Mei 2024) - `README.md` reviewed and updated. Examples verified (with notes on `verify_segment_examples.py` behavior).
- [x] Step 4.7: Final Testing and Status Update
    - [x] Step 4.7.1: Update Dokumen Status dan Progress (SELESAI per 25 Mei 2024) - This document and `status-todolist-saran.md` updated.
    - [x] Step 4.7.2: Uji `pytest` Final (SELESAI per 25 Mei 2024) - All 91 `pytest` tests passed.
- [x] Step 4.8: Release v1.0.0 (SELESAI per 8 Jan 2025)
    - [x] Step 4.8.1: Tagging Git v1.0.0 - Tag `v1.0.0` dibuat dan di-push ke repository.
    - [x] Step 4.8.2: Build Package dengan Perubahan Terbaru - Package rebuilt dengan `setup.py sdist bdist_wheel`.
    - [x] Step 4.8.3: Update Dokumentasi Rilis - Progress log dan status document diupdate.

---

## Phase 5: Post-Release V1.0 (Perencanaan Masa Depan)

**Objective:** Perbaikan pasca-rilis dan pengembangan fitur untuk versi selanjutnya.

### Langkah Selanjutnya (V1.1 atau V2.0):

- [ ] Step 5.1: GitHub Release Formal
    - [ ] Buat Release di GitHub dengan tag v1.0.0
    - [ ] Upload artefak build (.tar.gz dan .whl) ke release

- [ ] Step 5.2: PyPI Publishing
    - [ ] Setup PyPI API token
    - [ ] Upload package ke PyPI menggunakan `twine upload dist/*`

- [ ] Step 5.3: Post-Release Improvements (V1.1)
    - [ ] Analisis feedback dari pengguna
    - [ ] Perbaiki edge cases yang ditemukan
    - [ ] Tambahkan lebih banyak kata dasar (jika perlu)
    - [ ] Optimasi performa

- [ ] Step 5.4: Future Enhancements (V2.0)
    - [ ] Context-aware stemming (menggunakan konteks kalimat)
    - [ ] Machine learning assisted disambiguation
    - [ ] Support untuk dialek/regional Bahasa Indonesia
    - [ ] API endpoint untuk web service