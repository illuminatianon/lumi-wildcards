# Wildcard Refactoring Guide: From Inline Choices to Modular Templates

## Overview

This guide documents the methodology for refactoring wildcard YAML files by extracting inline choice fragments into separate wildcard sets and creating modular, template-based systems that eliminate repetition bias and maximize variety.

## Core Problems with Inline Choices

### 1. Repetition Bias
When you have entries like:
```yaml
- "frontal view with symmetrical composition"
- "frontal close-up shot"
- "centered frontal view"
- "frontal medium shot"
```

The word "frontal" appears in multiple hardcoded entries, creating bias where "frontal" gets picked more often than other viewpoints simply because it appears more frequently.

### 2. Limited Combinations
Inline choices like `{frontal|rear|profile} view` only give you 3 options, but when you extract to modular templates, you can combine any viewpoint with any composition style, distance, etc., creating exponentially more variety.

### 3. Maintenance Overhead
Adding a new viewpoint requires updating multiple entries manually instead of just adding it to one subcategory.

## Refactoring Methodology

### Step 1: Identify Inline Choice Patterns
Look for repeated words/phrases that could be variables:
- "frontal", "rear", "profile" → viewpoint subcategory
- "wide", "medium", "close-up" → shot_distance subcategory
- "symmetrical", "centered", "balanced" → composition_style subcategory

### Step 2: Extract to Subcategories
Create reusable subcategories at the bottom of the YAML file:
```yaml
viewpoint:
  - frontal
  - rear
  - profile
  - three-quarter
  - over-the-shoulder

shot_distance:
  - wide
  - medium
  - close-up
  - extreme close-up
```

### Step 3: Create Template Patterns
Replace hardcoded entries with template patterns using wildcard references:
```yaml
orientation:
  - "__std/xl/camera/viewpoint__ view"
  - "__std/xl/camera/viewpoint__ camera shot"
  - "__std/xl/camera/viewpoint__ view with __std/xl/camera/composition_style__ composition"
  - "__std/xl/camera/composition_style__ __std/xl/camera/viewpoint__ view"
```

### Step 4: Design Multiple Template Variations
Create different grammatical structures to avoid repetitive phrasing:
- Simple: `"__std/xl/camera/viewpoint__ view"`
- Descriptive: `"__std/xl/camera/viewpoint__ view with __std/xl/camera/composition_style__ composition"`
- Reversed: `"__std/xl/camera/composition_style__ __std/xl/camera/viewpoint__ view"`

## Handling the "All" Category Problem

### The Problem
Primary categories become compositional templates rather than standalone descriptions. When someone calls `__std/xl/camera/angle__`, they might get `"__std/xl/camera/camera_angle_type__ shot"` which requires further resolution.

### Two Solutions

#### Option 1: Standalone Primary Categories
Rework each primary category to return complete, self-contained descriptions that don't require composition.

#### Option 2: Compositional "All" Category (Recommended)
Use the `all` category as a composition orchestrator:

```yaml
all:
  - "__std/xl/camera/angle__, __std/xl/camera/distance__, __std/xl/camera/orientation__"
  - "__std/xl/camera/distance__ with __std/xl/camera/composition__ and __std/xl/camera/style__"
  - "__std/xl/camera/style__ __std/xl/camera/angle__ featuring __std/xl/camera/orientation__"
  - "__std/xl/camera/orientation__ in __std/xl/camera/distance__ with __std/xl/camera/composition__"
```

This approach:
- Provides complete descriptions when using `__std/xl/namespace/all__`
- Maintains modular building blocks for individual category access
- Creates varied grammatical structures
- Allows flexible combinations (not every pattern needs all categories)

## Best Practices

### 1. Logical Grouping
Group related concepts together:
- Camera angles: low-angle, high-angle, eye-level
- Shot distances: wide, medium, close-up
- Viewpoints: frontal, rear, profile

### 2. Cross-Context Utility
If subcategories might be useful elsewhere, consider adding them to `util.yaml`:
```yaml
util:
  positioning:
    - centered
    - balanced
    - symmetrical
    - frontal
    - side
```

### 3. Template Variety
Create multiple ways to combine the same components:
- Different word orders
- Different connecting words (with, featuring, using, in)
- Different levels of detail (2-3 categories vs 4-5)

### 4. Maintain Professional Terminology
Ensure all extracted terms are proper terminology for the domain (camera work, art styles, etc.).

## Benefits of This Approach

1. **Eliminates Repetition Bias**: Each term appears once in its subcategory
2. **Exponential Variety**: Any viewpoint can combine with any composition style
3. **Maintainable**: Add new options to one place
4. **Reusable**: Subcategories can be referenced by other wildcard files
5. **Structured Variety**: Multiple template patterns prevent repetitive phrasing
6. **Complete Descriptions**: The `all` category provides full, usable descriptions

## Example Transformation

### Before (Repetition Bias):
```yaml
camera:
  orientation:
    - "frontal view"
    - "frontal view with symmetrical composition"
    - "frontal close-up shot"
    - "rear view"
    - "profile view"
```

### After (Modular Templates):
```yaml
camera:
  all:
    - "__std/xl/camera/orientation__, __std/xl/camera/distance__"
    - "__std/xl/camera/distance__ with __std/xl/camera/composition__"
  
  orientation:
    - "__std/xl/camera/viewpoint__ view"
    - "__std/xl/camera/viewpoint__ view with __std/xl/camera/composition_style__ composition"
    - "__std/xl/camera/viewpoint__ __std/xl/camera/shot_distance__ shot"
  
  viewpoint:
    - frontal
    - rear
    - profile
  
  composition_style:
    - symmetrical
    - centered
    - balanced
```

This transformation eliminates "frontal" bias while creating many more possible combinations.
