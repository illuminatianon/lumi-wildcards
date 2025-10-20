# Text Transformer

A generalized script for transforming lines of text according to LLM prompts. Originally designed for generating booru-style tags, but now supports any type of text transformation.

## Usage

```bash
python text_transformer.py input.txt output.txt --type <prompt_type> [options]
```

### Arguments

- `input`: Input file with text lines to transform (one per line)
- `output`: Output file for transformed results
- `--type`: Type of transformation prompt to use (see available types below)
- `--format`: Output format style (`default`, `booru`, `plain`)
- `--reasoning-effort`: Reasoning effort level (`low`, `medium`, `high`)
- `--verbose`: Enable verbose reasoning output
- `--dry-run`: Show what would be processed without making API calls

### Available Prompt Types

The script uses predefined prompt types with simple identifiers:

- `costume-booru`: Generate booru-style costume tags
- `pose-booru`: Generate booru-style pose tags
- `pose-xl`: Generate SDXL-style pose descriptions

Use `--help` to see all available types with descriptions.

### Output Formats

- `default`: Auto-detects format based on prompt type (booru format for booru-* prompts, plain for others)
- `booru`: Formats output as `(original:0.5), transformed_text`
- `plain`: Returns only the transformed text

### Examples

```bash
# Generate booru costume tags
python text_transformer.py descriptions.txt costume_tags.txt --type costume-booru

# Generate pose tags with verbose reasoning
python text_transformer.py poses.txt pose_tags.txt --type pose-booru --verbose

# Generate SDXL pose descriptions with plain output format
python text_transformer.py descriptions.txt poses.txt --type pose-xl --format plain

# Dry run to see what would be processed
python text_transformer.py input.txt output.txt --type costume-booru --dry-run
```

## Adding Custom Prompts

1. Create a new `.md` file in the `prompts/` directory with your system prompt
2. Add an entry to the `get_prompt_config()` function in `text_transformer.py`:
   ```python
   "your-id": {
       "file": "your-prompt-file.md",  # Single file
       "description": "Brief description of what it does"
   }
   ```

   Or for multiple prompt files that get combined:
   ```python
   "your-id": {
       "file": ["base-prompt.md", "specific-prompt.md"],  # Multiple files
       "description": "Brief description of what it does"
   }
   ```
3. The new prompt type will be available with the simple identifier

### Multiple Prompt Files

The script supports combining multiple prompt files in a specified order. When using an array of files, they are loaded and combined with `---` separators between them. This is useful for:

- Combining general guidelines with specific instructions
- Reusing common prompt components across different types
- Building complex prompts from modular pieces

Example: `pose-xl` combines the general SDXL prompting guide with specific pose generation instructions.

### Prompt File Format

```markdown
# Your Prompt Title

Your system prompt instructions here.

## Guidelines:
- Specific instructions for the transformation
- Output format requirements
- Any constraints or rules

## Output Format:
Specify how the output should be formatted.
```

## Requirements

- Python 3.7+
- OpenAI API key (set as environment variable `OPENAI_API_KEY`)
- Required packages: `openai`, `tqdm`

## Migration from booru_tagger.py

The old `booru_tagger.py` script has been renamed and generalized with new simple identifiers:

- Old `--type costume` → New `--type costume-booru`
- Old `--type pose` → New `--type pose-booru`
- Output format automatically detects booru-style formatting for *-booru prompt types
