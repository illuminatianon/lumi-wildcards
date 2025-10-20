#!/usr/bin/env python3
"""
Booru Tag Generator - Generate booru-style tags for various types of descriptions.
Supports costume, pose, and other tag types with specialized system prompts.
"""
import argparse
from openai import OpenAI
import sys
from pathlib import Path
from tqdm import tqdm

def load_system_prompt(prompt_type):
    """Load the system prompt from the appropriate markdown file based on type."""
    prompt_files = {
        "costume": "booru-costume-tag-generator.md",
        "pose": "booru-pose-tag-generator.md"
    }
    
    if prompt_type not in prompt_files:
        print(f"Error: Unknown prompt type '{prompt_type}'. Available types: {list(prompt_files.keys())}", file=sys.stderr)
        sys.exit(1)
    
    try:
        prompt_path = Path(__file__).parent / prompt_files[prompt_type]
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading system prompt for '{prompt_type}': {e}", file=sys.stderr)
        fallback_prompts = {
            "costume": "Generate booru-style costume tags from the description. Return 5-6 tags maximum.",
            "pose": "Generate booru-style pose and action tags from the description. Return 3-4 tags maximum."
        }
        return fallback_prompts.get(prompt_type, "Generate booru-style tags from the description.")

def get_booru_tags(input_line, system_prompt, prompt_type, reasoning_effort="medium", verbose=False):
    """Get booru tags for a description using GPT-4."""
    # Initialize OpenAI client when needed
    client = OpenAI()
    
    # Create the user message with the appropriate label based on type
    type_labels = {
        "costume": "Costume",
        "pose": "Pose/Action"
    }
    label = type_labels.get(prompt_type, "Input")
    user_prompt = f"\n\n{label}: {input_line.strip()}\n\nTags:"
    
    system_prompt = system_prompt + user_prompt
    
    try:
        # Prepare API call parameters
        api_params = {
            "model": "gpt-5-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
            ],
            "max_completion_tokens": 10000,
            "reasoning_effort": "medium"
        }
                
        response = client.chat.completions.create(**api_params)
        tags = response.choices[0].message.content
        
        # If verbose mode is enabled, show reasoning
        if verbose and hasattr(response.choices[0].message, 'reasoning'):
            print(f"\n--- Reasoning for '{input_line.strip()}' ---")
            print(response.choices[0].message.reasoning)
            print("--- End Reasoning ---\n")
        
        if tags:
            tags = tags.strip()
            return f"({input_line.strip()}:0.5), {tags}"
        else:
            return input_line.strip()
    except Exception as e:
        print(f"Error processing '{input_line.strip()}': {e}", file=sys.stderr)
        return input_line.strip()

def main():
    parser = argparse.ArgumentParser(
        description="Generate booru tags for descriptions",
        epilog="""
Examples:
  python booru_tagger.py input.txt output.txt --type costume
  python booru_tagger.py poses.txt pose_tags.txt --type pose --verbose
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("input", help="Input file with descriptions (one per line)")
    parser.add_argument("output", help="Output file for tagged results")
    parser.add_argument("--type", choices=["costume", "pose"], default="costume",
                        help="Type of tags to generate (default: costume)")
    parser.add_argument("--reasoning-effort", choices=["low", "medium", "high"], default="medium",
                        help="Reasoning effort level for the model (default: medium)")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose reasoning output")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be processed without making API calls")
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Check if required system prompt file exists
    prompt_files = {
        "costume": "booru-costume-tag-generator.md",
        "pose": "booru-pose-tag-generator.md"
    }
    prompt_path = Path(__file__).parent / prompt_files[args.type]
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
    
    type_descriptions = {
        "costume": "costumes",
        "pose": "poses"
    }
    desc = type_descriptions.get(args.type, "items")
    
    if args.dry_run:
        print(f"Dry run mode - would process {len(non_empty_lines)} {desc}:")
        print(f"Input file: {input_path}")
        print(f"Output file: {output_path}")
        print(f"Type: {args.type}")
        print(f"System prompt file: {prompt_files[args.type]}")
        print("\nSample inputs:")
        for i, line in enumerate(non_empty_lines[:3]):
            print(f"  {i+1}. {line}")
        if len(non_empty_lines) > 3:
            print(f"  ... and {len(non_empty_lines) - 3} more")
        return
    
    for line in tqdm(non_empty_lines, desc=f"Processing {desc}", unit=args.type):
        tagged_line = get_booru_tags(line, system_prompt, args.type, args.reasoning_effort, args.verbose)
        results.append(tagged_line)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(result + '\n')
    
    print(f"Completed! Results saved to {output_path}")

if __name__ == "__main__":
    main()