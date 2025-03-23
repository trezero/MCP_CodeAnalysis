#!/usr/bin/env python3
"""
Pine Script Linter - Enforces coding standards for Pine Script files.
"""

import os
import re
import sys
import json
import glob
from typing import List, Dict, Any, Tuple, Optional
import argparse
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored terminal output
init()

# Default configuration path
DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "pinescript", "config.json"
)

class PineLinter:
    """Pine Script linter that checks Pine Script files for compliance with coding standards."""

    def __init__(self, config_path: str = DEFAULT_CONFIG_PATH):
        """Initialize the linter with configuration."""
        self.config = self._load_config(config_path)
        
        # Compile regular expressions for performance
        self.version_pattern = re.compile(r'//@version\s*=\s*\d+')
        self.section_pattern = re.compile(r'//\s*=+\s*([A-Z][A-Z\s]+[A-Z])\s*=+\s*//\s*\n')
        self.function_pattern = re.compile(r'([a-zA-Z0-9_]+)\s*\([^)]*\)\s*=>')
        self.input_pattern = re.compile(r'([a-zA-Z0-9_]+)\s*=\s*input\.')
        self.var_declaration_pattern = re.compile(r'(?:^|\n)var\s+([a-zA-Z0-9_]+(?:\[\s*\])?\s*=)')
        self.indented_var_pattern = re.compile(r'^\s+var\s+', re.MULTILINE)
        self.const_pattern = re.compile(r'(?:^|\n)const\s+([a-zA-Z0-9_]+(?:\[\s*\])?\s*=)')
        
        # Pattern for operators that might continue to the next line
        self.operators_pattern = re.compile(r'[\?\:\(\[\{]|\band\b|\bor\b|\+|\-|\*|\/|\=|\<|\>|,')
        
        # Patterns for checking naming conventions
        self.camel_case_pattern = re.compile(r'^[a-z][a-zA-Z0-9]*$')
        self.snake_case_pattern = re.compile(r'^[A-Z][A-Z0-9_]*$')
        self.prefixed_pattern = {
            "functions": re.compile(r'^f_[a-zA-Z0-9_]+$'),
            "inputs": re.compile(r'^i_[a-zA-Z0-9_]+$'),
            "variables": re.compile(r'^v_[a-zA-Z0-9_]+$'),
            "constants": re.compile(r'^c_[A-Z0-9_]+$')
        }
        
        # Set of valid section names from config
        self.valid_sections = set(self.config["rules"].get("required_sections", []))
        
        # Define the expected order of sections from config
        self.section_order = self.config["rules"].get("section_order", [])
        
        # Define allowed function placement sections
        self.function_placement_section = self.config["rules"].get("function_placement", {}).get("section", "FUNCTION DEFINITIONS")
        
        # Define allowed input placement sections
        self.input_placement_sections = self.config["rules"].get("input_placement", {}).get("sections", ["INPUT PARAMETERS"])
        
        # Define allowed variable declaration placement section
        self.var_declaration_section = self.config["rules"].get("variable_declaration_placement", {}).get("section", "VARIABLE DECLARATIONS")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config
        except Exception as e:
            print(f"{Fore.RED}Error loading configuration: {e}{Style.RESET_ALL}")
            return {
                "rules": {
                    "require_version_declaration": True,
                    "indented_variable_declaration": True,
                    "missing_line_continuation": True,
                    "required_sections": [],
                    "section_order": [],
                    "function_placement": {
                        "enforce": True,
                        "section": "FUNCTION DEFINITIONS"
                    },
                    "input_placement": {
                        "enforce": True,
                        "sections": ["INPUT PARAMETERS"]
                    },
                    "variable_declaration_placement": {
                        "enforce": True,
                        "section": "VARIABLE DECLARATIONS"
                    },
                    "naming_conventions": {
                        "functions": "camelCase",
                        "inputs": "camelCase",
                        "variables": "camelCase",
                        "constants": "SNAKE_CASE"
                    },
                    "tradingview_style": True
                },
                "file_extensions": [".pine", ".pinescript"],
                "ignore_patterns": ["**/vendor/**", "**/deprecated/**"]
            }
    
    def check_naming_convention(self, name: str, convention_type: str) -> bool:
        """Check if a name follows the specified naming convention."""
        convention = self.config["rules"].get("naming_conventions", {}).get(convention_type, "")
        
        if convention == "camelCase":
            return bool(self.camel_case_pattern.match(name))
        elif convention == "SNAKE_CASE":
            return bool(self.snake_case_pattern.match(name))
        elif convention.endswith("*") and convention_type in self.prefixed_pattern:
            # For prefix-based conventions (e.g., "f_*")
            return bool(self.prefixed_pattern[convention_type].match(name))
        
        return True  # If no convention is specified, consider it valid
    
    def get_severity(self, rule_name: str) -> str:
        """Get the severity level for a rule."""
        for level, rules in self.config.get("severity_levels", {}).items():
            if rule_name in rules:
                return level
        return "info"  # Default to info level
    
    def get_severity_color(self, rule_name: str) -> Tuple[str, str]:
        """Get the severity level and color for a rule."""
        severity = self.get_severity(rule_name)
        if severity == "error":
            return "ERROR", Fore.RED
        elif severity == "warning":
            return "WARNING", Fore.YELLOW
        else:
            return "INFO", Fore.BLUE

    def check_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Check a Pine Script file for linting issues."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            issues.append({
                'rule': 'file_read_error',
                'message': f"Could not read file: {str(e)}",
                'line': 0,
                'severity': 'error'
            })
            return issues
        
        # Check for version declaration
        if self.config['rules'].get('require_version_declaration', False):
            version_match = re.search(r'^//@version\s*=\s*\d+(\.\d+)?', content, re.MULTILINE)
            if not version_match:
                issues.append({
                    'rule': 'require_version_declaration',
                    'message': "Missing version declaration (e.g., //@version=6)",
                    'line': 1,
                    'severity': self.get_severity('require_version_declaration')
                })
        
        # Find sections in the file
        section_pattern = r'//\s*=+\s*([A-Z][A-Z\s]+[A-Z])\s*=+\s*//'
        sections = []
        for i, line in enumerate(lines):
            match = re.search(section_pattern, line)
            if match:
                section_name = match.group(1).strip()
                sections.append({
                    'name': section_name,
                    'line': i + 1,
                    'end_line': len(lines)  # Will be updated when we find the next section
                })
                
                # Update the end line of the previous section
                if len(sections) > 1:
                    sections[-2]['end_line'] = i
        
        # Check for required sections
        if self.config['rules'].get('required_sections'):
            required_sections = set(self.config['rules']['required_sections'])
            found_sections = set(section['name'] for section in sections)
            missing_sections = required_sections - found_sections
            
            for section_name in missing_sections:
                issues.append({
                    'rule': 'required_sections',
                    'message': f"Missing required section: {section_name}",
                    'line': 1,
                    'severity': 'warning'
                })
        
        # Check section order
        if self.config['rules'].get('section_order') and len(sections) > 1:
            expected_order = self.config['rules']['section_order']
            for i in range(len(sections) - 1):
                current_section = sections[i]['name']
                next_section = sections[i + 1]['name']
                
                if current_section in expected_order and next_section in expected_order:
                    current_idx = expected_order.index(current_section)
                    next_idx = expected_order.index(next_section)
                    
                    if current_idx > next_idx:
                        issues.append({
                            'rule': 'section_order',
                            'message': f"Section '{next_section}' should come before '{current_section}'",
                            'line': sections[i + 1]['line'],
                            'severity': self.get_severity('section_order')
                        })
        
        # Find the VARIABLE DECLARATIONS section
        var_section = None
        for section in sections:
            if section['name'] == 'VARIABLE DECLARATIONS':
                var_section = section
                break
        
        # Check for variable declarations outside the VARIABLE DECLARATIONS section
        if var_section and self.config['rules'].get('variable_declaration_placement', {}).get('enforce', False):
            # Look for variable declarations at the top of the file (before any section)
            top_var_pattern = r'^var\s+\w+\s+\w+\s*=.*$'
            for i, line in enumerate(lines):
                # Skip if we're already in a section
                if any(section['line'] - 1 <= i <= section['end_line'] - 1 for section in sections if section['name'] == 'VARIABLE DECLARATIONS'):
                    continue
                
                # Check if this is a variable declaration
                if re.match(top_var_pattern, line.strip()):
                    issues.append({
                        'rule': 'variable_declaration_placement',
                        'message': f"Variable declaration should be in the VARIABLE DECLARATIONS section",
                        'line': i + 1,
                        'severity': self.get_severity('variable_declaration_placement')
                    })
            
            # Look for variable declarations in other sections
            var_pattern = r'^\s*var\s+\w+\s+\w+\s*=.*$'
            for section in sections:
                if section['name'] != 'VARIABLE DECLARATIONS':
                    for i in range(section['line'], section['end_line']):
                        if i - 1 < len(lines) and re.match(var_pattern, lines[i - 1].strip()):
                            issues.append({
                                'rule': 'variable_declaration_placement',
                                'message': f"Variable declaration should be in the VARIABLE DECLARATIONS section, not in {section['name']}",
                                'line': i,
                                'severity': self.get_severity('variable_declaration_placement')
                            })
        
        # Check for function definitions outside the FUNCTION DEFINITIONS section
        if self.config['rules'].get('function_placement', {}).get('enforce', False):
            function_section = None
            for section in sections:
                if section['name'] == self.config['rules']['function_placement']['section']:
                    function_section = section
                    break
            
            if function_section:
                # Look for function definitions outside the FUNCTION DEFINITIONS section
                func_pattern = r'^\s*(\w+)\s*\(\s*\)\s*=>\s*'
                for i, line in enumerate(lines):
                    if i + 1 < function_section['line'] or i + 1 > function_section['end_line']:
                        match = re.match(func_pattern, line)
                        if match:
                            issues.append({
                                'rule': 'function_placement',
                                'message': f"Function '{match.group(1)}' should be defined in the {self.config['rules']['function_placement']['section']} section",
                                'line': i + 1,
                                'severity': self.get_severity('function_placement')
                            })
        
        # Check for input declarations outside the INPUT PARAMETERS section
        if self.config['rules'].get('input_placement', {}).get('enforce', False):
            input_sections = []
            for section in sections:
                if section['name'] in self.config['rules']['input_placement']['sections']:
                    input_sections.append(section)
            
            if input_sections:
                # Look for input declarations outside the allowed sections
                input_pattern = r'^\s*\w+\s*=\s*input\.'
                for i, line in enumerate(lines):
                    in_input_section = False
                    for section in input_sections:
                        if section['line'] <= i + 1 <= section['end_line']:
                            in_input_section = True
                            break
                    
                    if not in_input_section and re.match(input_pattern, line):
                        issues.append({
                            'rule': 'input_placement',
                            'message': f"Input declaration should be in one of the allowed input sections",
                            'line': i + 1,
                            'severity': self.get_severity('input_placement')
                        })
        
        # Check for indentation in variable declarations
        if self.config['rules'].get('indented_variable_declaration', False):
            var_pattern = r'^var\s+\w+\s+\w+\s*=.*$'
            for i, line in enumerate(lines):
                if re.match(var_pattern, line.strip()) and not line.startswith('var'):
                    issues.append({
                        'rule': 'indented_variable_declaration',
                        'message': "Variable declarations should not be indented",
                        'line': i + 1,
                        'severity': self.get_severity('indented_variable_declaration')
                    })
        
        # Check for missing line continuation
        if self.config['rules'].get('missing_line_continuation', False):
            operators = ['+', '-', '*', '/', '==', '!=', '>', '<', '>=', '<=', 'and', 'or', '?', ':']
            for i, line in enumerate(lines):
                stripped_line = line.strip()
                if any(stripped_line.endswith(op) for op in operators):
                    # Check if the next line is indented
                    if i + 1 < len(lines) and lines[i + 1].startswith(' '):
                        continue  # Properly continued
                    
                    issues.append({
                        'rule': 'missing_line_continuation',
                        'message': "Line ends with an operator but the next line is not indented",
                        'line': i + 1,
                        'severity': self.get_severity('missing_line_continuation')
                    })
        
        # Check naming conventions
        if self.config['rules'].get('naming_conventions'):
            # Check function names
            func_pattern = r'^\s*(\w+)\s*\(\s*\)\s*=>\s*'
            for i, line in enumerate(lines):
                match = re.match(func_pattern, line)
                if match:
                    func_name = match.group(1)
                    convention = self.config['rules']['naming_conventions'].get('functions')
                    if convention and not self.check_naming_convention(func_name, convention):
                        issues.append({
                            'rule': 'naming_conventions',
                            'message': f"Function name '{func_name}' does not follow {convention} convention",
                            'line': i + 1,
                            'severity': self.get_severity('naming_conventions')
                        })
            
            # Check variable names
            var_pattern = r'^\s*var\s+\w+\s+(\w+)\s*=.*$'
            for i, line in enumerate(lines):
                match = re.match(var_pattern, line)
                if match:
                    var_name = match.group(1)
                    convention = self.config['rules']['naming_conventions'].get('variables')
                    if convention and not self.check_naming_convention(var_name, convention):
                        issues.append({
                            'rule': 'naming_conventions',
                            'message': f"Variable name '{var_name}' does not follow {convention} convention",
                            'line': i + 1,
                            'severity': self.get_severity('naming_conventions')
                        })
            
            # Check input names
            input_pattern = r'^\s*(\w+)\s*=\s*input\.'
            for i, line in enumerate(lines):
                match = re.match(input_pattern, line)
                if match:
                    input_name = match.group(1)
                    convention = self.config['rules']['naming_conventions'].get('inputs')
                    if convention and not self.check_naming_convention(input_name, convention):
                        issues.append({
                            'rule': 'naming_conventions',
                            'message': f"Input name '{input_name}' does not follow {convention} convention",
                            'line': i + 1,
                            'severity': self.get_severity('naming_conventions')
                        })
        
        # Check for imports outside the IMPORTS section
        import_pattern = r'^import\s+[\w/]+.*$'
        import_section = None
        for section in sections:
            if section['name'] == 'IMPORTS':
                import_section = section
                break
        
        if import_section:
            # Look for imports outside the IMPORTS section
            for i, line in enumerate(lines):
                if i + 1 < import_section['line'] or i + 1 > import_section['end_line']:
                    if re.match(import_pattern, line.strip()):
                        issues.append({
                            'rule': 'import_placement',
                            'message': "Import statement should be in the IMPORTS section",
                            'line': i + 1,
                            'severity': 'error'
                        })
        
        return issues
    
    def lint_file(self, file_path: str, verbose: bool = False) -> bool:
        """Lint a single file and print issues."""
        if not os.path.exists(file_path):
            print(f"{Fore.RED}File not found: {file_path}{Style.RESET_ALL}")
            return False
        
        # Check file extension
        _, ext = os.path.splitext(file_path)
        if ext not in self.config.get("file_extensions", [".pine", ".pinescript"]):
            if verbose:
                print(f"{Fore.YELLOW}Skipping file with unsupported extension: {file_path}{Style.RESET_ALL}")
            return True
        
        # Check ignore patterns
        for pattern in self.config.get("ignore_patterns", []):
            if glob.fnmatch.fnmatch(file_path, pattern):
                if verbose:
                    print(f"{Fore.YELLOW}Ignoring file matching pattern '{pattern}': {file_path}{Style.RESET_ALL}")
                return True
        
        issues = self.check_file(file_path)
        
        if not issues:
            if verbose:
                print(f"{Fore.GREEN}✓ {file_path} - No issues found{Style.RESET_ALL}")
            return True
        
        print(f"\n{Fore.CYAN}File: {file_path}{Style.RESET_ALL}")
        
        for issue in issues:
            severity, color = self.get_severity_color(issue['rule'])
            print(f"{color}{severity}: {issue['message']} (line {issue['line']}){Style.RESET_ALL}")
        
        return False
    
    def lint_directory(self, directory: str, recursive: bool = True, verbose: bool = False) -> bool:
        """Lint all Pine Script files in a directory."""
        if not os.path.isdir(directory):
            print(f"{Fore.RED}Directory not found: {directory}{Style.RESET_ALL}")
            return False
        
        success = True
        for ext in self.config.get("file_extensions", [".pine", ".pinescript"]):
            if recursive:
                pattern = os.path.join(directory, f"**/*{ext}")
                files = glob.glob(pattern, recursive=True)
            else:
                pattern = os.path.join(directory, f"*{ext}")
                files = glob.glob(pattern)
            
            for file_path in files:
                # Skip files matching ignore patterns
                skip = False
                for ignore_pattern in self.config.get("ignore_patterns", []):
                    if glob.fnmatch.fnmatch(file_path, ignore_pattern):
                        if verbose:
                            print(f"{Fore.YELLOW}Ignoring file matching pattern '{ignore_pattern}': {file_path}{Style.RESET_ALL}")
                        skip = True
                        break
                
                if not skip and not self.lint_file(file_path, verbose):
                    success = False
        
        return success

def main():
    """Main entry point for the linter."""
    parser = argparse.ArgumentParser(description="Pine Script Linter")
    parser.add_argument("path", help="File or directory to lint")
    parser.add_argument("-c", "--config", help="Path to configuration file", default=DEFAULT_CONFIG_PATH)
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively lint directories")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    linter = PineLinter(args.config)
    
    if os.path.isfile(args.path):
        success = linter.lint_file(args.path, args.verbose)
    else:
        success = linter.lint_directory(args.path, args.recursive, args.verbose)
    
    if success:
        print(f"\n{Fore.GREEN}Linting completed successfully!{Style.RESET_ALL}")
        sys.exit(0)
    else:
        print(f"\n{Fore.RED}Linting completed with issues.{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main() 