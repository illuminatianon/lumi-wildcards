# Outfit Overhaul

## Introduction

We will be doing a complete overhaul of the std/xl/outfit.yaml wildcard file.

Although it already contains a great deal of variety, it is not without its issues:

1. Insufficient body coverage.
   - We have items like "sarong" or "miniskirt" which are not necessarily paired with a top, leading to unwanted nudity.
2. uneven use of accessories
3. the current "all" is formulaic

## The Plan

We will adopt a kind of "RPG" slot system:

1. Head
2. Torso
3. Legs
4. Feet
5. Hands
6. Neck
7. Ears
8. Wrists
9. Waist
10. Fingers
11. Back
12. Shoulders

Each slot will have a list of items that can be worn in it.

We will break down the existing garment_types into their categories. overlap is permissible.

We don't need to fill every slot on every prompt. The only exception to this rule is we must have a TOP and a BOTTOM.
