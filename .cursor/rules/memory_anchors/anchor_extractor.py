#!/usr/bin/env python3

"""Memory Anchor Extractor

This script extracts memory anchors from the codebase and
generates an index of anchors.

Maturity: beta

Why:
- Memory anchors provide semantic markers in the codebase
- They need to be indexed to be useful for navigation
- This script automates the extraction and indexing of memory anchors
- Makes it easier to navigate and understand the codebase structure
"""

import argparse
import json
import os
import re
from pathlib import Path
import yaml
from collections import defaultdict

class AnchorExtractor:
    """Extracts memory anchors from code files."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.anchors = []
        
        # Patterns for memory anchors in different file types
        self.patterns = {
            'js': r'\/\*\*\s*\n(?:.*\n)*?\s*\*\s*@memoryAnchor\s+\{([^}]+)\}\s+([^\n]+)',
            'ts': r'\/\*\*\s*\n(?:.*\n)*?\s*\*\s*@memoryAnchor\s+\{([^}]+)\}\s+([^\n]+)',
            'py': r'"""\n(?:.*\n)*?Memory Anchor:\s*\{([^}]+)\}\s+([^\n]+)',
            'pine': r'\/\/\s*@memoryAnchor\s+\{([^}]+)\}\s+([^\n]+)',
            'md': r'<!--\s*MEMORY_ANCHOR:\s*\{([^}]+)\}\s+([^\n]+)\s*-->'
        }
    
    def extract_anchors(self, directory_path, exclude_patterns=None):
        """Extract memory anchors from files in a directory."""
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
        """Extract memory anchors from a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                pattern = self.patterns.get(file_type)
                if not pattern:
                    return
                
                matches = re.finditer(pattern, content)
                
                for match in matches:
                    anchor_type = match.group(1).strip()
                    description = match.group(2).strip()
                    
                    # Get line number
                    line_number = content[:match.start()].count('\n') + 1
                    
                    # Get context (the line containing the anchor)
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_end = content.find('\n', match.end())
                    if line_end == -1:
                        line_end = len(content)
                    
                    context = content[line_start:line_end].strip()
                    
                    self.anchors.append({
                        'file': str(file_path),
                        'type': anchor_type,
                        'description': description,
                        'line': line_number,
                        'context': context
                    })
                    
                    if self.verbose:
                        print(f"Extracted anchor: {anchor_type} - {description} from {file_path}:{line_number}")
        
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    def save_anchors(self, output_file, format='json'):
        """Save extracted anchors to a file."""
        # Group anchors by type
        anchors_by_type = defaultdict(list)
        for anchor in self.anchors:
            anchors_by_type[anchor['type']].append(anchor)
        
        # Group anchors by file
        anchors_by_file = defaultdict(list)
        for anchor in self.anchors:
            anchors_by_file[anchor['file']].append(anchor)
        
        # Prepare output data
        output_data = {
            'metadata': {
                'timestamp': Path(output_file).stat().st_mtime if Path(output_file).exists() else None,
                'total_anchors': len(self.anchors),
                'anchor_types': list(anchors_by_type.keys())
            },
            'anchors': self.anchors,
            'by_type': {anchor_type: anchors for anchor_type, anchors in anchors_by_type.items()},
            'by_file': {file: anchors for file, anchors in anchors_by_file.items()}
        }
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(output_data, f, indent=2)
            elif format == 'yaml':
                yaml.dump(output_data, f, sort_keys=False)
        
        print(f"Saved {len(self.anchors)} memory anchors to {output_file}")
        
        # Print summary
        print("\nMemory Anchor Summary:")
        print(f"  Total anchors: {len(self.anchors)}")
        print("  Anchor types:")
        for anchor_type, anchors in anchors_by_type.items():
            print(f"    {anchor_type}: {len(anchors)} anchors")

def main():
    parser = argparse.ArgumentParser(description="Extract memory anchors from code")
    parser.add_argument("source_dir", help="Source directory to scan")
    parser.add_argument("--output", default="memory_anchors.json", help="Output file")
    parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Output format")
    parser.add_argument("--exclude", nargs="+", default=["node_modules", "dist", "build", ".git"],
                        help="Patterns to exclude (default: node_modules dist build .git)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    extractor = AnchorExtractor(verbose=args.verbose)
    extractor.extract_anchors(args.source_dir, exclude_patterns=args.exclude)
    extractor.save_anchors(args.output, format=args.format)

if __name__ == "__main__":
    main() 