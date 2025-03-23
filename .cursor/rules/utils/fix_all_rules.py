#!/usr/bin/env python3

import os
import re
from pathlib import Path

def parse_frontmatter(content):
    """Parse frontmatter from file content."""
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    if not match:
        return None, 0
    
    frontmatter = {}
    for line in match.group(1).split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()
    
    return frontmatter, len(match.group(0))

def get_appropriate_globs(file_path):
    """Return appropriate glob patterns based on file type."""
    path_str = str(file_path).lower()
    
    if "main.mdc" in path_str:
        return "**/*"
    elif "accessibility" in path_str:
        return "**/*.html, **/*.css, **/*.js, **/*.jsx, **/*.ts, **/*.tsx, **/*.vue, **/*.svelte"
    elif "typescript" in path_str or "component_analyzer" in path_str:
        return "**/*.ts, **/*.tsx, **/*.js, **/*.jsx"
    elif "pinescript" in path_str:
        return "**/*.pine"
    elif "style_guide" in path_str:
        return "**/*.css, **/*.scss, **/*.less, **/*.js, **/*.jsx, **/*.ts, **/*.tsx, **/*.html"
    elif "web3_security" in path_str:
        return "**/*.sol, **/*.js, **/*.ts"
    elif "documentation" in path_str or "cheatsheets" in path_str:
        return "**/*.md, **/*.markdown, **/*.txt"
    else:
        return "**/*"

def fix_brace_expansion(globs):
    """Fix brace expansion syntax in glob patterns."""
    if '{' in globs and '}' in globs:
        # Extract patterns from brace expansion
        patterns = []
        brace_matches = re.findall(r'\*\*\/\*\.{([^}]+)}', globs)
        
        for match in brace_matches:
            extensions = match.split(',')
            for ext in extensions:
                patterns.append(f"**/*.{ext.strip()}")
        
        return ", ".join(patterns)
    return globs

def get_includes_for_category(category_path):
    """Get appropriate includes for a category-level rule file."""
    includes = []
    
    if category_path.is_dir():
        for child in category_path.iterdir():
            if child.is_dir():
                for subfile in child.glob("*.mdc"):
                    if subfile.name != category_path.name:
                        includes.append(f"{child.name}/{subfile.name}")
            elif child.name.endswith(".mdc") and child.name != category_path.name:
                includes.append(child.name)
    
    return includes

def fix_rule_file(file_path):
    """Fix a rule file's frontmatter."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse existing frontmatter if any
        existing_frontmatter, frontmatter_end = parse_frontmatter(content)
        
        # Create new frontmatter
        new_frontmatter = {
            'Description': existing_frontmatter.get('Description', f"Rules for {file_path.stem}"),
            'Model': 'fusion',
            'Context_window': 'large'
        }
        
        # Set appropriate globs
        if existing_frontmatter and 'Globs' in existing_frontmatter:
            new_frontmatter['Globs'] = fix_brace_expansion(existing_frontmatter['Globs'])
        else:
            new_frontmatter['Globs'] = get_appropriate_globs(file_path)
        
        # Add includes if this is a category-level rule
        if is_category_rule(file_path) and not is_specific_subrule(file_path):
            includes = get_includes_for_category(file_path.parent)
            if includes:
                new_frontmatter['Includes'] = includes
        
        # Keep other fields from existing frontmatter
        if existing_frontmatter:
            for key, value in existing_frontmatter.items():
                if key not in ['Description', 'Globs', 'Model', 'Context_window', 'Includes']:
                    new_frontmatter[key] = value
        
        # Format new frontmatter
        formatted_frontmatter = "---\n"
        
        # First add the core fields in a specific order
        for field in ['Description', 'Globs', 'Model', 'Context_window']:
            if field in new_frontmatter:
                formatted_frontmatter += f"{field}: {new_frontmatter[field]}\n"
                
        # Then add Includes if present
        if 'Includes' in new_frontmatter:
            formatted_frontmatter += "Includes:\n"
            for include in new_frontmatter['Includes']:
                formatted_frontmatter += f"  - {include}\n"
        
        # Then add any remaining fields
        for key, value in new_frontmatter.items():
            if key not in ['Description', 'Globs', 'Model', 'Context_window', 'Includes']:
                formatted_frontmatter += f"{key}: {value}\n"
        
        formatted_frontmatter += "---\n"
        
        # Replace existing frontmatter or add new frontmatter
        if existing_frontmatter:
            new_content = formatted_frontmatter + content[frontmatter_end:]
        else:
            new_content = formatted_frontmatter + content
        
        # Write updated content back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def is_main_rule(file_path):
    """Check if this is the main rule file."""
    return file_path.name == "main.mdc"

def is_category_rule(file_path):
    """Check if this is a category-level rule file."""
    parts = file_path.parts
    return len(parts) >= 2 and parts[-2].endswith("rules") and not is_specific_subrule(file_path)

def is_specific_subrule(file_path):
    """Check if this is a specific sub-rule file."""
    parts = file_path.parts
    return len(parts) >= 3 and parts[-3].endswith("rules")

def main():
    rules_dir = Path(__file__).parent.parent
    fixed_count = 0
    
    for mdc_file in sorted(rules_dir.rglob('*.mdc')):
        relative_path = mdc_file.relative_to(rules_dir)
        print(f"Checking {relative_path}...", end="")
        
        if fix_rule_file(mdc_file):
            print(" Fixed!")
            fixed_count += 1
        else:
            print(" No changes needed or error occurred.")
    
    print(f"\nFixed {fixed_count} rule files.")

if __name__ == '__main__':
    main() 