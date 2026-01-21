# Progress ModernKataKupas

## Recent Updates

### 2026-01-21: Fix Critical Bug & Logic Improvements
- **Fixed `ValueError` in `segment()`**: Resolved a crash caused by `_handle_reduplication` returning an incorrect number of values for hyphenated words.
- **Improved Reduplication Logic**:
    - Implemented dedicated `_handle_dwipurwa` method for partial reduplication in non-hyphenated words (e.g., *lelaki*).
    - Refined *Dwilingga Salin Suara* heuristics to prevent false positives (e.g., *rumah-rumah* identified as phonetic change).
    - Updated output format for phonetic reduplication to include the variant (e.g., `sayur~rs(~mayur)`).
    - Added *gotong-royong* to `config.yaml`.
- **Enhanced Affix Stripping**:
    - Re-enabled "Option 4" in `_strip_prefixes_detailed` to allow aggressive stripping for complex words like *dilemparkan*.
    - Optimized prefix stripping order (swapped Option 1 and 2) to prioritize reverse morphophonemics check, fixing segmentation for words like *menyapu*.
- **Test Suite Updates**:
    - Updated `tests/test_separator.py` expectations to reflect accurate segmentation for complex words (*dipersemakmurkan*, *berkejar-kejaran*).
    - Fixed idempotency test in `tests/test_reconstructor.py` by using standard form *mengomunikasikan*.
    - Verified all 94 tests pass.

### 2025-01-08: V1.0.0 Release
- Completed all Baby Steps for V1.0.
- Finalized `setup.py` and package build.
- Updated `README.md` with comprehensive documentation.
- All tests passing.
- Tagged `v1.0.0`.

## Pending Tasks
- Fix remaining `mypy` type hint errors (approx. 38 errors).
- Add unit tests for `cli.py` and `config_loader.py`.
- Perform comprehensive review of `kata_dasar.txt` to remove potentially confusing entries.
