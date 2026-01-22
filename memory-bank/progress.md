# Progress ModernKataKupas

## Recent Updates

### 2026-01-22: Release Preparation v1.0.1
- **Version Bump**: Updated version to `v1.0.1` across `setup.py`, `__init__.py`, `cli.py`, and `README.md`.
- **Code Quality**: Resolved `DeprecationWarning`s from `importlib.resources` by implementing a compatible fallback mechanism for Python 3.9+ vs older versions.
- **Documentation**: Updated `README.md` to reflect the new version status.
- **Verification**: Verified existing test suite (including CLI and Config tests) passes with `pytest --cov`.
- **Memory Bank**: Updated status and progress logs.

### 2026-01-21 (Part 2): Code Quality Improvements
- **Fixed `mypy` Errors**: Resolved all 38 type hint errors across the codebase.
    - Updated `config_loader.py` with correct type casting and stubs ignore.
    - Fixed return types in `stemmer_interface.py` and `reconstructor.py`.
    - Added safety assertions in `rules.py` for file paths.
    - Corrected type annotations in `cli.py` and `separator.py`.
- **Verified Stability**: All 94 existing tests passed after refactoring for type safety.

### 2026-01-21 (Part 1): Fix Critical Bug & Logic Improvements
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
- Perform comprehensive review of `kata_dasar.txt` to remove potentially confusing entries.
- Publish v1.0.1 to GitHub and PyPI.
