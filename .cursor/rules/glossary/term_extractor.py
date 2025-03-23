#!/usr/bin/env python3

"""Glossary Term Extractor

This script extracts domain-specific terms from the codebase and
generates a glossary entry template for each term.

Maturity: beta

Why:
- Maintaining a glossary manually is time-consuming
- This script automates the initial extraction of terms
- Helps ensure consistent terminology across the codebase
- Makes it easier to build and maintain a comprehensive glossary
"""

import argparse
import os
import re
from pathlib import Path
import json
import yaml
from collections import Counter

def extract_terms(file_path, patterns, existing_terms=None):
    """Extract terms from a file based on patterns."""
    if existing_terms is None:
        existing_terms = set()
    
    terms = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            for pattern_name, pattern in patterns.items():
                matches = re.finditer(pattern, content)
                for match in matches:
                    term = match.group(1)
                    
                    # Skip common words, single characters, and numbers
                    if (len(term) <= 1 or term.lower() in COMMON_WORDS or 
                            term.isdigit() or term in existing_terms):
                        continue
                    
                    # Get context (the line containing the term)
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_end = content.find('\n', match.end())
                    if line_end == -1:
                        line_end = len(content)
                    
                    context = content[line_start:line_end].strip()
                    
                    if term not in terms:
                        terms[term] = {
                            'type': pattern_name,
                            'occurrences': 1,
                            'contexts': [context],
                            'files': [str(file_path)]
                        }
                    else:
                        terms[term]['occurrences'] += 1
                        if context not in terms[term]['contexts']:
                            terms[term]['contexts'].append(context)
                        if str(file_path) not in terms[term]['files']:
                            terms[term]['files'].append(str(file_path))
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return terms

def generate_glossary_entry(term, data):
    """Generate a glossary entry template for a term."""
    return {
        "term": term,
        "type": data['type'],
        "definition": "",
        "context": "Found in: " + ", ".join(data['files']),
        "examples": data['contexts'][:3],  # Limit to 3 examples
        "related_terms": [],
        "occurrences": data['occurrences']
    }

# Common words to exclude
COMMON_WORDS = {
    'the', 'and', 'for', 'with', 'this', 'that', 'from', 'not', 'have', 'has',
    'get', 'set', 'new', 'function', 'class', 'var', 'let', 'const', 'return',
    'true', 'false', 'null', 'undefined', 'import', 'export', 'default', 'as',
    'if', 'else', 'while', 'for', 'do', 'switch', 'case', 'break', 'continue',
    'try', 'catch', 'finally', 'throw', 'async', 'await', 'public', 'private',
    'protected', 'static', 'final', 'void', 'int', 'string', 'boolean', 'number',
    'object', 'array', 'map', 'set', 'date', 'error', 'promise', 'then', 'of'
}

def main():
    parser = argparse.ArgumentParser(description="Extract domain-specific terms")
    parser.add_argument("--source-dir", default=".", help="Source directory")
    parser.add_argument("--output", default="glossary_terms.json", help="Output file")
    parser.add_argument("--format", choices=["json", "yaml", "markdown"], default="json", 
                        help="Output format (default: json)")
    parser.add_argument("--min-occurrences", type=int, default=2, 
                        help="Minimum occurrences to include a term (default: 2)")
    parser.add_argument("--existing-glossary", help="Path to existing glossary file to update")
    args = parser.parse_args()
    
    # Patterns to match domain-specific terms
    patterns = {
        "class": r'class\s+(\w+)',
        "function": r'function\s+(\w+)',
        "method": r'(\w+)\s*\([^)]*\)\s*{',
        "constant": r'const\s+(\w+)\s*=',
        "variable": r'let\s+(\w+)\s*=',
        "interface": r'interface\s+(\w+)',
        "type": r'type\s+(\w+)\s*=',
        "enum": r'enum\s+(\w+)',
        "component": r'<(\w+)[^>]*>',
        "module": r'import.*from\s+[\'"](.+?)[\'"]',
        "python_class": r'class\s+(\w+)',
        "python_function": r'def\s+(\w+)',
        "python_variable": r'(\w+)\s*=',
        "pine_function": r'(\w+)\s*\([^)]*\)\s*=>'
    }
    
    existing_terms = set()
    existing_glossary = {}
    
    # Load existing glossary if provided
    if args.existing_glossary and os.path.exists(args.existing_glossary):
        try:
            with open(args.existing_glossary, 'r') as f:
                if args.existing_glossary.endswith('.json'):
                    existing_glossary = json.load(f)
                elif args.existing_glossary.endswith(('.yaml', '.yml')):
                    existing_glossary = yaml.safe_load(f)
                
                if isinstance(existing_glossary, dict) and 'terms' in existing_glossary:
                    existing_terms = {entry['term'] for entry in existing_glossary['terms']}
                elif isinstance(existing_glossary, list):
                    existing_terms = {entry['term'] for entry in existing_glossary if 'term' in entry}
        except Exception as e:
            print(f"Error loading existing glossary: {e}")
    
    all_terms = {}
    
    # Walk through the source directory
    for root, _, files in os.walk(args.source_dir):
        for file in files:
            if file.endswith(('.js', '.jsx', '.ts', '.tsx', '.py', '.pine', '.pinescript')):
                file_path = os.path.join(root, file)
                terms = extract_terms(file_path, patterns, existing_terms)
                
                # Merge terms
                for term, data in terms.items():
                    if term in all_terms:
                        all_terms[term]['occurrences'] += data['occurrences']
                        all_terms[term]['contexts'].extend(data['contexts'])
                        all_terms[term]['files'].extend(data['files'])
                        # Remove duplicates
                        all_terms[term]['contexts'] = list(dict.fromkeys(all_terms[term]['contexts']))
                        all_terms[term]['files'] = list(dict.fromkeys(all_terms[term]['files']))
                    else:
                        all_terms[term] = data
    
    # Filter terms by minimum occurrences
    filtered_terms = {term: data for term, data in all_terms.items() 
                     if data['occurrences'] >= args.min_occurrences}
    
    # Generate glossary entries
    glossary_entries = [generate_glossary_entry(term, data) 
                        for term, data in filtered_terms.items()]
    
    # Sort by occurrences (descending)
    glossary_entries.sort(key=lambda x: x['occurrences'], reverse=True)
    
    # Prepare output
    output = {
        "metadata": {
            "total_terms": len(glossary_entries),
            "extraction_date": Path(args.output).stat().st_mtime if Path(args.output).exists() else None,
            "source_directory": args.source_dir
        },
        "terms": glossary_entries
    }
    
    # Save to file
    with open(args.output, 'w') as f:
        if args.format == 'json':
            json.dump(output, f, indent=2)
        elif args.format == 'yaml':
            yaml.dump(output, f, sort_keys=False)
        elif args.format == 'markdown':
            f.write("# Glossary of Terms\n\n")
            f.write(f"*Generated from {args.source_dir}*\n\n")
            f.write(f"*Total terms: {len(glossary_entries)}*\n\n")
            
            for entry in glossary_entries:
                f.write(f"## {entry['term']}\n\n")
                f.write(f"**Type**: {entry['type']}\n\n")
                f.write(f"**Definition**: *To be filled*\n\n")
                f.write(f"**Context**: {entry['context']}\n\n")
                if entry['examples']:
                    f.write("**Examples**:\n\n")
                    for example in entry['examples']:
                        f.write(f"```\n{example}\n```\n\n")
                f.write(f"**Occurrences**: {entry['occurrences']}\n\n")
                f.write("---\n\n")
    
    print(f"Extracted {len(glossary_entries)} terms to {args.output}")
    print(f"Top 10 terms by occurrence:")
    for entry in glossary_entries[:10]:
        print(f"  - {entry['term']} ({entry['occurrences']} occurrences)")

if __name__ == "__main__":
    main() 