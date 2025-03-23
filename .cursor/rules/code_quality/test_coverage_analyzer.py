#!/usr/bin/env python3

"""Test Coverage Analyzer

This script analyzes test coverage in the codebase,
identifying areas that need better test coverage.

Maturity: beta

Why:
- Well-tested code is more reliable and easier to maintain
- This script helps identify untested functions, classes, and modules
- Promotes consistent testing standards
- Helps maintain code quality and prevent regressions
"""

import argparse
import json
import os
import re
from pathlib import Path
import yaml
from collections import defaultdict

class TestCoverageAnalyzer:
    """Analyzes test coverage in the codebase."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = {
            'files': {},
            'summary': {
                'total_files': 0,
                'tested_files': 0,
                'total_functions': 0,
                'tested_functions': 0,
                'test_coverage': 0
            }
        }
        
        # Patterns to identify test files
        self.test_file_patterns = [
            r'.*\.test\.[jt]sx?$',
            r'.*\.spec\.[jt]sx?$',
            r'.*_test\.py$',
            r'test_.*\.py$'
        ]
        
        # Patterns to identify test functions
        self.test_function_patterns = {
            'js': [
                r'test\([\'"]([^\'"]+)[\'"]',
                r'it\([\'"]([^\'"]+)[\'"]',
                r'describe\([\'"]([^\'"]+)[\'"]'
            ],
            'ts': [
                r'test\([\'"]([^\'"]+)[\'"]',
                r'it\([\'"]([^\'"]+)[\'"]',
                r'describe\([\'"]([^\'"]+)[\'"]'
            ],
            'py': [
                r'def\s+test_(\w+)',
                r'def\s+(\w+)_test'
            ]
        }
        
        # Patterns to identify code elements
        self.code_patterns = {
            'js': {
                'function': r'function\s+(\w+)',
                'class': r'class\s+(\w+)',
                'method': r'(\w+)\s*\([^)]*\)\s*{',
                'component': r'const\s+(\w+)\s*=\s*\(',
                'hook': r'const\s+use(\w+)\s*='
            },
            'ts': {
                'function': r'function\s+(\w+)',
                'class': r'class\s+(\w+)',
                'method': r'(\w+)\s*\([^)]*\)\s*{',
                'component': r'const\s+(\w+)(?::\s*React\.FC|\s*=\s*\()',
                'hook': r'const\s+use(\w+)\s*='
            },
            'py': {
                'function': r'def\s+(\w+)',
                'class': r'class\s+(\w+)'
            }
        }
    
    def analyze_directory(self, directory_path, exclude_patterns=None):
        """Analyze test coverage in files in a directory."""
        if exclude_patterns is None:
            exclude_patterns = ['node_modules', 'dist', 'build', '.git']
        
        directory_path = Path(directory_path)
        
        if not directory_path.is_dir():
            print(f"Error: {directory_path} is not a directory")
            return
        
        # First pass: collect all code files and test files
        code_files = []
        test_files = []
        
        for root, dirs, files in os.walk(directory_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in str(Path(root) / d) for pattern in exclude_patterns)]
            
            for file in files:
                file_path = Path(root) / file
                
                # Check if it's a test file
                is_test_file = any(re.match(pattern, str(file_path)) for pattern in self.test_file_patterns)
                
                if is_test_file:
                    test_files.append(file_path)
                elif file.endswith(('.js', '.jsx', '.ts', '.tsx', '.py')):
                    code_files.append(file_path)
        
        # Second pass: analyze test files to extract test cases
        test_cases = self._extract_test_cases(test_files)
        
        # Third pass: analyze code files and match with test cases
        self._analyze_code_files(code_files, test_cases)
        
        # Calculate summary
        self._calculate_summary()
    
    def _extract_test_cases(self, test_files):
        """Extract test cases from test files."""
        test_cases = []
        
        for file_path in test_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Determine file type
                file_type = None
                if file_path.suffix in ['.js', '.jsx']:
                    file_type = 'js'
                elif file_path.suffix in ['.ts', '.tsx']:
                    file_type = 'ts'
                elif file_path.suffix == '.py':
                    file_type = 'py'
                else:
                    continue
                
                # Extract test cases
                for pattern in self.test_function_patterns.get(file_type, []):
                    for match in re.finditer(pattern, content):
                        test_name = match.group(1)
                        line_number = content[:match.start()].count('\n') + 1
                        
                        test_cases.append({
                            'name': test_name,
                            'file': str(file_path),
                            'line': line_number
                        })
                
                if self.verbose:
                    print(f"Extracted {len(test_cases)} test cases from {file_path}")
            
            except Exception as e:
                print(f"Error extracting test cases from {file_path}: {e}")
        
        return test_cases
    
    def _analyze_code_files(self, code_files, test_cases):
        """Analyze code files and match with test cases."""
        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Determine file type
                file_type = None
                if file_path.suffix in ['.js', '.jsx']:
                    file_type = 'js'
                elif file_path.suffix in ['.ts', '.tsx']:
                    file_type = 'ts'
                elif file_path.suffix == '.py':
                    file_type = 'py'
                else:
                    continue
                
                file_results = {
                    'type': file_type,
                    'elements': [],
                    'tested_count': 0,
                    'total_count': 0,
                    'test_coverage': 0
                }
                
                # Extract code elements
                for element_type, pattern in self.code_patterns.get(file_type, {}).items():
                    for match in re.finditer(pattern, content):
                        name = match.group(1)
                        line_number = content[:match.start()].count('\n') + 1
                        
                        # Check if the element is tested
                        is_tested = False
                        matching_tests = []
                        
                        # Simple matching: look for the element name in test cases
                        for test_case in test_cases:
                            if name.lower() in test_case['name'].lower():
                                is_tested = True
                                matching_tests.append(test_case)
                        
                        # Also check if the file has a corresponding test file
                        file_stem = file_path.stem
                        file_has_test = any(
                            file_stem in str(test_file) or 
                            file_stem.replace('_', '') in str(test_file).replace('_', '')
                            for test_file in test_files
                        )
                        
                        element = {
                            'name': name,
                            'type': element_type,
                            'line': line_number,
                            'is_tested': is_tested,
                            'matching_tests': matching_tests,
                            'file_has_test': file_has_test
                        }
                        
                        file_results['elements'].append(element)
                        file_results['total_count'] += 1
                        
                        if is_tested:
                            file_results['tested_count'] += 1
                
                # Calculate coverage for the file
                if file_results['total_count'] > 0:
                    file_results['test_coverage'] = file_results['tested_count'] / file_results['total_count'] * 100
                
                self.results['files'][str(file_path)] = file_results
                
                if self.verbose:
                    print(f"Analyzed {file_path}")
            
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
    
    def _calculate_summary(self):
        """Calculate summary statistics."""
        total_files = len(self.results['files'])
        tested_files = sum(1 for file_data in self.results['files'].values() if file_data['tested_count'] > 0)
        total_functions = sum(file_data['total_count'] for file_data in self.results['files'].values())
        tested_functions = sum(file_data['tested_count'] for file_data in self.results['files'].values())
        
        # Calculate overall test coverage
        test_coverage = (tested_functions / total_functions * 100) if total_functions > 0 else 0
        
        self.results['summary'] = {
            'total_files': total_files,
            'tested_files': tested_files,
            'total_functions': total_functions,
            'tested_functions': tested_functions,
            'test_coverage': test_coverage
        }
    
    def save_results(self, output_file, format='json'):
        """Save analysis results to a file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(self.results, f, indent=2)
            elif format == 'yaml':
                yaml.dump(self.results, f, sort_keys=False)
        
        print(f"Saved test coverage analysis results to {output_file}")
    
    def generate_report(self, output_file):
        """Generate a human-readable report."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Test Coverage Report\n\n")
            
            # Write summary
            f.write("## Summary\n\n")
            f.write(f"- Total files analyzed: {self.results['summary']['total_files']}\n")
            f.write(f"- Files with tests: {self.results['summary']['tested_files']} ({self.results['summary']['tested_files'] / self.results['summary']['total_files'] * 100:.2f}% if self.results['summary']['total_files'] > 0 else 0:.2f}%)\n")
            f.write(f"- Total functions/classes: {self.results['summary']['total_functions']}\n")
            f.write(f"- Tested functions/classes: {self.results['summary']['tested_functions']} ({self.results['summary']['tested_functions'] / self.results['summary']['total_functions'] * 100:.2f}% if self.results['summary']['total_functions'] > 0 else 0:.2f}%)\n")
            f.write(f"- Overall test coverage: {self.results['summary']['test_coverage']:.2f}%\n\n")
            
            # Write files with lowest test coverage
            f.write("## Files with Lowest Test Coverage\n\n")
            f.write("| File | Type | Coverage | Tested | Total |\n")
            f.write("|------|------|----------|--------|-------|\n")
            
            # Sort files by test coverage (ascending)
            files_by_coverage = sorted(
                [(file_path, file_data) for file_path, file_data in self.results['files'].items() if file_data['total_count'] > 0],
                key=lambda x: x[1]['test_coverage']
            )
            
            # Write top 20 files with lowest coverage
            for file_path, file_data in files_by_coverage[:20]:
                f.write(f"| {file_path} | {file_data['type']} | {file_data['test_coverage']:.2f}% | {file_data['tested_count']} | {file_data['total_count']} |\n")
            
            f.write("\n")
            
            # Write untested elements
            f.write("## Untested Elements\n\n")
            
            # Group by file
            for file_path, file_data in self.results['files'].items():
                untested = [e for e in file_data['elements'] if not e['is_tested']]
                
                if untested:
                    f.write(f"### {file_path}\n\n")
                    f.write("| Element | Type | Line | File Has Tests |\n")
                    f.write("|---------|------|------|---------------|\n")
                    
                    for element in untested:
                        f.write(f"| {element['name']} | {element['type']} | {element['line']} | {'Yes' if element['file_has_test'] else 'No'} |\n")
                    
                    f.write("\n")
        
        print(f"Generated test coverage report at {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Analyze test coverage")
    parser.add_argument("source_dir", help="Source directory to analyze")
    parser.add_argument("--output", default="test_coverage_analysis.json", help="Output file")
    parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Output format")
    parser.add_argument("--report", help="Generate human-readable report")
    parser.add_argument("--exclude", nargs="+", default=["node_modules", "dist", "build", ".git"],
                        help="Patterns to exclude (default: node_modules dist build .git)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    analyzer = TestCoverageAnalyzer(verbose=args.verbose)
    analyzer.analyze_directory(args.source_dir, exclude_patterns=args.exclude)
    analyzer.save_results(args.output, format=args.format)
    
    if args.report:
        analyzer.generate_report(args.report)

if __name__ == "__main__":
    main() 