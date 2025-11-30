import argparse
from pathlib import Path
from dynamicprompts.generators import RandomPromptGenerator
from dynamicprompts.wildcards.wildcard_manager import WildcardManager


def main():
    parser = argparse.ArgumentParser(
        description="Generate prompts using wildcards from the lumi-wildcards collection"
    )
    parser.add_argument(
        "prompt",
        help="The prompt template to generate (e.g., '__std/xl/pose/all__')"
    )
    parser.add_argument(
        "-c", "--count",
        type=int,
        default=100,
        help="Number of prompt variations to generate (default: 100)"
    )

    args = parser.parse_args()

    # Initialize wildcard manager with the wildcards directory
    wm = WildcardManager(Path("d:/dev/ai/lumi-wildcards/wildcards"))

    # Generate prompts
    generator = RandomPromptGenerator(wildcard_manager=wm)
    generated_prompts = generator.generate(args.prompt, args.count)

    # Output generated prompts
    for p in generated_prompts:
        print(p)


if __name__ == "__main__":
    main()