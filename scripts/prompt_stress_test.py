#!/usr/bin/env -S uv run --quiet
# /// script
# dependencies = [
#   "dynamicprompts @ file:///mnt/d/dev/ai/dynamicprompts",
#   "pyyaml",
# ]
# ///

import re
import sys
import argparse
from collections import Counter, defaultdict
from pathlib import Path
from dynamicprompts.generators import RandomPromptGenerator
from dynamicprompts.wildcards.wildcard_manager import WildcardManager

def main():
    parser = argparse.ArgumentParser(description='Analyze wildcard prompt generation frequencies')
    parser.add_argument('prompt', nargs='?',
                       default='__std/xl/outfit/all__',
                       help='Prompt template to analyze (default: __std/xl/outfit/all__)')
    parser.add_argument('-n', '--num-gens', type=int, default=100,
                       help='Number of generations to run (default: 100)')
    parser.add_argument('-w', '--wildcards-root', type=str,
                       default='wildcards',
                       help='Path to wildcards directory (default: wildcards)')
    parser.add_argument('-o', '--output', type=str,
                       help='Output file to save results (optional)')
    parser.add_argument('--debug', action='store_true',
                       help='Show first 5 generated prompts for debugging')
    parser.add_argument('--blacklist', type=str, nargs='*',
                       default=['with', 'and', 'the'],
                       help='(DEPRECATED: use --exclude) Words to ignore in analysis (default: with and the)')
    parser.add_argument('--exclude', type=str, nargs='*',
                       help='Words to ignore in analysis (can be space-separated or quoted string)')
    parser.add_argument('--no-blacklist', action='store_true',
                       help='(DEPRECATED: use --no-exclude) Disable word exclusion entirely')
    parser.add_argument('--no-exclude', action='store_true',
                       help='Disable word exclusion entirely')
    parser.add_argument('--min-word-length', type=int, default=3,
                       help='Minimum word length to include in analysis (default: 3)')
    parser.add_argument('--top-words', type=int, default=50,
                       help='Number of top words to show in overall analysis (default: 50)')
    parser.add_argument('--top-per-source', type=int, default=15,
                       help='Number of top words to show per source (default: 15)')
    parser.add_argument('--over-weight-threshold', type=float, default=0.8,
                       help='Threshold for identifying over-weighted words (default: 0.8 = 80%%)')
    parser.add_argument('--under-weight-threshold', type=float, default=0.05,
                       help='Threshold for identifying under-weighted words (default: 0.05 = 5%%)')
    parser.add_argument('--rare-words-limit', type=int, default=20,
                       help='Maximum number of rare words to show (default: 20)')
    args = parser.parse_args()

    # --- config
    # Handle wildcard root path - resolve relative to script location if using default
    if args.wildcards_root == 'wildcards':
        # Get the script directory and navigate to the project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        WILDCARD_ROOT = project_root / "wildcards"
    else:
        WILDCARD_ROOT = Path(args.wildcards_root)

    PROMPT_TEMPLATE = args.prompt.strip()
    NGENS = args.num_gens

    # Validate arguments
    if not WILDCARD_ROOT.exists():
        print(f"Error: Wildcards directory '{WILDCARD_ROOT}' does not exist.")
        sys.exit(1)

    if args.over_weight_threshold <= 0 or args.over_weight_threshold > 1:
        print("Error: over-weight-threshold must be between 0 and 1.")
        sys.exit(1)

    if args.under_weight_threshold <= 0 or args.under_weight_threshold > 1:
        print("Error: under-weight-threshold must be between 0 and 1.")
        sys.exit(1)

    # Set up exclusion list (handle both old --blacklist and new --exclude)
    if args.no_blacklist or args.no_exclude:
        excluded_words = set()
    else:
        # Determine which exclusion list to use
        if args.exclude is not None:
            # Use new --exclude parameter
            exclude_list = args.exclude
        else:
            # Fall back to --blacklist for backward compatibility
            exclude_list = args.blacklist

        # Handle both space-separated arguments and quoted strings
        excluded_words = set()
        for item in exclude_list:
            # Split each item by spaces in case it's a quoted string with multiple words
            words = item.split()
            for word in words:
                excluded_words.add(word.lower())

    # Keep blacklist variable name for backward compatibility in output
    blacklist = excluded_words

    print(f"Analyzing prompt template: {PROMPT_TEMPLATE}")
    print(f"Using wildcards from: {WILDCARD_ROOT}")
    print(f"Generating {NGENS} samples...")
    if args.debug:
        print("Debug mode enabled - will show first 5 generated prompts\n")

    # --- setup
    wm = WildcardManager(WILDCARD_ROOT)
    generator = RandomPromptGenerator(wildcard_manager=wm)

    # --- run generations
    outputs = generator.generate(PROMPT_TEMPLATE, NGENS)

    # --- track frequencies
    word_counts = Counter()
    source_counts = defaultdict(Counter)

    # regex to ignore inline sets like {a|b|c}
    brace_re = re.compile(r"\{[^{}]*\}")
    # regex to match wildcard references
    wild_re = re.compile(r"__([a-zA-Z0-9_/.-]+)__")

    for i, p in enumerate(outputs):
        if args.debug and i < 5:  # Print first 5 for debugging
            print(f"=== Generated prompt {i+1} ===")
            print(p)
            print()

        # Split the generated prompt into lines
        generated_lines = p.strip().splitlines()
        template_lines = PROMPT_TEMPLATE.strip().splitlines()

        # Process each line of the template and match it to generated content
        for template_idx, template_line in enumerate(template_lines):
            template_line = template_line.strip().strip(",")
            if not template_line or not template_line.startswith("__"):
                continue

            # Extract the wildcard source name
            match = wild_re.match(template_line)
            if not match:
                continue
            source = match.group(1)

            # Get the corresponding generated line
            if template_idx < len(generated_lines):
                generated_line = generated_lines[template_idx].strip().strip(",")

                # Remove any inline {a|b|c} sets from the generated content
                clean_line = brace_re.sub("", generated_line)

                # Extract words (letters, numbers, underscores)
                words = re.findall(r"[a-zA-Z0-9_]+", clean_line.lower())

                # Count words
                for w in words:
                    if len(w) >= args.min_word_length and w not in blacklist:  # Skip short words and blacklisted words
                        word_counts[w] += 1
                        source_counts[source][w] += 1

    # --- report
    output_lines = []
    output_lines.append(f"\n=== ANALYSIS RESULTS ({NGENS} generations) ===")
    output_lines.append(f"Total unique words: {len(word_counts)}")
    output_lines.append(f"Total word instances: {sum(word_counts.values())}")
    if blacklist:
        output_lines.append(f"Excluded words: {', '.join(sorted(blacklist))}")
    else:
        output_lines.append("No words excluded")

    output_lines.append(f"\n=== top {args.top_words} words overall ===")
    for word, count in word_counts.most_common(args.top_words):
        percentage = (count / NGENS) * 100
        output_lines.append(f"{word:20s} {count:4d} ({percentage:5.1f}%)")

    output_lines.append("\n=== per-source summary ===")
    for src, counter in source_counts.items():
        total_words = sum(counter.values())
        output_lines.append(f"\n[{src}] - {total_words} total words, top {args.top_per_source}:")
        for w, c in counter.most_common(args.top_per_source):
            percentage = (c / NGENS) * 100
            output_lines.append(f"  {w:20s} {c:4d} ({percentage:5.1f}%)")

    # --- identify potential issues
    output_lines.append("\n=== potential issues ===")
    over_threshold_pct = args.over_weight_threshold * 100
    output_lines.append(f"Words appearing in >{over_threshold_pct:.0f}% of generations (may indicate over-weighting):")
    for word, count in word_counts.most_common():
        if count > NGENS * args.over_weight_threshold:
            percentage = (count / NGENS) * 100
            output_lines.append(f"  {word:20s} {count:4d} ({percentage:5.1f}%)")
        else:
            break

    under_threshold_pct = args.under_weight_threshold * 100
    output_lines.append(f"\nWords appearing in <{under_threshold_pct:.0f}% of generations (may indicate under-weighting):")
    rare_words = [(w, c) for w, c in word_counts.items() if c < NGENS * args.under_weight_threshold and c > 1]
    rare_words.sort(key=lambda x: x[1], reverse=True)
    for word, count in rare_words[:args.rare_words_limit]:
        percentage = (count / NGENS) * 100
        output_lines.append(f"  {word:20s} {count:4d} ({percentage:5.1f}%)")

    # Output results
    result_text = '\n'.join(output_lines)
    print(result_text)

    print("\nAnalysis complete")

    # Save to file if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result_text)
        print(f"\nResults saved to: {args.output}")

if __name__ == "__main__":
    main()
