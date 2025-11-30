#!/usr/bin/env python3
"""
YAML Linter for Wildcard Files
Lints all YAML files in the wildcards/std/xl directory
"""

import subprocess
import sys
import os
from pathlib import Path

def lint_wildcards():
    """Lint all YAML wildcard files in std/xl directory"""
    
    # Path to wildcard directory
    wildcard_dir = Path("wildcards/std/xl")
    
    if not wildcard_dir.exists():
        print(f"Error: Directory {wildcard_dir} not found!")
        return 1
    
    # Find all YAML files
    yaml_files = list(wildcard_dir.glob("*.yaml"))
    
    if not yaml_files:
        print(f"No YAML files found in {wildcard_dir}")
        return 0
    
    print(f"Linting {len(yaml_files)} wildcard files in {wildcard_dir}/")
    print("-" * 50)
    
    # Run yamllint on each file
    errors_found = False
    
    for yaml_file in sorted(yaml_files):
        try:
            result = subprocess.run(
                ["yamllint", "-c", ".yamllint", "-f", "parsable", str(yaml_file)], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                print(f"PASS {yaml_file.name}")
            else:
                errors_found = True
                print(f"FAIL {yaml_file.name}")
                if result.stdout:
                    # Format the output nicely
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            # Extract just the error part after the filename
                            parts = line.split(':', 3)
                            if len(parts) >= 4:
                                line_num = parts[1]
                                col_num = parts[2] 
                                error = parts[3].strip()
                                print(f"   Line {line_num}, Col {col_num}: {error}")
                            else:
                                print(f"   {line}")
                
        except FileNotFoundError:
            print("ERROR: yamllint not found! Please install it with: pip install yamllint")
            return 1
        except Exception as e:
            print(f"ERROR: Error linting {yaml_file.name}: {e}")
            errors_found = True
    
    print("-" * 50)
    if errors_found:
        print("FAIL: Linting completed with errors")
        return 1
    else:
        print("PASS: All wildcard files passed linting!")
        return 0

if __name__ == "__main__":
    sys.exit(lint_wildcards())
