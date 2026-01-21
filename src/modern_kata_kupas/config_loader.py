# src/modern_kata_kupas/config_loader.py
"""
Configuration loader for ModernKataKupas.
Loads configuration from YAML files.
"""
import os
import logging
from typing import Dict, List, Tuple, Any, Optional

try:
    import yaml # type: ignore[import-untyped]
except ImportError:
    yaml = None

# Default configuration (fallback if YAML not available or file not found)
DEFAULT_CONFIG = {
    "min_stem_lengths": {
        "possessive": 3,
        "derivational": 4,
        "particle": 3,
    },
    "dwilingga_salin_suara_pairs": [
        {"base": "sayur", "variant": "mayur"},
        {"base": "bolak", "variant": "balik"},
        {"base": "warna", "variant": "warni"},
        {"base": "ramah", "variant": "tamah"},
        {"base": "gerak", "variant": "gerik"},
        {"base": "lauk", "variant": "pauk"},
        {"base": "serba", "variant": "serbi"},
        {"base": "belah", "variant": "beli"},
        {"base": "buyut", "variant": "moyut"},
        {"base": "kacau", "variant": "balau"},
        {"base": "cing", "variant": "cang"},
        {"base": "ganti", "variant": "genti"},
        {"base": "kali", "variant": "keli"},
        {"base": "sulam", "variant": "selam"},
        {"base": "tukar", "variant": "tekER"},
        {"base": "ubah", "variant": "embuh"},
        {"base": "hanyut", "variant": "hilir"},
        {"base": "jaja", "variant": "jiwi"},
        {"base": "pacak", "variant": "pecik"},
        {"base": "saur", "variant": "segar"},
        {"base": "amit", "variant": "emtik"},
        {"base": "balik", "variant": "bolak"},
        {"base": "balik", "variant": "balek"},
        {"base": "jangkau", "variant": "jingkau"},
    ],
    "features": {
        "enable_loanword_affixation": True,
        "enable_reduplication": True,
        "enable_morphophonemic_rules": True,
    }
}


class ConfigLoader:
    """
    Loads and manages configuration for ModernKataKupas.

    Supports loading from YAML files or using default configuration.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initializes the ConfigLoader.

        Args:
            config_path (Optional[str]): Path to a custom config YAML file.
                If None, attempts to load the default packaged config.yaml.
                If YAML is not available or file not found, uses DEFAULT_CONFIG.
        """
        self.config: Dict[str, Any] = {}
        self._load_config(config_path)

    def _load_config(self, config_path: Optional[str] = None) -> None:
        """
        Loads configuration from file or uses default.

        Args:
            config_path (Optional[str]): Path to config file.
        """
        if yaml is None:
            logging.warning(
                "PyYAML not installed. Using default configuration. "
                "Install with: pip install pyyaml"
            )
            self.config = DEFAULT_CONFIG
            return

        if config_path and os.path.exists(config_path):
            # Load from custom path
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
                logging.info(f"Loaded config from: {config_path}")
                return
            except Exception as e:
                logging.error(f"Error loading config from {config_path}: {e}")

        # Try to load default packaged config
        try:
            import importlib.resources
            try:
                # Python 3.9+
                with importlib.resources.files('modern_kata_kupas.data').joinpath('config.yaml').open('r') as f:
                    self.config = yaml.safe_load(f)
                logging.info("Loaded default packaged config.yaml")
                return
            except AttributeError:
                # Python 3.8 fallback
                import importlib.resources as pkg_resources
                config_text = pkg_resources.read_text('modern_kata_kupas.data', 'config.yaml')
                self.config = yaml.safe_load(config_text)
                logging.info("Loaded default packaged config.yaml (Python 3.8 fallback)")
                return
        except Exception as e:
            logging.warning(f"Could not load packaged config.yaml: {e}")

        # Fallback to default config
        logging.info("Using hardcoded default configuration")
        self.config = DEFAULT_CONFIG

    def get_min_stem_length(self, suffix_type: str) -> int:
        """
        Gets the minimum stem length for a given suffix type.

        Args:
            suffix_type (str): Type of suffix ('possessive', 'derivational', 'particle').

        Returns:
            int: Minimum stem length.
        """
        return int(self.config.get("min_stem_lengths", {}).get(suffix_type, 3))

    def get_dwilingga_pairs(self) -> List[Tuple[str, str]]:
        """
        Gets the list of phonetic reduplication pairs.

        Returns:
            List[Tuple[str, str]]: List of (base, variant) tuples.
        """
        pairs_config = self.config.get("dwilingga_salin_suara_pairs", [])
        return [(pair["base"], pair["variant"]) for pair in pairs_config]

    def is_feature_enabled(self, feature_name: str) -> bool:
        """
        Checks if a feature is enabled.

        Args:
            feature_name (str): Name of the feature.

        Returns:
            bool: True if enabled, False otherwise.
        """
        return bool(self.config.get("features", {}).get(feature_name, True))

    def get(self, key: str, default: Any = None) -> Any:
        """
        Gets a configuration value.

        Args:
            key (str): Configuration key.
            default (Any): Default value if key not found.

        Returns:
            Any: Configuration value.
        """
        return self.config.get(key, default)
