#!/usr/bin/env python3

"""Documentation Analyzer

This script analyzes documentation coverage in the codebase,
identifying areas that need better documentation.

Maturity: beta

Why:
- Well-documented code is easier to maintain and understand
- This script helps identify undocumented functions, classes, and modules
- Promotes consistent documentation standards
- Helps maintain code quality and knowledge sharing
"""

import argparse
import json
import os
import re
from pathlib import Path
import ast
import yaml
from collections import defaultdict

class DocumentationAnalyzer:
    """Analyzes documentation coverage in the codebase."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = {
            'files': {},
            'summary': {
                'total_files': 0,
                'total_functions': 0,
                'total_classes': 0,
                'documented_functions': 0,
                'documented_classes': 0,
                'documentation_coverage': 0
            }
        }
        
        # Documentation patterns for different file types
        self.doc_patterns = {
            'js': {
                'function': r'\/\*\*\s*\n(?:.*\n)*?\s*\*\/\s*\n\s*function\s+(\w+)',
                'class': r'\/\*\*\s*\n(?:.*\n)*?\s*\*\/\s*\n\s*class\s+(\w+)',
                'method': r'\/\*\*\s*\n(?:.*\n)*?\s*\*\/\s*\n\s*(\w+)\s*\(',
                'component': r'\/\*\*\s*\n(?:.*\n)*?\s*\*\/\s*\n\s*const\s+(\w+)\s*=\s*\(',
                'hook': r'\/\*\*\s*\n(?:.*\n)*?\s*\*\/\s*\n\s*const\s+use(\w+)\s*='
            },
            'ts': {
                'interface': r'\/\*\*\s*\n(?:.*\n)*?\s*\*\/\s*\n\s*interface\s+(\w+)',
                'type': r'\/\*\*\s*\n(?:.*\n)*?\s*\*\/\s*\n\s*type\s+(\w+)',
                'function': r'\/\*\*\s*\n(?:.*\n)*?\s*\*\/\s*\n\s*function\s+(\w+)',
                'class': r'\/\*\*\s*\n(?:.*\n)*?\s*\*\/\s*\n\s*class\s+(\w+)',
                'method': r'\/\*\*\s*\n(?:.*\n)*?\s*\*\/\s*\n\s*(\w+)\s*\(',
                'component': r'\/\*\*\s*\n(?:.*\n)*?\s*\*\/\s*\n\s*const\s+(\w+)(?::\s*React\.FC|\s*=\s*\()',
                'hook': r'\/\*\*\s*\n(?:.*\n)*?\s*\*\/\s*\n\s*const\s+use(\w+)\s*='
            },
            'py': {
                'module': r'"""\s*\n(?:.*\n)*?\s*"""',
                'class': r'class\s+(\w+)[^:]*:\s*\n\s*"""',
                'function': r'def\s+(\w+)[^:]*:\s*\n\s*"""'
            },
            'pine': {
                'script': r'\/\/\s*@description\s+([^\n]+)',
                'function': r'\/\/\s*@function\s+([^\n]+)'
            }
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
                'interface': r'interface\s+(\w+)',
                'type': r'type\s+(\w+)',
                'function': r'function\s+(\w+)',
                'class': r'class\s+(\w+)',
                'method': r'(\w+)\s*\([^)]*\)\s*{',
                'component': r'const\s+(\w+)(?::\s*React\.FC|\s*=\s*\()',
                'hook': r'const\s+use(\w+)\s*='
            },
            'py': {
                'module': r'',  # Special case, handled separately
                'class': r'class\s+(\w+)',
                'function': r'def\s+(\w+)'
            },
            'pine': {
                'script': r'',  # Special case, handled separately
                'function': r'(\w+)\s*\(\s*\)\s*=>'
            }
        }
    
    def analyze_directory(self, directory_path, exclude_patterns=None):
        """Analyze documentation coverage in files in a directory."""
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
                
                # Analyze based on file type
                if file.endswith(('.js', '.jsx')):
                    self._analyze_js_file(file_path)
                elif file.endswith(('.ts', '.tsx')):
                    self._analyze_ts_file(file_path)
                elif file.endswith('.py'):
                    self._analyze_py_file(file_path)
                elif file.endswith(('.pine', '.pinescript')):
                    self._analyze_pine_file(file_path)
        
        # Calculate summary
        self._calculate_summary()
    
    def _analyze_js_file(self, file_path):
        """Analyze documentation coverage in a JavaScript file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_results = {
                'type': 'js',
                'elements': [],
                'documented_count': 0,
                'total_count': 0,
                'documentation_coverage': 0
            }
            
            # Find all code elements
            for element_type, pattern in self.code_patterns['js'].items():
                for match in re.finditer(pattern, content):
                    name = match.group(1)
                    line_number = content[:match.start()].count('\n') + 1
                    
                    # Check if the element is documented
                    is_documented = False
                    
                    # Look for documentation before the element
                    doc_pattern = self.doc_patterns['js'][element_type]
                    for doc_match in re.finditer(doc_pattern, content):
                        doc_name = doc_match.group(1)
                        if doc_name == name:
                            is_documented = True
                            break
                    
                    file_results['elements'].append({
                        'name': name,
                        'type': element_type,
                        'line': line_number,
                        'is_documented': is_documented
                    })
                    
                    file_results['total_count'] += 1
                    if is_documented:
                        file_results['documented_count'] += 1
            
            # Calculate coverage
            if file_results['total_count'] > 0:
                file_results['documentation_coverage'] = file_results['documented_count'] / file_results['total_count'] * 100
            
            self.results['files'][str(file_path)] = file_results
            
            if self.verbose:
                print(f"Analyzed {file_path}")
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _analyze_ts_file(self, file_path):
        """Analyze documentation coverage in a TypeScript file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_results = {
                'type': 'ts',
                'elements': [],
                'documented_count': 0,
                'total_count': 0,
                'documentation_coverage': 0
            }
            
            # Find all code elements
            for element_type, pattern in self.code_patterns['ts'].items():
                for match in re.finditer(pattern, content):
                    name = match.group(1)
                    line_number = content[:match.start()].count('\n') + 1
                    
                    # Check if the element is documented
                    is_documented = False
                    
                    # Look for documentation before the element
                    doc_pattern = self.doc_patterns['ts'][element_type]
                    for doc_match in re.finditer(doc_pattern, content):
                        doc_name = doc_match.group(1)
                        if doc_name == name:
                            is_documented = True
                            break
                    
                    file_results['elements'].append({
                        'name': name,
                        'type': element_type,
                        'line': line_number,
                        'is_documented': is_documented
                    })
                    
                    file_results['total_count'] += 1
                    if is_documented:
                        file_results['documented_count'] += 1
            
            # Calculate coverage
            if file_results['total_count'] > 0:
                file_results['documentation_coverage'] = file_results['documented_count'] / file_results['total_count'] * 100
            
            self.results['files'][str(file_path)] = file_results
            
            if self.verbose:
                print(f"Analyzed {file_path}")
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _analyze_py_file(self, file_path):
        """Analyze documentation coverage in a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_results = {
                'type': 'py',
                'elements': [],
                'documented_count': 0,
                'total_count': 0,
                'documentation_coverage': 0
            }
            
            # Check for module docstring
            module_doc = re.search(r'^"""[\s\S]*?"""', content)
            has_module_doc = bool(module_doc)
            
            file_results['elements'].append({
                'name': str(file_path.name),
                'type': 'module',
                'line': 1,
                'is_documented': has_module_doc
            })
            
            file_results['total_count'] += 1
            if has_module_doc:
                file_results['documented_count'] += 1
            
            # Parse Python code
            try:
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check for class docstring
                        has_doc = bool(ast.get_docstring(node))
                        
                        file_results['elements'].append({
                            'name': node.name,
                            'type': 'class',
                            'line': node.lineno,
                            'is_documented': has_doc
                        })
                        
                        file_results['total_count'] += 1
                        if has_doc:
                            file_results['documented_count'] += 1
                    
                    elif isinstance(node, ast.FunctionDef):
                        # Skip if it's a method (already counted with class)
                        if isinstance(node.parent, ast.ClassDef):
                            continue
                        
                        # Check for function docstring
                        has_doc = bool(ast.get_docstring(node))
                        
                        file_results['elements'].append({
                            'name': node.name,
                            'type': 'function',
                            'line': node.lineno,
                            'is_documented': has_doc
                        })
                        
                        file_results['total_count'] += 1
                        if has_doc:
                            file_results['documented_count'] += 1
            
            except SyntaxError:
                # Fall back to regex for Python files with syntax errors
                for element_type, pattern in self.code_patterns['py'].items():
                    if not pattern:  # Skip special cases
                        continue
                    
                    for match in re.finditer(pattern, content):
                        name = match.group(1)
                        line_number = content[:match.start()].count('\n') + 1
                        
                        # Check if the element is documented
                        is_documented = False
                        
                        # Look for documentation after the element declaration
                        doc_pattern = self.doc_patterns['py'][element_type]
                        if re.search(f"{pattern}[^:]*:\s*\n\s*\"\"\"", content):
                            is_documented = True
                        
                        file_results['elements'].append({
                            'name': name,
                            'type': element_type,
                            'line': line_number,
                            'is_documented': is_documented
                        })
                        
                        file_results['total_count'] += 1
                        if is_documented:
                            file_results['documented_count'] += 1
            
            # Calculate coverage
            if file_results['total_count'] > 0:
                file_results['documentation_coverage'] = file_results['documented_count'] / file_results['total_count'] * 100
            
            self.results['files'][str(file_path)] = file_results
            
            if self.verbose:
                print(f"Analyzed {file_path}")
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _analyze_pine_file(self, file_path):
        """Analyze documentation coverage in a Pine Script file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_results = {
                'type': 'pine',
                'elements': [],
                'documented_count': 0,
                'total_count': 0,
                'documentation_coverage': 0
            }
            
            # Check for script description
            script_doc = re.search(r'\/\/\s*@description\s+([^\n]+)', content)
            has_script_doc = bool(script_doc)
            
            file_results['elements'].append({
                'name': str(file_path.name),
                'type': 'script',
                'line': 1,
                'is_documented': has_script_doc
            })
            
            file_results['total_count'] += 1
            if has_script_doc:
                file_results['documented_count'] += 1
            
            # Find all functions
            function_pattern = r'(\w+)\s*\(\s*\)\s*=>'
            for match in re.finditer(function_pattern, content):
                name = match.group(1)
                line_number = content[:match.start()].count('\n') + 1
                
                # Check if the function is documented
                is_documented = False
                
                # Look for documentation before the function
                doc_pattern = r'\/\/\s*@function\s+' + re.escape(name)
                if re.search(doc_pattern, content):
                    is_documented = True
                
                file_results['elements'].append({
                    'name': name,
                    'type': 'function',
                    'line': line_number,
                    'is_documented': is_documented
                })
                
                file_results['total_count'] += 1
                if is_documented:
                    file_results['documented_count'] += 1
            
            # Calculate coverage
            if file_results['total_count'] > 0:
                file_results['documentation_coverage'] = file_results['documented_count'] / file_results['total_count'] * 100
            
            self.results['files'][str(file_path)] = file_results
            
            if self.verbose:
                print(f"Analyzed {file_path}")
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _calculate_summary(self):
        """Calculate summary statistics."""
        total_files = len(self.results['files'])
        total_functions = 0
        total_classes = 0
        documented_functions = 0
        documented_classes = 0
        
        for file_path, file_data in self.results['files'].items():
            for element in file_data['elements']:
                if element['type'] in ['function', 'method', 'hook']:
                    total_functions += 1
                    if element['is_documented']:
                        documented_functions += 1
                elif element['type'] in ['class', 'interface', 'type', 'component']:
                    total_classes += 1
                    if element['is_documented']:
                        documented_classes += 1
        
        # Calculate overall documentation coverage
        total_elements = total_functions + total_classes
        documented_elements = documented_functions + documented_classes
        documentation_coverage = (documented_elements / total_elements * 100) if total_elements > 0 else 0
        
        self.results['summary'] = {
            'total_files': total_files,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'documented_functions': documented_functions,
            'documented_classes': documented_classes,
            'documentation_coverage': documentation_coverage
        }
    
    def save_results(self, output_file, format='json'):
        """Save analysis results to a file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(self.results, f, indent=2)
            elif format == 'yaml':
                yaml.dump(self.results, f, sort_keys=False)
        
        print(f"Saved documentation analysis results to {output_file}")
    
    def generate_report(self, output_file):
        """Generate a human-readable report."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Documentation Coverage Report\n\n")
            
            # Write summary
            f.write("## Summary\n\n")
            f.write(f"- Total files analyzed: {self.results['summary']['total_files']}\n")
            f.write(f"- Total functions: {self.results['summary']['total_functions']}\n")
            f.write(f"- Total classes: {self.results['summary']['total_classes']}\n")
            f.write(f"- Documented functions: {self.results['summary']['documented_functions']} ({(self.results['summary']['documented_functions'] / self.results['summary']['total_functions'] * 100) if self.results['summary']['total_functions'] > 0 else 0:.2f}%)\n")
            f.write(f"- Documented classes: {self.results['summary']['documented_classes']} ({(self.results['summary']['documented_classes'] / self.results['summary']['total_classes'] * 100) if self.results['summary']['total_classes'] > 0 else 0:.2f}%)\n")
            f.write(f"- Overall documentation coverage: {self.results['summary']['documentation_coverage']:.2f}%\n\n")
            
            # Write files with lowest documentation coverage
            f.write("## Files with Lowest Documentation Coverage\n\n")
            f.write("| File | Type | Coverage | Documented | Total |\n")
            f.write("|------|------|----------|------------|-------|\n")
            
            # Sort files by documentation coverage (ascending)
            files_by_coverage = sorted(
                [(file_path, file_data) for file_path, file_data in self.results['files'].items() if file_data['total_count'] > 0],
                key=lambda x: x[1]['documentation_coverage']
            )
            
            # Write top 20 files with lowest coverage
            for file_path, file_data in files_by_coverage[:20]:
                f.write(f"| {file_path} | {file_data['type']} | {file_data['documentation_coverage']:.2f}% | {file_data['documented_count']} | {file_data['total_count']} |\n")
            
            f.write("\n")
            
            # Write undocumented elements
            f.write("## Undocumented Elements\n\n")
            
            # Group by file
            for file_path, file_data in self.results['files'].items():
                undocumented = [e for e in file_data['elements'] if not e['is_documented']]
                
                if undocumented:
                    f.write(f"### {file_path}\n\n")
                    f.write("| Element | Type | Line |\n")
                    f.write("|---------|------|------|\n")
                    
                    for element in undocumented:
                        f.write(f"| {element['name']} | {element['type']} | {element['line']} |\n")
                    
                    f.write("\n")
        
        print(f"Generated documentation report at {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Analyze documentation coverage")
    parser.add_argument("source_dir", help="Source directory to analyze")
    parser.add_argument("--output", default="documentation_analysis.json", help="Output file")
    parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Output format")
    parser.add_argument("--report", help="Generate human-readable report")
    parser.add_argument("--exclude", nargs="+", default=["node_modules", "dist", "build", ".git"],
                        help="Patterns to exclude (default: node_modules dist build .git)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    analyzer = DocumentationAnalyzer(verbose=args.verbose)
    analyzer.analyze_directory(args.source_dir, exclude_patterns=args.exclude)
    analyzer.save_results(args.output, format=args.format)
    
    if args.report:
        analyzer.generate_report(args.report)

if __name__ == "__main__":
    main() 