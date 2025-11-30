# AI Agent Guide for Lumi Wildcards

This document provides guidance for AI agents working with the Lumi Wildcards project, including system architecture, testing tools, and development workflows.

## Project Overview

Lumi Wildcards is a modular prompt system for Stable Diffusion XL using Dynamic Prompts. The system enables sophisticated prompt composition through wildcard files, template patterns, and hierarchical references.

**Core Documentation:**
- [Dynamic Prompts System Guide](prompts/dynamic-prompts.md) - Complete reference for wildcard syntax, YAML structure, and composition patterns
- [SDXL Prompting Guide](prompts/prompting-guide-sdxl.md) - Technical reference for SDXL-specific prompt engineering

## Directory Structure

```
lumi-wildcards/
├── wildcards/std/xl/     # Primary wildcard namespace
│   ├── *.yaml           # Wildcard definition files
├── scripts/             # Development and testing tools
├── prompts/             # Documentation and AI prompts
│   ├── dynamic-prompts.md
│   └── wct/            # Wildcard Categorization Tool prompts
└── AGENTS.md           # This file
```

## Development Tools

### Environment Setup

**When using WSL (Windows Subsystem for Linux):**
Before running any Python scripts, activate the WSL virtual environment:
```bash
source .venvwsl/bin/activate
```

**When using native Windows:**
Use the appropriate Windows virtual environment activation method for your setup.

### Core Testing Scripts

#### 1. `scripts/wc_test.py` - Wildcard Generation Tester
**Purpose:** Generate sample outputs from wildcard templates for validation

**Usage:**
```bash
# WSL
source .venvwsl/bin/activate
python scripts/wc_test.py "__std/xl/outfit/all__" --count 100
```

**Key Features:**
- Tests individual wildcard files or categories
- Generates specified number of variations
- Outputs to stdout for inspection
- Validates wildcard resolution and syntax

#### 2. `scripts/prompt_stress_test.py` - Statistical Analysis Tool
**Purpose:** Analyze wildcard generation patterns and identify potential issues

**Usage:**
```bash
# WSL - Basic analysis
source .venvwsl/bin/activate
python scripts/prompt_stress_test.py "__std/xl/outfit/all__" -n 1000

# WSL - Advanced analysis with custom parameters
source .venvwsl/bin/activate
python scripts/prompt_stress_test.py "__std/xl/character/all__" \
  --num-gens 500 \
  --top-words 25 \
  --over-weight-threshold 0.9 \
  --under-weight-threshold 0.02 \
  --output analysis_report.txt
```

**Key Features:**
- Statistical frequency analysis of generated terms
- Identifies over-weighted words (appearing too frequently)
- Identifies under-weighted words (appearing too rarely)
- Per-source breakdown showing contribution from each wildcard file
- Customizable thresholds and output limits
- Debug mode for sample output inspection

**Parameters:**
- `--num-gens`: Number of generations to analyze (default: 100)
- `--wildcards-root`: Path to wildcards directory (default: wildcards)
- `--min-word-length`: Minimum word length for analysis (default: 3)
- `--top-words`: Number of top words to show (default: 50)
- `--over-weight-threshold`: Threshold for over-weighted detection (default: 0.8)
- `--under-weight-threshold`: Threshold for under-weighted detection (default: 0.05)
- `--blacklist`: Words to ignore in analysis (default: with, and, the)

#### 3. `scripts/lint-wildcards.py` - YAML Validation Tool
**Purpose:** Validate YAML syntax and formatting in wildcard files

**Usage:**
```bash
# WSL
source .venvwsl/bin/activate
python scripts/lint-wildcards.py

# or via npm (works in both WSL and Windows)
npm run lint-wildcards
```

**Key Features:**
- Validates all YAML files in `wildcards/std/xl/`
- Uses yamllint with project-specific configuration
- Provides detailed error reporting with line/column information
- Returns appropriate exit codes for CI/CD integration

## Wildcard System Architecture

### Reference Syntax
```yaml
# File references
__std/xl/filename__           # Entire file or primary category
__std/xl/filename/category__  # Specific category

# Inline substitutions
{option1|option2|option3}     # Random selection
{4$$a|b|c|d|e}               # Pick 4 items
{3$$, $$__std/xl/style__}    # Pick 3, comma-separated
```

### YAML Structure Requirements
- Root key must match filename (`style.yaml` → `style:`)
- All content under root key with proper indentation
- Quote lines starting with `{`, `__`, or special characters
- Use `all` category as primary composition orchestrator

## Development Workflow for AI Agents

### 1. Understanding Existing Wildcards
```bash
# WSL - Examine wildcard structure
source .venvwsl/bin/activate
python scripts/wc_test.py "__std/xl/outfit/all__" --count 20

# WSL - Analyze statistical distribution
source .venvwsl/bin/activate
python scripts/prompt_stress_test.py "__std/xl/outfit/all__" --debug
```

### 2. Creating New Wildcards
1. Follow YAML structure requirements from [dynamic-prompts.md](prompts/dynamic-prompts.md)
2. Use template patterns instead of hardcoded combinations
3. Validate syntax: `source .venvwsl/bin/activate && python scripts/lint-wildcards.py`
4. Test generation: `source .venvwsl/bin/activate && python scripts/wc_test.py "__std/xl/newfile/all__"`
5. Analyze distribution: `source .venvwsl/bin/activate && python scripts/prompt_stress_test.py "__std/xl/newfile/all__"`

### 3. Refactoring Existing Wildcards
1. Analyze current patterns: `source .venvwsl/bin/activate && python scripts/prompt_stress_test.py [wildcard] --debug`
2. Identify repetition bias and over-weighted terms
3. Extract repeated elements into subcategories
4. Create template patterns for modular composition
5. Validate changes with testing tools

### 4. Quality Assurance
- **Syntax Validation:** All YAML files must pass `scripts/lint-wildcards.py`
- **Generation Testing:** Use `scripts/wc_test.py` to verify expected outputs
- **Statistical Analysis:** Use `scripts/prompt_stress_test.py` to identify bias
- **Integration Testing:** Test wildcard references across files

## Best Practices for AI Agents

### 1. Maintain Modularity
- Keep individual categories accessible and reusable
- Use clear separation of concerns between files
- Ensure components can be referenced independently

### 2. Eliminate Repetition Bias
- Extract repeated words into subcategories
- Use template patterns instead of hardcoded combinations
- Ensure equal weighting of all options

### 3. Professional Terminology
- Use domain-appropriate language for art, photography, and SDXL
- Maintain consistency across related files
- Validate terminology accuracy against established references

### 4. Testing Integration
- Always test changes with provided tools before finalizing
- Use statistical analysis to validate balanced distribution
- Verify cross-file references resolve correctly

## Error Handling and Debugging

### Common Issues:
1. **YAML Syntax Errors:** Use `scripts/lint-wildcards.py` for validation
2. **Broken References:** Test with `scripts/wc_test.py` to identify missing files/categories
3. **Repetition Bias:** Use `scripts/prompt_stress_test.py` to identify over-weighted terms
4. **Unbalanced Distribution:** Analyze per-source breakdown in stress test results

### Debugging Workflow:
1. Run lint check: `source .venvwsl/bin/activate && python scripts/lint-wildcards.py`
2. Test generation: `source .venvwsl/bin/activate && python scripts/wc_test.py [wildcard] --count 10`
3. Analyze patterns: `source .venvwsl/bin/activate && python scripts/prompt_stress_test.py [wildcard] --debug`
4. Review statistical output for bias indicators

This guide provides the foundation for AI agents to effectively work with the Lumi Wildcards system while maintaining quality and consistency standards.
