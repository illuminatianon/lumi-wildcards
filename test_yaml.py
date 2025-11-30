#!/usr/bin/env python3

import yaml
import sys

def test_yaml_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        print(f"✓ YAML file '{filename}' is valid!")
        
        if isinstance(data, dict):
            print(f"✓ Contains {len(data)} top-level keys:")
            for key in data.keys():
                if isinstance(data[key], dict):
                    print(f"  - {key}: {len(data[key])} subcategories")
                else:
                    print(f"  - {key}: {type(data[key]).__name__}")
        
        # Test a few specific categories
        if 'outfit' in data:
            outfit_data = data['outfit']
            if 'all' in outfit_data:
                print(f"✓ 'all' category has {len(outfit_data['all'])} template patterns")
            if 'garment_type' in outfit_data:
                print(f"✓ 'garment_type' category has {len(outfit_data['garment_type'])} items")
            if 'style_modifier' in outfit_data:
                print(f"✓ 'style_modifier' category has {len(outfit_data['style_modifier'])} items")
        
        return True
        
    except yaml.YAMLError as e:
        print(f"✗ YAML parsing error in '{filename}':")
        print(f"  {e}")
        return False
    except FileNotFoundError:
        print(f"✗ File '{filename}' not found")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "wildcards/std/xl/outfit.yaml"
    test_yaml_file(filename)
