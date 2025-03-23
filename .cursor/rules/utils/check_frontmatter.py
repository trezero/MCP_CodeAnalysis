#!/usr/bin/env python3

import os
import re
from pathlib import Path

def has_frontmatter(content):
    """Check if the content has proper frontmatter."""
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    if not match:
        return False
    
    # Check for required fields
    required_fields = ['Description', 'Globs', 'Model', 'Context_window']
    frontmatter = match.group(1)
    return all(field in frontmatter for field in required_fields)

def check_rule_files():
    """Check all .mdc files in the rules directory for proper frontmatter."""
    rules_dir = Path(__file__).parent.parent
    missing_frontmatter = []
    
    for mdc_file in rules_dir.rglob('*.mdc'):
        try:
            with open(mdc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not has_frontmatter(content):
                relative_path = mdc_file.relative_to(rules_dir)
                missing_frontmatter.append(str(relative_path))
        except Exception as e:
            print(f"Error reading {mdc_file}: {e}")
    
    return missing_frontmatter

def main():
    missing = check_rule_files()
    if missing:
        print("\nFiles missing proper frontmatter:")
        for file in sorted(missing):
            print(f"- {file}")
        print(f"\nTotal files needing fixes: {len(missing)}")
    else:
        print("All rule files have proper frontmatter!")

if __name__ == '__main__':
    main() 