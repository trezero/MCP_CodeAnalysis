#!/usr/bin/env python3
"""
Pine Script Fixer - Automatically fixes common issues in Pine Script files.
"""

import os
import re
import sys
import glob
import json
import argparse
from typing import List, Dict, Any, Tuple, Optional
from colorama import Fore, Style, init
import fnmatch

# Initialize colorama for cross-platform colored terminal output
init()

# Default configuration path
DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "pinescript", "config.json"
)

# Standard section headers
SECTION_HEADERS = [
    "// =================== METADATA =================== //",
    "// =================== INPUT GROUPS =================== //",
    "// =================== INPUT PARAMETERS =================== //",
    "// =================== VARIABLE DECLARATIONS =================== //",
    "// =================== FUNCTION DEFINITIONS =================== //",
    "// =================== MAIN CALCULATIONS =================== //",
    "// =================== VISUALIZATION =================== //",
    "// =================== ALERTS =================== //"
]

class PineFixer:
    """Pine Script fixer that automatically fixes common issues."""
    
    def __init__(self, config_path: str = DEFAULT_CONFIG_PATH):
        """Initialize the fixer."""
        self.config = self._load_config(config_path)
        self.section_pattern = re.compile(r'//\s*=+\s*([A-Z\s]+)\s*=+\s*//')
        self.function_pattern = re.compile(r'(?:export\s+)?(?:method\s+)?(?:\w+\s+)?(?:function\s+)?(\w+)\s*\([^)]*\)\s*=>\s*(?:.+?)(?=\n\n|\n\w|\n$|$)', re.DOTALL)
        self.version_pattern = re.compile(r'//\s*@version\s*=\s*(\d+)')
        self.input_pattern = re.compile(r'(?:export\s+)?(\w+)\s*=\s*input\..*?(?=\n\n|\n\w|\n$|$)', re.DOTALL)
        self.variable_pattern = re.compile(r'(?:var|varip)\s+(?:float|int|bool|string|color|label|line|box|array|table|matrix)?\s*(\w+)\s*=.*?(?=\n\n|\n\w|\n$|$)', re.DOTALL)
        self.all_var_pattern = re.compile(r'\b(var|varip)\s+(?:float|int|bool|string|color|label|line|box|array|table|matrix)?\s*(\w+)\s*=', re.DOTALL)
        
        # Patterns for checking naming conventions
        self.camel_case_pattern = re.compile(r'^[a-z][a-zA-Z0-9]*$')
        self.snake_case_pattern = re.compile(r'^[A-Z][A-Z0-9_]*$')
        self.prefixed_pattern = {
            "functions": re.compile(r'^f_[a-zA-Z0-9_]+$'),
            "inputs": re.compile(r'^i_[a-zA-Z0-9_]+$'),
            "variables": re.compile(r'^v_[a-zA-Z0-9_]+$'),
            "constants": re.compile(r'^c_[a-zA-Z0-9_]+$')
        }
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"{Fore.RED}Error loading configuration: {e}{Style.RESET_ALL}")
            # Return default configuration
            return {
                "rules": {
                    "require_version_declaration": True,
                    "required_sections": [
                        "METADATA", "INPUT GROUPS", "INPUT PARAMETERS", 
                        "VARIABLE DECLARATIONS", "FUNCTION DEFINITIONS", 
                        "MAIN CALCULATIONS", "VISUALIZATION", "ALERTS"
                    ],
                    "section_order": [
                        "METADATA", "INPUT GROUPS", "INPUT PARAMETERS", 
                        "VARIABLE DECLARATIONS", "FUNCTION DEFINITIONS", 
                        "MAIN CALCULATIONS", "VISUALIZATION", "ALERTS"
                    ],
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
                    "tradingview_style": True,
                    "indented_variable_declaration": False,
                    "missing_line_continuation": False,
                    "import_placement": {
                        "enforce": False
                    },
                    "line_continuation": {
                        "enforce": False
                    }
                },
                "file_extensions": [".pine", ".pinescript"],
                "severity_levels": {
                    "error": ["require_version_declaration", "function_placement"],
                    "warning": ["section_order", "input_placement", "variable_declaration_placement"],
                    "info": ["naming_conventions"]
                }
            }
    
    def to_camel_case(self, name: str) -> str:
        """Convert a name to camelCase."""
        # Handle prefixed names (e.g., f_calculate_average -> calculateAverage)
        if name.startswith(('f_', 'i_', 'v_')):
            name = name[2:]
        
        # Convert snake_case to camelCase
        parts = name.split('_')
        camel_case = parts[0].lower() + ''.join(part.capitalize() for part in parts[1:])
        
        return camel_case
    
    def to_snake_case(self, name: str) -> str:
        """Convert a name to SNAKE_CASE."""
        # Handle prefixed names (e.g., c_max_lookback -> MAX_LOOKBACK)
        if name.startswith('c_'):
            name = name[2:]
        
        # Convert to SNAKE_CASE
        return name.upper()
    
    def fix_naming_convention(self, name: str, convention_type: str) -> str:
        """Fix a name to follow the specified naming convention."""
        convention = self.config["rules"].get("naming_conventions", {}).get(convention_type, "")
        
        if convention == "camelCase" and not self.camel_case_pattern.match(name):
            return self.to_camel_case(name)
        elif convention == "SNAKE_CASE" and not self.snake_case_pattern.match(name):
            return self.to_snake_case(name)
        elif convention.endswith("*") and not self.prefixed_pattern.get(convention_type, re.compile(".*")).match(name):
            # For prefix-based conventions (e.g., "f_*")
            prefix = convention[:-1]  # Remove the * from the end
            if not name.startswith(prefix):
                return prefix + name
        
        return name  # If already follows convention or no convention specified
    
    def fix_file(self, file_path: str, backup: bool = True, verbose: bool = False) -> bool:
        """Fix a Pine Script file according to the configured rules."""
        if not os.path.isfile(file_path):
            print(f"Error: File {file_path} does not exist")
            return False
        
        if not any(file_path.endswith(ext) for ext in self.config["file_extensions"]):
            if verbose:
                print(f"Skipping {file_path} (not a Pine Script file)")
            return False
        
        # Check if file should be ignored
        for pattern in self.config["ignore_patterns"]:
            if fnmatch.fnmatch(file_path, pattern):
                if verbose:
                    print(f"Skipping {file_path} (matches ignore pattern {pattern})")
                return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                original_content = content
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return False
        
        # Create backup if requested
        if backup:
            backup_path = f"{file_path}.bak"
            try:
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                if verbose:
                    print(f"Created backup at {backup_path}")
            except Exception as e:
                print(f"Error creating backup {backup_path}: {e}")
                return False
        
        # Add version declaration if missing
        if self.config["rules"].get("require_version_declaration", False):
            version_match = re.search(r'^//@version\s*=\s*\d+(\.\d+)?', content, re.MULTILINE)
            if not version_match:
                content = f"//@version=6\n{content}"
                if verbose:
                    print(f"Added version declaration to {file_path}")
        
        # Fix indented variable declarations
        if self.config["rules"].get("indented_variable_declaration", False):
            content = re.sub(r'^\s+(var\s+\w+\s+\w+\s*=.*$)', r'\1', content, flags=re.MULTILINE)
        
        # Find sections in the file
        section_pattern = r'//\s*=+\s*([A-Z][A-Z\s]+[A-Z])\s*=+\s*//'
        sections = []
            lines = content.split('\n')
        
        for i, line in enumerate(lines):
            match = re.search(section_pattern, line)
            if match:
                section_name = match.group(1).strip()
                sections.append({
                    'name': section_name,
                    'line': i,
                    'end_line': len(lines) - 1  # Will be updated when we find the next section
                })
                
                # Update the end line of the previous section
                if len(sections) > 1:
                    sections[-2]['end_line'] = i - 1
        
        # Add missing required sections
        if self.config["rules"].get("required_sections"):
            required_sections = self.config["rules"]["required_sections"]
            found_sections = [s["name"] for s in sections]
            
            # Get the expected order of sections
            section_order = self.config["rules"].get("section_order", required_sections)
            
            # Add missing sections in the correct order
            for section in section_order:
                if section not in found_sections:
                    # Find where to insert the section
                    insert_index = len(lines)
                    
                    # If there are sections after this one in the order, insert before them
                    for existing_section in sections:
                        if existing_section["name"] in section_order and section_order.index(section) < section_order.index(existing_section["name"]):
                            insert_index = existing_section["line"]
                            break
                    
                    # Insert the section header
                    section_header = f"\n// =================== {section} =================== //\n"
                    lines.insert(insert_index, section_header)
                    
                    # Update section positions
                    for s in sections:
                        if s["line"] >= insert_index:
                            s["line"] += 2
                            s["end_line"] += 2
                    
                    # Add the new section to our list
                    new_section = {
                        "name": section,
                        "line": insert_index,
                        "end_line": insert_index + 1
                    }
                    
                    # Insert in the correct position in our sections list
                    insert_pos = 0
                    for i, s in enumerate(sections):
                        if s["line"] > new_section["line"]:
                            insert_pos = i
                            break
                        insert_pos = i + 1
                    
                    sections.insert(insert_pos, new_section)
                    
                    if verbose:
                        print(f"Added missing section: {section}")
        
        # Move variable declarations to the VARIABLE DECLARATIONS section
        if self.config["rules"].get("variable_declaration_placement", {}).get("enforce", False):
            var_section = None
            for section in sections:
                if section["name"] == "VARIABLE DECLARATIONS":
                    var_section = section
                    break
            
            if var_section:
                # Find variable declarations at the top of the file (before any section)
                var_pattern = r'^var\s+\w+\s+\w+\s*=.*$'
                var_declarations = []
                lines_to_remove = []
                
                # First pass: collect variable declarations at the top
                for i, line in enumerate(lines):
                    # Skip if we're already in a section
                    if any(section["line"] <= i <= section["end_line"] for section in sections if section["name"] == "VARIABLE DECLARATIONS"):
                    continue
                
                    # Check if this is a variable declaration
                    if re.match(var_pattern, line.strip()):
                        var_declarations.append(line)
                        lines_to_remove.append(i)
                
                # Second pass: remove the declarations from their original positions
                for i in sorted(lines_to_remove, reverse=True):
                    del lines[i]
                    
                    # Update section positions
                    for section in sections:
                        if section["line"] > i:
                            section["line"] -= 1
                        if section["end_line"] > i:
                            section["end_line"] -= 1
                
                # Insert the declarations at the end of the VARIABLE DECLARATIONS section
                insert_pos = var_section["end_line"]
                for decl in var_declarations:
                    lines.insert(insert_pos, decl)
                    insert_pos += 1
                    
                    # Update section positions
                    for section in sections:
                        if section["line"] > insert_pos - 1:
                            section["line"] += 1
                        if section["end_line"] >= insert_pos - 1:
                            section["end_line"] += 1
        
        # Move import statements to the IMPORTS section
        if self.config["rules"].get("import_placement", {}).get("enforce", False):
            import_section = None
            for section in sections:
                if section["name"] == "IMPORTS":
                    import_section = section
                    break
            
            if import_section:
                # Find import statements outside the IMPORTS section
                import_pattern = r'^import\s+[\w/]+.*$'
                import_statements = []
                lines_to_remove = []
                
                # First pass: collect import statements outside the IMPORTS section
                for i, line in enumerate(lines):
                    # Skip if we're already in the IMPORTS section
                    if import_section["line"] <= i + 1 <= import_section["end_line"]:
                        continue
                    
                    # Check if this is an import statement
                    if re.match(import_pattern, line.strip()):
                        import_statements.append(line)
                        lines_to_remove.append(i)
                
                # Second pass: remove the import statements from their original positions
                for i in sorted(lines_to_remove, reverse=True):
                    del lines[i]
                    
                    # Update section positions
                    for section in sections:
                        if section["line"] > i + 1:
                            section["line"] -= 1
                        if section["end_line"] > i + 1:
                            section["end_line"] -= 1
                
                # Insert the import statements at the end of the IMPORTS section
                insert_pos = import_section["end_line"] - 1
                for stmt in import_statements:
                    lines.insert(insert_pos, stmt)
                    insert_pos += 1
                    
                    # Update section positions
                    for section in sections:
                        if section["line"] > insert_pos:
                            section["line"] += 1
                        if section["end_line"] >= insert_pos:
                            section["end_line"] += 1
        
        # Fix line continuation issues
        if self.config["rules"].get("line_continuation", {}).get("enforce", False):
            operators = ['+', '-', '*', '/', '==', '!=', '>', '<', '>=', '<=', 'and', 'or', '?', ':']
            i = 0
            while i < len(lines) - 1:
                line = lines[i]
                stripped_line = line.strip()
                
                # Check if line ends with an operator
                if any(stripped_line.endswith(op) for op in operators):
                    next_line = lines[i + 1]
                    
                    # If the next line is not indented, add indentation
                    if next_line and not next_line.startswith(' ') and not next_line.startswith('\t'):
                        lines[i + 1] = '    ' + next_line
                if verbose:
                            print(f"Fixed line continuation at line {i + 1}")
                
                i += 1
        
        # Fix function placement
        if self.config["rules"].get("function_placement", {}).get("enforce", False):
            function_section = None
            for section in sections:
                if section["name"] == self.config["rules"]["function_placement"]["section"]:
                    function_section = section
                    break
            
            if function_section:
                # Find function definitions outside the FUNCTION DEFINITIONS section
                func_pattern = r'^\s*(\w+)\s*\(\s*\)\s*=>\s*'
                func_blocks = []
                lines_to_remove = []
                
                # First pass: collect function blocks
                i = 0
                while i < len(lines):
                    # Skip if we're in the function section
                    if function_section["line"] <= i <= function_section["end_line"]:
                        i += 1
                        continue
                    
                    line = lines[i]
                    match = re.match(func_pattern, line)
                    
                    if match:
                        # Found a function definition
                        func_name = match.group(1)
                        func_block = [line]
                        lines_to_remove.append(i)
                        
                        # Collect the function body
                        j = i + 1
                        indent_level = len(line) - len(line.lstrip())
                        
                        while j < len(lines):
                            next_line = lines[j]
                            
                            # If we hit a blank line or a line with less indentation, we're done
                            if not next_line.strip() or (next_line.strip() and len(next_line) - len(next_line.lstrip()) <= indent_level):
                                break
                            
                            func_block.append(next_line)
                            lines_to_remove.append(j)
                            j += 1
                        
                        func_blocks.append(func_block)
                        i = j
                        else:
                        i += 1
                
                # Second pass: remove the function blocks from their original positions
                for i in sorted(lines_to_remove, reverse=True):
                    del lines[i]
                    
                    # Update section positions
                    for section in sections:
                        if section["line"] > i:
                            section["line"] -= 1
                        if section["end_line"] >= i:
                            section["end_line"] -= 1
                
                # Third pass: add the function blocks to the FUNCTION DEFINITIONS section
                if func_blocks:
                    # Find the right position to insert (after the section header)
                    insert_pos = function_section["line"] + 1
                    
                    # Insert the function blocks
                    for block in func_blocks:
                        for i, line in enumerate(block):
                            lines.insert(insert_pos + i, line)
                        insert_pos += len(block)
                        # Add a blank line between functions
                        lines.insert(insert_pos, '')
                        insert_pos += 1
                    
                    # Update section positions
                    total_lines_added = sum(len(block) + 1 for block in func_blocks)
                    for section in sections:
                        if section["line"] > function_section["line"]:
                            section["line"] += total_lines_added
                        if section["end_line"] >= function_section["line"]:
                            section["end_line"] += total_lines_added
                    
                    if verbose:
                        print(f"Moved {len(func_blocks)} function definitions to the {self.config['rules']['function_placement']['section']} section")
        
        # Fix input placement
        if self.config["rules"].get("input_placement", {}).get("enforce", False):
            input_sections = []
            for section in sections:
                if section["name"] in self.config["rules"]["input_placement"]["sections"]:
                    input_sections.append(section)
            
            if input_sections:
                # Use the first input section
                input_section = input_sections[0]
                
                # Find input declarations outside the allowed sections
                input_pattern = r'^\s*(\w+)\s*=\s*input\.'
                input_lines = []
                lines_to_remove = []
                
                # First pass: collect input declarations
                for i, line in enumerate(lines):
                    # Skip if we're in an input section
                    in_input_section = False
                    for section in input_sections:
                        if section["line"] <= i <= section["end_line"]:
                            in_input_section = True
                            break
                    
                    if in_input_section:
                        continue
                    
                    match = re.match(input_pattern, line)
                    if match:
                        input_lines.append(line)
                        lines_to_remove.append(i)
                
                # Second pass: remove the input declarations from their original positions
                for i in sorted(lines_to_remove, reverse=True):
                    del lines[i]
                    
                    # Update section positions
                    for section in sections:
                        if section["line"] > i:
                            section["line"] -= 1
                        if section["end_line"] >= i:
                            section["end_line"] -= 1
                
                # Third pass: add the input declarations to the input section
                if input_lines:
                    # Find the right position to insert (after the section header)
                    insert_pos = input_section["line"] + 1
                    
                    # Insert the input declarations
                    for i, line in enumerate(input_lines):
                        lines.insert(insert_pos + i, line)
                    
                    # Update section positions
        for section in sections:
                        if section["line"] > input_section["line"]:
                            section["line"] += len(input_lines)
                        if section["end_line"] >= input_section["line"]:
                            section["end_line"] += len(input_lines)
                    
                    if verbose:
                        print(f"Moved {len(input_lines)} input declarations to the {input_section['name']} section")
        
        # Fix naming conventions
        if self.config["rules"].get("naming_conventions"):
            # Fix function names
            def replace_function(match):
                func_name = match.group(1)
                fixed_name = self.fix_naming_convention(func_name, "functions")
                if fixed_name != func_name:
                    if verbose:
                        print(f"Renamed function: {func_name} -> {fixed_name}")
                    return match.group(0).replace(func_name, fixed_name)
                return match.group(0)
            
            content = '\n'.join(lines)
            content = re.sub(r'(\w+)\s*\(\s*\)\s*=>\s*', replace_function, content)
            
            # Fix input names
            def replace_input(match):
                input_name = match.group(1)
                fixed_name = self.fix_naming_convention(input_name, "inputs")
                if fixed_name != input_name:
                    if verbose:
                        print(f"Renamed input: {input_name} -> {fixed_name}")
                    return match.group(0).replace(input_name, fixed_name)
                return match.group(0)
            
            content = re.sub(r'(\w+)\s*=\s*input\.', replace_input, content)
            
            # Fix variable names
            def replace_variable(match):
                var_name = match.group(1)
                fixed_name = self.fix_naming_convention(var_name, "variables")
                if fixed_name != var_name:
                    if verbose:
                        print(f"Renamed variable: {var_name} -> {fixed_name}")
                    return match.group(0).replace(var_name, fixed_name)
                return match.group(0)
            
            content = re.sub(r'var\s+\w+\s+(\w+)\s*=', replace_variable, content)
            
            # Fix constant names
            def replace_constant(match):
                const_name = match.group(1)
                fixed_name = self.fix_naming_convention(const_name, "constants")
                if fixed_name != const_name:
                if verbose:
                        print(f"Renamed constant: {const_name} -> {fixed_name}")
                    return match.group(0).replace(const_name, fixed_name)
                return match.group(0)
            
            content = re.sub(r'const\s+\w+\s+(\w+)\s*=', replace_constant, content)
        else:
            content = '\n'.join(lines)
        
        # Write the fixed content back to the file
        if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                if verbose:
                    print(f"Fixed {file_path}")
                return True
            except Exception as e:
                print(f"Error writing to {file_path}: {e}")
                return False
        else:
            if verbose:
                print(f"No changes needed for {file_path}")
            return True
    
    def fix_directory(self, directory: str, recursive: bool = True, backup: bool = True, verbose: bool = False) -> bool:
        """Fix all Pine Script files in a directory."""
        if not os.path.isdir(directory):
            print(f"{Fore.RED}Directory not found: {directory}{Style.RESET_ALL}")
            return False
        
        success = True
        for ext in [".pine", ".pinescript"]:
            if recursive:
                pattern = os.path.join(directory, f"**/*{ext}")
                files = glob.glob(pattern, recursive=True)
            else:
                pattern = os.path.join(directory, f"*{ext}")
                files = glob.glob(pattern)
            
            for file_path in files:
                if not self.fix_file(file_path, backup, verbose):
                    success = False
        
        return success

def main():
    """Main entry point for the fixer."""
    parser = argparse.ArgumentParser(description="Pine Script Fixer")
    parser.add_argument("path", help="File or directory to fix")
    parser.add_argument("-c", "--config", help="Path to configuration file", default=DEFAULT_CONFIG_PATH)
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively fix directories")
    parser.add_argument("-n", "--no-backup", action="store_true", help="Don't create backup files")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    fixer = PineFixer(args.config)
    
    if os.path.isfile(args.path):
        success = fixer.fix_file(args.path, not args.no_backup, args.verbose)
    else:
        success = fixer.fix_directory(args.path, args.recursive, not args.no_backup, args.verbose)
    
    if success:
        print(f"\n{Fore.GREEN}Fixing completed successfully!{Style.RESET_ALL}")
        sys.exit(0)
    else:
        print(f"\n{Fore.RED}Fixing completed with issues.{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main() 