#!/usr/bin/env python3

import os
import re
from pathlib import Path

def get_rule_type(file_path):
    """Determine the type of rule based on its path and name."""
    relative_path = file_path.relative_to(Path(__file__).parent.parent)
    parts = relative_path.parts
    
    if len(parts) == 1 and parts[0] == 'main.mdc':
        return 'main'
    elif len(parts) == 2 and parts[1].endswith('.mdc'):
        return 'category'
    else:
        return 'specific'

def get_default_frontmatter(file_path):
    """Generate default frontmatter based on file path and content."""
    relative_path = file_path.relative_to(Path(__file__).parent.parent)
    rule_type = get_rule_type(file_path)
    
    # Base frontmatter fields
    frontmatter = {
        'Description': f'Rules for {relative_path.stem}',
        'Model': 'fusion',
        'Context_window': 'medium'
    }
    
    # Set globs based on rule type and file location
    if rule_type == 'main':
        frontmatter['Globs'] = '**/*'
        # Main rule includes all category rules
        frontmatter['Includes'] = [
            'code_health/code_health.mdc',
            'code_quality/code_quality.mdc',
            'accessibility/accessibility.mdc',
            'pinescript/pinescript.mdc',
            'web3_security/web3_security.mdc',
            'component_analyzer/component_analyzer.mdc',
            'metadata/metadata.mdc',
            'delta/delta.mdc',
            'code_index/code_index.mdc',
            'cheatsheets/cheatsheets.mdc',
            'debug_history/debug_history.mdc',
            'knowledge_graph/knowledge_graph.mdc',
            'style_guide/style_guide.mdc',
            'onboarding/onboarding.mdc',
            'feedback/feedback.mdc',
            'memory_anchors/memory_anchors.mdc',
            'maturity_model/maturity_model.mdc',
            'cross_reference/cross_reference.mdc',
            'documentation/why_documentation.mdc',
            'sandbox/sandbox.mdc',
            'glossary/glossary.mdc',
            'patterns/patterns.mdc',
            'qa/qa.mdc',
            'monetization_analysis/monetization_analysis.mdc'
        ]
    elif rule_type == 'category':
        category = relative_path.parts[0]
        if category == 'code_quality':
            frontmatter['Globs'] = '**/*.{ts,tsx,js,jsx}'
            frontmatter['Includes'] = [
                'typescript_workflow.mdc',
                'typescript_test_cleanup.mdc'
            ]
        elif category == 'pinescript':
            frontmatter['Globs'] = '**/*.pine'
            frontmatter['Includes'] = [
                'auto_snapshot.mdc',
                'snapshot_commands.mdc',
                'snapshot_context_menu.mdc',
                'test_cleanup.mdc'
            ]
        elif category == 'code_health':
            frontmatter['Globs'] = '**/*'
            frontmatter['Includes'] = [
                'test_file_cleanup.mdc'
            ]
        else:
            frontmatter['Globs'] = '**/*'
    else:  # specific rule
        if 'typescript' in str(file_path):
            frontmatter['Globs'] = '**/*.{ts,tsx}'
        elif 'pinescript' in str(file_path):
            frontmatter['Globs'] = '**/*.pine'
        else:
            frontmatter['Globs'] = '**/*'
    
    # Format the frontmatter
    frontmatter_str = '---\n'
    for key, value in frontmatter.items():
        if isinstance(value, list):
            frontmatter_str += f'{key}:\n'
            for item in value:
                frontmatter_str += f'  - {item}\n'
        else:
            frontmatter_str += f'{key}: {value}\n'
    frontmatter_str += '---\n'
    
    return frontmatter_str

def parse_existing_frontmatter(content):
    """Parse existing frontmatter and return it as a dictionary."""
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    if not match:
        return {}
    
    frontmatter = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if value.startswith('[') and value.endswith(']'):
                # Handle list values
                value = [item.strip() for item in value[1:-1].split(',')]
            frontmatter[key] = value
    
    return frontmatter

def fix_frontmatter(file_path):
    """Add or update frontmatter in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get existing frontmatter
        existing_frontmatter = parse_existing_frontmatter(content)
        
        # Get new frontmatter
        new_frontmatter = get_default_frontmatter(file_path)
        
        # If file has no frontmatter, add it
        if not existing_frontmatter:
            new_content = new_frontmatter + content
        else:
            # Keep existing content but update frontmatter
            content_after_frontmatter = content[content.find('---', 3) + 3:]
            new_content = new_frontmatter + content_after_frontmatter
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    rules_dir = Path(__file__).parent.parent
    fixed_count = 0
    
    # List of files that need fixing (from check_frontmatter.py output)
    files_to_fix = [
        'code_health/test_file_cleanup.mdc',
        'code_quality/typescript_test_cleanup.mdc',
        'code_quality/typescript_workflow.mdc',
        'pinescript/auto_snapshot.mdc',
        'pinescript/snapshot_commands.mdc',
        'pinescript/snapshot_context_menu.mdc',
        'pinescript/test_cleanup.mdc'
    ]
    
    for file_path in files_to_fix:
        full_path = rules_dir / file_path
        if fix_frontmatter(full_path):
            print(f"Fixed: {file_path}")
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} out of {len(files_to_fix)} files")

if __name__ == '__main__':
    main() 