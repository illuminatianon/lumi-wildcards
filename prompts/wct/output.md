SYSTEM: WILDCARD OUTPUT

Input: structured cleaned data (from cleanup step).
If output=text:
  - Flatten all entries into plain text lines suitable for a .txt wildcard.
If output=yaml:
  - Generate YAML using this format:
      pose:
        all:
          - __std/xl/pose/category_a__
          - __std/xl/pose/category_b__
        category_a:
          - example line a
          - example line b
        category_b:
          ...
Ensure indentation, spacing, and syntax are valid YAML 1.2.
