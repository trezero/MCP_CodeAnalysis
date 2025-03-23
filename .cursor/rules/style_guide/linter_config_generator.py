#!/usr/bin/env python3

"""Style Guide Linter Configuration Generator

This script generates configuration files for various linters and formatters
based on the project's style guide.

Maturity: beta

Why:
- Manually configuring linters is error-prone and time-consuming
- This ensures consistent configuration across the project
- Centralizes style decisions in one place
- Makes it easier to update style rules project-wide
"""

import argparse
import json
import os
import yaml
from pathlib import Path

# Define base configurations
ESLINT_BASE = {
    "extends": ["eslint:recommended", "plugin:@typescript-eslint/recommended"],
    "parser": "@typescript-eslint/parser",
    "plugins": ["@typescript-eslint"],
    "rules": {
        "indent": ["error", 2],
        "quotes": ["error", "single"],
        "semi": ["error", "always"],
        "no-unused-vars": ["warn", {"argsIgnorePattern": "^_"}],
        "max-len": ["warn", {"code": 100}],
        "eqeqeq": ["error", "always"],
        "curly": ["error", "all"],
        "brace-style": ["error", "1tbs"]
    }
}

PRETTIER_BASE = {
    "singleQuote": True,
    "trailingComma": "es5",
    "tabWidth": 2,
    "semi": True,
    "printWidth": 100,
    "bracketSpacing": True,
    "arrowParens": "always"
}

PYLINT_BASE = {
    "disable": [
        "missing-docstring",
        "invalid-name"
    ],
    "max-line-length": 100,
    "good-names": ["i", "j", "k", "ex", "Run", "_", "id", "db"],
    "ignore-patterns": ["^\\.#"],
    "output-format": "colorized"
}

def generate_eslint_config(output_path):
    """Generate ESLint configuration file."""
    with open(output_path, 'w') as f:
        json.dump(ESLINT_BASE, f, indent=2)
    print(f"ESLint config generated at {output_path}")

def generate_prettier_config(output_path):
    """Generate Prettier configuration file."""
    with open(output_path, 'w') as f:
        json.dump(PRETTIER_BASE, f, indent=2)
    print(f"Prettier config generated at {output_path}")

def generate_pylint_config(output_path):
    """Generate Pylint configuration file."""
    with open(output_path, 'w') as f:
        f.write("[MASTER]\n")
        f.write("disable=" + ",".join(PYLINT_BASE["disable"]) + "\n")
        f.write(f"max-line-length={PYLINT_BASE['max-line-length']}\n")
        f.write("good-names=" + ",".join(PYLINT_BASE["good-names"]) + "\n")
        f.write(f"ignore-patterns={PYLINT_BASE['ignore-patterns'][0]}\n")
        f.write(f"output-format={PYLINT_BASE['output-format']}\n")
    print(f"Pylint config generated at {output_path}")

def generate_editorconfig(output_path):
    """Generate EditorConfig file."""
    content = """# EditorConfig is awesome: https://EditorConfig.org

# top-most EditorConfig file
root = true

# Unix-style newlines with a newline ending every file
[*]
end_of_line = lf
insert_final_newline = true
charset = utf-8
trim_trailing_whitespace = true
indent_style = space
indent_size = 2

# 4 space indentation for Python
[*.py]
indent_size = 4

# Tab indentation for Makefiles
[Makefile]
indent_style = tab

# Markdown files
[*.md]
trim_trailing_whitespace = false
"""
    with open(output_path, 'w') as f:
        f.write(content)
    print(f"EditorConfig generated at {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate linter configurations")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    parser.add_argument("--configs", default="all", 
                        choices=["all", "eslint", "prettier", "pylint", "editorconfig"],
                        help="Which configurations to generate")
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.configs in ["all", "eslint"]:
        generate_eslint_config(output_dir / ".eslintrc.json")
    
    if args.configs in ["all", "prettier"]:
        generate_prettier_config(output_dir / ".prettierrc.json")
    
    if args.configs in ["all", "pylint"]:
        generate_pylint_config(output_dir / ".pylintrc")
    
    if args.configs in ["all", "editorconfig"]:
        generate_editorconfig(output_dir / ".editorconfig")

if __name__ == "__main__":
    main() 