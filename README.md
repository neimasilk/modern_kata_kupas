# ModernKataKupas - Indonesian Sub-word Separator

## Overview
ModernKataKupas is a Python library for Indonesian sub-word separation, designed to enhance LLM performance and low-resource NLP applications. This rule-based algorithm provides accurate morphological analysis of Indonesian words.

## Installation
```bash
pip install modern_kata_kupas
```

## Basic Usage
```python
from modern_kata_kupas import Separator

separator = Separator()
result = separator.separate("beruang")  # Returns ['ber', 'uang']
```

## API Documentation
### `Separator` Class
- `separate(word: str) -> List[str]`: Main method to separate Indonesian words into sub-words
- `set_dictionary(dict_path: str)`: Load custom dictionary

### Exceptions
All exceptions inherit from `ModernKataKupasError`:
- `DictionaryError`
- `RuleError`
- `WordNotInDictionaryError`

## Contributing
Please report issues and feature requests via GitHub issues.

## License
MIT License