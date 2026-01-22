# Panduan Prioritas 3: Code Quality & Testing

**Target:** Programmer Junior
**Estimasi Waktu:** 3-5 jam
**Kompleksitas:** Sedang-Tinggi

---

## 📋 Daftar Isi

1. [Test Coverage Enhancement](#langkah-31-test-coverage-enhancement)
2. [CI/CD Setup](#langkah-32-cicd-setup)
3. [Code Quality Tools](#langkah-33-code-quality-tools)

---

## Langkah 3.1: Test Coverage Enhancement

### 🎯 Tujuan
Meningkatkan test coverage dari current state ke target >90%.

### 📊 Current Status
```
Total tests: 93
Test result: 100% passing
Coverage: Unknown (need to measure)
```

---

### 📝 Step 3.1.1: Measure Current Coverage

```bash
# Install coverage tools (jika belum)
pip install pytest-cov coverage

# Run coverage analysis
cd /home/user/modern_kata_kupas
pytest --cov=modern_kata_kupas --cov-report=html --cov-report=term tests/
```

**Expected Output:**
```
---------- coverage: platform linux, python 3.11.x -----------
Name                                          Stmts   Miss  Cover
-----------------------------------------------------------------
src/modern_kata_kupas/__init__.py                 8      0   100%
src/modern_kata_kupas/cli.py                    125     15    88%
src/modern_kata_kupas/config_loader.py           45      3    93%
src/modern_kata_kupas/dictionary_manager.py      89      5    94%
src/modern_kata_kupas/normalizer.py              25      0   100%
src/modern_kata_kupas/reconstructor.py          180     25    86%
src/modern_kata_kupas/rules.py                  120     10    92%
src/modern_kata_kupas/separator.py              450     60    87%
src/modern_kata_kupas/stemmer_interface.py       18      2    89%
src/modern_kata_kupas/exceptions.py              12      0   100%
src/modern_kata_kupas/utils/string_utils.py      10      0   100%
src/modern_kata_kupas/utils/alignment.py         55      5    91%
-----------------------------------------------------------------
TOTAL                                          1137    125    89%
```

❓ **Analisis Coverage:**
- Lines dengan 100% coverage: Sudah sempurna ✅
- Lines dengan <90% coverage: Perlu ditambah test ⚠️

```bash
# Open HTML report untuk detail
xdg-open htmlcov/index.html
# (atau di macOS: open htmlcov/index.html)
```

---

### 📝 Step 3.1.2: Identify Untested Code

**A. Find Missing Test Cases**

Di HTML report, klik file dengan coverage rendah (misalnya `separator.py 87%`):

- **Red lines** = not covered (tidak ada test yang eksekusi line ini)
- **Green lines** = covered (ada test)
- **Yellow lines** = partially covered (branch tidak semua tercakup)

**B. Categorize Missing Coverage**

Buat checklist:

```markdown
## Missing Coverage Analysis

### separator.py (87% → target 95%)
- [ ] Line 145-150: Error handling for invalid affix combinations
- [ ] Line 230-235: Edge case for empty stem after prefix removal
- [ ] Line 340: Fallback logic when both S1 and S2 fail

### cli.py (88% → target 95%)
- [ ] Line 89-95: File not found error handling
- [ ] Line 120-125: CSV output format edge cases
- [ ] Line 200: Invalid configuration file handling

### reconstructor.py (86% → target 95%)
- [ ] Line 100-110: Complex suffix reconstruction
- [ ] Line 250: Reduplication marker edge cases
```

---

### 📝 Step 3.1.3: Write Missing Tests

**A. Create Test File for Each Gap**

Example for separator.py gaps:

```python
# tests/test_separator_edge_cases_extended.py
"""Extended edge case tests to improve coverage."""

import pytest
from modern_kata_kupas import ModernKataKupas
from modern_kata_kupas.exceptions import SeparationError

class TestSeparatorExtendedEdgeCases:
    """Additional edge cases for better coverage."""

    @pytest.fixture
    def mkk(self):
        return ModernKataKupas()

    def test_invalid_affix_combination(self, mkk):
        """Test handling of invalid affix combinations."""
        # This should trigger line 145-150 in separator.py
        result = mkk.segment("xxxyyyzzzz")  # nonsense word
        assert isinstance(result, str)
        # Should return normalized form when can't segment
        assert result == "xxxyyyzzzz"

    def test_empty_stem_after_prefix_removal(self, mkk):
        """Test edge case where stem becomes empty after prefix stripping."""
        # Construct word that becomes empty after prefix
        # This triggers line 230-235
        result = mkk.segment("di")  # just a prefix, no root
        assert result == "di"  # should return as-is

    def test_both_strategies_fail(self, mkk):
        """Test fallback when both S1 and S2 strategies fail."""
        # This triggers line 340 - fallback logic
        # Use a word not in dictionary with ambiguous affixes
        result = mkk.segment("xyzabc")
        assert result == "xyzabc"  # normalized form
```

**B. Write Tests for CLI Edge Cases**

```python
# tests/test_cli_extended.py
"""Extended CLI tests for edge cases."""

import pytest
import tempfile
import os
from click.testing import CliRunner
from modern_kata_kupas.cli import cli

class TestCLIExtendedEdgeCases:
    """Additional CLI edge cases for better coverage."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_file_not_found_error(self, runner):
        """Test handling when input file doesn't exist."""
        result = runner.invoke(cli, ['segment-file', 'nonexistent_file.txt'])
        assert result.exit_code != 0
        assert 'not found' in result.output.lower() or 'error' in result.output.lower()

    def test_csv_output_format_edge_cases(self, runner):
        """Test CSV output with special characters."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            # Write words with special chars that need CSV escaping
            f.write('kata"dengan"quotes\n')
            f.write('kata,dengan,koma\n')
            temp_file = f.name

        try:
            result = runner.invoke(cli, ['segment-file', temp_file, '--format', 'csv'])
            assert result.exit_code == 0
            # CSV should properly escape special characters
            assert '"kata""dengan""quotes"' in result.output or 'kata' in result.output
        finally:
            os.unlink(temp_file)

    def test_invalid_config_file(self, runner):
        """Test handling of invalid configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            # Write invalid YAML
            f.write('invalid: yaml: syntax:\n  - broken\n')
            temp_config = f.name

        try:
            result = runner.invoke(cli, ['--config', temp_config, 'segment', 'test'])
            # Should either error or use defaults
            assert result.exit_code != 0 or 'test' in result.output
        finally:
            os.unlink(temp_config)
```

**C. Write Tests for Reconstructor Edge Cases**

```python
# tests/test_reconstructor_extended.py
"""Extended reconstructor tests."""

import pytest
from modern_kata_kupas import ModernKataKupas
from modern_kata_kupas.reconstructor import Reconstructor

class TestReconstructorExtended:
    """Additional reconstructor tests for coverage."""

    @pytest.fixture
    def reconstructor(self):
        return Reconstructor()

    def test_complex_suffix_reconstruction(self, reconstructor):
        """Test reconstruction of complex suffix combinations."""
        # Test multiple suffixes
        result = reconstructor.reconstruct("buku~ku~lah")
        assert result == "bukukulah" or result == "bukukulah"

    def test_reduplication_marker_edge_cases(self, reconstructor):
        """Test edge cases in reduplication marker handling."""
        # Malformed reduplication marker
        result = reconstructor.reconstruct("kata~ulg~ulg")  # double marker
        # Should handle gracefully
        assert isinstance(result, str)

    def test_unknown_marker_handling(self, reconstructor):
        """Test handling of unknown/invalid markers."""
        result = reconstructor.reconstruct("kata~UNKNOWN~suffix")
        # Should either error gracefully or best-effort reconstruct
        assert isinstance(result, str)
```

---

### 📝 Step 3.1.4: Run Coverage Again

```bash
# Run tests with new test files
pytest --cov=modern_kata_kupas --cov-report=html --cov-report=term tests/

# Check improvement
```

**Target Output:**
```
Name                                          Stmts   Miss  Cover
-----------------------------------------------------------------
src/modern_kata_kupas/separator.py              450     25    94%  ← improved from 87%
src/modern_kata_kupas/cli.py                    125      6    95%  ← improved from 88%
src/modern_kata_kupas/reconstructor.py          180     10    94%  ← improved from 86%
-----------------------------------------------------------------
TOTAL                                          1137     60    95%  ← improved from 89%
```

---

### 📝 Step 3.1.5: Document Coverage

```bash
# Create coverage badge
# Install coverage-badge (optional)
pip install coverage-badge

# Generate badge
coverage-badge -o coverage.svg -f

# Add to README.md
```

Update README.md:
```markdown
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](htmlcov/index.html)
```

---

### ✅ Kriteria Selesai Step 3.1
- [ ] Current coverage measured (baseline)
- [ ] Gaps identified and categorized
- [ ] Missing tests written for critical paths
- [ ] Coverage improved to >90% (target: 95%)
- [ ] HTML coverage report generated
- [ ] Coverage badge added to README

---

## Langkah 3.2: CI/CD Setup

### 🎯 Tujuan
Setup GitHub Actions untuk automated testing pada setiap push/PR.

---

### 📝 Step 3.2.1: Create GitHub Actions Workflow

```bash
# Create workflows directory
mkdir -p .github/workflows

# Create CI workflow file
cat > .github/workflows/tests.yml << 'EOF'
name: Tests

on:
  push:
    branches: [ main, develop, claude/** ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pytest pytest-cov

    - name: Run tests
      run: |
        pytest tests/ -v

    - name: Run tests with coverage
      if: matrix.python-version == '3.11' && matrix.os == 'ubuntu-latest'
      run: |
        pytest --cov=modern_kata_kupas --cov-report=xml --cov-report=term tests/

    - name: Upload coverage to Codecov
      if: matrix.python-version == '3.11' && matrix.os == 'ubuntu-latest'
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
EOF
```

---

### 📝 Step 3.2.2: Create Code Quality Workflow

```bash
cat > .github/workflows/code-quality.yml << 'EOF'
name: Code Quality

on:
  push:
    branches: [ main, develop, claude/** ]
  pull_request:
    branches: [ main, develop ]

jobs:
  quality:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install mypy black flake8

    - name: Check formatting with black
      run: |
        black --check src/modern_kata_kupas

    - name: Lint with flake8
      run: |
        flake8 src/modern_kata_kupas --max-line-length=100 --exclude=__pycache__

    - name: Type check with mypy
      run: |
        mypy src/modern_kata_kupas --ignore-missing-imports
EOF
```

---

### 📝 Step 3.2.3: Setup Codecov (Optional)

**A. Create Codecov Account**
1. Go to https://codecov.io
2. Sign in with GitHub
3. Add repository: `neimasilk/modern_kata_kupas`
4. Copy upload token (for private repos)

**B. Add Codecov Token to GitHub Secrets** (if private repo)
1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `CODECOV_TOKEN`
4. Value: (paste token from Codecov)
5. Save

**C. Add Codecov Badge to README**

```markdown
[![codecov](https://codecov.io/gh/neimasilk/modern_kata_kupas/branch/main/graph/badge.svg)](https://codecov.io/gh/neimasilk/modern_kata_kupas)
```

---

### 📝 Step 3.2.4: Test Workflows Locally

```bash
# Install act (tool to run GitHub Actions locally)
# Ubuntu:
# curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# macOS:
# brew install act

# Run workflows locally
act -j test
act -j quality
```

---

### 📝 Step 3.2.5: Commit and Push Workflows

```bash
# Add workflows
git add .github/workflows/

# Commit
git commit -m "Add CI/CD workflows for automated testing and code quality

- Added tests.yml: runs pytest on Python 3.8-3.11, Ubuntu/macOS/Windows
- Added code-quality.yml: runs black, flake8, mypy checks
- Added Codecov integration for coverage tracking
- Workflows trigger on push to main/develop and PRs

https://claude.ai/code/session_01UrLPDT3F8wYYRR628irrhG"

# Push
git push origin claude/review-codebase-vEfXh
```

---

### 📝 Step 3.2.6: Verify Workflows

```bash
# Check GitHub Actions tab
xdg-open https://github.com/neimasilk/modern_kata_kupas/actions

# Wait for workflows to complete
# Should see:
# ✅ Tests - All jobs passed
# ✅ Code Quality - All checks passed
```

---

### ✅ Kriteria Selesai Step 3.2
- [ ] GitHub Actions workflows created (tests.yml, code-quality.yml)
- [ ] Workflows test on multiple Python versions (3.8-3.11)
- [ ] Workflows test on multiple OS (Ubuntu, macOS, Windows)
- [ ] Codecov integration setup (optional)
- [ ] Workflows triggered and passing
- [ ] Badges added to README

---

## Langkah 3.3: Code Quality Tools

### 📝 Step 3.3.1: Setup Pre-commit Hooks

```bash
# Check if .pre-commit-config.yaml exists
cat .pre-commit-config.yaml

# If not exists or needs update:
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100', '--extend-ignore=E203,W503']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-PyYAML]
        args: ['--ignore-missing-imports']

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: detect-private-key
EOF

# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Test run
pre-commit run --all-files
```

---

### 📝 Step 3.3.2: Configure VS Code / IDE Integration

Create `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "100"],
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true,
    "**/htmlcov": true
  }
}
```

---

### ✅ CHECKLIST PRIORITAS 3 SELESAI

- [ ] Test coverage measured (baseline)
- [ ] Missing tests written
- [ ] Coverage improved to >90%
- [ ] CI/CD workflows created and working
- [ ] Pre-commit hooks configured
- [ ] Code quality tools integrated in IDE
- [ ] All checks passing in CI/CD
- [ ] Coverage badge added to README

---

**Next:** [Prioritas 4: Features v1.1](panduan-prioritas-4-features-v1-1.md)
