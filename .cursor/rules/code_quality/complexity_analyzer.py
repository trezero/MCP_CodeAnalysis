#!/usr/bin/env python3

"""Complexity Analyzer

This script analyzes the complexity of code in the codebase,
identifying areas that may need refactoring.

Maturity: beta

Why:
- Complex code is harder to maintain and more prone to bugs
- This script helps identify overly complex functions and classes
- Provides metrics to guide refactoring efforts
- Helps maintain code quality over time
"""

import argparse
import json
import os
import re
from pathlib import Path
import ast
import yaml
from radon.complexity import cc_visit
from radon.metrics import h_visit
from radon.raw import analyze
from collections import defaultdict
import sys

# Add parent directory to path to import rule_loader
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from rule_loader import rule_loader

class ComplexityAnalyzer:
    """Analyzes code complexity in the codebase."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = {
            'files': {},
            'summary': {
                'total_files': 0,
                'total_functions': 0,
                'total_classes': 0,
                'average_complexity': 0,
                'complexity_distribution': {
                    'simple': 0,
                    'moderate': 0,
                    'complex': 0,
                    'very_complex': 0
                }
            }
        }
        
        # Get glob patterns from rules
        self.glob_patterns = rule_loader.get_globs_for_category('code_quality')
        if not self.glob_patterns:
            # Default patterns if none found in rules
            self.glob_patterns = ['**/*.py', '**/*.js', '**/*.ts', '**/*.jsx', '**/*.tsx']
        
        if self.verbose:
            print(f"Using glob patterns: {self.glob_patterns}")
    
    def analyze_directory(self, directory_path, exclude_patterns=None):
        """Analyze complexity of files in a directory."""
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
        """Analyze complexity of a JavaScript file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use radon to analyze JavaScript
            # Note: radon is primarily for Python, but works reasonably well for JS
            results = cc_visit(content)
            
            functions = []
            classes = []
            
            for item in results:
                if item.type == 'function':
                    functions.append({
                        'name': item.name,
                        'complexity': item.complexity,
                        'line': item.lineno,
                        'end_line': item.endline,
                        'rank': self._get_complexity_rank(item.complexity)
                    })
                elif item.type == 'class':
                    classes.append({
                        'name': item.name,
                        'complexity': item.complexity,
                        'line': item.lineno,
                        'end_line': item.endline,
                        'rank': self._get_complexity_rank(item.complexity),
                        'methods': [
                            {
                                'name': method.name,
                                'complexity': method.complexity,
                                'line': method.lineno,
                                'end_line': method.endline,
                                'rank': self._get_complexity_rank(method.complexity)
                            }
                            for method in item.methods
                        ]
                    })
            
            # Get raw metrics
            raw_metrics = analyze(content)
            
            # Get Halstead metrics
            try:
                h_metrics = h_visit(content)
                halstead = {
                    'h1': h_metrics.h1,
                    'h2': h_metrics.h2,
                    'N1': h_metrics.N1,
                    'N2': h_metrics.N2,
                    'vocabulary': h_metrics.vocabulary,
                    'length': h_metrics.length,
                    'calculated_length': h_metrics.calculated_length,
                    'volume': h_metrics.volume,
                    'difficulty': h_metrics.difficulty,
                    'effort': h_metrics.effort,
                    'time': h_metrics.time,
                    'bugs': h_metrics.bugs
                }
            except:
                halstead = {}
            
            self.results['files'][str(file_path)] = {
                'type': 'javascript',
                'functions': functions,
                'classes': classes,
                'total_complexity': sum(f['complexity'] for f in functions) + sum(c['complexity'] for c in classes),
                'average_complexity': (sum(f['complexity'] for f in functions) + sum(c['complexity'] for c in classes)) / 
                                     (len(functions) + len(classes)) if (len(functions) + len(classes)) > 0 else 0,
                'raw_metrics': {
                    'loc': raw_metrics.loc,
                    'lloc': raw_metrics.lloc,
                    'sloc': raw_metrics.sloc,
                    'comments': raw_metrics.comments,
                    'multi': raw_metrics.multi,
                    'blank': raw_metrics.blank
                },
                'halstead_metrics': halstead
            }
            
            if self.verbose:
                print(f"Analyzed {file_path}")
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _analyze_ts_file(self, file_path):
        """Analyze complexity of a TypeScript file."""
        # TypeScript analysis is similar to JavaScript
        self._analyze_js_file(file_path)
        
        # Update the file type
        if str(file_path) in self.results['files']:
            self.results['files'][str(file_path)]['type'] = 'typescript'
    
    def _analyze_py_file(self, file_path):
        """Analyze complexity of a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use radon to analyze Python
            results = cc_visit(content)
            
            functions = []
            classes = []
            
            for item in results:
                if item.type == 'function':
                    functions.append({
                        'name': item.name,
                        'complexity': item.complexity,
                        'line': item.lineno,
                        'end_line': item.endline,
                        'rank': self._get_complexity_rank(item.complexity)
                    })
                elif item.type == 'class':
                    classes.append({
                        'name': item.name,
                        'complexity': item.complexity,
                        'line': item.lineno,
                        'end_line': item.endline,
                        'rank': self._get_complexity_rank(item.complexity),
                        'methods': [
                            {
                                'name': method.name,
                                'complexity': method.complexity,
                                'line': method.lineno,
                                'end_line': method.endline,
                                'rank': self._get_complexity_rank(method.complexity)
                            }
                            for method in item.methods
                        ]
                    })
            
            # Get raw metrics
            raw_metrics = analyze(content)
            
            # Get Halstead metrics
            try:
                h_metrics = h_visit(content)
                halstead = {
                    'h1': h_metrics.h1,
                    'h2': h_metrics.h2,
                    'N1': h_metrics.N1,
                    'N2': h_metrics.N2,
                    'vocabulary': h_metrics.vocabulary,
                    'length': h_metrics.length,
                    'calculated_length': h_metrics.calculated_length,
                    'volume': h_metrics.volume,
                    'difficulty': h_metrics.difficulty,
                    'effort': h_metrics.effort,
                    'time': h_metrics.time,
                    'bugs': h_metrics.bugs
                }
            except:
                halstead = {}
            
            self.results['files'][str(file_path)] = {
                'type': 'python',
                'functions': functions,
                'classes': classes,
                'total_complexity': sum(f['complexity'] for f in functions) + sum(c['complexity'] for c in classes),
                'average_complexity': (sum(f['complexity'] for f in functions) + sum(c['complexity'] for c in classes)) / 
                                     (len(functions) + len(classes)) if (len(functions) + len(classes)) > 0 else 0,
                'raw_metrics': {
                    'loc': raw_metrics.loc,
                    'lloc': raw_metrics.lloc,
                    'sloc': raw_metrics.sloc,
                    'comments': raw_metrics.comments,
                    'multi': raw_metrics.multi,
                    'blank': raw_metrics.blank
                },
                'halstead_metrics': halstead
            }
            
            if self.verbose:
                print(f"Analyzed {file_path}")
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _analyze_pine_file(self, file_path):
        """Analyze complexity of a Pine Script file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple analysis for Pine Script
            # Count functions and estimate complexity
            function_pattern = r'(\w+)\s*\(\s*\)\s*=>'
            functions = []
            
            for match in re.finditer(function_pattern, content):
                name = match.group(1)
                start_pos = match.start()
                
                # Find the function body
                line_number = content[:start_pos].count('\n') + 1
                
                # Estimate complexity based on conditionals and loops
                function_content = content[start_pos:]
                if_count = function_content.count('if ')
                else_count = function_content.count('else')
                for_count = function_content.count('for ')
                while_count = function_content.count('while ')
                
                # Simple complexity estimate
                complexity = 1 + if_count + else_count + for_count + while_count
                
                functions.append({
                    'name': name,
                    'complexity': complexity,
                    'line': line_number,
                    'end_line': None,
                    'rank': self._get_complexity_rank(complexity)
                })
            
            # Count lines
            lines = content.split('\n')
            loc = len(lines)
            blank = sum(1 for line in lines if not line.strip())
            comments = sum(1 for line in lines if line.strip().startswith('//'))
            
            self.results['files'][str(file_path)] = {
                'type': 'pine',
                'functions': functions,
                'classes': [],
                'total_complexity': sum(f['complexity'] for f in functions),
                'average_complexity': sum(f['complexity'] for f in functions) / len(functions) if functions else 0,
                'raw_metrics': {
                    'loc': loc,
                    'blank': blank,
                    'comments': comments,
                    'sloc': loc - blank - comments
                }
            }
            
            if self.verbose:
                print(f"Analyzed {file_path}")
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _get_complexity_rank(self, complexity):
        """Get the rank of a complexity score."""
        if complexity <= 5:
            return 'simple'
        elif complexity <= 10:
            return 'moderate'
        elif complexity <= 20:
            return 'complex'
        else:
            return 'very_complex'
    
    def _calculate_summary(self):
        """Calculate summary statistics."""
        total_files = len(self.results['files'])
        total_functions = sum(len(file_data.get('functions', [])) for file_data in self.results['files'].values())
        total_classes = sum(len(file_data.get('classes', [])) for file_data in self.results['files'].values())
        
        # Calculate complexity distribution
        complexity_distribution = defaultdict(int)
        
        for file_path, file_data in self.results['files'].items():
            for function in file_data.get('functions', []):
                complexity_distribution[function['rank']] += 1
            
            for class_data in file_data.get('classes', []):
                complexity_distribution[class_data['rank']] += 1
                for method in class_data.get('methods', []):
                    complexity_distribution[method['rank']] += 1
        
        # Calculate average complexity
        total_complexity = sum(file_data.get('total_complexity', 0) for file_data in self.results['files'].values())
        average_complexity = total_complexity / (total_functions + total_classes) if (total_functions + total_classes) > 0 else 0
        
        self.results['summary'] = {
            'total_files': total_files,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'total_complexity': total_complexity,
            'average_complexity': average_complexity,
            'complexity_distribution': {
                'simple': complexity_distribution['simple'],
                'moderate': complexity_distribution['moderate'],
                'complex': complexity_distribution['complex'],
                'very_complex': complexity_distribution['very_complex']
            }
        }
    
    def save_results(self, output_file, format='json'):
        """Save analysis results to a file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(self.results, f, indent=2)
            elif format == 'yaml':
                yaml.dump(self.results, f, sort_keys=False)
        
        print(f"Saved complexity analysis results to {output_file}")
    
    def generate_report(self, output_file):
        """Generate a human-readable report."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Code Complexity Analysis Report\n\n")
            
            # Write summary
            f.write("## Summary\n\n")
            f.write(f"- Total files analyzed: {self.results['summary']['total_files']}\n")
            f.write(f"- Total functions: {self.results['summary']['total_functions']}\n")
            f.write(f"- Total classes: {self.results['summary']['total_classes']}\n")
            f.write(f"- Average complexity: {self.results['summary']['average_complexity']:.2f}\n\n")
            
            # Write complexity distribution
            f.write("## Complexity Distribution\n\n")
            f.write("| Complexity | Count | Percentage |\n")
            f.write("|------------|-------|------------|\n")
            
            total = sum(self.results['summary']['complexity_distribution'].values())
            for rank, count in self.results['summary']['complexity_distribution'].items():
                percentage = (count / total * 100) if total > 0 else 0
                f.write(f"| {rank} | {count} | {percentage:.2f}% |\n")
            
            f.write("\n")
            
            # Write most complex functions
            f.write("## Most Complex Functions\n\n")
            f.write("| Function | File | Complexity | Rank |\n")
            f.write("|----------|------|------------|------|\n")
            
            # Collect all functions
            all_functions = []
            for file_path, file_data in self.results['files'].items():
                for function in file_data.get('functions', []):
                    all_functions.append({
                        'name': function['name'],
                        'file': file_path,
                        'complexity': function['complexity'],
                        'rank': function['rank']
                    })
                
                for class_data in file_data.get('classes', []):
                    for method in class_data.get('methods', []):
                        all_functions.append({
                            'name': f"{class_data['name']}.{method['name']}",
                            'file': file_path,
                            'complexity': method['complexity'],
                            'rank': method['rank']
                        })
            
            # Sort by complexity (descending)
            all_functions.sort(key=lambda x: x['complexity'], reverse=True)
            
            # Write top 20 most complex functions
            for function in all_functions[:20]:
                f.write(f"| {function['name']} | {function['file']} | {function['complexity']} | {function['rank']} |\n")
            
            f.write("\n")
            
            # Write most complex files
            f.write("## Most Complex Files\n\n")
            f.write("| File | Type | Total Complexity | Average Complexity |\n")
            f.write("|------|------|------------------|--------------------|\n")
            
            # Sort files by total complexity
            files_by_complexity = sorted(
                [(file_path, file_data) for file_path, file_data in self.results['files'].items()],
                key=lambda x: x[1].get('total_complexity', 0),
                reverse=True
            )
            
            # Write top 20 most complex files
            for file_path, file_data in files_by_complexity[:20]:
                f.write(f"| {file_path} | {file_data.get('type', 'unknown')} | {file_data.get('total_complexity', 0)} | {file_data.get('average_complexity', 0):.2f} |\n")
        
        print(f"Generated complexity report at {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Analyze code complexity")
    parser.add_argument("source_dir", help="Source directory to analyze")
    parser.add_argument("--output", default="complexity_analysis.json", help="Output file")
    parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Output format")
    parser.add_argument("--report", help="Generate human-readable report")
    parser.add_argument("--exclude", nargs="+", default=["node_modules", "dist", "build", ".git"],
                        help="Patterns to exclude (default: node_modules dist build .git)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    analyzer = ComplexityAnalyzer(verbose=args.verbose)
    analyzer.analyze_directory(args.source_dir, exclude_patterns=args.exclude)
    analyzer.save_results(args.output, format=args.format)
    
    if args.report:
        analyzer.generate_report(args.report)

if __name__ == "__main__":
    main() 