#!/usr/bin/env python3

"""
Documentation generator for Cursor rules and scripts.
This creates comprehensive documentation of the entire rules system.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from config import config

def generate_markdown_documentation(output_path):
    """Generate markdown documentation for all rules and scripts."""
    integration_map = config.get_integration_map()
    script_paths = config.get_script_paths()
    
    with open(output_path, 'w') as f:
        f.write("# Cursor Rules and Scripts Documentation\n\n")
        
        f.write("## Overview\n\n")
        f.write(f"This documentation covers {len(integration_map)} rules and {len(script_paths)} scripts.\n\n")
        
        # Document rules by category
        f.write("## Rules by Category\n\n")
        
        categories = {}
        for rule_path, integration_info in integration_map.items():
            category = os.path.dirname(rule_path)
            if category not in categories:
                categories[category] = []
            
            categories[category].append({
                'path': rule_path,
                'metadata': integration_info['metadata'],
                'related_scripts': integration_info['related_scripts']
            })
        
        for category, rules in categories.items():
            category_name = os.path.basename(category) if category else "Root"
            f.write(f"### {category_name.capitalize()}\n\n")
            
            for rule in rules:
                rule_name = os.path.basename(rule['path']).replace('.mdc', '')
                f.write(f"#### {rule_name}\n\n")
                
                metadata = rule['metadata']
                if 'Description' in metadata:
                    f.write(f"{metadata['Description']}\n\n")
                
                f.write("**Configuration:**\n\n")
                for key, value in metadata.items():
                    if key != 'Description':
                        f.write(f"- **{key}**: {value}\n")
                
                f.write("\n**Related Scripts:**\n\n")
                if rule['related_scripts']:
                    for script_path in rule['related_scripts']:
                        script_name = os.path.basename(script_path)
                        f.write(f"- {script_name}\n")
                else:
                    f.write("No related scripts found.\n")
                
                f.write("\n")
        
        # Document scripts by category
        f.write("## Scripts by Category\n\n")
        
        script_categories = {}
        for script_path in script_paths:
            category = os.path.dirname(os.path.relpath(script_path, config.rules_dir))
            if category not in script_categories:
                script_categories[category] = []
            
            script_categories[category].append(script_path)
        
        for category, scripts in script_categories.items():
            category_name = os.path.basename(category) if category else "Root"
            f.write(f"### {category_name.capitalize()}\n\n")
            
            for script_path in scripts:
                script_name = os.path.basename(script_path)
                f.write(f"#### {script_name}\n\n")
                
                # Extract docstring if available
                docstring = ""
                try:
                    with open(script_path, 'r') as script_file:
                        content = script_file.read()
                        if '"""' in content:
                            start = content.find('"""') + 3
                            end = content.find('"""', start)
                            if end != -1:
                                docstring = content[start:end].strip()
                except:
                    pass
                
                if docstring:
                    f.write(f"{docstring}\n\n")
                
                f.write(f"**Path**: `{os.path.relpath(script_path, config.rules_dir)}`\n\n")
                
                f.write("\n")
    
    print(f"Documentation generated at {output_path}")

def main():
    output_path = os.path.join(config.rules_dir, "DOCUMENTATION.md")
    generate_markdown_documentation(output_path)

if __name__ == "__main__":
    main() 