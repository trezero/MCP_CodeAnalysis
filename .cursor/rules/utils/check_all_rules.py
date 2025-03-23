#!/usr/bin/env python3

import os
import re
from pathlib import Path

def parse_frontmatter(content):
    """Parse frontmatter from file content."""
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    if not match:
        return None
    
    frontmatter = {}
    for line in match.group(1).split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()
    
    return frontmatter

def check_rule_file(file_path):
    """Check a rule file for proper frontmatter."""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter = parse_frontmatter(content)
        if not frontmatter:
            issues.append("Missing frontmatter")
            return issues
        
        # Check required fields
        for field in ['Description', 'Globs', 'Model', 'Context_window']:
            if field not in frontmatter:
                issues.append(f"Missing required field: {field}")
        
        # Check Globs format
        if 'Globs' in frontmatter:
            globs = frontmatter['Globs']
            if '{' in globs and '}' in globs:
                issues.append("Globs uses brace expansion syntax which may not work. Use comma-separated patterns instead.")
            
            if globs.strip() == "" or globs.strip() == "**/*" and not is_main_rule(file_path):
                if not is_specific_subrule(file_path):
                    issues.append("Globs is empty or too generic for non-main rule file")
        
        # Check if category rule includes its sub-rules
        if is_category_rule(file_path) and 'Includes' not in frontmatter:
            issues.append("Category rule should include sub-rules")
        
    except Exception as e:
        issues.append(f"Error reading file: {e}")
    
    return issues

def is_main_rule(file_path):
    """Check if this is the main rule file."""
    return file_path.name == "main.mdc"

def is_category_rule(file_path):
    """Check if this is a category-level rule file."""
    return len(file_path.parts) >= 2 and file_path.parts[-2] == "rules" and file_path.name.endswith(".mdc")

def is_specific_subrule(file_path):
    """Check if this is a specific sub-rule file."""
    return len(file_path.parts) > 2 and file_path.parts[-3] == "rules"

def main():
    rules_dir = Path(__file__).parent.parent
    issues_found = False
    
    for mdc_file in sorted(rules_dir.rglob('*.mdc')):
        relative_path = mdc_file.relative_to(rules_dir)
        issues = check_rule_file(mdc_file)
        
        if issues:
            issues_found = True
            print(f"\n{relative_path}:")
            for issue in issues:
                print(f"  - {issue}")
    
    if not issues_found:
        print("All rule files have proper frontmatter and configuration!")

if __name__ == '__main__':
    main() 