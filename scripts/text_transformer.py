#!/usr/bin/env python3
"""
Text Transformer - Transform lines of text according to LLM prompts.
Supports various transformation types with specialized system prompts.
"""
import argparse
from openai import OpenAI
import sys
from pathlib import Path
from tqdm import tqdm
import json

def discover_available_prompts():
    """Discover all available prompt files in the prompts directory."""
    prompts_dir = Path(__file__).parent.parent / "prompts"
    if not prompts_dir.exists():
        return {}

    prompt_files = {}
    for prompt_file in prompts_dir.glob("*.md"):
        # Extract prompt type from filename (remove .md extension)
        prompt_type = prompt_file.stem
        prompt_files[prompt_type] = prompt_file.name

    return prompt_files

def load_system_prompt(prompt_type):
    """Load the system prompt from the appropriate markdown file based on type."""
    prompt_files = discover_available_prompts()

    if prompt_type not in prompt_files:
        available_types = list(prompt_files.keys())
        print(f"Error: Unknown prompt type '{prompt_type}'. Available types: {available_types}", file=sys.stderr)
        sys.exit(1)

    try:
        prompt_path = Path(__file__).parent.parent / "prompts" / prompt_files[prompt_type]
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading system prompt for '{prompt_type}': {e}", file=sys.stderr)
        return f"Transform the following text according to the '{prompt_type}' style."

def transform_text(input_line, system_prompt, prompt_type, reasoning_effort="medium", verbose=False, output_format="default"):
    """Transform text using an LLM according to the system prompt."""
    # Initialize OpenAI client when needed
    client = OpenAI()

    # Create the user message - for backward compatibility, keep some specific labels
    type_labels = {
        "booru-costume-tag-generator": "Costume",
        "booru-pose-tag-generator": "Pose/Action"
    }
    label = type_labels.get(prompt_type, "Input")
    user_prompt = f"\n\n{label}: {input_line.strip()}\n\nOutput:"

    system_prompt = system_prompt + user_prompt

    try:
        # Prepare API call parameters
        api_params = {
            "model": "gpt-5-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
            ],
            "max_completion_tokens": 10000,
            "reasoning_effort": reasoning_effort
        }

        response = client.chat.completions.create(**api_params)
        output = response.choices[0].message.content

        # If verbose mode is enabled, show reasoning
        if verbose and hasattr(response.choices[0].message, 'reasoning'):
            print(f"\n--- Reasoning for '{input_line.strip()}' ---")
            print(response.choices[0].message.reasoning)
            print("--- End Reasoning ---\n")

        if output:
            output = output.strip()
            # Apply output formatting based on type or format specification
            if output_format == "booru" or prompt_type.startswith("booru-"):
                return f"({input_line.strip()}:0.5), {output}"
            else:
                return output
        else:
            return input_line.strip()
    except Exception as e:
        print(f"Error processing '{input_line.strip()}': {e}", file=sys.stderr)
        return input_line.strip()

def main():
    # Discover available prompt types
    available_prompts = discover_available_prompts()

    parser = argparse.ArgumentParser(
        description="Transform lines of text according to LLM prompts",
        epilog=f"""
Available prompt types: {', '.join(available_prompts.keys())}

Examples:
  python text_transformer.py input.txt output.txt --type booru-costume-tag-generator
  python text_transformer.py poses.txt pose_tags.txt --type booru-pose-tag-generator --verbose
  python text_transformer.py descriptions.txt transformed.txt --type custom-prompt --format plain
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("input", help="Input file with text lines to transform (one per line)")
    parser.add_argument("output", help="Output file for transformed results")
    parser.add_argument("--type", choices=list(available_prompts.keys()),
                        default=list(available_prompts.keys())[0] if available_prompts else None,
                        help="Type of transformation prompt to use")
    parser.add_argument("--format", choices=["default", "booru", "plain"], default="default",
                        help="Output format style (default: auto-detect from prompt type)")
    parser.add_argument("--reasoning-effort", choices=["low", "medium", "high"], default="medium",
                        help="Reasoning effort level for the model (default: medium)")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose reasoning output")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be processed without making API calls")
    args = parser.parse_args()
    
    if not available_prompts:
        print("Error: No prompt files found in the prompts directory", file=sys.stderr)
        sys.exit(1)

    if args.type is None:
        print("Error: No prompt type specified and no prompts available", file=sys.stderr)
        sys.exit(1)

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found", file=sys.stderr)
        sys.exit(1)

    # Check if required system prompt file exists
    prompt_path = Path(__file__).parent.parent / "prompts" / available_prompts[args.type]
    if not prompt_path.exists():
        print(f"Error: System prompt file '{prompt_path}' not found for type '{args.type}'", file=sys.stderr)
        sys.exit(1)

    # Load the system prompt based on type
    system_prompt = load_system_prompt(args.type)

    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    results = []
    # Filter out empty lines for progress tracking
    non_empty_lines = [line.strip() for line in lines if line.strip()]

    # Determine output format
    output_format = args.format
    if output_format == "default":
        output_format = "booru" if args.type.startswith("booru-") else "plain"

    if args.dry_run:
        print(f"Dry run mode - would process {len(non_empty_lines)} lines:")
        print(f"Input file: {input_path}")
        print(f"Output file: {output_path}")
        print(f"Prompt type: {args.type}")
        print(f"Output format: {output_format}")
        print(f"System prompt file: {available_prompts[args.type]}")
        print("\nSample inputs:")
        for i, line in enumerate(non_empty_lines[:3]):
            print(f"  {i+1}. {line}")
        if len(non_empty_lines) > 3:
            print(f"  ... and {len(non_empty_lines) - 3} more")
        return

    for line in tqdm(non_empty_lines, desc=f"Transforming text", unit="line"):
        transformed_line = transform_text(line, system_prompt, args.type, args.reasoning_effort, args.verbose, output_format)
        results.append(transformed_line)

    with open(output_path, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(result + '\n')

    print(f"Completed! Results saved to {output_path}")

if __name__ == "__main__":
    main()