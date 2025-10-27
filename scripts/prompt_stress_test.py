import re
import sys
import argparse
from collections import Counter, defaultdict
from pathlib import Path
from dynamicprompts.generators import RandomPromptGenerator
from dynamicprompts.wildcards.wildcard_manager import WildcardManager

def main():
    parser = argparse.ArgumentParser(description='Analyze wildcard prompt generation frequencies')
    parser.add_argument('-n', '--num-gens', type=int, default=100,
                       help='Number of generations to run (default: 100)')
    parser.add_argument('-o', '--output', type=str,
                       help='Output file to save results (optional)')
    parser.add_argument('--debug', action='store_true',
                       help='Show first 5 generated prompts for debugging')
    parser.add_argument('--blacklist', type=str, nargs='*',
                       default=['with', 'and', 'the'],
                       help='Words to ignore in analysis (default: with and the)')
    parser.add_argument('--no-blacklist', action='store_true',
                       help='Disable word blacklist entirely')
    args = parser.parse_args()

    # --- config
    WILDCARD_ROOT = Path("d:/dev/ai/lumi-wildcards/wildcards")
    PROMPT_TEMPLATE = """
__std/xl/style/all__,
__std/xl/camera/all__,
__std/xl/character/all__,
__std/xl/outfit/all__,
__std/xl/location/all__,
__std/xl/environment/all__,
__std/xl/distance/all__,
__std/xl/lighting/all__,
__std/xl/details/all__"""
    NGENS = args.num_gens

    # Set up blacklist
    if args.no_blacklist:
        blacklist = set()
    else:
        blacklist = set(word.lower() for word in args.blacklist)

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
                    if len(w) > 2 and w not in blacklist:  # Skip very short words and blacklisted words
                        word_counts[w] += 1
                        source_counts[source][w] += 1

    # --- report
    output_lines = []
    output_lines.append(f"\n=== ANALYSIS RESULTS ({NGENS} generations) ===")
    output_lines.append(f"Total unique words: {len(word_counts)}")
    output_lines.append(f"Total word instances: {sum(word_counts.values())}")
    if blacklist:
        output_lines.append(f"Blacklisted words: {', '.join(sorted(blacklist))}")
    else:
        output_lines.append("No words blacklisted")

    output_lines.append("\n=== top 50 words overall ===")
    for word, count in word_counts.most_common(50):
        percentage = (count / NGENS) * 100
        output_lines.append(f"{word:20s} {count:4d} ({percentage:5.1f}%)")

    output_lines.append("\n=== per-source summary ===")
    for src, counter in source_counts.items():
        total_words = sum(counter.values())
        output_lines.append(f"\n[{src}] - {total_words} total words, top 15:")
        for w, c in counter.most_common(15):
            percentage = (c / NGENS) * 100
            output_lines.append(f"  {w:20s} {c:4d} ({percentage:5.1f}%)")

    # --- identify potential issues
    output_lines.append("\n=== potential issues ===")
    output_lines.append("Words appearing in >80% of generations (may indicate over-weighting):")
    for word, count in word_counts.most_common():
        if count > NGENS * 0.8:
            percentage = (count / NGENS) * 100
            output_lines.append(f"  {word:20s} {count:4d} ({percentage:5.1f}%)")
        else:
            break

    output_lines.append("\nWords appearing in <5% of generations (may indicate under-weighting):")
    rare_words = [(w, c) for w, c in word_counts.items() if c < NGENS * 0.05 and c > 1]
    rare_words.sort(key=lambda x: x[1], reverse=True)
    for word, count in rare_words[:20]:  # Show top 20 rare words
        percentage = (count / NGENS) * 100
        output_lines.append(f"  {word:20s} {count:4d} ({percentage:5.1f}%)")

    # Output results
    result_text = '\n'.join(output_lines)
    print(result_text)

    # Save to file if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result_text)
        print(f"\nResults saved to: {args.output}")

if __name__ == "__main__":
    main()
