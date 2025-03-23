#!/usr/bin/env python3

"""Style Guide Checker

This script checks code files against the project's style guide and
reports violations.

Maturity: beta

Why:
- Automated style checking ensures consistent code quality
- Helps developers identify style issues before code review
- Provides a quick way to check compliance with project standards
- Can be integrated into CI/CD pipelines for enforcement
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

class StyleChecker:
    """Checks code files against style guidelines."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.violations = []
    
    def check_file(self, file_path):
        """Check a single file for style violations."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"Error: File {file_path} does not exist")
            return []
        
        file_violations = []
        
        # Determine file type and apply appropriate checks
        if file_path.suffix in ['.js', '.jsx', '.ts', '.tsx']:
            file_violations.extend(self._check_js_ts_file(file_path))
        elif file_path.suffix == '.py':
            file_violations.extend(self._check_python_file(file_path))
        elif file_path.suffix in ['.pine', '.pinescript']:
            file_violations.extend(self._check_pine_script_file(file_path))
        else:
            if self.verbose:
                print(f"Skipping unsupported file type: {file_path}")
            return []
        
        return file_violations
    
    def _check_js_ts_file(self, file_path):
        """Check JavaScript/TypeScript file for style violations."""
        violations = []
        
        # Check if ESLint is available
        try:
            result = subprocess.run(
                ['npx', 'eslint', '--format', 'json', str(file_path)],
                capture_output=True,
                text=True,
                check=False
            )
            
            # Parse ESLint output
            if result.stdout:
                try:
                    eslint_results = json.loads(result.stdout)
                    for file_result in eslint_results:
                        for message in file_result.get('messages', []):
                            violations.append({
                                'file': str(file_path),
                                'line': message.get('line', 0),
                                'column': message.get('column', 0),
                                'rule': message.get('ruleId', 'unknown'),
                                'message': message.get('message', ''),
                                'severity': 'error' if message.get('severity') == 2 else 'warning'
                            })
                except json.JSONDecodeError:
                    print(f"Error parsing ESLint output for {file_path}")
        except FileNotFoundError:
            # Fall back to basic checks if ESLint is not available
            violations.extend(self._basic_js_ts_checks(file_path))
        
        return violations
    
    def _basic_js_ts_checks(self, file_path):
        """Perform basic style checks for JS/TS files without ESLint."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    # Check line length
                    if len(line.rstrip('\n')) > 100:
                        violations.append({
                            'file': str(file_path),
                            'line': i,
                            'column': 101,
                            'rule': 'max-len',
                            'message': 'Line exceeds maximum length of 100',
                            'severity': 'warning'
                        })
                    
                    # Check for trailing whitespace
                    if line.rstrip('\n') != line.rstrip():
                        violations.append({
                            'file': str(file_path),
                            'line': i,
                            'column': len(line.rstrip('\n')),
                            'rule': 'no-trailing-whitespace',
                            'message': 'Line contains trailing whitespace',
                            'severity': 'warning'
                        })
                    
                    # Check for console.log statements
                    if 'console.log(' in line:
                        violations.append({
                            'file': str(file_path),
                            'line': i,
                            'column': line.find('console.log('),
                            'rule': 'no-console',
                            'message': 'Unexpected console statement',
                            'severity': 'warning'
                        })
        except Exception as e:
            print(f"Error checking {file_path}: {e}")
        
        return violations
    
    def _check_python_file(self, file_path):
        """Check Python file for style violations."""
        violations = []
        
        # Check if pylint is available
        try:
            result = subprocess.run(
                ['pylint', '--output-format=json', str(file_path)],
                capture_output=True,
                text=True,
                check=False
            )
            
            # Parse pylint output
            if result.stdout:
                try:
                    pylint_results = json.loads(result.stdout)
                    for message in pylint_results:
                        violations.append({
                            'file': str(file_path),
                            'line': message.get('line', 0),
                            'column': message.get('column', 0),
                            'rule': message.get('symbol', 'unknown'),
                            'message': message.get('message', ''),
                            'severity': 'error' if message.get('type') in ['error', 'fatal'] else 'warning'
                        })
                except json.JSONDecodeError:
                    print(f"Error parsing pylint output for {file_path}")
        except FileNotFoundError:
            # Fall back to basic checks if pylint is not available
            violations.extend(self._basic_python_checks(file_path))
        
        return violations
    
    def _basic_python_checks(self, file_path):
        """Perform basic style checks for Python files without pylint."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    # Check line length
                    if len(line.rstrip('\n')) > 100:
                        violations.append({
                            'file': str(file_path),
                            'line': i,
                            'column': 101,
                            'rule': 'line-too-long',
                            'message': 'Line too long (>100 characters)',
                            'severity': 'warning'
                        })
                    
                    # Check for trailing whitespace
                    if line.rstrip('\n') != line.rstrip():
                        violations.append({
                            'file': str(file_path),
                            'line': i,
                            'column': len(line.rstrip('\n')),
                            'rule': 'trailing-whitespace',
                            'message': 'Line contains trailing whitespace',
                            'severity': 'warning'
                        })
                    
                    # Check for print statements
                    if re.search(r'^\s*print\(', line):
                        violations.append({
                            'file': str(file_path),
                            'line': i,
                            'column': line.find('print('),
                            'rule': 'print-statement',
                            'message': 'Use logging instead of print statements',
                            'severity': 'warning'
                        })
        except Exception as e:
            print(f"Error checking {file_path}: {e}")
        
        return violations
    
    def _check_pine_script_file(self, file_path):
        """Check Pine Script file for style violations."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    # Check line length
                    if len(line.rstrip('\n')) > 100:
                        violations.append({
                            'file': str(file_path),
                            'line': i,
                            'column': 101,
                            'rule': 'line-too-long',
                            'message': 'Line too long (>100 characters)',
                            'severity': 'warning'
                        })
                    
                    # Check for trailing whitespace
                    if line.rstrip('\n') != line.rstrip():
                        violations.append({
                            'file': str(file_path),
                            'line': i,
                            'column': len(line.rstrip('\n')),
                            'rule': 'trailing-whitespace',
                            'message': 'Line contains trailing whitespace',
                            'severity': 'warning'
                        })
                    
                    # Check for missing var keyword for variables that don't need recalculation
                    if re.search(r'^\s*(float|int|bool|string|color)\s+\w+\s*=\s*[^=]', line):
                        if not re.search(r'^\s*var\s+(float|int|bool|string|color)', line):
                            violations.append({
                                'file': str(file_path),
                                'line': i,
                                'column': 0,
                                'rule': 'missing-var-keyword',
                                'message': 'Consider using "var" for variables that don\'t need recalculation on every bar',
                                'severity': 'warning'
                            })
        except Exception as e:
            print(f"Error checking {file_path}: {e}")
        
        return violations
    
    def check_directory(self, directory_path, exclude_patterns=None):
        """Check all files in a directory for style violations."""
        if exclude_patterns is None:
            exclude_patterns = ['node_modules', 'dist', 'build', '.git']
        
        directory_path = Path(directory_path)
        
        if not directory_path.is_dir():
            print(f"Error: {directory_path} is not a directory")
            return
        
        all_files = []
        
        # Collect all files to check
        for root, dirs, files in os.walk(directory_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in str(Path(root) / d) for pattern in exclude_patterns)]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in ['.js', '.jsx', '.ts', '.tsx', '.py', '.pine', '.pinescript']:
                    all_files.append(file_path)
        
        if self.verbose:
            print(f"Found {len(all_files)} files to check")
        
        # Check files in parallel
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(self.check_file, all_files))
        
        # Flatten results
        for file_violations in results:
            self.violations.extend(file_violations)
    
    def report_violations(self, output_format='text', output_file=None):
        """Report style violations in the specified format."""
        if not self.violations:
            print("No style violations found!")
            return
        
        if output_format == 'text':
            self._report_text(output_file)
        elif output_format == 'json':
            self._report_json(output_file)
        elif output_format == 'html':
            self._report_html(output_file)
        else:
            print(f"Unsupported output format: {output_format}")
    
    def _report_text(self, output_file=None):
        """Report violations in text format."""
        # Sort violations by file and line number
        sorted_violations = sorted(
            self.violations,
            key=lambda v: (v['file'], v['line'], v['column'])
        )
        
        # Group violations by file
        violations_by_file = {}
        for violation in sorted_violations:
            file_path = violation['file']
            if file_path not in violations_by_file:
                violations_by_file[file_path] = []
            violations_by_file[file_path].append(violation)
        
        # Generate report
        report = []
        report.append(f"Found {len(self.violations)} style violations in {len(violations_by_file)} files\n")
        
        for file_path, file_violations in violations_by_file.items():
            report.append(f"File: {file_path}")
            report.append("-" * 80)
            
            for violation in file_violations:
                severity = violation['severity'].upper()
                rule = violation['rule']
                line = violation['line']
                column = violation['column']
                message = violation['message']
                
                report.append(f"{severity} {rule} at line {line}, column {column}: {message}")
            
            report.append("")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"Report written to {output_file}")
        else:
            print(report_text)
    
    def _report_json(self, output_file=None):
        """Report violations in JSON format."""
        report = {
            'summary': {
                'total_violations': len(self.violations),
                'files_with_violations': len(set(v['file'] for v in self.violations)),
                'errors': len([v for v in self.violations if v['severity'] == 'error']),
                'warnings': len([v for v in self.violations if v['severity'] == 'warning'])
            },
            'violations': self.violations
        }
        
        report_json = json.dumps(report, indent=2)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_json)
            print(f"Report written to {output_file}")
        else:
            print(report_json)
    
    def _report_html(self, output_file=None):
        """Report violations in HTML format."""
        if not output_file:
            output_file = 'style_report.html'
        
        # Sort violations by file and line number
        sorted_violations = sorted(
            self.violations,
            key=lambda v: (v['file'], v['line'], v['column'])
        )
        
        # Group violations by file
        violations_by_file = {}
        for violation in sorted_violations:
            file_path = violation['file']
            if file_path not in violations_by_file:
                violations_by_file[file_path] = []
            violations_by_file[file_path].append(violation)
        
        # Generate HTML report
        html = []
        html.append('<!DOCTYPE html>')
        html.append('<html lang="en">')
        html.append('<head>')
        html.append('  <meta charset="UTF-8">')
        html.append('  <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html.append('  <title>Style Guide Checker Report</title>')
        html.append('  <style>')
        html.append('    body { font-family: Arial, sans-serif; margin: 20px; }')
        html.append('    h1 { color: #333; }')
        html.append('    .summary { margin-bottom: 20px; }')
        html.append('    .file { margin-bottom: 30px; }')
        html.append('    .file-header { background-color: #f0f0f0; padding: 10px; border-radius: 5px; }')
        html.append('    .violations { margin-left: 20px; }')
        html.append('    .violation { margin: 10px 0; padding: 5px; border-left: 3px solid #ccc; }')
        html.append('    .error { border-left-color: #d9534f; }')
        html.append('    .warning { border-left-color: #f0ad4e; }')
        html.append('    .severity { font-weight: bold; }')
        html.append('    .error .severity { color: #d9534f; }')
        html.append('    .warning .severity { color: #f0ad4e; }')
        html.append('  </style>')
        html.append('</head>')
        html.append('<body>')
        
        html.append('  <h1>Style Guide Checker Report</h1>')
        
        # Summary
        html.append('  <div class="summary">')
        html.append(f'    <p>Found <strong>{len(self.violations)}</strong> style violations in <strong>{len(violations_by_file)}</strong> files.</p>')
        html.append(f'    <p>Errors: <strong>{len([v for v in self.violations if v["severity"] == "error"])}</strong>, Warnings: <strong>{len([v for v in self.violations if v["severity"] == "warning"])}</strong></p>')
        html.append('  </div>')
        
        # Violations by file
        for file_path, file_violations in violations_by_file.items():
            html.append('  <div class="file">')
            html.append(f'    <div class="file-header"><strong>File:</strong> {file_path}</div>')
            html.append('    <div class="violations">')
            
            for violation in file_violations:
                severity = violation['severity']
                rule = violation['rule']
                line = violation['line']
                column = violation['column']
                message = violation['message']
                
                html.append(f'      <div class="violation {severity}">')
                html.append(f'        <span class="severity">{severity.upper()}</span> <strong>{rule}</strong> at line {line}, column {column}')
                html.append(f'        <div>{message}</div>')
                html.append('      </div>')
            
            html.append('    </div>')
            html.append('  </div>')
        
        html.append('</body>')
        html.append('</html>')
        
        with open(output_file, 'w') as f:
            f.write('\n'.join(html))
        
        print(f"HTML report written to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Check code files against style guidelines")
    parser.add_argument("path", help="File or directory to check")
    parser.add_argument("--format", choices=["text", "json", "html"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--output", help="Output file (default: stdout for text/json, style_report.html for html)")
    parser.add_argument("--exclude", nargs="+", default=["node_modules", "dist", "build", ".git"],
                        help="Patterns to exclude (default: node_modules dist build .git)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    checker = StyleChecker(verbose=args.verbose)
    
    path = Path(args.path)
    if path.is_file():
        checker.check_file(path)
    elif path.is_dir():
        checker.check_directory(path, exclude_patterns=args.exclude)
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)
    
    checker.report_violations(output_format=args.format, output_file=args.output)

if __name__ == "__main__":
    main() 