# Panduan Prioritas 2: Dictionary Curation

**Target:** Programmer Junior
**Estimasi Waktu:** 4-8 jam (bisa dilakukan bertahap)
**Kompleksitas:** Sedang (memerlukan pengetahuan bahasa Indonesia)

---

## 📋 Daftar Isi

1. [Tujuan dan Overview](#tujuan-dan-overview)
2. [Langkah 2.1: Audit kata_dasar.txt](#langkah-21-audit-kata_dasartxt)
3. [Langkah 2.2: Expand loanwords.txt](#langkah-22-expand-loanwordstxt)
4. [Langkah 2.3: Testing & Validation](#langkah-23-testing--validation)

---

## Tujuan dan Overview

### 🎯 Mengapa Dictionary Curation Penting?

Kualitas segmentasi ModernKataKupas sangat bergantung pada kamus kata dasar. Masalah umum:

1. **False Positives**: Kata yang bukan root word masuk ke `kata_dasar.txt`
   - Contoh: "bermain" (seharusnya root: "main", bukan "bermain")
   - Akibat: `segment("bermain")` → `"bermain"` (tidak tersegmentasi)
   - Seharusnya: `segment("bermain")` → `"ber~main"`

2. **Missing Roots**: Root word yang umum tidak ada di kamus
   - Contoh: "taruh" tidak ada di kamus
   - Akibat: `segment("mempertaruhkan")` → `"mempertaruhkan"` (tidak tersegmentasi)
   - Seharusnya: `segment("mempertaruhkan")` → `"meN~per~taruh~kan"`

3. **Outdated Loanwords**: Kata serapan modern tidak ada
   - Contoh: "podcast", "vlog", "livestream"
   - Akibat: Tidak bisa segmentasi "mem-podcast", "nge-vlog"

### 📊 Status Saat Ini

```
kata_dasar.txt:  29,936 entries
loanwords.txt:   5,804 entries
```

### 🎯 Target Setelah Curation

```
kata_dasar.txt:  ~28,000-29,000 entries (cleaned)
loanwords.txt:   ~6,500-7,000 entries (expanded)
```

---

## Langkah 2.1: Audit kata_dasar.txt

### Tujuan
Membersihkan `kata_dasar.txt` dari entries yang salah/ambigu.

### Prasyarat
- Text editor (VS Code, Sublime, atau nano)
- Python 3.8+
- Pemahaman morfologi bahasa Indonesia

---

### 📝 Step 2.1.1: Backup Original File

**CRITICAL:** Selalu backup sebelum edit!

```bash
# Navigasi ke data directory
cd /home/user/modern_kata_kupas/src/modern_kata_kupas/data

# Create backup dengan timestamp
cp kata_dasar.txt kata_dasar.txt.backup.$(date +%Y%m%d)

# Verifikasi backup
ls -lh kata_dasar.txt*
```

**Expected Output:**
```
-rw-r--r-- 1 user user 236K Jan 22 10:00 kata_dasar.txt
-rw-r--r-- 1 user user 236K Jan 22 10:00 kata_dasar.txt.backup.20260122
```

✅ Backup created!

---

### 🔍 Step 2.1.2: Identify Problematic Entries

**A. Find Words with Prefixes** (likely false positives)

```bash
# Cari kata yang mulai dengan prefix umum
grep "^ber" kata_dasar.txt | head -20
grep "^meN" kata_dasar.txt | head -20  # Note: will find "men", "mem", etc.
grep "^di" kata_dasar.txt | head -20
grep "^ter" kata_dasar.txt | head -20
grep "^per" kata_dasar.txt | head -20
grep "^ke" kata_dasar.txt | head -20
```

**Expected:** List of potential false positives

Contoh output:
```
bermain
berhasil
berjalan
...
```

❓ **Cara Analisis:**

Untuk setiap kata, tanya:
1. Apakah ini BENAR-BENAR kata dasar?
2. Atau ini kata berimbuhan yang masuk salah?

**Contoh Decision Tree:**

| Kata | Root? | Prefix? | Keep? | Alasan |
|------|-------|---------|-------|---------|
| bermain | ❌ | ber- + main | ❌ Remove | "main" adalah root |
| benar | ✅ | - | ✅ Keep | "benar" memang kata dasar |
| bersih | ✅ | - | ✅ Keep | "bersih" adalah kata dasar (bukan ber+sih) |
| berjalan | ❌ | ber- + jalan | ❌ Remove | "jalan" adalah root |

**B. Find Words with Suffixes**

```bash
# Kata yang berakhir dengan suffix umum
grep "an$" kata_dasar.txt | head -30
grep "kan$" kata_dasar.txt | head -30
grep "i$" kata_dasar.txt | head -30
```

Analisis sama seperti prefixes.

**C. Create Suspect List**

```bash
# Simpan suspects ke file untuk review manual
grep "^ber" kata_dasar.txt > suspects_ber.txt
grep "an$" kata_dasar.txt > suspects_an.txt
grep "kan$" kata_dasar.txt > suspects_kan.txt

# Count
wc -l suspects_*.txt
```

---

### ✏️ Step 2.1.3: Manual Review & Cleanup

**A. Setup Review Process**

Buat spreadsheet atau text file untuk tracking:

```bash
# Create review log
cat > review_log.txt << EOF
# Dictionary Review Log
# Date: $(date)
# Reviewer: [Your Name]

## Words Removed
Format: word|reason|replacement_root

## Words Added
Format: word|reason

## Words Modified
Format: old_word|new_word|reason

EOF
```

**B. Review Systematic Categories**

Review per kategori untuk efisiensi:

**Kategori 1: ber- prefix candidates**

```bash
# Open suspects file
nano suspects_ber.txt
```

Manual review checklist:
- [ ] Baca setiap kata
- [ ] Cek: apakah root-nya ada di dictionary?
- [ ] Jika ya dan kata ini = ber+root → mark for removal
- [ ] Jika kata dasar genuine (seperti "benar") → keep

**Example workflow:**

```
bermain → root "main" ada? → YES → REMOVE → log "bermain|ber+main|main"
benar → root "nar" ada? → NO → benar IS root → KEEP
bersih → root "sih" ada? → NO → bersih IS root → KEEP
berjalan → root "jalan" ada? → YES → REMOVE → log "berjalan|ber+jalan|jalan"
```

**C. Create Removal List**

```bash
# Buat file dengan words to remove
cat > words_to_remove.txt << EOF
bermain
berjalan
berkata
# ... dst (add kata-kata yang salah)
EOF
```

**D. Execute Removal**

```bash
# Gunakan script Python untuk safe removal
python3 << 'SCRIPT'
# Read original
with open('kata_dasar.txt', 'r', encoding='utf-8') as f:
    words = set(line.strip() for line in f if line.strip())

# Read removal list
with open('words_to_remove.txt', 'r', encoding='utf-8') as f:
    to_remove = set(line.strip() for line in f if line.strip() and not line.startswith('#'))

# Remove
cleaned = words - to_remove

# Sort and save
with open('kata_dasar_cleaned.txt', 'w', encoding='utf-8') as f:
    for word in sorted(cleaned):
        f.write(word + '\n')

print(f"Original: {len(words)} words")
print(f"Removed: {len(to_remove)} words")
print(f"Cleaned: {len(cleaned)} words")
SCRIPT
```

**Expected Output:**
```
Original: 29936 words
Removed: 237 words
Cleaned: 29699 words
```

**E. Verify Cleaned Dictionary**

```bash
# Cek beberapa removal berhasil
grep "^bermain$" kata_dasar_cleaned.txt
# Expected: no output (word removed)

grep "^main$" kata_dasar_cleaned.txt
# Expected: main (root word exists)

# Cek genuine root words masih ada
grep "^benar$" kata_dasar_cleaned.txt
# Expected: benar
```

---

### 🔬 Step 2.1.4: Test Impact of Changes

**A. Create Test Script**

```bash
# Buat test script
cat > test_dictionary_impact.py << 'EOF'
#!/usr/bin/env python3
"""Test impact of dictionary changes on segmentation."""

from modern_kata_kupas import ModernKataKupas

# Test words that should be affected by cleanup
test_cases = [
    ("bermain", "ber~main"),  # Should now segment (if "bermain" was removed)
    ("berjalan", "ber~jalan"),
    ("makanan", "makan~an"),
    ("menulis", "meN~tulis"),
    # Add more test cases
]

# Initialize with old dict
mkk_old = ModernKataKupas(dictionary_path="kata_dasar.txt")

# Initialize with cleaned dict
mkk_new = ModernKataKupas(dictionary_path="kata_dasar_cleaned.txt")

print("=" * 60)
print("DICTIONARY CLEANUP IMPACT TEST")
print("=" * 60)

changes = 0
for word, expected in test_cases:
    result_old = mkk_old.segment(word)
    result_new = mkk_new.segment(word)

    if result_old != result_new:
        changes += 1
        status = "✓" if result_new == expected else "?"
        print(f"{status} {word}")
        print(f"  Old: {result_old}")
        print(f"  New: {result_new}")
        print(f"  Expected: {expected}")
        print()

print(f"Total changes: {changes}/{len(test_cases)}")
EOF

chmod +x test_dictionary_impact.py
```

**B. Run Test**

```bash
python3 test_dictionary_impact.py
```

**Expected Output:**
```
============================================================
DICTIONARY CLEANUP IMPACT TEST
============================================================
✓ bermain
  Old: bermain
  New: ber~main
  Expected: ber~main

✓ berjalan
  Old: berjalan
  New: ber~jalan
  Expected: ber~jalan

Total changes: 2/4
```

**C. Validate Against Full Test Suite**

```bash
# Copy cleaned dict over original (after satisfied with results)
# BACKUP FIRST!
cp kata_dasar.txt kata_dasar.txt.pre_cleanup_backup
cp kata_dasar_cleaned.txt kata_dasar.txt

# Run full test suite
cd /home/user/modern_kata_kupas
python3 -m pytest tests/ -v

# Check results
```

⚠️ **Expected:** Some tests might fail if they depended on the old (incorrect) dictionary.

**Action if tests fail:**
1. Review failing tests
2. Determine if:
   - Test expectations need update (test was wrong)
   - Dictionary change was too aggressive (revert specific words)
3. Update tests OR revert problematic dictionary changes

---

### 📊 Step 2.1.5: Document Changes

```bash
# Create documentation
cat > DICTIONARY_CHANGELOG.md << EOF
# Dictionary Changelog

## v1.0.2-alpha ($(date +%Y-%m-%d))

### kata_dasar.txt Changes

#### Removed (False Positives)
Total removed: XXX entries

**Reason: Derived words with ber- prefix**
- bermain → use "main"
- berjalan → use "jalan"
- berkata → use "kata"
(list all removals)

**Reason: Derived words with -an suffix**
- makanan → use "makan"
(if any)

#### Added (Missing Roots)
Total added: XXX entries

- taruh (reason: common root, missing)
- (list all additions)

### Impact
- Original entries: 29,936
- Removed: XXX
- Added: YYY
- Final count: ZZZ

### Verification
- All tests passing: [YES/NO]
- Spot check on 100 random words: PASS
- Regression test on known good segmentations: PASS

EOF
```

---

### ✅ Kriteria Selesai Step 2.1
- [ ] kata_dasar.txt backed up
- [ ] Systematic review completed for major categories
- [ ] Removal list created and executed
- [ ] Impact testing completed
- [ ] Full test suite runs (with updated expectations if needed)
- [ ] Changes documented in DICTIONARY_CHANGELOG.md
- [ ] Cleaned dictionary committed to git

---

## Langkah 2.2: Expand loanwords.txt

### Tujuan
Menambahkan kata serapan modern agar dapat disegmentasi dengan afiks Indonesia.

### 📝 Step 2.2.1: Identify Missing Loanwords

**A. Collect Candidates from Common Domains**

Buat daftar kandidat per domain:

```bash
cat > loanword_candidates.txt << EOF
# Technology
podcast
vlog
livestream
streaming
coding
debugging
testing
framework
library
database
cloud
server
client
browser
website
email
smartphone
tablet
laptop
wifi
bluetooth
software
hardware
startup
fintech
e-commerce

# Social Media
influencer
follower
subscriber
content
creator
viral
trending
hashtag
story
reels
feed

# Business
meeting
deadline
presentation
report
target
marketing
branding
launching

# Daily Life
shopping
parking
jogging
cycling
selfie

# Food & Drink
burger
pizza
pasta
sushi
steak
coffee
cappuccino
latte

# Education
workshop
seminar
webinar
training
tutorial
course
quiz

EOF
```

**B. Check Which Are Missing**

```bash
# Script to check missing loanwords
python3 << 'SCRIPT'
with open('loanword_candidates.txt', 'r') as f:
    candidates = [line.strip() for line in f if line.strip() and not line.startswith('#')]

with open('loanwords.txt', 'r', encoding='utf-8') as f:
    existing = set(line.strip() for line in f)

missing = [w for w in candidates if w not in existing]

print(f"Total candidates: {len(candidates)}")
print(f"Already in loanwords: {len(candidates) - len(missing)}")
print(f"Missing: {len(missing)}")
print("\nMissing words:")
for word in sorted(missing):
    print(f"  {word}")
SCRIPT
```

---

### 📝 Step 2.2.2: Validate and Add Loanwords

**A. Validate Each Candidate**

Untuk setiap kata, verifikasi:

1. ✅ Kata ini memang digunakan dalam bahasa Indonesia?
2. ✅ Kata ini bisa menerima afiks Indonesia?
   - Contoh: "nge-vlog", "mem-posting", "di-upload"
3. ✅ Ejaan sudah sesuai KBBI/umum?

**B. Create Additions File**

```bash
# Buat file words to add (setelah validasi manual)
cat > loanwords_to_add.txt << EOF
# Verified loanwords to add
# Format: word (one per line)

podcast
vlog
streaming
coding
debugging
# ... dst (only validated words)
EOF
```

**C. Add to loanwords.txt**

```bash
# Backup first
cp loanwords.txt loanwords.txt.backup.$(date +%Y%m%d)

# Append new words
cat loanwords_to_add.txt >> loanwords.txt

# Sort and remove duplicates
sort -u loanwords.txt -o loanwords_sorted.txt
mv loanwords_sorted.txt loanwords.txt

# Verify
wc -l loanwords.txt
```

---

### 🧪 Step 2.2.3: Test New Loanwords

```bash
# Test script
python3 << 'SCRIPT'
from modern_kata_kupas import ModernKataKupas

mkk = ModernKataKupas()

# Test with Indonesian affixes
test_words = [
    ("nge-vlog", "loanword"),
    ("mem-posting", "loanword"),
    ("di-download", "loanword"),
]

print("Testing new loanwords with affixes:")
for word, word_type in test_words:
    result = mkk.segment(word)
    print(f"  {word} → {result}")
SCRIPT
```

---

### ✅ Kriteria Selesai Step 2.2
- [ ] Loanword candidates collected from multiple domains
- [ ] Each candidate validated (usage + affixation)
- [ ] loanwords.txt backed up
- [ ] New loanwords added and sorted
- [ ] Test cases created and passing
- [ ] Changes documented

---

## Langkah 2.3: Testing & Validation

### 📝 Step 2.3.1: Comprehensive Test Suite

```bash
# Run all tests
cd /home/user/modern_kata_kupas
python3 -m pytest tests/ -v --tb=short

# Check for failures
```

### 📝 Step 2.3.2: Regression Testing

Create regression test file:

```python
# tests/test_dictionary_regression.py
"""Regression tests for dictionary changes."""

import pytest
from modern_kata_kupas import ModernKataKupas

class TestDictionaryRegression:
    """Ensure dictionary changes don't break known good segmentations."""

    @pytest.fixture
    def mkk(self):
        return ModernKataKupas()

    def test_common_words_still_segment_correctly(self, mkk):
        """Known good segmentations should still work."""
        test_cases = [
            ("menulis", "meN~tulis"),
            ("makanan", "makan~an"),
            ("dibaca", "di~baca"),  # if "baca" is in dict
            # Add 50-100 known good cases
        ]

        for word, expected in test_cases:
            result = mkk.segment(word)
            assert result == expected, f"Regression: {word} → {result} (expected {expected})"
```

---

### 📝 Step 2.3.3: Commit Changes

```bash
# Add all changes
git add src/modern_kata_kupas/data/kata_dasar.txt
git add src/modern_kata_kupas/data/loanwords.txt
git add DICTIONARY_CHANGELOG.md
git add tests/test_dictionary_regression.py

# Commit
git commit -m "Dictionary curation: cleanup kata_dasar and expand loanwords

- Removed XXX false positive entries from kata_dasar.txt
- Added YYY missing root words
- Expanded loanwords.txt with ZZZ modern tech/social media terms
- Added regression tests for dictionary changes
- All tests passing

See DICTIONARY_CHANGELOG.md for detailed changes.

https://claude.ai/code/session_01UrLPDT3F8wYYRR628irrhG"

# Push
git push origin claude/review-codebase-vEfXh
```

---

## ✅ CHECKLIST PRIORITAS 2 SELESAI

- [ ] kata_dasar.txt reviewed and cleaned
- [ ] False positives removed (ber-, -an suffixes, etc.)
- [ ] Missing common roots added
- [ ] loanwords.txt expanded with modern terms
- [ ] All changes tested and validated
- [ ] Regression tests added
- [ ] DICTIONARY_CHANGELOG.md created
- [ ] Changes committed and pushed

**Estimated Impact:**
- Segmentation accuracy improvement: +5-10%
- Coverage of modern vocabulary: +15-20%
- False negative reduction: ~30-40%

---

**Next:** [Prioritas 3: Code Quality & Testing](panduan-prioritas-3-testing.md)
