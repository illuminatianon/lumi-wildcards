# Dynamic Prompts Wildcard System Guide

## Overview

Dynamic Prompts is a powerful system for creating modular, reusable prompt components using wildcard files. This system allows for sophisticated prompt composition through references, substitutions, and template patterns.

## Directory Structure & Namespaces

```
wildcards/
├── std/xl/           # Standard XL namespace (primary workspace)
│   ├── style.yaml    # Art styles and techniques
│   ├── camera.yaml   # Camera angles, distances, compositions
│   ├── util.yaml     # Cross-context utility components
│   └── ...
└── other/namespaces/ # Additional namespaces as needed
```

**Key Points:**

- Each subdirectory creates a namespace (e.g., `std/xl`)
- Primary work happens in the `std/xl` namespace
- Files can reference other files within or across namespaces

## Wildcard Reference Syntax

### Basic References

```
__std/xl/filename__           # References entire file or primary category
__std/xl/filename/category__  # References specific category within YAML file
```

### Substitution Fragments

```
{option1|option2|option3}     # Randomly picks one option
{4$$a|b|c|d|e}               # Picks 4 items from the list
{3$$, $$__std/xl/style__}    # Picks 3 items, joins with commas
```

### Advanced Patterns

```
{2-4$$__std/xl/camera/angle__}        # Picks 2-4 items
{$$__std/xl/style__ and __std/xl/camera__} # Combines multiple references
```

## File Formats

### 1. Simple Text Lists

```
option one
option two
option three
```

### 2. YAML Structure (Recommended)

```yaml
filename: # Must match the filename (e.g., style.yaml → style:)
  # Primary category - what gets called by __std/xl/filename__
  all:
    - "__std/xl/filename/subcategory1__ with __std/xl/filename/subcategory2__"
    - "__std/xl/filename/subcategory2__ __std/xl/filename/subcategory1__"

  # Individual categories for modular access
  subcategory1:
    - option1
    - option2
    - option3

  subcategory2:
    - optionA
    - optionB
    - optionC
```

## YAML Formatting Rules

### Required Structure

- **Root key must match filename**: `style.yaml` → `style:`
- **All content under root key**: Proper YAML indentation required
- **Quotes for special characters**: Any line starting with `{`, `__`, or special chars must be quoted

### Example:

```yaml
camera:
  all:
    - "__std/xl/camera/angle__, __std/xl/camera/distance__" # Quoted - starts with __
    - "normal text entry" # Optional quotes

  angle:
    - low-angle shot # No quotes needed
    - high-angle view # No quotes needed
    - "{dramatic|subtle} perspective" # Quoted - starts with {
```

## Template Patterns & Composition

### Modular Templates

Instead of hardcoded combinations, use template patterns:

**Before (Limited):**

```yaml
- "frontal view with symmetrical composition"
- "rear view with balanced framing"
```

**After (Exponential Combinations):**

```yaml
- "__std/xl/camera/viewpoint__ view with __std/xl/camera/composition__ composition"
- "__std/xl/camera/composition__ __std/xl/camera/viewpoint__ framing"
```

### The "All" Category Pattern

Use `all` as a composition orchestrator for complete descriptions:

```yaml
camera:
  all:
    - "__std/xl/camera/angle__, __std/xl/camera/distance__, __std/xl/camera/orientation__"
    - "__std/xl/camera/distance__ with __std/xl/camera/composition__ and __std/xl/camera/style__"
    - "__std/xl/camera/style__ __std/xl/camera/angle__ featuring __std/xl/camera/orientation__"

  # Individual building blocks
  angle: [...]
  distance: [...]
  orientation: [...]
```

## Cross-File References & Utilities

### Referencing Other Files

```yaml
style:
  all:
    - "__std/xl/style/art_medium__ with __std/xl/camera/angle__" # Cross-file reference
    - "__std/xl/util/intensity__ __std/xl/style/rendering__" # Using utilities
```

### Utility Components (util.yaml)

Store commonly used descriptors for cross-context reuse:

```yaml
util:
  intensity:
    - soft
    - dramatic
    - subtle

  positioning:
    - centered
    - balanced
    - asymmetrical
```

## Best Practices

### 1. Eliminate Repetition Bias

- Extract repeated words into subcategories
- Use template patterns instead of hardcoded combinations
- Ensure equal weighting of all options

### 2. Create Structured Variety

- Multiple template patterns for the same components
- Different grammatical structures
- Varied combination lengths (2-3 vs 4-5 components)

### 3. Maintain Modularity

- Individual categories remain accessible
- Components can be reused across files
- Clear separation of concerns

### 4. Professional Terminology

- Use domain-appropriate language
- Maintain consistency across related files
- Validate terminology accuracy

## Example Usage in Prompts

```
A portrait of a character, __std/xl/style/all__, __std/xl/camera/all__
```

This might resolve to:

```
A portrait of a character, oil painting with dramatic rendering and vivid colors,
low-angle shot with close-up framing featuring three-quarter view
```

## Integration with AI Systems

When used as part of a composited system prompt, this wildcard system provides:

- **Consistent terminology** across all generated content
- **Infinite variety** through modular combinations
- **Professional quality** through curated component libraries
- **Maintainable structure** for easy updates and extensions

### Errata

Use `uv run scripts/wc_test.py __some/wildcard/file__` to test your wildcards single wildcard files. It will generate 100 iterations and print to stdout.

Use `uv run scripts/prompt_stress_test.py -n 100 --exclude "with and the from illuminati eldritch"` to test wildcards holistically. It will generate 100 iterations based on my current master prompt and print a frequency analysis. Use --help to figure out cli params if necessary. This tool only takes a few seconds to run (scaling with -n) so you don't have to wait forever for it to be finished. When it is done, it will emit the words "Analysis complete", so watch for that instead of whatever you've been doing (timeout? idk waiting 1 minute is too long)
