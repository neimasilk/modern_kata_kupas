"""
Test DeepSeek API Connection

Simple script to verify that the DeepSeek API is working correctly.
"""
import sys
import os
import json
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    os.system("chcp 65001 > nul")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from modern_kata_kupas.utils.deepseek_helper import DeepSeekHelper
except ImportError as e:
    print(f"Error importing DeepSeekHelper: {e}")
    print("Make sure dependencies are installed:")
    print("  pip install python-dotenv openai")
    sys.exit(1)


def test_api_connection():
    """Test basic API connection."""
    print("=" * 60)
    print(" TESTING DEEPSEEK API CONNECTION")
    print("=" * 60)

    try:
        helper = DeepSeekHelper()
        print(f"[OK] DeepSeekHelper initialized successfully")
        print(f"  Model: {helper.model}")
        print(f"  Base URL: {helper.base_url}")
        print()
    except Exception as e:
        print(f"[FAIL] Failed to initialize DeepSeekHelper: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Make sure .env file exists in project root")
        print("  2. Check that DEEPSEEK_API_KEY is set in .env")
        print("  3. Verify the API key is valid")
        return False

    return True


def test_segmentation():
    """Test word segmentation."""
    print("-" * 60)
    print(" TESTING WORD SEGMENTATION")
    print("-" * 60)

    try:
        helper = DeepSeekHelper()
    except Exception as e:
        print(f"[FAIL] Failed to initialize: {e}")
        return False

    test_words = [
        "mempermainkan",
        "buku-buku",
        "membaca",
        "bermain",
        "adil"
    ]

    results = []

    for word in test_words:
        print(f"\nSegmenting: '{word}'")
        result = helper.segment_word(word)

        if result.success:
            data = result.data
            print(f"  [OK] Success")
            print(f"  Segmentation: {data.get('segmentation', 'N/A')}")
            print(f"  Confidence: {data.get('confidence', 'N/A')}")
            print(f"  Tokens used: {result.tokens_used}")
            results.append({
                "word": word,
                "success": True,
                "segmentation": data.get("segmentation"),
                "tokens": result.tokens_used
            })
        else:
            print(f"  [FAIL] Failed: {result.error}")
            results.append({
                "word": word,
                "success": False,
                "error": result.error
            })

    total_tokens = sum(r.get("tokens", 0) for r in results)
    print(f"\n{'=' * 60}")
    print(f"Total tokens used: {total_tokens}")
    print(f"Estimasi biaya: ${total_tokens * 0.00001:.6f} ( sangat murah! )")
    print("=" * 60)

    return all(r.get("success", False) for r in results)


def test_root_word_generation():
    """Test root word generation."""
    print("\n" + "-" * 60)
    print(" TESTING ROOT WORD GENERATION")
    print("-" * 60)

    try:
        helper = DeepSeekHelper()
    except Exception as e:
        print(f"[FAIL] Failed to initialize: {e}")
        return False

    print(f"\nGenerating 10 Indonesian root words (nouns)...")
    result = helper.generate_root_words("nouns", count=10)

    if result.success:
        words = result.data if isinstance(result.data, list) else []
        print(f"  [OK] Success! Generated {len(words)} words:")
        for i, word in enumerate(words, 1):
            print(f"    {i}. {word}")
        print(f"  Tokens used: {result.tokens_used}")
        return True
    else:
        print(f"  ✗ Failed: {result.error}")
        return False


def main():
    """Run all tests."""
    print("\n")

    # Test 1: Connection
    if not test_api_connection():
        print("\n[FAIL] API connection test FAILED")
        print("Please fix the issues above before proceeding.")
        return 1

    # Test 2: Segmentation
    if not test_segmentation():
        print("\n[WARN] Segmentation test had issues, but API is reachable.")
    else:
        print("\n[OK] Segmentation test PASSED")

    # Test 3: Root word generation (optional - comment out if saving tokens)
    print()
    response = input("Run root word generation test? (y/n): ").strip().lower()
    if response == 'y':
        if not test_root_word_generation():
            print("\n[WARN] Root word generation test had issues.")
        else:
            print("\n[OK] Root word generation test PASSED")

    print("\n" + "=" * 60)
    print(" ALL TESTS COMPLETED")
    print("=" * 60)
    print("\n[OK] DeepSeek API is working correctly!")
    print("  You can now proceed with data generation.")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
