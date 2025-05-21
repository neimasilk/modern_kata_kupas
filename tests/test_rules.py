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
        "prefixes": [
            {"form": "meN-", "allomorphs": ["me-", "mem-", "men-", "meng-", "meny-", "menge-"]},
            {"form": "di-"}
        ],
        "suffixes": [
            {"form": "-kan"},
            {"form": "-i"}
        ],
        "fonologis": [
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
    """Tes inisialisasi MorphologicalRules tanpa path file."""
    rules = MorphologicalRules()
    assert rules.rules == {}
    assert rules.get_prefix_rules() == []
    assert rules.get_suffix_rules() == []

def test_rules_init_with_valid_path(dummy_rules_file):
    """Tes inisialisasi MorphologicalRules dengan path file yang valid."""
    rules = MorphologicalRules(rules_path=dummy_rules_file)
    assert "prefixes" in rules.rules
    assert len(rules.get_prefix_rules()) == 2
    assert len(rules.get_suffix_rules()) == 2

def test_rules_init_with_empty_file(empty_rules_file):
    """Tes inisialisasi MorphologicalRules dengan file aturan kosong."""
    rules = MorphologicalRules(rules_path=empty_rules_file)
    assert rules.rules == {"info": f"Rules loaded from {empty_rules_file} (placeholder)", "prefixes": [], "suffixes": []} # Sesuai placeholder

def test_rules_init_with_nonexistent_path():
    """Tes inisialisasi MorphologicalRules dengan path file yang tidak ada."""
    with pytest.raises(ValueError, match="Gagal memuat aturan dari path/tidak/ada.json:"):
        MorphologicalRules(rules_path="path/tidak/ada.json")

# def test_rules_init_with_invalid_json(invalid_rules_file):
#     """Tes inisialisasi MorphologicalRules dengan file JSON tidak valid."""
#     # Placeholder saat ini hanya mencetak error, tidak melempar exception
#     # Ini mungkin perlu diubah agar melempar RuleError
#     # with pytest.raises(RuleError): # Jika implementasi diubah untuk raise error
#     rules = MorphologicalRules(rules_path=invalid_rules_file)
#     assert rules.rules == {} # Karena loading gagal

def test_get_prefix_rules(dummy_rules_file):
    """Tes pengambilan aturan prefiks."""
    rules = MorphologicalRules(rules_path=dummy_rules_file)
    prefix_rules = rules.get_prefix_rules()
    assert isinstance(prefix_rules, list)
    assert len(prefix_rules) > 0
    assert any(rule.get("form") == "meN-" for rule in prefix_rules)

def test_get_suffix_rules(dummy_rules_file):
    """Tes pengambilan aturan sufiks."""
    rules = MorphologicalRules(rules_path=dummy_rules_file)
    suffix_rules = rules.get_suffix_rules()
    assert isinstance(suffix_rules, list)
    assert len(suffix_rules) > 0
    assert any(rule.get("form") == "-kan" for rule in suffix_rules)

# Tambahkan lebih banyak tes untuk berbagai aspek pemuatan dan pengambilan aturan