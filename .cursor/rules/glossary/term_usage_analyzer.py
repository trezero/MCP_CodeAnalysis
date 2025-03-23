#!/usr/bin/env python3

"""Term Usage Analyzer

This script analyzes how glossary terms are used throughout the codebase,
identifying inconsistencies and suggesting improvements.

Maturity: beta

Why:
- Consistent terminology is crucial for maintainable code
- This script helps identify where terms are used inconsistently
- Provides insights into which terms are most important
- Helps improve documentation by highlighting key terms
"""

import argparse
import json
import os
import re
from pathlib import Path
import yaml
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import numpy as np

class TermUsageAnalyzer:
    """Analyzes how glossary terms are used throughout the codebase."""
    
    def __init__(self, glossary_file, verbose=False):
        self.verbose = verbose
        self.glossary = self.load_glossary(glossary_file)
        self.term_usage = defaultdict(list)
        self.term_variants = defaultdict(set)
        self.term_counts = Counter()
    
    def load_glossary(self, glossary_file):
        """Load glossary data from a file."""
        try:
            with open(glossary_file, 'r', encoding='utf-8') as f:
                if glossary_file.endswith('.json'):
                    data = json.load(f)
                elif glossary_file.endswith(('.yaml', '.yml')):
                    data = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported file format: {glossary_file}")
            
            # Normalize data structure
            if isinstance(data, dict) and 'terms' in data:
                terms = data['terms']
            elif isinstance(data, list):
                terms = data
            else:
                raise ValueError("Invalid glossary format")
            
            # Extract term names
            return {term['term']: term for term in terms}
        
        except Exception as e:
            print(f"Error loading glossary: {e}")
            return {}
    
    def analyze_directory(self, directory_path, exclude_patterns=None):
        """Analyze term usage in a directory."""
        if exclude_patterns is None:
            exclude_patterns = ['node_modules', 'dist', 'build', '.git']
        
        directory_path = Path(directory_path)
        
        if not directory_path.is_dir():
            print(f"Error: {directory_path} is not a directory")
            return
        
        # Prepare terms for searching
        terms = list(self.glossary.keys())
        
        # Generate variants (camelCase, snake_case, etc.)
        for term in terms:
            self.term_variants[term].add(term)
            
            # Add camelCase variant
            if ' ' in term:
                camel_case = term.split(' ')[0] + ''.join(word.capitalize() for word in term.split(' ')[1:])
                self.term_variants[term].add(camel_case)
            
            # Add snake_case variant
            if ' ' in term:
                snake_case = term.replace(' ', '_').lower()
                self.term_variants[term].add(snake_case)
            
            # Add kebab-case variant
            if ' ' in term:
                kebab_case = term.replace(' ', '-').lower()
                self.term_variants[term].add(kebab_case)
            
            # Add PascalCase variant
            if ' ' in term:
                pascal_case = ''.join(word.capitalize() for word in term.split(' '))
                self.term_variants[term].add(pascal_case)
        
        # Walk through the directory
        for root, dirs, files in os.walk(directory_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in str(Path(root) / d) for pattern in exclude_patterns)]
            
            for file in files:
                if file.endswith(('.js', '.jsx', '.ts', '.tsx', '.py', '.md', '.pine', '.pinescript')):
                    file_path = Path(root) / file
                    self.analyze_file(file_path)
    
    def analyze_file(self, file_path):
        """Analyze term usage in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                for term, variants in self.term_variants.items():
                    for variant in variants:
                        # Use word boundary to match whole words
                        pattern = r'\b' + re.escape(variant) + r'\b'
                        matches = list(re.finditer(pattern, content))
                        
                        if matches:
                            for match in matches:
                                # Get context (the line containing the term)
                                line_start = content.rfind('\n', 0, match.start()) + 1
                                line_end = content.find('\n', match.end())
                                if line_end == -1:
                                    line_end = len(content)
                                
                                line_number = content[:match.start()].count('\n') + 1
                                context = content[line_start:line_end].strip()
                                
                                self.term_usage[term].append({
                                    'file': str(file_path),
                                    'line': line_number,
                                    'variant': variant,
                                    'context': context
                                })
                                self.term_counts[term] += 1
            
            if self.verbose:
                print(f"Analyzed {file_path}")
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def generate_report(self, output_file):
        """Generate a report of term usage."""
        report = {
            'summary': {
                'total_terms': len(self.glossary),
                'terms_found': len(self.term_counts),
                'terms_not_found': len(self.glossary) - len(self.term_counts),
                'total_occurrences': sum(self.term_counts.values())
            },
            'term_counts': dict(self.term_counts),
            'term_usage': dict(self.term_usage),
            'recommendations': self.generate_recommendations()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"Report generated at {output_file}")
        
        # Print summary
        print("\nSummary:")
        print(f"  Total terms in glossary: {report['summary']['total_terms']}")
        print(f"  Terms found in codebase: {report['summary']['terms_found']}")
        print(f"  Terms not found in codebase: {report['summary']['terms_not_found']}")
        print(f"  Total occurrences: {report['summary']['total_occurrences']}")

def main():
    parser = argparse.ArgumentParser(description="Analyze term usage in the codebase")
    parser.add_argument("glossary_file", help="Path to the glossary file (JSON or YAML)")
    parser.add_argument("--directory", help="Directory to analyze")
    parser.add_argument("--output", help="Output file for the term usage report")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    analyzer = TermUsageAnalyzer(args.glossary_file, verbose=args.verbose)
    
    if args.directory:
        analyzer.analyze_directory(args.directory)
    
    if args.output:
        analyzer.generate_report(args.output)
    else:
        print("No output file specified. Use --output to save the term usage report.")

if __name__ == "__main__":
    main() 