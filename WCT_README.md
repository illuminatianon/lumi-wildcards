# WCT (Wildcard Tool)

A comprehensive tool for analyzing, categorizing, and cleaning wildcard files used with Stable Diffusion XL. The tool uses LLM prompts to understand wildcard file structure and provide intelligent analysis and cleanup.

## Features

- **Categorization**: Automatically categorize wildcard entries into logical groups
- **Analysis**: Generate frequency tables and detailed reports on wildcard distribution
- **Cleanup**: Reconstruct wildcard files with balanced representation and reduced redundancy
- **Multiple Output Formats**: Support for both plain text and YAML output
- **Caching**: Intelligent caching of categorization results for faster subsequent operations
- **Verbose Mode**: Optional detailed reasoning output from the LLM

## Installation

Ensure you have the required dependencies:

```bash
pip install PyYAML openai
```

Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Basic Commands

```bash
# Categorize a wildcard file
python wct.py poses.txt --categorize

# Analyze distribution (short frequency table)
python wct.py poses.txt --analyze short

# Analyze distribution (detailed report)
python wct.py poses.txt --analyze long

# Clean up and reconstruct the file
python wct.py poses.txt --cleanup

# Clean up and output as YAML
python wct.py poses.txt --cleanup --output yaml

# Save results to a file
python wct.py poses.txt --analyze long --save-to analysis_report.txt
```

### Advanced Options

```bash
# Force refresh cached categorization
python wct.py poses.txt --categorize --force-refresh

# Use verbose mode to see LLM reasoning
python wct.py poses.txt --analyze short --verbose

# Adjust reasoning effort (affects quality and cost)
python wct.py poses.txt --cleanup --reasoning-effort high

# Combine multiple operations
python wct.py poses.txt --categorize --analyze long --cleanup --output yaml
```

## Modes

### --categorize
Performs semantic analysis of the wildcard file to:
- Identify the overall purpose/theme
- Group entries into logical categories
- Cache results for future operations

### --analyze {short|long}
Analyzes the distribution and patterns:
- **short**: Simple frequency table showing category counts and percentages
- **long**: Detailed report including redundancy analysis, bias observations, and improvement suggestions

### --cleanup
Reconstructs the wildcard file by:
- Removing or merging redundant entries
- Balancing representation across categories
- Generating new entries for underrepresented categories
- Maintaining the original tone and style

### --output {text|yaml}
Controls output format:
- **text**: Plain text lines suitable for .txt wildcard files
- **yaml**: Structured YAML format with categories and subcategories

## Examples

### Example 1: Quick Analysis
```bash
python wct.py wildcards/std/poses.txt --analyze short
```

Output:
```
=== ANALYSIS (SHORT) ===
total entries: 122

frequency by category:
- dynamic_action: 27 (22.1%)
- stylistic_variations: 18 (14.8%)
- gestures_hands: 11 (9.0%)
- expressive_emotion: 11 (9.0%)
...
```

### Example 2: Full Workflow
```bash
# Step 1: Categorize and cache results
python wct.py poses.txt --categorize

# Step 2: Detailed analysis
python wct.py poses.txt --analyze long --save-to poses_analysis.txt

# Step 3: Clean up and restructure
python wct.py poses.txt --cleanup --output yaml --save-to poses_cleaned.yaml
```

### Example 3: Verbose Analysis
```bash
python wct.py poses.txt --analyze long --verbose --reasoning-effort high
```

## File Structure

The tool uses modular prompts located in `prompts/wct/`:
- `wildcard_intro.md`: Base context about wildcards and SDXL
- `categorize.md`: Categorization system prompt
- `analyze.md`: Analysis system prompt  
- `cleanup.md`: Cleanup and reconstruction prompt
- `output.md`: Output formatting prompt

## Caching

Categorization results are cached in `.wct_cache/` to speed up subsequent operations. Use `--force-refresh` to regenerate cached categorizations.

## Tips

1. **Start with categorization**: Always run `--categorize` first to understand your wildcard structure
2. **Use short analysis for quick insights**: `--analyze short` gives you a quick overview
3. **Combine operations**: You can run multiple modes in one command for efficiency
4. **Save important results**: Use `--save-to` for analyses and cleaned files you want to keep
5. **Experiment with reasoning effort**: Higher effort levels provide better quality but cost more

## Integration

WCT follows the same patterns as other tools in this repository:
- Uses the same prompt loading system as `text_transformer.py`
- Supports similar CLI patterns and verbose modes
- Integrates with the existing `prompts/` directory structure

## Troubleshooting

- **"PyYAML not found"**: Install with `pip install PyYAML`
- **"OpenAI API key required"**: Set the `OPENAI_API_KEY` environment variable
- **Parsing errors**: Some LLM responses may not be valid YAML; the tool will fall back to raw text storage
- **Cache issues**: Use `--force-refresh` to regenerate cached categorizations
