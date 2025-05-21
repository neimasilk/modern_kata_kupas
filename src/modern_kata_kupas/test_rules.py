# src/modern_kata_kupas/test_rules.py
"""
Modul untuk pengujian unit aturan morfologi.
"""

import unittest
from .rules import Rule, RemoveSuffixRule, MorphologicalRules

class TestRule(unittest.TestCase):
    """
    Kelas dasar untuk menguji Rule ABC.
    """
    def test_rule_is_abstract(self):
        """Test bahwa Rule adalah abstract class."""
        with self.assertRaises(TypeError):
            Rule()

class TestRemoveSuffixRule(unittest.TestCase):
    """
    Kelas untuk menguji RemoveSuffixRule.
    """
    def test_remove_suffix(self):
        """Test penghapusan suffix yang valid."""
        rule = RemoveSuffixRule(["kan", "i"])
        self.assertEqual(rule.apply("mengatakan"), "mengata")
        self.assertEqual(rule.apply("mengulangi"), "mengulang")
        
        # Test case untuk fitur 0.4
        self.assertEqual(rule.apply("meyakinkan"), "meyakin")
        self.assertEqual(rule.apply("melukai"), "meluka")
        self.assertEqual(rule.apply("membatukan"), "membatu")
        self.assertEqual(rule.apply("memasuki"), "memasuk")
    
    def test_no_suffix_match(self):
        """Test ketika tidak ada suffix yang cocok."""
        rule = RemoveSuffixRule(["-kan", "-i"])
        self.assertEqual(rule.apply("membaca"), "membaca")

class TestMorphologicalRules(unittest.TestCase):
    """
    Kelas untuk menguji MorphologicalRules.
    """
    
    def test_load_rules(self):
        """Test memuat aturan dari file JSON."""
        import tempfile
        import os
        
        # Buat file aturan dummy
        rules_data = {
            "prefixes": [{"form": "me-", "allomorphs": ["mem-", "men-"]}],
            "suffixes": [{"form": "-kan"}],
            "phonological": [{"pattern": "N-p", "replacement": "m-p"}]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            import json
            json.dump(rules_data, f)
            temp_path = f.name
        
        try:
            rules = MorphologicalRules(temp_path)
            self.assertEqual(len(rules.get_prefix_rules()), 1)
            self.assertEqual(len(rules.get_suffix_rules()), 1)
        finally:
            os.unlink(temp_path)
    
    def test_invalid_rules_file(self):
        """Test handling file aturan yang tidak valid."""
        with self.assertRaises(ValueError):
            MorphologicalRules("file_tidak_ada.json")

if __name__ == '__main__':
    unittest.main()