#!/usr/bin/env python3

"""Cross-Reference Extractor

This script extracts cross-references from the codebase and
generates a cross-reference index.

Maturity: beta

Why:
- Understanding dependencies between components is crucial for maintenance
- Manual tracking of cross-references is error-prone
- This script automates the extraction of cross-references
- Makes it easier to understand the impact of changes
"""

import argparse
import json
import os
import re
from pathlib import Path
import yaml
from collections import defaultdict

class ReferenceExtractor:
    """Extracts cross-references from code files."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.references = []
        
        # Patterns for explicit cross-references
        self.explicit_patterns = {
            'js': r'\/\*\*\s*\n(?:.*\n)*?\s*\*\s*@crossref\s+\{([^}]+)\}\s+([^\s-]+)\s*-\s*([^\n]+)',
            'ts': r'\/\*\*\s*\n(?:.*\n)*?\s*\*\s*@crossref\s+\{([^}]+)\}\s+([^\s-]+)\s*-\s*([^\n]+)',
            'py': r'"""\n(?:.*\n)*?Cross-references:\n\s*-\s*\{([^}]+)\}\s+([^\s-]+)\s*-\s*([^\n]+)',
            'pine': r'\/\/\s*@crossref\s+\{([^}]+)\}\s+([^\s-]+)\s*-\s*([^\n]+)',
            'md': r'<!--\s*CROSSREF:\s*\{([^}]+)\}\s+([^\s-]+)\s*-\s*([^\n]+)\s*-->'
        }
        
        # Patterns for implicit references
        self.implicit_patterns = {
            'js': {
                'import': r'import\s+(?:[\w\s{},*]+\s+from\s+)?[\'"]([^\'"]*)[\'"]\s*;?',
                'require': r'require\s*\(\s*[\'"]([^\'"]*)[\'"]\s*\)',
                'component': r'<([A-Z]\w+)(?:\s|\/|>)',
                'extends': r'class\s+\w+\s+extends\s+(\w+)',
                'implements': r'class\s+\w+(?:\s+extends\s+\w+)?\s+implements\s+([\w,\s]+)'
            },
            'ts': {
                'import': r'import\s+(?:[\w\s{},*]+\s+from\s+)?[\'"]([^\'"]*)[\'"]\s*;?',
                'require': r'require\s*\(\s*[\'"]([^\'"]*)[\'"]\s*\)',
                'component': r'<([A-Z]\w+)(?:\s|\/|>)',
                'extends': r'class\s+\w+\s+extends\s+(\w+)',
                'implements': r'class\s+\w+(?:\s+extends\s+\w+)?\s+implements\s+([\w,\s]+)',
                'type': r'import\s+type\s+\{([^}]*)\}\s+from\s+[\'"]([^\'"]*)[\'"]\s*;?'
            },
            'py': {
                'import': r'(?:from\s+([^\s]+)\s+import|import\s+([^\s]+))',
                'inherit': r'class\s+\w+\s*\(([^)]*)\):',
                'decorator': r'@(\w+)'
            },
            'pine': {
                'import': r'import\s+([^\s]+)',
                'function_call': r'(\w+)\s*\('
            }
        }
    
    def extract_references(self, directory_path, exclude_patterns=None):
        """Extract references from files in a directory."""
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
                
                # Determine file type
                if file.endswith(('.js', '.jsx')):
                    self._extract_from_file(file_path, 'js')
                elif file.endswith(('.ts', '.tsx')):
                    self._extract_from_file(file_path, 'ts')
                elif file.endswith('.py'):
                    self._extract_from_file(file_path, 'py')
                elif file.endswith(('.pine', '.pinescript')):
                    self._extract_from_file(file_path, 'pine')
                elif file.endswith('.md'):
                    self._extract_from_file(file_path, 'md')
    
    def _extract_from_file(self, file_path, file_type):
        """Extract references from a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract explicit cross-references
            if file_type in self.explicit_patterns:
                pattern = self.explicit_patterns[file_type]
                matches = re.finditer(pattern, content)
                
                for match in matches:
                    ref_type = match.group(1).strip()
                    target = match.group(2).strip()
                    description = match.group(3).strip()
                    
                    self.references.append({
                        'source': str(file_path),
                        'target': target,
                        'type': ref_type,
                        'description': description,
                        'explicit': True
                    })
                    
                    if self.verbose:
                        print(f"Explicit reference: {file_path} -> {target} ({ref_type})")
            
            # Extract implicit references
            if file_type in self.implicit_patterns:
                for ref_type, pattern in self.implicit_patterns[file_type].items():
                    matches = re.finditer(pattern, content)
                    
                    for match in matches:
                        if ref_type == 'type' and file_type == 'ts':
                            # Special handling for TypeScript type imports
                            types = match.group(1).split(',')
                            source = match.group(2)
                            
                            for type_name in types:
                                type_name = type_name.strip()
                                if type_name:
                                    self.references.append({
                                        'source': str(file_path),
                                        'target': source,
                                        'referenced_type': type_name,
                                        'type': 'type_import',
                                        'explicit': False
                                    })
                        else:
                            target = match.group(1)
                            
                            # Skip self-references and empty targets
                            if not target or target == file_path.stem:
                                continue
                            
                            self.references.append({
                                'source': str(file_path),
                                'target': target,
                                'type': ref_type,
                                'explicit': False
                            })
                            
                            if self.verbose:
                                print(f"Implicit reference: {file_path} -> {target} ({ref_type})")
        
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    def save_references(self, output_file, format='json'):
        """Save extracted references to a file."""
        # Group references by source
        references_by_source = defaultdict(list)
        for ref in self.references:
            references_by_source[ref['source']].append(ref)
        
        # Group references by target
        references_by_target = defaultdict(list)
        for ref in self.references:
            references_by_target[ref['target']].append(ref)
        
        # Prepare output data
        output_data = {
            'metadata': {
                'timestamp': Path(output_file).stat().st_mtime if Path(output_file).exists() else None,
                'total_references': len(self.references),
                'explicit_references': sum(1 for ref in self.references if ref.get('explicit', False)),
                'implicit_references': sum(1 for ref in self.references if not ref.get('explicit', False))
            },
            'references': self.references,
            'by_source': {source: refs for source, refs in references_by_source.items()},
            'by_target': {target: refs for target, refs in references_by_target.items()}
        }
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(output_data, f, indent=2)
            elif format == 'yaml':
                yaml.dump(output_data, f, sort_keys=False)
        
        print(f"Saved {len(self.references)} references to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Extract cross-references from code")
    parser.add_argument("source_dir", help="Source directory to scan")
    parser.add_argument("--output", default="cross_references.json", help="Output file")
    parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Output format")
    parser.add_argument("--exclude", nargs="+", default=["node_modules", "dist", "build", ".git"],
                        help="Patterns to exclude (default: node_modules dist build .git)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    extractor = ReferenceExtractor(verbose=args.verbose)
    extractor.extract_references(args.source_dir, exclude_patterns=args.exclude)
    extractor.save_references(args.output, format=args.format)

if __name__ == "__main__":
    main() 