#!/usr/bin/env python3
"""
Wildcard Extractor - Extract wildcard categories from images using OpenAI Vision API

This script processes images to identify visual elements and generate wildcard entries
for Stable Diffusion prompt generation, based on the style taxonomy defined in
wildcard-extractor.md and prompting-guide-sdxl.md.
"""

import os
import sys
import json
import base64
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import glob

import openai
from tqdm import tqdm


class WildcardExtractor:
    """Extract wildcard categories from images using OpenAI Vision API."""
    
    def __init__(self, wildcard_base_dir: Optional[str] = None, 
                 api_key: Optional[str] = None,
                 script_dir: Optional[str] = None):
        """
        Initialize the WildcardExtractor.
        
        Args:
            wildcard_base_dir: Base directory containing wildcard files (defaults to ./wildcard)
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            script_dir: Directory containing the script and markdown files (auto-detected if None)
        """
        if wildcard_base_dir is None:
            wildcard_base_dir = str(Path(__file__).parent / "wildcard")
        self.wildcard_base_dir = Path(wildcard_base_dir)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Auto-detect script directory if not provided
        if script_dir is None:
            script_dir = str(Path(__file__).parent)
        self.script_dir = Path(script_dir)
        
        # Load system prompt from markdown file
        self.system_prompt = self._load_system_prompt()
        
        # Map wildcard categories to actual files
        self.wildcard_mapping = self._discover_wildcard_files()
        
        print(f"Found {len(self.wildcard_mapping)} wildcard file mappings:")
        for category, file_path in self.wildcard_mapping.items():
            print(f"  {category} -> {file_path}")

    def _load_system_prompt(self) -> str:
        """Load the system prompt from wildcard-extractor.md"""
        prompt_file = self.script_dir / "wildcard-extractor.md"
        
        if not prompt_file.exists():
            # Fallback to hardcoded prompt if file not found
            print(f"Warning: {prompt_file} not found, using hardcoded prompt")
            return self._get_fallback_system_prompt()
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract the system prompt content (everything after the first heading)
            lines = content.split('\n')
            # Skip the first heading line and any empty lines
            start_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('### **SYSTEM PROMPT'):
                    start_idx = i + 1
                    break
            
            return '\n'.join(lines[start_idx:]).strip()
            
        except Exception as e:
            print(f"Error loading prompt from {prompt_file}: {e}")
            return self._get_fallback_system_prompt()

    def _discover_wildcard_files(self) -> Dict[str, Path]:
        """
        Discover actual wildcard files and map categories to them.
        
        Returns:
            Dictionary mapping category names to actual file paths
        """
        mapping = {}
        
        # Define the category mappings to actual files we found
        category_mappings = {
            # Core visual categories - these exist in std/xl/
            "camera": "std/xl/camera.txt",
            "details": "std/xl/details.txt", 
            "distance": "std/xl/distance.txt",
            "environment": "std/xl/environment.txt",
            "lighting": "std/xl/lighting.txt",
            "motion": "std/xl/motion.txt",
            "pose": "std/xl/pose.txt",
            "style": "std/xl/style.txt",
            
            # Outfit categories - map to existing std/outfit/ files
            "accessories": "std/outfit/accessories.txt",
            "bunnygirl": "std/outfit/bunnygirl.txt", 
            "dress": "std/outfit/dress.txt",
            "skirt": "std/outfit/skirt.txt",
            "uniform": "std/outfit/uniform.txt",
            "misc": "std/outfit/misc.txt"
        }
        
        for category, relative_path in category_mappings.items():
            # Try different possible locations
            possible_paths = [
                self.wildcard_base_dir / relative_path,
                Path("wildcard") / relative_path
            ]
            
            # Use the first existing file, or the primary path if none exist
            file_path = None
            for path in possible_paths:
                if path.exists():
                    file_path = path
                    break
            
            if file_path is None:
                # Use the first option as default (will be created if needed)
                file_path = possible_paths[0]
                
            mapping[category] = file_path
            
        return mapping

    def _get_fallback_system_prompt(self) -> str:
        """Fallback system prompt if markdown file can't be loaded"""
        return """You are a **visual style taxonomist**.  
Your task is to analyze a submitted image and produce **prompt fragment entries** organized into predefined wildcard categories used for Stable Diffusion / SDXL style generation.

Each category corresponds to a text file of interchangeable **variants**.  
Each line you generate represents **one possible variation** that could appear when the wildcard is expanded.  
All lines within the same category should describe alternate but compatible interpretations of the image's visual traits.

Your goal is to identify visual elements (composition, lighting, rendering style, character pose, outfit, etc.) and assign them to the correct wildcard categories.

#### **Wildcard Categories and Their Meanings**

| File | Purpose | Examples |
|------|----------|----------|
| `camera` | Shot type, angle, framing, or lens perspective. | "low-angle shot", "wide shot", "overhead view", "dutch angle" |
| `details` | Small symbolic or environmental flourishes. | "shards of glass hover", "a transparent serpent coils nearby", "floating sigils in background" |
| `distance` | Background or far-field elements. | "in the distance, ruins fade into fog", "beyond her, fragmented towers rise" |
| `environment` | Immediate setting or atmosphere around the subject. | "suspended in an abstract void", "amid swirling smoke", "under fractured sky" |
| `lighting` | Light source, color, and quality. | "rim-lit silhouette", "pale diffuse lighting", "harsh high-contrast illumination" |
| `motion` | Visible or implied movement (of subject or medium). | "lines tremble with nervous energy", "paint drips follow gravity", "colors bleed together" |
| `pose` | Character posture, body language, or attitude. | "she floats weightlessly", "she leans forward", "arms spread wide" |
| `style` | Rendering, medium, or overall aesthetic. | "watercolor wash", "abstract oil painting", "high-contrast monochrome ink style" |

**Outfit-related**

| File | Purpose | Examples |
|------|----------|----------|
| `accessories` | Minor garments, jewelry, or props. | "wearing fingerless gloves and choker", "a metallic bracelet catches the light" |
| `bunnygirl` | Bunny-themed outfits or hybrids. | "futuristic bunny uniform", "bunny-inspired bodysuit with ribbons" |
| `dress` | Dresses and gowns. | "flowing chiffon dress", "gothic lace gown", "asymmetrical slip dress" |
| `skirt` | Skirt-based outfits. | "pleated skirt with blouse", "frayed denim skirt", "layered tulle skirt" |
| `uniform` | Structured, thematic uniforms. | "minor league baseball uniform", "ceremonial academy outfit", "military jacket with insignia" |
| `misc` | Catch-all for clothing not fitting the above. | "layered streetwear ensemble", "armored bodysuit", "tattered robes" |

#### **Output Format**

Return a single JSON object where:
- Each key is one of the category names (without .txt extension).  
- Each value is an array of short strings.  
- Each string is **one variant line** that could be added to the corresponding wildcard file.  
- If a category isn't relevant, omit it.

**Guidelines:**
- Describe what is visually evident, not inferred narrative meaning.
- Keep each line self-contained and prompt-usable.
- Avoid redundancy across lines within the same category.
- Don't use full sentences; each line should be a compact descriptive phrase.
- Maintain neutral tone—no subjective words like "beautiful" or "eerie."
- Multiple lines under a key = alternate variations, not sequential descriptors.
- Skip any category irrelevant to the current image."""

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _get_system_prompt(self) -> str:
        """Get the system prompt for wildcard extraction."""
        return self.system_prompt

    def extract_wildcards(self, image_path: str) -> Dict[str, List[str]]:
        """
        Extract wildcard categories from an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary mapping wildcard filenames to lists of extracted variations
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Encode image
        base64_image = self._encode_image(image_path)
        
        # Create the message
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt()
            },
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze this image and extract wildcard categories as JSON:"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        # Call OpenAI API
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=2000,
                temperature=0.5
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            
            if not content:
                raise ValueError("Empty response from OpenAI")
            
            # Extract JSON from response (in case there's extra text)
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_content = content[json_start:json_end]
            wildcards = json.loads(json_content)
            
            return wildcards
            
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return {}

    def append_to_wildcard_files(self, wildcards: Dict[str, List[str]], 
                                dry_run: bool = False) -> None:
        """
        Append extracted wildcards to their respective files.
        
        Args:
            wildcards: Dictionary mapping category names to lists of wildcard entries
            dry_run: If True, only print what would be written without actually writing
        """
        for category, entries in wildcards.items():
            if not entries:
                continue
            
            # Normalize category name (remove .txt extension if present)
            normalized_category = category.replace('.txt', '') if category.endswith('.txt') else category
            
            # Get the actual file path for this category
            if normalized_category not in self.wildcard_mapping:
                print(f"Warning: Unknown category '{category}' (normalized: '{normalized_category}'), skipping")
                continue
                
            file_path = self.wildcard_mapping[normalized_category]
            
            if dry_run:
                print(f"\nWould append to {file_path}:")
                for entry in entries:
                    print(f"  + {entry}")
                continue
            
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Read existing entries to avoid duplicates
            existing_entries = set()
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_entries = {line.strip() for line in f if line.strip()}
            
            # Filter out duplicates
            new_entries = [entry for entry in entries if entry not in existing_entries]
            
            if new_entries:
                with open(file_path, 'a', encoding='utf-8') as f:
                    for entry in new_entries:
                        f.write(f"{entry}\n")
                print(f"Added {len(new_entries)} new entries to {normalized_category} ({file_path})")
            else:
                print(f"No new entries for {normalized_category} (all were duplicates)")

    def process_image(self, image_path: str, dry_run: bool = False) -> Dict[str, List[str]]:
        """
        Process a single image and optionally append results to wildcard files.
        
        Args:
            image_path: Path to the image file
            dry_run: If True, don't actually write to files
            
        Returns:
            Dictionary of extracted wildcards
        """
        print(f"Processing: {os.path.basename(image_path)}")
        
        wildcards = self.extract_wildcards(image_path)
        
        if wildcards:
            print(f"Extracted {sum(len(entries) for entries in wildcards.values())} wildcard entries")
            self.append_to_wildcard_files(wildcards, dry_run=dry_run)
        else:
            print("No wildcards extracted")
            
        return wildcards

    def process_images(self, image_paths: List[str], dry_run: bool = False) -> Dict[str, Dict[str, List[str]]]:
        """
        Process multiple images with progress tracking.
        
        Args:
            image_paths: List of paths to image files
            dry_run: If True, don't actually write to files
            
        Returns:
            Dictionary mapping image paths to their extracted wildcards
        """
        results = {}
        
        for image_path in tqdm(image_paths, desc="Processing images"):
            try:
                wildcards = self.process_image(image_path, dry_run=dry_run)
                results[image_path] = wildcards
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
                results[image_path] = {}
                
        return results

    @staticmethod
    def discover_image_files(paths: List[str]) -> List[str]:
        """
        Discover image files from a list of paths (files or directories).
        
        Args:
            paths: List of file paths or directory paths
            
        Returns:
            List of valid image file paths
        """
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
        discovered_files = []
        
        for path in paths:
            path_obj = Path(path)
            
            if path_obj.is_file():
                # Single file
                if path_obj.suffix.lower() in image_extensions:
                    discovered_files.append(str(path_obj))
                else:
                    print(f"Warning: '{path}' is not a recognized image file")
                    
            elif path_obj.is_dir():
                # Directory - find all image files
                print(f"Scanning directory: {path}")
                dir_files = []
                for ext in image_extensions:
                    pattern = str(path_obj / f"*{ext}")
                    dir_files.extend(glob.glob(pattern))
                    pattern = str(path_obj / f"*{ext.upper()}")
                    dir_files.extend(glob.glob(pattern))
                
                # Remove duplicates from this directory before adding to main list
                unique_dir_files = list(set(dir_files))
                discovered_files.extend(unique_dir_files)
                print(f"Found {len(unique_dir_files)} image files in {path}")
                
            else:
                print(f"Warning: Path not found: {path}")
        
        # Remove duplicates and sort
        discovered_files = sorted(list(set(discovered_files)))
        return discovered_files

    def generate_summary_report(self, results: Dict[str, Dict[str, List[str]]], 
                              summary_file: str) -> None:
        """
        Generate a markdown summary report of all extracted wildcards.
        
        Args:
            results: Dictionary mapping image paths to their extracted wildcards
            summary_file: Path to save the summary markdown file
        """
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"# Wildcard Extraction Summary\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Overall statistics
                total_images = len(results)
                total_entries = sum(
                    sum(len(entries) for entries in wildcards.values()) 
                    for wildcards in results.values() if wildcards
                )
                
                f.write(f"## Summary Statistics\n\n")
                f.write(f"- **Images Processed:** {total_images}\n")
                f.write(f"- **Total Wildcards Extracted:** {total_entries}\n")
                f.write(f"- **Average per Image:** {total_entries/total_images:.1f}\n\n")
                
                # Category breakdown
                category_totals = {}
                for wildcards in results.values():
                    if wildcards:
                        for category, entries in wildcards.items():
                            normalized_cat = category.replace('.txt', '') if category.endswith('.txt') else category
                            category_totals[normalized_cat] = category_totals.get(normalized_cat, 0) + len(entries)
                
                if category_totals:
                    f.write(f"## Category Breakdown\n\n")
                    for category, count in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
                        f.write(f"- **{category}:** {count} entries\n")
                    f.write("\n")
                
                # Per-file details
                f.write(f"## Per-File Results\n\n")
                
                for image_path, wildcards in results.items():
                    image_name = Path(image_path).name
                    f.write(f"### {image_name}\n\n")
                    
                    if not wildcards:
                        f.write("*No wildcards extracted*\n\n")
                        continue
                        
                    total_for_image = sum(len(entries) for entries in wildcards.values())
                    f.write(f"**Total entries:** {total_for_image}\n\n")
                    
                    for category, entries in wildcards.items():
                        if entries:
                            normalized_cat = category.replace('.txt', '') if category.endswith('.txt') else category
                            f.write(f"#### {normalized_cat.title()} ({len(entries)} entries)\n\n")
                            for entry in entries:
                                f.write(f"- {entry}\n")
                            f.write("\n")
                
                # All unique entries by category
                f.write(f"## All Extracted Wildcards by Category\n\n")
                
                all_entries_by_category = {}
                for wildcards in results.values():
                    if wildcards:
                        for category, entries in wildcards.items():
                            normalized_cat = category.replace('.txt', '') if category.endswith('.txt') else category
                            if normalized_cat not in all_entries_by_category:
                                all_entries_by_category[normalized_cat] = set()
                            all_entries_by_category[normalized_cat].update(entries)
                
                for category in sorted(all_entries_by_category.keys()):
                    entries = sorted(all_entries_by_category[category])
                    f.write(f"### {category.title()} ({len(entries)} unique entries)\n\n")
                    for entry in entries:
                        f.write(f"- {entry}\n")
                    f.write("\n")
                        
            print(f"Summary report saved to: {summary_file}")
            
        except Exception as e:
            print(f"Error generating summary report: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract wildcard categories from images using OpenAI Vision API"
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Path(s) to image files or directories to process"
    )
    parser.add_argument(
        "--wildcard-dir",
        help="Base directory for wildcard files (default: ./wildcard)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be written without actually writing files"
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (defaults to OPENAI_API_KEY environment variable)"
    )
    parser.add_argument(
        "--summary-file",
        help="Save a complete summary report to this markdown file"
    )
    
    args = parser.parse_args()
    
    try:
        extractor = WildcardExtractor(
            wildcard_base_dir=args.wildcard_dir,
            api_key=args.api_key
        )
        
        # Discover all image files from paths (files and directories)
        print("Discovering image files...")
        valid_images = extractor.discover_image_files(args.paths)
        
        if not valid_images:
            print("No valid image files found!")
            sys.exit(1)
        
        print(f"Found {len(valid_images)} image files to process")
        
        # Process images
        results = extractor.process_images(valid_images, dry_run=args.dry_run)
        
        # Calculate summary statistics
        total_entries = sum(
            sum(len(entries) for entries in wildcards.values()) 
            for wildcards in results.values() if wildcards
        )
        
        successful_images = len([r for r in results.values() if r])
        
        print(f"\n=== Summary ===")
        print(f"Processed {len(valid_images)} images")
        print(f"Successfully extracted from {successful_images} images")
        print(f"Extracted {total_entries} total wildcard entries")
        
        if args.dry_run:
            print("(Dry run - no files were modified)")
        
        # Generate summary report if requested
        if args.summary_file and results:
            print(f"\nGenerating summary report...")
            extractor.generate_summary_report(results, args.summary_file)
        
    except KeyboardInterrupt:
        print("\nCancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()