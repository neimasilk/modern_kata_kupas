#!/usr/bin/env python3
# src/modern_kata_kupas/cli.py
"""
Command-line interface for ModernKataKupas.
"""
import sys
import argparse
import json
from typing import List, Optional, Any
from .separator import ModernKataKupas


def segment_word(mkk: ModernKataKupas, word: str, format_output: str = 'text') -> str:
    """
    Segment a single word and format output.

    Args:
        mkk: ModernKataKupas instance
        word: Word to segment
        format_output: Output format ('text', 'json')

    Returns:
        Formatted output string
    """
    segmented = mkk.segment(word)

    if format_output == 'json':
        return json.dumps({'word': word, 'segmented': segmented}, ensure_ascii=False)
    else:
        return f"{word} → {segmented}"


def reconstruct_word(mkk: ModernKataKupas, segmented: str, format_output: str = 'text') -> str:
    """
    Reconstruct a word from segmented form.

    Args:
        mkk: ModernKataKupas instance
        segmented: Segmented word string
        format_output: Output format ('text', 'json')

    Returns:
        Formatted output string
    """
    reconstructed = mkk.reconstruct(segmented)

    if format_output == 'json':
        return json.dumps({'segmented': segmented, 'reconstructed': reconstructed}, ensure_ascii=False)
    else:
        return f"{segmented} → {reconstructed}"


def batch_segment(mkk: ModernKataKupas, input_file: str, output_file: Optional[str] = None,
                  format_output: str = 'text') -> None:
    """
    Segment words from input file.

    Args:
        mkk: ModernKataKupas instance
        input_file: Path to input file (one word per line)
        output_file: Path to output file (if None, prints to stdout)
        format_output: Output format ('text', 'json', 'csv')
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results: List[Any] = []
    for word in words:
        segmented = mkk.segment(word)
        if format_output == 'json':
            results.append({'word': word, 'segmented': segmented})
        elif format_output == 'csv':
            results.append(f"{word},{segmented}")
        else:
            results.append(f"{word} → {segmented}")

    # Format output
    if format_output == 'json':
        output_text = json.dumps(results, ensure_ascii=False, indent=2)
    else:
        output_text = '\n'.join([str(r) for r in results])

    # Write output
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_text + '\n')
            print(f"Results written to {output_file}")
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_text)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='ModernKataKupas - Indonesian Morphological Segmenter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Segment a single word
  mkk segment "mempertaruhkan"

  # Reconstruct from segmented form
  mkk reconstruct "meN~per~taruh~kan"

  # Batch segment from file
  mkk segment-file input.txt -o output.txt

  # Output in JSON format
  mkk segment "menulis" --format json

  # Output in CSV format
  mkk segment-file input.txt --format csv
        '''
    )

    parser.add_argument('--version', action='version', version='ModernKataKupas 1.0.0')
    parser.add_argument('--dictionary', '-d', help='Path to custom dictionary file')
    parser.add_argument('--rules', '-r', help='Path to custom rules file')
    parser.add_argument('--config', '-c', help='Path to custom config file')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Segment command
    segment_parser = subparsers.add_parser('segment', help='Segment a single word')
    segment_parser.add_argument('word', help='Word to segment')
    segment_parser.add_argument('--format', '-f', choices=['text', 'json'],
                                default='text', help='Output format')

    # Reconstruct command
    reconstruct_parser = subparsers.add_parser('reconstruct', help='Reconstruct word from segmented form')
    reconstruct_parser.add_argument('segmented', help='Segmented word (e.g., "meN~tulis")')
    reconstruct_parser.add_argument('--format', '-f', choices=['text', 'json'],
                                   default='text', help='Output format')

    # Batch segment command
    batch_parser = subparsers.add_parser('segment-file', help='Segment words from file')
    batch_parser.add_argument('input', help='Input file (one word per line)')
    batch_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    batch_parser.add_argument('--format', '-f', choices=['text', 'json', 'csv'],
                             default='text', help='Output format')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize ModernKataKupas
    try:
        mkk = ModernKataKupas(
            dictionary_path=args.dictionary,
            rules_file_path=args.rules,
            config_path=args.config
        )
    except Exception as e:
        print(f"Error initializing ModernKataKupas: {e}", file=sys.stderr)
        sys.exit(1)

    # Execute command
    try:
        if args.command == 'segment':
            result = segment_word(mkk, args.word, args.format)
            print(result)
        elif args.command == 'reconstruct':
            result = reconstruct_word(mkk, args.segmented, args.format)
            print(result)
        elif args.command == 'segment-file':
            batch_segment(mkk, args.input, args.output, args.format)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
