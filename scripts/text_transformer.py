#!/usr/bin/env -S uv run --quiet
# /// script
# dependencies = [
#   "openai",
#   "tqdm",
# ]
# ///
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

def get_prompt_config():
    """Get predefined prompt types with simple identifiers and descriptions."""
    return {
        "costume-booru": {
            "file": "booru-costume-tag-generator.md",
            "description": "Generate booru-style costume tags"
        },
        "pose-booru": {
            "file": "booru-pose-tag-generator.md",
            "description": "Generate booru-style pose tags"
        },
        "pose-xl": {
            "file": ["prompting-guide-sdxl.md", "sdxl-pose-generator.md"],
            "description": "Generate SDXL-style pose descriptions"
        },
        "costume-xl": {
            "file": ["prompting-guide-sdxl.md", "sdxl-costume-generator.md"],
            "description": "Generate SDXL-style costume descriptors"
        }
    }

def get_available_prompts():
    """Get available prompt types that actually exist on disk."""
    config = get_prompt_config()
    prompts_dir = Path(__file__).parent.parent / "prompts"

    available = {}
    for prompt_id, prompt_info in config.items():
        files = prompt_info["file"]

        # Handle both single file and array of files
        if isinstance(files, str):
            files = [files]

        # Check if all required files exist
        all_exist = True
        for file_name in files:
            prompt_path = prompts_dir / file_name
            if not prompt_path.exists():
                all_exist = False
                break

        if all_exist:
            available[prompt_id] = prompt_info

    return available

def load_system_prompt(prompt_type):
    """Load the system prompt from the appropriate markdown file(s) based on type."""
    available_prompts = get_available_prompts()

    if prompt_type not in available_prompts:
        available_types = list(available_prompts.keys())
        print(f"Error: Unknown prompt type '{prompt_type}'. Available types: {available_types}", file=sys.stderr)
        sys.exit(1)

    try:
        files = available_prompts[prompt_type]["file"]

        # Handle both single file and array of files
        if isinstance(files, str):
            files = [files]

        # Load and combine all prompt files in order
        combined_prompt = ""
        prompts_dir = Path(__file__).parent.parent / "prompts"

        for i, file_name in enumerate(files):
            prompt_path = prompts_dir / file_name
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

                # Add separator between files (except for the first one)
                if i > 0:
                    combined_prompt += "\n\n---\n\n"

                combined_prompt += content

        return combined_prompt

    except Exception as e:
        print(f"Error loading system prompt for '{prompt_type}': {e}", file=sys.stderr)
        return f"Transform the following text according to the '{prompt_type}' style."

def transform_text(input_line, system_prompt, prompt_type, reasoning_effort="medium", verbose=False, output_format="default"):
    """Transform text using an LLM according to the system prompt."""
    # Initialize OpenAI client when needed
    client = OpenAI()

    # Create the user message - use specific labels for certain prompt types
    type_labels = {
        "costume-booru": "Costume",
        "pose-booru": "Pose/Action",
        "pose-xl": "Pose/Action"
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
            if output_format == "booru" or prompt_type.endswith("-booru"):
                return f"({input_line.strip()}:0.5), {output}"
            else:
                return output
        else:
            return input_line.strip()
    except Exception as e:
        print(f"Error processing '{input_line.strip()}': {e}", file=sys.stderr)
        return input_line.strip()

def main():
    # Get available prompt types
    available_prompts = get_available_prompts()

    # Create help text with descriptions
    type_descriptions = []
    for prompt_id, prompt_info in available_prompts.items():
        type_descriptions.append(f"  {prompt_id:<15} - {prompt_info['description']}")

    help_text = "\n".join(type_descriptions) if type_descriptions else "  No prompt types available"

    parser = argparse.ArgumentParser(
        description="Transform lines of text according to LLM prompts",
        epilog=f"""
Available prompt types:
{help_text}

Examples:
  python text_transformer.py input.txt output.txt --type costume-booru
  python text_transformer.py poses.txt pose_tags.txt --type pose-booru --verbose
  python text_transformer.py descriptions.txt transformed.txt --type pose-xl --format plain
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

    # Check if required system prompt file(s) exist
    files = available_prompts[args.type]["file"]
    if isinstance(files, str):
        files = [files]

    prompts_dir = Path(__file__).parent.parent / "prompts"
    for file_name in files:
        prompt_path = prompts_dir / file_name
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
        output_format = "booru" if args.type.endswith("-booru") else "plain"

    if args.dry_run:
        print(f"Dry run mode - would process {len(non_empty_lines)} lines:")
        print(f"Input file: {input_path}")
        print(f"Output file: {output_path}")
        print(f"Prompt type: {args.type} - {available_prompts[args.type]['description']}")
        print(f"Output format: {output_format}")

        # Show prompt files (handle both single and multiple files)
        files = available_prompts[args.type]["file"]
        if isinstance(files, str):
            print(f"System prompt file: {files}")
        else:
            print(f"System prompt files: {', '.join(files)}")

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