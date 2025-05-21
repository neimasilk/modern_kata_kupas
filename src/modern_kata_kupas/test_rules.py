# src/modern_kata_kupas/test_rules.py
"""
Modul untuk pengujian unit aturan morfologi.
"""

import unittest
from .rules import Rule, RemoveSuffixRule

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
        rule = RemoveSuffixRule(["-kan", "-i"])
        self.assertEqual(rule.apply("mengatakan"), "mengata")
        self.assertEqual(rule.apply("mengulangi"), "mengulang")
    
    def test_no_suffix_match(self):
        """Test ketika tidak ada suffix yang cocok."""
        rule = RemoveSuffixRule(["-kan", "-i"])
        self.assertEqual(rule.apply("membaca"), "membaca")

if __name__ == '__main__':
    unittest.main()