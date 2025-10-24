#!/usr/bin/env python3
"""
WCT (Wildcard Tool) - Analyze, categorize, and clean wildcard files for Stable Diffusion.
Supports multiple modes for comprehensive wildcard file management.
"""
import argparse
import json
import sys
from pathlib import Path
from openai import OpenAI
import yaml
from typing import Dict, List, Any, Optional
import tempfile
import os

class WildcardTool:
    """Main class for wildcard file processing."""
    
    def __init__(self, reasoning_effort: str = "medium", verbose: bool = False):
        """Initialize the wildcard tool."""
        self.client = OpenAI()
        self.reasoning_effort = reasoning_effort
        self.verbose = verbose
        self.prompts_dir = Path(__file__).parent / "prompts" / "wct"
        
        # Cache for categorization results
        self.cache_dir = Path(__file__).parent / ".wct_cache"
        self.cache_dir.mkdir(exist_ok=True)
    
    def load_prompt(self, prompt_name: str) -> str:
        """Load a prompt from the prompts/wct directory."""
        prompt_files = {
            "sdxl": "sdxl-prompting-guide.md",
            "intro": "wildcard_intro.md",
            "categorize": "categorize.md",
            "analyze": "analyze.md",
            "cleanup": "cleanup.md",
            "output": "output.md"
        }

        if prompt_name not in prompt_files:
            raise ValueError(f"Unknown prompt: {prompt_name}")

        # SDXL prompt is in parent prompts directory, others are in wct subdirectory
        if prompt_name == "sdxl":
            prompt_path = self.prompts_dir.parent / "prompting-guide-sdxl.md"
        else:
            prompt_path = self.prompts_dir / prompt_files[prompt_name]
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    def get_cache_path(self, input_file: Path) -> Path:
        """Get cache file path for categorization results."""
        cache_name = f"{input_file.stem}_categories.json"
        return self.cache_dir / cache_name
    
    def load_cached_categories(self, input_file: Path) -> Optional[Dict[str, Any]]:
        """Load cached categorization results if available."""
        cache_path = self.get_cache_path(input_file)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                if self.verbose:
                    print(f"Warning: Could not load cache: {e}")
        return None
    
    def save_cached_categories(self, input_file: Path, categories: Dict[str, Any]):
        """Save categorization results to cache."""
        cache_path = self.get_cache_path(input_file)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(categories, f, indent=2)
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not save cache: {e}")
    
    def call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Make a call to the LLM with the given prompts."""
        try:
            api_params = {
                "model": "gpt-5",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_completion_tokens": 10000,
                "reasoning_effort": self.reasoning_effort
            }
            
            response = self.client.chat.completions.create(**api_params)
            output = response.choices[0].message.content
            
            # Show reasoning if verbose mode is enabled
            if self.verbose and hasattr(response.choices[0].message, 'reasoning'):
                print(f"\n--- LLM Reasoning ---")
                print(response.choices[0].message.reasoning)
                print("--- End Reasoning ---\n")
            
            return output
            
        except Exception as e:
            print(f"Error calling LLM: {e}", file=sys.stderr)
            sys.exit(1)

    def filter_real_categories(self, categories: Dict[str, Any]) -> Dict[str, Any]:
        """Filter out synthetic categories that contain only references like __std/xl/path/category__"""
        if not isinstance(categories, dict):
            return categories

        filtered = {}
        for key, value in categories.items():
            if key in ['purpose', 'raw_response']:
                # Keep metadata fields
                filtered[key] = value
            elif isinstance(value, list):
                # Check if this is a real category (contains actual entries, not just references)
                real_entries = []
                for entry in value:
                    if isinstance(entry, str) and not (entry.startswith('__') and entry.endswith('__')):
                        real_entries.append(entry)

                # Only include categories that have real entries
                if real_entries:
                    filtered[key] = real_entries
            else:
                # Keep non-list values (like descriptions)
                filtered[key] = value

        return filtered

    def categorize(self, input_file: Path, force_refresh: bool = False) -> Dict[str, Any]:
        """Categorize the wildcard file and cache results."""
        # Check cache first unless force refresh
        if not force_refresh:
            cached = self.load_cached_categories(input_file)
            if cached:
                if self.verbose:
                    print("Using cached categorization results")
                return cached
        
        # Load wildcard file content
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Combine intro and categorize prompts
        sdxl_prompt = self.load_prompt("sdxl")
        intro_prompt = self.load_prompt("intro")
        categorize_prompt = self.load_prompt("categorize")
        system_prompt = f"{sdxl_prompt}\n\n---\n\n{intro_prompt}\n\n---\n\n{categorize_prompt}"
        
        user_prompt = f"Wildcard filename: {input_file.name}\n\nWildcard file content:\n\n{content}"
        
        response = self.call_llm(system_prompt, user_prompt)
        
        # Parse the response as YAML/structured data
        try:
            # Try to extract YAML from the response
            if "```yaml" in response:
                yaml_start = response.find("```yaml") + 7
                yaml_end = response.find("```", yaml_start)
                yaml_content = response[yaml_start:yaml_end].strip()
                categories = yaml.safe_load(yaml_content)
            elif "purpose:" in response:
                # Direct YAML response
                categories = yaml.safe_load(response)
            else:
                # Fallback: treat as structured text
                categories = {"raw_response": response}
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not parse categorization as YAML: {e}")
            categories = {"raw_response": response}
        
        # Cache the results
        self.save_cached_categories(input_file, categories)
        
        return categories
    
    def analyze(self, input_file: Path, analysis_type: str = "short", categories: Optional[Dict[str, Any]] = None) -> str:
        """Analyze the wildcard file distribution and patterns."""
        # Load wildcard file content
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get categories if not provided
        if categories is None:
            categories = self.categorize(input_file)

        # Filter out synthetic categories for analysis
        categories = self.filter_real_categories(categories)
        
        # Combine intro and analyze prompts
        sdxl_prompt = self.load_prompt("sdxl")
        intro_prompt = self.load_prompt("intro")
        analyze_prompt = self.load_prompt("analyze")
        system_prompt = f"{sdxl_prompt}\n\n---\n\n{intro_prompt}\n\n---\n\n{analyze_prompt}"
        
        # Prepare user prompt with categories and mode
        categories_text = yaml.dump(categories, default_flow_style=False) if categories else "No categories available"
        user_prompt = f"""Wildcard filename: {input_file.name}
Mode: {analysis_type}

Categories:
{categories_text}

Wildcard file content:
{content}"""
        
        return self.call_llm(system_prompt, user_prompt)
    
    def cleanup(self, input_file: Path, categories: Optional[Dict[str, Any]] = None, analysis: Optional[str] = None) -> str:
        """Clean up and reconstruct the wildcard file."""
        # Load wildcard file content
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get categories and analysis if not provided
        if categories is None:
            categories = self.categorize(input_file)

        # Filter out synthetic categories for cleanup
        categories = self.filter_real_categories(categories)

        if analysis is None:
            analysis = self.analyze(input_file, "long", categories)
        
        # Combine intro and cleanup prompts
        sdxl_prompt = self.load_prompt("sdxl")
        intro_prompt = self.load_prompt("intro")
        cleanup_prompt = self.load_prompt("cleanup")
        system_prompt = f"{sdxl_prompt}\n\n---\n\n{intro_prompt}\n\n---\n\n{cleanup_prompt}"
        
        # Prepare user prompt with all context
        categories_text = yaml.dump(categories, default_flow_style=False) if categories else "No categories available"
        user_prompt = f"""Wildcard filename: {input_file.name}

Categories:
{categories_text}

Analysis Results:
{analysis}

Original Wildcard Content:
{content}"""
        
        return self.call_llm(system_prompt, user_prompt)
    
    def output_format(self, cleaned_content: str, output_type: str = "text", categories: Optional[Dict[str, Any]] = None, input_file: Optional[Path] = None) -> str:
        """Format the output according to the specified type."""
        if output_type == "text":
            # For text output, just return the cleaned content as-is
            return cleaned_content
        elif output_type == "yaml":
            # Use the output prompt to generate YAML format
            sdxl_prompt = self.load_prompt("sdxl")
            intro_prompt = self.load_prompt("intro")
            output_prompt = self.load_prompt("output")
            system_prompt = f"{sdxl_prompt}\n\n---\n\n{intro_prompt}\n\n---\n\n{output_prompt}"
            
            categories_text = yaml.dump(categories, default_flow_style=False) if categories else "No categories available"
            filename_text = f"Wildcard filename: {input_file.name}" if input_file else "Wildcard filename: unknown"
            user_prompt = f"""{filename_text}
Output format: yaml

Categories:
{categories_text}

Cleaned content to format:
{cleaned_content}"""
            
            return self.call_llm(system_prompt, user_prompt)
        else:
            raise ValueError(f"Unknown output type: {output_type}")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="WCT (Wildcard Tool) - Analyze, categorize, and clean wildcard files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  wct.py poses.txt --categorize
  wct.py poses.txt --analyze short
  wct.py poses.txt --analyze long --verbose
  wct.py poses.txt --cleanup --output yaml
  wct.py poses.txt --categorize --analyze short --cleanup --save-to cleaned_poses.yaml
  wct.py poses.txt --cleanup --force-refresh --reasoning-effort high
        """
    )
    
    parser.add_argument("input", help="Input wildcard file to process")
    parser.add_argument("--analyze", choices=["short", "long"], 
                        help="Analyze the wildcard file (short=frequency table, long=detailed report)")
    parser.add_argument("--categorize", action="store_true",
                        help="Perform categorization step and display results")
    parser.add_argument("--cleanup", action="store_true", 
                        help="Clean up and reconstruct the wildcard file")
    parser.add_argument("--output", choices=["text", "yaml"], default="text",
                        help="Output format (text=plain lines, yaml=structured format)")
    parser.add_argument("--reasoning-effort", choices=["low", "medium", "high"], default="medium",
                        help="Reasoning effort level for the model")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose output including LLM reasoning")
    parser.add_argument("--force-refresh", action="store_true",
                        help="Force refresh of cached categorization results")
    parser.add_argument("--save-to", help="Save output to specified file instead of printing")
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found", file=sys.stderr)
        sys.exit(1)
    
    # At least one action must be specified
    if not any([args.analyze, args.categorize, args.cleanup]):
        print("Error: Must specify at least one action (--analyze, --categorize, or --cleanup)", file=sys.stderr)
        sys.exit(1)
    
    # Initialize the tool
    tool = WildcardTool(reasoning_effort=args.reasoning_effort, verbose=args.verbose)
    
    try:
        output_content = ""
        categories = None
        
        # Execute requested operations in logical order
        if args.categorize or args.analyze or args.cleanup:
            if args.verbose:
                print("Performing categorization...")
            categories = tool.categorize(input_path, args.force_refresh)
            
            if args.categorize:
                output_content += "=== CATEGORIZATION RESULTS ===\n"
                output_content += yaml.dump(categories, default_flow_style=False)
                output_content += "\n"
        
        if args.analyze:
            if args.verbose:
                print(f"Performing {args.analyze} analysis...")
            analysis = tool.analyze(input_path, args.analyze, categories)
            output_content += f"=== ANALYSIS ({args.analyze.upper()}) ===\n"
            output_content += analysis + "\n\n"
        
        if args.cleanup:
            if args.verbose:
                print("Performing cleanup...")
            # Get detailed analysis for cleanup if not already done
            analysis = tool.analyze(input_path, "long", categories) if not args.analyze else None
            cleaned = tool.cleanup(input_path, categories, analysis)
            
            # Format the output
            formatted_output = tool.output_format(cleaned, args.output, categories, input_path)
            output_content += "=== CLEANED OUTPUT ===\n"
            output_content += formatted_output
        
        # Output results
        if args.save_to:
            with open(args.save_to, 'w', encoding='utf-8') as f:
                f.write(output_content)
            print(f"Results saved to {args.save_to}")
        else:
            print(output_content)
            
    except KeyboardInterrupt:
        print("\nCancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
