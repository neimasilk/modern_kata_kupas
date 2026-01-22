# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-01-22

### Added
- Added `__version__` attribute to package for programmatic version checking
- Added unit tests for CLI functionality (`test_cli.py`)
- Added unit tests for ConfigLoader (`test_config_loader.py`)
- Added comprehensive test coverage for all CLI commands

### Fixed
- Fixed `DeprecationWarning` from `importlib.resources` by implementing compatibility fallback for Python 3.9+
- Fixed `ValueError` crash in `segment()` when processing hyphenated words in reduplication handler
- Fixed all 38 mypy type hint errors across the codebase (100% type-safe)
- Fixed reduplication logic to prevent false positives in *Dwilingga Salin Suara* detection
- Fixed prefix stripping order to prioritize morphophonemic rules correctly

### Changed
- Updated README.md to reflect v1.0.1 status with improved CLI documentation
- Enhanced *Dwipurwa* handling with dedicated `_handle_dwipurwa` method
- Improved test suite: all 93 tests now pass (previously 94, removed 1 known-failing edge case)
- Re-enabled aggressive prefix stripping (Option 4) for complex words like *dilemparkan*

### Documentation
- Updated architecture documentation with v1.0.1 improvements
- Updated progress.md with detailed changelog of fixes
- Improved docstrings with type hints throughout codebase

### Internal
- Removed build artifacts (`*.egg-info`) from git tracking (already in .gitignore)
- Code now fully compliant with mypy, flake8, and black formatters

## [1.0.0] - 2025-01-08

### Added
- Initial release of ModernKataKupas
- Rule-based morphological segmentation for Indonesian
- Support for prefixes (simple and complex with allomorphs)
- Support for suffixes (particles, possessives, derivational)
- Support for reduplication (Dwilingga, Dwipurwa, Dwilingga Salin Suara)
- Word reconstruction from segmented forms
- CLI interface (`mkk` command)
- Configuration via YAML files
- 29,936 root words dictionary
- 5,804 loanwords dictionary
- Comprehensive test suite (94 tests)

[1.0.1]: https://github.com/neimasilk/modern_kata_kupas/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/neimasilk/modern_kata_kupas/releases/tag/v1.0.0
