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

The script automatically discovers all `.md` files in the `prompts/` directory. Each file becomes a prompt type using its filename (without extension).

Current available types:
- `booru-costume-tag-generator`: Generate booru-style costume tags
- `booru-pose-tag-generator`: Generate booru-style pose tags  
- `simple-summarizer`: Create concise summaries of text

### Output Formats

- `default`: Auto-detects format based on prompt type (booru format for booru-* prompts, plain for others)
- `booru`: Formats output as `(original:0.5), transformed_text`
- `plain`: Returns only the transformed text

### Examples

```bash
# Generate booru costume tags
python text_transformer.py descriptions.txt costume_tags.txt --type booru-costume-tag-generator

# Summarize text with verbose reasoning
python text_transformer.py articles.txt summaries.txt --type simple-summarizer --verbose

# Dry run to see what would be processed
python text_transformer.py input.txt output.txt --type simple-summarizer --dry-run
```

## Creating Custom Prompts

1. Create a new `.md` file in the `prompts/` directory
2. Write your system prompt instructions
3. The filename (without `.md`) becomes the prompt type
4. The script will automatically discover and make it available

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

The old `booru_tagger.py` script has been renamed and generalized. For backward compatibility:

- Old `--type costume` → New `--type booru-costume-tag-generator`
- Old `--type pose` → New `--type booru-pose-tag-generator`
- Output format automatically detects booru-style formatting for booru-* prompt types
