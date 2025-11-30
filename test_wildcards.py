#!/usr/bin/env python3

import yaml
import random

def load_wildcard_data(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def test_wildcard_categories(data):
    """Test that all referenced categories exist"""
    outfit_data = data['outfit']

    # Check that all categories referenced in 'all' exist
    all_patterns = outfit_data.get('all', [])
    referenced_categories = set()

    for pattern in all_patterns:
        # Extract category references like __std/xl/outfit/category__
        import re
        matches = re.findall(r'__std/xl/outfit/([^_/]+)__', pattern)
        referenced_categories.update(matches)
        print(f"Pattern: {pattern}")
        print(f"  Found categories: {matches}")

    print(f"Categories referenced in 'all' patterns: {len(referenced_categories)}")
    print("Referenced categories:", sorted(referenced_categories))

    missing_categories = []
    existing_categories = []
    for category in sorted(referenced_categories):
        if category not in outfit_data:
            missing_categories.append(category)
        else:
            existing_categories.append(category)
            print(f"✓ {category}: {len(outfit_data[category])} items")

    if missing_categories:
        print(f"✗ Missing categories: {missing_categories}")
        return False
    else:
        print("✓ All referenced categories exist!")

        # Also check for categories that exist but aren't referenced
        all_categories = set(outfit_data.keys())
        unreferenced = all_categories - referenced_categories - {'all'}
        if unreferenced:
            print(f"ℹ Unreferenced categories (available for use): {sorted(unreferenced)}")

        return True

def simulate_wildcard_generation(data, num_samples=10):
    """Simulate wildcard generation by randomly selecting from categories"""
    outfit_data = data['outfit']
    
    print(f"\nGenerating {num_samples} sample outfit descriptions:")
    print("-" * 50)
    
    for i in range(num_samples):
        # Pick a random pattern from 'all'
        pattern = random.choice(outfit_data['all'])
        
        # Simple simulation - replace category references with random items
        result = pattern
        import re
        
        # Find all category references
        matches = re.findall(r'__std/xl/outfit/([^_]+)__', pattern)
        for category in matches:
            if category in outfit_data and outfit_data[category]:
                replacement = random.choice(outfit_data[category])
                result = result.replace(f'__std/xl/outfit/{category}__', replacement, 1)
        
        print(f"{i+1:2d}. {result}")

if __name__ == "__main__":
    try:
        data = load_wildcard_data("wildcards/std/xl/outfit.yaml")
        
        print("Testing wildcard category references...")
        if test_wildcard_categories(data):
            simulate_wildcard_generation(data)
        
    except Exception as e:
        print(f"Error: {e}")
