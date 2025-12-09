#!/usr/bin/env -S uv run --quiet
# /// script
# dependencies = [
#   "transformers",
# ]
# ///
"""
Simple token counter that mimics Stable Diffusion 1.5's tokenization.
SD 1.5 uses OpenAI's CLIP tokenizer with a maximum context length of 77 tokens.
"""

import argparse
import sys
from typing import List, Optional

try:
    from transformers import CLIPTokenizer
except ImportError:
    print("Error: transformers library not found. Install with: pip install transformers")
    sys.exit(1)


class SD15TokenCounter:
    """Token counter that mimics Stable Diffusion 1.5's tokenization behavior."""
    
    def __init__(self):
        """Initialize with the same tokenizer used by SD 1.5."""
        # SD 1.5 uses OpenAI's CLIP tokenizer
        self.tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")
        self.max_tokens = 77  # SD 1.5's maximum context length
    
    def count_tokens(self, text: str) -> dict:
        """
        Count tokens in the given text.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            Dictionary with token count information
        """
        # Tokenize the text
        tokens = self.tokenizer.encode(text, add_special_tokens=True)
        
        # Get token strings for display
        token_strings = self.tokenizer.convert_ids_to_tokens(tokens)
        
        return {
            'text': text,
            'token_count': len(tokens),
            'tokens': tokens,
            'token_strings': token_strings,
            'max_tokens': self.max_tokens,
            'exceeds_limit': len(tokens) > self.max_tokens,
            'tokens_over_limit': max(0, len(tokens) - self.max_tokens)
        }
    
    def print_token_info(self, text: str, verbose: bool = False):
        """Print token information for the given text."""
        result = self.count_tokens(text)
        
        print(f"Text: '{result['text']}'")
        print(f"Token count: {result['token_count']}/{result['max_tokens']}")
        
        if result['exceeds_limit']:
            print(f"⚠️  WARNING: Exceeds limit by {result['tokens_over_limit']} tokens!")
            print("   Text will be truncated by Stable Diffusion")
        else:
            print("✅ Within token limit")
        
        if verbose:
            print(f"\nTokens: {result['tokens']}")
            print(f"Token strings: {result['token_strings']}")
        
        print("-" * 50)


def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(
        description="Count tokens using Stable Diffusion 1.5's tokenizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sd15_token_counter.py "a beautiful landscape"
  python sd15_token_counter.py --verbose "masterpiece, highly detailed"
  python sd15_token_counter.py --file prompts.txt
        """
    )
    
    parser.add_argument(
        'text',
        nargs='?',
        help='Text to tokenize (if not using --file)'
    )
    
    parser.add_argument(
        '--file', '-f',
        help='Read text from file (one prompt per line)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed token information'
    )
    
    args = parser.parse_args()
    
    if not args.text and not args.file:
        parser.error("Must provide either text or --file argument")
    
    # Initialize token counter
    counter = SD15TokenCounter()
    
    if args.file:
        # Process file
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"Processing {len(lines)} prompts from '{args.file}':")
            print("=" * 50)
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line:  # Skip empty lines
                    print(f"Prompt {i}:")
                    counter.print_token_info(line, args.verbose)
                    
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
    else:
        # Process single text
        counter.print_token_info(args.text, args.verbose)


if __name__ == '__main__':
    main()