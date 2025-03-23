#!/usr/bin/env python3

"""Style Guide Documentation Generator

This script generates documentation from code comments and style guide rules,
creating a living style guide for the project.

Maturity: beta

Why:
- Keeping documentation in sync with code is challenging
- This automates the process of extracting style examples from code
- Provides a central reference for developers
- Makes style guide more accessible and useful
"""

import argparse
import json
import os
import re
from pathlib import Path
import markdown
import yaml

class DocumentationGenerator:
    """Generates documentation from code comments and style guide rules."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.examples = {
            'js': [],
            'ts': [],
            'py': [],
            'pine': []
        }
        self.rules = {}
    
    def extract_examples(self, directory_path, exclude_patterns=None):
        """Extract style examples from code files."""
        if exclude_patterns is None:
            exclude_patterns = ['node_modules', 'dist', 'build', '.git']
        
        directory_path = Path(directory_path)
        
        if not directory_path.is_dir():
            print(f"Error: {directory_path} is not a directory")
            return
        
        # Walk through the directory
        for root, dirs, files in os.walk(directory_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in str(Path(root) / d) for pattern in exclude_patterns)]
            
            for file in files:
                file_path = Path(root) / file
                
                # Process different file types
                if file_path.suffix in ['.js', '.jsx']:
                    self._extract_js_examples(file_path)
                elif file_path.suffix in ['.ts', '.tsx']:
                    self._extract_ts_examples(file_path)
                elif file_path.suffix == '.py':
                    self._extract_py_examples(file_path)
                elif file_path.suffix in ['.pine', '.pinescript']:
                    self._extract_pine_examples(file_path)
    
    def _extract_js_examples(self, file_path):
        """Extract style examples from JavaScript files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Look for style examples in comments
                pattern = r'\/\*\*\s*\n\s*\*\s*@styleguide\s*\n([\s\S]*?)\*\/\s*\n([\s\S]*?)(?=\/\*\*|$)'
                matches = re.finditer(pattern, content)
                
                for match in matches:
                    comment = match.group(1)
                    code = match.group(2).strip()
                    
                    # Extract metadata from comment
                    title_match = re.search(r'\*\s*@title\s*(.*?)(?=\n\s*\*|\n\s*\*\/)', comment)
                    category_match = re.search(r'\*\s*@category\s*(.*?)(?=\n\s*\*|\n\s*\*\/)', comment)
                    description_match = re.search(r'\*\s*@description\s*([\s\S]*?)(?=\n\s*\*\s*@|\n\s*\*\/)', comment)
                    
                    title = title_match.group(1).strip() if title_match else "Unnamed Example"
                    category = category_match.group(1).strip() if category_match else "Uncategorized"
                    description = description_match.group(1).strip() if description_match else ""
                    
                    # Clean up description (remove leading asterisks)
                    description = re.sub(r'\n\s*\*\s*', '\n', description)
                    
                    self.examples['js'].append({
                        'title': title,
                        'category': category,
                        'description': description,
                        'code': code,
                        'file': str(file_path)
                    })
                    
                    if self.verbose:
                        print(f"Extracted JS example: {title} from {file_path}")
        except Exception as e:
            print(f"Error extracting examples from {file_path}: {e}")
    
    def _extract_ts_examples(self, file_path):
        """Extract style examples from TypeScript files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Look for style examples in comments (similar to JS)
                pattern = r'\/\*\*\s*\n\s*\*\s*@styleguide\s*\n([\s\S]*?)\*\/\s*\n([\s\S]*?)(?=\/\*\*|$)'
                matches = re.finditer(pattern, content)
                
                for match in matches:
                    comment = match.group(1)
                    code = match.group(2).strip()
                    
                    # Extract metadata from comment
                    title_match = re.search(r'\*\s*@title\s*(.*?)(?=\n\s*\*|\n\s*\*\/)', comment)
                    category_match = re.search(r'\*\s*@category\s*(.*?)(?=\n\s*\*|\n\s*\*\/)', comment)
                    description_match = re.search(r'\*\s*@description\s*([\s\S]*?)(?=\n\s*\*\s*@|\n\s*\*\/)', comment)
                    
                    title = title_match.group(1).strip() if title_match else "Unnamed Example"
                    category = category_match.group(1).strip() if category_match else "Uncategorized"
                    description = description_match.group(1).strip() if description_match else ""
                    
                    # Clean up description (remove leading asterisks)
                    description = re.sub(r'\n\s*\*\s*', '\n', description)
                    
                    self.examples['ts'].append({
                        'title': title,
                        'category': category,
                        'description': description,
                        'code': code,
                        'file': str(file_path)
                    })
                    
                    if self.verbose:
                        print(f"Extracted TS example: {title} from {file_path}")
        except Exception as e:
            print(f"Error extracting examples from {file_path}: {e}")
    
    def _extract_py_examples(self, file_path):
        """Extract style examples from Python files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Look for style examples in comments
                pattern = r'\/\*\*\s*\n\s*\*\s*@styleguide\s*\n([\s\S]*?)\*\/\s*\n([\s\S]*?)(?=\/\*\*|$)'
                matches = re.finditer(pattern, content)
                
                for match in matches:
                    comment = match.group(1)
                    code = match.group(2).strip()
                    
                    # Extract metadata from comment
                    title_match = re.search(r'\*\s*@title\s*(.*?)(?=\n\s*\*|\n\s*\*\/)', comment)
                    category_match = re.search(r'\*\s*@category\s*(.*?)(?=\n\s*\*|\n\s*\*\/)', comment)
                    description_match = re.search(r'\*\s*@description\s*([\s\S]*?)(?=\n\s*\*\s*@|\n\s*\*\/)', comment)
                    
                    title = title_match.group(1).strip() if title_match else "Unnamed Example"
                    category = category_match.group(1).strip() if category_match else "Uncategorized"
                    description = description_match.group(1).strip() if description_match else ""
                    
                    # Clean up description (remove leading asterisks)
                    description = re.sub(r'\n\s*\*\s*', '\n', description)
                    
                    self.examples['py'].append({
                        'title': title,
                        'category': category,
                        'description': description,
                        'code': code,
                        'file': str(file_path)
                    })
                    
                    if self.verbose:
                        print(f"Extracted Python example: {title} from {file_path}")
        except Exception as e:
            print(f"Error extracting examples from {file_path}: {e}")
    
    def _extract_pine_examples(self, file_path):
        """Extract style examples from Pine Script files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Look for style examples in comments
                pattern = r'\/\*\*\s*\n\s*\*\s*@styleguide\s*\n([\s\S]*?)\*\/\s*\n([\s\S]*?)(?=\/\*\*|$)'
                matches = re.finditer(pattern, content)
                
                for match in matches:
                    comment = match.group(1)
                    code = match.group(2).strip()
                    
                    # Extract metadata from comment
                    title_match = re.search(r'\*\s*@title\s*(.*?)(?=\n\s*\*|\n\s*\*\/)', comment)
                    category_match = re.search(r'\*\s*@category\s*(.*?)(?=\n\s*\*|\n\s*\*\/)', comment)
                    description_match = re.search(r'\*\s*@description\s*([\s\S]*?)(?=\n\s*\*\s*@|\n\s*\*\/)', comment)
                    
                    title = title_match.group(1).strip() if title_match else "Unnamed Example"
                    category = category_match.group(1).strip() if category_match else "Uncategorized"
                    description = description_match.group(1).strip() if description_match else ""
                    
                    # Clean up description (remove leading asterisks)
                    description = re.sub(r'\n\s*\*\s*', '\n', description)
                    
                    self.examples['pine'].append({
                        'title': title,
                        'category': category,
                        'description': description,
                        'code': code,
                        'file': str(file_path)
                    })
                    
                    if self.verbose:
                        print(f"Extracted Pine example: {title} from {file_path}")
        except Exception as e:
            print(f"Error extracting examples from {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate style guide documentation")
    parser.add_argument("path", help="File or directory to extract examples from")
    parser.add_argument("--exclude", nargs="+", default=["node_modules", "dist", "build", ".git"],
                        help="Patterns to exclude (default: node_modules dist build .git)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    generator = DocumentationGenerator(verbose=args.verbose)
    
    path = Path(args.path)
    if path.is_file():
        generator.extract_examples(path, exclude_patterns=args.exclude)
    elif path.is_dir():
        generator.extract_examples(path, exclude_patterns=args.exclude)
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)
    
    # Save examples to file
    examples_dir = Path("examples")
    examples_dir.mkdir(parents=True, exist_ok=True)
    
    for category, examples in generator.examples.items():
        category_dir = examples_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        for example in examples:
            filename = f"{example['title'].replace(' ', '_').replace('/', '_').replace('@', '_')}.md"
            filepath = category_dir / filename
            with open(filepath, 'w') as f:
                f.write(f"# {example['title']}")
                f.write("\n\n")
                f.write(f"**Category:** {example['category']}")
                f.write("\n\n")
                f.write(f"**Description:** {example['description']}")
                f.write("\n\n")
                f.write("```")
                f.write("\n")
                f.write(example['code'])
                f.write("\n")
                f.write("```")
                f.write("\n\n")
                f.write(f"**File:** [{example['file']}]({example['file']})")
            
            print(f"Saved example: {filepath}")

if __name__ == "__main__":
    main() 