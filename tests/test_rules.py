# tests/test_rules.py
"""
Unit tests untuk MorphologicalRules.
"""

import pytest
import os
import json # Untuk membuat file aturan dummy
from modern_kata_kupas.rules import MorphologicalRules
from modern_kata_kupas.exceptions import RuleError

@pytest.fixture
def dummy_rules_file(tmp_path):
    """Membuat file aturan JSON dummy untuk tes."""
    rules_content = {
        "prefixes": {
            "meN-": [{"form": "meN-", "allomorphs": ["me-", "mem-", "men-", "meng-", "meny-", "menge-"]}],
            "di-": [{"form": "di-"}]
        },
        "suffixes": {
            "-kan": [{"form": "-kan"}],
            "-i": [{"form": "-i"}]
        },
        "fonologis": [ # This section is not directly used by prefix_rules/suffix_rules but part of all_rules
            {"pattern": "N-p", "replacement": "m-p"} 
        ]
    }
    file_path = tmp_path / "dummy_rules.json"
    with open(file_path, 'w') as f:
        json.dump(rules_content, f)
    return str(file_path)

@pytest.fixture
def empty_rules_file(tmp_path):
    """Membuat file aturan JSON dummy yang kosong untuk tes."""
    content = '''
    {
        "prefixes": [],
        "suffixes": []
    }
    '''
    file_path = tmp_path / "empty_rules.json"
    with open(file_path, 'w') as f:
        json.dump(json.loads(content), f)
    return str(file_path)

@pytest.fixture
def invalid_rules_file(tmp_path):
    """Membuat file aturan dengan format JSON tidak valid."""
    file_path = tmp_path / "invalid_rules.json"
    with open(file_path, 'w') as f:
        f.write("这不是一个JSON文件") # Not a JSON file
    return str(file_path)

def test_rules_init_no_path():
    """Tes inisialisasi MorphologicalRules tanpa path file, jika path eksplisit tidak ada."""
    # This test assumes AFFIX_RULES_PATH (default) does not exist or is empty/invalid during test execution
    # or that we want to test the state if loading fails.
    # For a true "no path given and default fails" scenario:
    # rules = MorphologicalRules(rules_file_path="non_existent_default.json") # Force failure
    # self.assertEqual(rules.all_rules, {"prefixes": [], "suffixes": []})
    # self.assertEqual(rules.prefix_rules, {})
    # self.assertEqual(rules.suffix_rules, {})
    with pytest.raises(FileNotFoundError):
        MorphologicalRules(rules_file_path="non_existent_default.json")

def test_rules_init_with_valid_path(dummy_rules_file):
    """Tes inisialisasi MorphologicalRules dengan path file yang valid."""
    rules = MorphologicalRules(rules_file_path=dummy_rules_file)
    assert "prefixes" in rules.all_rules # Check that the loaded content is in all_rules
    assert "meN-" in rules.prefix_rules  # Check specific prefix key
    assert "di-" in rules.prefix_rules
    assert len(rules.prefix_rules) == 2     # Check number of prefix rule groups (keys)
    assert "-kan" in rules.suffix_rules
    assert "-i" in rules.suffix_rules
    assert len(rules.suffix_rules) == 2     # Check number of suffix rule groups (keys)

def test_rules_init_with_empty_file(empty_rules_file):
    """Tes inisialisasi MorphologicalRules dengan file aturan kosong."""
    rules = MorphologicalRules(rules_file_path=empty_rules_file)
    # all_rules will contain the raw loaded content: {"prefixes": [], "suffixes": []}
    # _load_rules will try to iterate over these empty lists, resulting in empty dicts for prefix_rules and suffix_rules
    assert rules.all_rules == {"prefixes": [], "suffixes": []}
    assert rules.prefix_rules == {}
    assert rules.suffix_rules == {}

def test_rules_init_with_nonexistent_path():
    """Tes inisialisasi MorphologicalRules dengan path file yang tidak ada."""
    with pytest.raises(FileNotFoundError): # Changed ValueError to FileNotFoundError
        MorphologicalRules(rules_file_path="path/tidak/ada.json")

# Renamed test to reflect what it's testing now (structure of prefix_rules)
def test_loaded_prefix_rules_structure(dummy_rules_file):
    """Tes struktur prefix_rules setelah memuat aturan."""
    rules = MorphologicalRules(rules_file_path=dummy_rules_file)
    prefix_rules = rules.prefix_rules
    assert isinstance(prefix_rules, dict)
    assert len(prefix_rules) > 0
    assert "meN-" in prefix_rules # Check if "meN-" is a key
    assert isinstance(prefix_rules["meN-"], list) # Value should be a list of rule dicts
    assert isinstance(prefix_rules["meN-"][0], dict) # First item in list is a dict
    assert prefix_rules["meN-"][0].get("form") == "meN-"

# Renamed test to reflect what it's testing now (structure of suffix_rules)
def test_loaded_suffix_rules_structure(dummy_rules_file):
    """Tes struktur suffix_rules setelah memuat aturan."""
    rules = MorphologicalRules(rules_file_path=dummy_rules_file)
    suffix_rules = rules.suffix_rules
    assert isinstance(suffix_rules, dict)
    assert len(suffix_rules) > 0
    assert "-kan" in suffix_rules # Check if "-kan" is a key
    assert isinstance(suffix_rules["-kan"], list)
    assert isinstance(suffix_rules["-kan"][0], dict)
    assert suffix_rules["-kan"][0].get("form") == "-kan"

# Tambahkan lebih banyak tes untuk berbagai aspek pemuatan dan pengambilan aturan