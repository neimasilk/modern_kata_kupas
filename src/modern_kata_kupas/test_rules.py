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
        rule = RemoveSuffixRule("kan")
        self.assertEqual(rule.apply("mengatakan"), "mengata")
        # The following test for "mengulangi" with "i" will no longer be covered by this rule instance.
        # A separate test or parameterization would be needed if "i" is to be tested with RemoveSuffixRule.
        # For now, focusing on fixing the type error.
        # self.assertEqual(rule.apply("mengulangi"), "mengulang") 
        rule_i = RemoveSuffixRule("i") # Added for "i"
        self.assertEqual(rule_i.apply("mengulangi"), "mengulang")
        
        # Test case untuk fitur 0.4
        self.assertEqual(rule.apply("meyakinkan"), "meyakin") # Uses rule for "kan"
        self.assertEqual(rule_i.apply("melukai"), "meluka") # Changed to use rule_i for "i"
        self.assertEqual(rule.apply("membatukan"), "membatu") # Uses rule for "kan"
        self.assertEqual(rule_i.apply("memasuki"), "memasuk") # Changed to use rule_i for "i"
    
    def test_no_suffix_match(self):
        """Test ketika tidak ada suffix yang cocok."""
        rule = RemoveSuffixRule("-kan") 
        self.assertEqual(rule.apply("membaca"), "membaca")
        # Test with "-i" as well, if that was the original intent for the list
        rule_i_no_match = RemoveSuffixRule("-i")
        self.assertEqual(rule_i_no_match.apply("membaca"), "membaca")

class TestMorphologicalRules(unittest.TestCase):
    """
    Kelas untuk menguji MorphologicalRules.
    """
    
    def test_rules_init_no_path(self):
        """Test inisialisasi tanpa path aturan."""
        rules = MorphologicalRules()
        expected_rules = {
            "prefixes": [],
            "suffixes": [],
            "info": "Placeholder: MorphologicalRules initialized without specific rules file."
        }
        self.assertEqual(rules.rules, expected_rules)
    
    def test_rules_init_with_empty_file(self):
        """Test inisialisasi dengan file aturan kosong."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"prefixes": [], "suffixes": []}')
            temp_path = f.name
        
        try:
            rules = MorphologicalRules(temp_path)
            expected_rules = {
                "prefixes": [],
                "suffixes": []
            }
            self.assertEqual(rules.rules, expected_rules)
        finally:
            os.unlink(temp_path)
    
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