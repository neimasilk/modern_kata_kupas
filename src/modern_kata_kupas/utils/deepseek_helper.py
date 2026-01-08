"""
DeepSeek API Helper Module for ModernKataKupas

This module provides a convenient interface to DeepSeek API for generating
and validating Indonesian morphological data for research purposes.

Security Note:
    - API key should be stored in .env file (never commit to git)
    - .env is excluded by .gitignore
    - Use .env.example as template

Usage:
    >>> from modern_kata_kupas.utils.deepseek_helper import DeepSeekHelper
    >>> helper = DeepSeekHelper()
    >>> result = helper.generate_root_words(category="verbs", count=50)
"""
import os
import json
import time
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
    from openai import OpenAI
except ImportError:
    load_dotenv = None
    OpenAI = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GenerationResult:
    """Result from a generation request."""
    success: bool
    data: Any
    error: Optional[str] = None
    tokens_used: int = 0
    retry_count: int = 0


class DeepSeekHelper:
    """
    Helper class for interacting with DeepSeek API.

    Handles API initialization, request management, retry logic,
    and prompt templating for Indonesian morphological data generation.

    Attributes:
        client: OpenAI client configured for DeepSeek
        model: Model identifier (default: deepseek-chat)
        max_retries: Maximum number of retry attempts
        rate_limit_delay: Delay between requests in seconds

    Example:
        >>> helper = DeepSeekHelper()
        >>> words = helper.generate_root_words("nouns", 50)
        >>> print(words)
    """

    # Prompt templates
    PROMPT_GENERATE_ROOT_WORDS = """You are a linguistics expert specializing in Indonesian morphology (Bahasa Indonesia).

Generate {count} Indonesian root words (kata dasar) from the category: "{category}"

Requirements:
- Only generate pure root words (kata dasar murni - no affixes attached)
- Common words in modern Indonesian usage
- Words that can be found in KBBI (Kamus Besar Bahasa Indonesia)
- Include both formal and commonly used colloquial words if applicable

Output format: JSON array of strings
Example output: ["buku", "makan", "rumah", "jalan"]

Generate exactly {count} words. Output ONLY the JSON array, no other text."""

    PROMPT_SEGMENT_WORD = """You are an expert in Indonesian morphological analysis.

Segment the following Indonesian word into its constituent morphemes (morphemes are the smallest units of meaning).

Word: "{word}"

Output format JSON:
{{
  "word": "{word}",
  "segmentation": "root~affix1~affix2",
  "morphemes": [
    {{"form": "meN", "type": "prefix", "position": "before"}},
    {{"form": "root", "type": "root", "position": "center"}},
    {{"form": "kan", "type": "suffix", "position": "after"}}
  ],
  "confidence": "high",
  "notes": "explanation if needed"
}}

Segmentation rules:
- Use canonical prefix forms: "meN" (not "men"/"meng"/"mem"), "ber", "di", "ter", "per", "peN", "ke", "se"
- Use "~" (tilde) as morpheme separator
- Morpheme order: prefixes (left to right) ~ root ~ suffixes (left to right)
- Reduplication markers: "ulg" for full reduplication (X-X), "rp" for partial (XX-root)
- If uncertain about segmentation, set confidence to "low"
- Only segment if you are reasonably confident in the analysis

Output ONLY valid JSON, no other text."""

    PROMPT_GENERATE_AFFIXED_VARIANTS = """For the Indonesian root word "{root_word}", generate morphologically valid words with Indonesian affixes.

Root word meaning: {meaning if provided else "you should know this"}

Generate words with these affix patterns:
1. meN- prefix (all valid allomorphs: me-, men-, meng-, meny-, mem-, menge-)
2. ber- prefix
3. ter- prefix
4. di- prefix
5. -kan suffix (causative/benefactive)
6. -i suffix (locative/repetitive)
7. -an suffix (nominalizer)
8. ke-...-an confix (circumfix)
9. Reduplication (full: X-X)
10. Complex combinations (2+ affixes, e.g., meN-kan, meN-i, ke-an-kan, etc.)

For each variant:
- Only include commonly used Indonesian words
- Apply morphophonemic rules correctly (e.g., memukul not memukul, menyapu not mensapu)
- Ensure the word is valid in KBBI or common usage

Output format JSON:
{{
  "root": "{root_word}",
  "variants": [
    {{"form": "main", "affixes": [], "pattern": "root", "valid": true, "frequency": "high"}},
    {{"form": "bermain", "affixes": ["ber"], "pattern": "prefix", "valid": true, "frequency": "high"}},
    {{"form": "memainkan", "affixes": ["meN", "kan"], "pattern": "prefix+suffix", "valid": true, "frequency": "high"}},
    {{"form": "permainan", "affixes": ["per", "an"], "pattern": "confix", "valid": true, "frequency": "medium"}}
  ]
}}

Output ONLY valid JSON, no other text."""

    PROMPT_VALIDATE_ROOT_WORD = """You are a linguistics expert in Indonesian morphology.

Determine if the following word is a pure Indonesian root word (kata dasar).

Word: "{word}"

A root word (kata dasar) is:
- The base form of a word without any affixes (prefixes, suffixes, infixes, confixes)
- Can be found in KBBI (Kamus Besar Bahasa Indonesia) as a base entry
- Not derived from another word through affixation

Output format JSON:
{{
  "word": "{word}",
  "is_root_word": true/false,
  "confidence": "high/medium/low",
  "explanation": "brief explanation",
  "if_not_root": "the actual root word if this is not a root word, or null"
}}

Output ONLY valid JSON, no other text."""

    PROMPT_CATEGORIZE_ERROR = """You are analyzing errors in an Indonesian morphological segmentation system.

Given the original word, the system's prediction, and the correct segmentation, categorize the error type.

Original word: "{word}"
System prediction: "{prediction}"
Correct segmentation: "{correct}"

Error types:
- "false_positive_prefix": System detected prefix that doesn't exist
- "false_negative_prefix": System missed a prefix
- "false_positive_suffix": System detected suffix that doesn't exist
- "false_negative_suffix": System missed a suffix
- "wrong_stem": System identified wrong root word
- "morphophonemic_error": Incorrect morphophonemic transformation
- "reduplication_error": Incorrect reduplication handling
- "ambiguity_error": Multiple valid segmentations, system chose wrong one
- "loanword_error": Incorrect handling of loanword
- "other": Other types of errors

Output format JSON:
{{
  "word": "{word}",
  "error_type": "error_category",
  "severity": "critical/major/minor",
  "explanation": "brief explanation of what went wrong",
  "suggestion": "how to fix this in the system"
}}

Output ONLY valid JSON, no other text."""

    PROMPT_ANALYZE_MORPHEMICS = """Analyze the morphophonemic changes that occur when this prefix is attached to the root word.

Prefix (canonical): "{prefix}"
Root word: "{root}"
Resulting form: "{result}"

Explain:
1. Which allomorph of the prefix is used and why
2. Any phonological changes (elision/luluh, assimilation, etc.)
3. The reverse process (how to recover the root from the prefixed form)

Output format JSON:
{{
  "prefix_canonical": "{prefix}",
  "allomorph_used": "specific allomorph (e.g., 'meng' from meN)",
  "root_initial": "first letter(s) of root",
  "change_type": "elision/assimilation/none/other",
  "elision_occurred": true/false,
  "elided_letter": "letter if elided or null",
  "explanation": "detailed explanation",
  "reverse_rule": "how to recover root from prefixed form"
}}

Output ONLY valid JSON, no other text."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 3,
        rate_limit_delay: float = 1.0
    ):
        """
        Initialize the DeepSeek API helper.

        Args:
            api_key: DeepSeek API key. If None, reads from DEEPSEEK_API_KEY env var
            base_url: API base URL. If None, reads from DEEPSEEK_BASE_URL env var
            model: Model to use. If None, reads from DEEPSEEK_MODEL env var
            max_retries: Maximum number of retry attempts for failed requests
            rate_limit_delay: Delay between requests in seconds

        Raises:
            ImportError: If required dependencies (dotenv, openai) are not installed
            ValueError: If API key cannot be found
        """
        if load_dotenv is None or OpenAI is None:
            raise ImportError(
                "Required dependencies not installed. "
                "Install with: pip install python-dotenv openai"
            )

        # Load environment variables from .env file
        load_dotenv()

        # Get API key
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DeepSeek API key not found. Set DEEPSEEK_API_KEY in .env file "
                "or pass api_key parameter."
            )

        # Get other configuration
        self.base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.max_retries = max_retries
        self.rate_limit_delay = rate_limit_delay

        # Initialize OpenAI client for DeepSeek
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        logger.info(f"DeepSeekHelper initialized with model: {self.model}")

    def _call_api(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> GenerationResult:
        """
        Make an API call to DeepSeek with retry logic.

        Args:
            prompt: The user prompt to send
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            system_prompt: Optional system prompt

        Returns:
            GenerationResult with success status and data
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        retry_count = 0
        last_error = None

        while retry_count <= self.max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"}
                )

                content = response.choices[0].message.content
                tokens_used = response.usage.total_tokens

                # Rate limiting delay
                time.sleep(self.rate_limit_delay)

                return GenerationResult(
                    success=True,
                    data=content,
                    tokens_used=tokens_used,
                    retry_count=retry_count
                )

            except Exception as e:
                last_error = e
                retry_count += 1
                if retry_count <= self.max_retries:
                    wait_time = self.rate_limit_delay * retry_count
                    logger.warning(f"API call failed, retrying in {wait_time}s... Error: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"API call failed after {self.max_retries} retries: {e}")

        return GenerationResult(
            success=False,
            data=None,
            error=str(last_error),
            retry_count=retry_count
        )

    def _parse_json_response(self, response: str) -> Any:
        """Parse JSON response with error handling."""
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response content: {response}")
            return None

    # ============================================================================
    # Public API Methods
    # ============================================================================

    def generate_root_words(
        self,
        category: str,
        count: int = 50
    ) -> GenerationResult:
        """
        Generate Indonesian root words from a specific category.

        Categories: nouns, verbs, adjectives, adverbs, numbers, etc.

        Args:
            category: Word category to generate
            count: Number of words to generate

        Returns:
            GenerationResult with list of root words
        """
        prompt = self.PROMPT_GENERATE_ROOT_WORDS.format(
            category=category,
            count=count
        )

        result = self._call_api(prompt, temperature=0.7)

        if result.success:
            parsed = self._parse_json_response(result.data)
            result.data = parsed if parsed else []
            logger.info(f"Generated {len(result.data)} root words for category '{category}'")

        return result

    def generate_root_words_batch(
        self,
        categories: List[str],
        count_per_category: int = 50
    ) -> Dict[str, List[str]]:
        """
        Generate root words for multiple categories.

        Args:
            categories: List of word categories
            count_per_category: Number of words per category

        Returns:
            Dictionary mapping category to list of words
        """
        results = {}
        total_tokens = 0

        for category in categories:
            logger.info(f"Generating root words for category: {category}")
            result = self.generate_root_words(category, count_per_category)

            if result.success:
                results[category] = result.data
                total_tokens += result.tokens_used
            else:
                logger.error(f"Failed to generate for category '{category}': {result.error}")
                results[category] = []

        logger.info(f"Batch generation complete. Total tokens used: {total_tokens}")
        return results

    def segment_word(
        self,
        word: str,
        include_raw: bool = False
    ) -> GenerationResult:
        """
        Get morphological segmentation of a word from DeepSeek.

        Args:
            word: Indonesian word to segment
            include_raw: Whether to include raw response

        Returns:
            GenerationResult with segmentation data
        """
        prompt = self.PROMPT_SEGMENT_WORD.format(word=word)
        result = self._call_api(prompt, temperature=0.2)

        if result.success:
            parsed = self._parse_json_response(result.data)
            result.data = parsed
            if include_raw:
                result.raw_response = result.data

        return result

    def segment_words_batch(
        self,
        words: List[str],
        show_progress: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Segment multiple words in batch.

        Args:
            words: List of words to segment
            show_progress: Whether to show progress (requires tqdm)

        Returns:
            List of segmentation results
        """
        results = []
        total_tokens = 0

        iterator = words
        if show_progress:
            try:
                from tqdm import tqdm
                iterator = tqdm(words, desc="Segmenting words")
            except ImportError:
                show_progress = False

        for word in iterator:
            result = self.segment_word(word)
            total_tokens += result.tokens_used

            if result.success:
                results.append(result.data)
            else:
                logger.warning(f"Failed to segment '{word}': {result.error}")
                results.append({
                    "word": word,
                    "segmentation": None,
                    "error": result.error
                })

        logger.info(f"Batch segmentation complete. Processed {len(results)} words, {total_tokens} tokens.")
        return results

    def generate_affixed_variants(
        self,
        root_word: str,
        meaning: Optional[str] = None
    ) -> GenerationResult:
        """
        Generate affixed variants of a root word.

        Args:
            root_word: Indonesian root word
            meaning: Optional meaning of the root word

        Returns:
            GenerationResult with list of affixed variants
        """
        prompt = self.PROMPT_GENERATE_AFFIXED_VARIANTS.format(
            root_word=root_word,
            meaning=meaning or "you should know this common Indonesian word"
        )

        result = self._call_api(prompt, temperature=0.5)

        if result.success:
            parsed = self._parse_json_response(result.data)
            result.data = parsed

        return result

    def validate_root_word(
        self,
        word: str
    ) -> GenerationResult:
        """
        Validate if a word is a pure Indonesian root word.

        Args:
            word: Word to validate

        Returns:
            GenerationResult with validation result
        """
        prompt = self.PROMPT_VALIDATE_ROOT_WORD.format(word=word)
        result = self._call_api(prompt, temperature=0.2)

        if result.success:
            parsed = self._parse_json_response(result.data)
            result.data = parsed

        return result

    def validate_root_words_batch(
        self,
        words: List[str],
        show_progress: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """
        Validate multiple words as root words.

        Args:
            words: List of words to validate
            show_progress: Whether to show progress

        Returns:
            Dictionary mapping word to validation result
        """
        results = {}

        iterator = words
        if show_progress:
            try:
                from tqdm import tqdm
                iterator = tqdm(words, desc="Validating root words")
            except ImportError:
                pass

        for word in iterator:
            result = self.validate_root_word(word)
            if result.success:
                results[word] = result.data
            else:
                results[word] = {
                    "word": word,
                    "is_root_word": False,
                    "error": result.error
                }

        return results

    def categorize_error(
        self,
        word: str,
        prediction: str,
        correct: str
    ) -> GenerationResult:
        """
        Categorize an error in morphological segmentation.

        Args:
            word: Original word
            prediction: System's prediction
            correct: Correct segmentation

        Returns:
            GenerationResult with error categorization
        """
        prompt = self.PROMPT_CATEGORIZE_ERROR.format(
            word=word,
            prediction=prediction,
            correct=correct
        )

        result = self._call_api(prompt, temperature=0.3)

        if result.success:
            parsed = self._parse_json_response(result.data)
            result.data = parsed

        return result

    def analyze_morphophonemics(
        self,
        prefix: str,
        root: str,
        result: str
    ) -> GenerationResult:
        """
        Analyze morphophonemic changes in prefix+root combination.

        Args:
            prefix: Canonical prefix form (e.g., "meN")
            root: Root word
            result: Resulting word after prefix application

        Returns:
            GenerationResult with morphophonemic analysis
        """
        prompt = self.PROMPT_ANALYZE_MORPHEMICS.format(
            prefix=prefix,
            root=root,
            result=result
        )

        result = self._call_api(prompt, temperature=0.2)

        if result.success:
            parsed = self._parse_json_response(result.data)
            result.data = parsed

        return result

    def generate_gold_standard_pair(
        self,
        word: str
    ) -> Dict[str, Any]:
        """
        Generate a gold standard segmentation for a word.

        This includes the segmentation, confidence level, and
        morpheme-by-morpheme breakdown.

        Args:
            word: Word to segment

        Returns:
            Dictionary with gold standard data
        """
        result = self.segment_word(word)

        if result.success:
            return {
                "word": word,
                **result.data,
                "tokens_used": result.tokens_used
            }
        else:
            return {
                "word": word,
                "error": result.error,
                "segmentation": None
            }


class DeepSeekDataGenerator:
    """
    High-level data generation orchestrator using DeepSeekHelper.

    This class provides methods for generating larger datasets
    for research purposes, including gold standard test sets,
    dictionary expansions, and error analysis datasets.
    """

    def __init__(self, helper: Optional[DeepSeekHelper] = None):
        """
        Initialize the data generator.

        Args:
            helper: DeepSeekHelper instance. If None, creates new one.
        """
        self.helper = helper or DeepSeekHelper()

    def generate_gold_standard_dataset(
        self,
        output_path: Union[str, Path],
        target_size: int = 1000,
        categories: Optional[List[str]] = None
    ) -> Path:
        """
        Generate a comprehensive gold standard test dataset.

        Creates a stratified dataset covering:
        - Pure root words
        - Single prefix words
        - Single suffix words
        - Confixes
        - Reduplication (all types)
        - Complex affixation
        - Loanwords with affixes

        Args:
            output_path: Path to save the CSV file
            target_size: Target number of entries
            categories: Categories to include (default: all)

        Returns:
            Path to the generated file
        """
        if categories is None:
            categories = [
                "root_pure",
                "prefix_single",
                "suffix_single",
                "confix",
                "reduplication_full",
                "reduplication_partial",
                "reduplication_phonetic",
                "complex",
                "loanword_affixed",
                "ambiguous"
            ]

        # This is a placeholder for the full implementation
        # The actual implementation will be in the generate_gold_standard.py script
        logger.info(f"Gold standard generation initiated. Target: {target_size} entries")
        logger.info(f"Output will be saved to: {output_path}")

        # Implementation will be in the separate script
        return Path(output_path)


# CLI convenience function
def main():
    """Simple CLI for testing the helper."""
    import argparse

    parser = argparse.ArgumentParser(description="DeepSeek Helper CLI")
    parser.add_argument("--test", action="store_true", help="Test API connection")
    parser.add_argument("--generate-roots", type=str, help="Generate root words for category")
    parser.add_argument("--count", type=int, default=10, help="Number of items to generate")
    parser.add_argument("--segment", type=str, help="Segment a word")

    args = parser.parse_args()

    try:
        helper = DeepSeekHelper()
    except (ImportError, ValueError) as e:
        print(f"Error initializing DeepSeek helper: {e}")
        return 1

    if args.test:
        print("Testing API connection...")
        result = helper.segment_word("membaca")
        if result.success:
            print("✓ API connection successful!")
            print(f"Response: {json.dumps(result.data, indent=2)}")
        else:
            print(f"✗ API connection failed: {result.error}")

    elif args.segment:
        print(f"Segmenting word: {args.segment}")
        result = helper.segment_word(args.segment)
        if result.success:
            print(json.dumps(result.data, indent=2))
        else:
            print(f"Error: {result.error}")

    elif args.generate_roots:
        print(f"Generating {args.count} root words for category: {args.generate_roots}")
        result = helper.generate_root_words(args.generate_roots, args.count)
        if result.success:
            print(json.dumps(result.data, indent=2))
        else:
            print(f"Error: {result.error}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    exit(main())
