import unittest
import os
import tempfile
import yaml
from modern_kata_kupas.config_loader import ConfigLoader

class TestConfigLoader(unittest.TestCase):
    def setUp(self):
        # Create a temporary config file for testing
        self.test_config = {
            "min_stem_lengths": {
                "possessive": 5,
                "derivational": 6,
                "particle": 4,
            },
            "dwilingga_salin_suara_pairs": [
                {"base": "testbase", "variant": "testvariant"}
            ],
            "features": {
                "enable_loanword_affixation": False,
                "enable_reduplication": True
            }
        }
        self.temp_config_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml', encoding='utf-8')
        yaml.dump(self.test_config, self.temp_config_file)
        self.temp_config_file.close()

    def tearDown(self):
        os.unlink(self.temp_config_file.name)

    def test_load_default_config(self):
        """Test loading the default configuration."""
        loader = ConfigLoader()
        # Check defaults (assuming default values from config_loader.py)
        self.assertEqual(loader.get_min_stem_length('possessive'), 3)
        self.assertEqual(loader.get_min_stem_length('derivational'), 4)
        self.assertTrue(loader.is_feature_enabled('enable_loanword_affixation'))

    def test_load_custom_config(self):
        """Test loading a custom configuration file."""
        loader = ConfigLoader(config_path=self.temp_config_file.name)
        
        # Check custom values
        self.assertEqual(loader.get_min_stem_length('possessive'), 5)
        self.assertEqual(loader.get_min_stem_length('derivational'), 6)
        self.assertEqual(loader.get_min_stem_length('particle'), 4)
        
        self.assertFalse(loader.is_feature_enabled('enable_loanword_affixation'))
        self.assertTrue(loader.is_feature_enabled('enable_reduplication'))
        
        pairs = loader.get_dwilingga_pairs()
        self.assertIn(('testbase', 'testvariant'), pairs)

    def test_load_invalid_path(self):
        """Test fallback when custom path is invalid."""
        loader = ConfigLoader(config_path="invalid/path/config.yaml")
        # Should fallback to default
        self.assertEqual(loader.get_min_stem_length('possessive'), 3)

    def test_get_generic(self):
        """Test the generic get method."""
        loader = ConfigLoader(config_path=self.temp_config_file.name)
        features = loader.get('features')
        self.assertIsInstance(features, dict)
        self.assertFalse(features['enable_loanword_affixation'])
        
        missing = loader.get('non_existent_key', 'default_val')
        self.assertEqual(missing, 'default_val')

if __name__ == '__main__':
    unittest.main()
