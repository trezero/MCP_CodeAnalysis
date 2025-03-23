#!/usr/bin/env python3

"""Glossary Generator

This script generates a formatted glossary from term definitions,
creating HTML, Markdown, or JSON output.

Maturity: beta

Why:
- A well-formatted glossary improves documentation accessibility
- Consistent formatting makes the glossary easier to navigate
- Multiple output formats support different use cases
- Automated generation ensures the glossary stays up-to-date
"""

import argparse
import json
import os
import re
from pathlib import Path
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader

class GlossaryGenerator:
    """Generates formatted glossary from term definitions."""
    
    def __init__(self, template_dir=None):
        if template_dir is None:
            # Use default templates directory relative to this script
            template_dir = Path(__file__).parent / "templates"
        
        self.template_dir = Path(template_dir)
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
    
    def load_glossary(self, input_file):
        """Load glossary data from a file."""
        input_path = Path(input_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Glossary file not found: {input_file}")
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                if input_path.suffix == '.json':
                    data = json.load(f)
                elif input_path.suffix in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported file format: {input_path.suffix}")
            
            # Normalize data structure
            if isinstance(data, dict) and 'terms' in data:
                terms = data['terms']
                metadata = data.get('metadata', {})
            elif isinstance(data, list):
                terms = data
                metadata = {}
            else:
                raise ValueError("Invalid glossary format")
            
            return {
                'metadata': metadata,
                'terms': terms
            }
        
        except Exception as e:
            raise Exception(f"Error loading glossary: {e}")
    
    def generate_html(self, glossary_data, output_file):
        """Generate HTML glossary."""
        template = self.env.get_template('glossary.html.j2')
        
        # Ensure template directory exists, create default if not
        if not self.template_dir.exists():
            self.template_dir.mkdir(parents=True)
            default_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ metadata.title|default('Glossary of Terms') }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        h2 {
            color: #444;
            margin-top: 30px;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
        }
        .term-type {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .term-definition {
            margin-bottom: 15px;
        }
        .term-examples {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            white-space: pre-wrap;
        }
        .term-context {
            font-style: italic;
            color: #666;
        }
        .term-related {
            margin-top: 10px;
        }
        .term-related a {
            margin-right: 10px;
            color: #0066cc;
            text-decoration: none;
        }
        .term-related a:hover {
            text-decoration: underline;
        }
        .alphabet-nav {
            margin: 20px 0;
            text-align: center;
        }
        .alphabet-nav a {
            display: inline-block;
            margin: 0 5px;
            color: #0066cc;
            text-decoration: none;
        }
        .alphabet-nav a:hover {
            text-decoration: underline;
        }
        .back-to-top {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #333;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <h1>{{ metadata.title|default('Glossary of Terms') }}</h1>
    
    {% if metadata %}
    <div class="metadata">
        <p>Total terms: {{ terms|length }}</p>
        {% if metadata.extraction_date %}
        <p>Last updated: {{ metadata.extraction_date }}</p>
        {% endif %}
        {% if metadata.source_directory %}
        <p>Source: {{ metadata.source_directory }}</p>
        {% endif %}
    </div>
    {% endif %}
    
    <div class="alphabet-nav" id="top">
        {% for letter in alphabet %}
        <a href="#{{ letter }}">{{ letter }}</a>
        {% endfor %}
    </div>
    
    {% for letter, letter_terms in terms_by_letter.items() %}
    <h2 id="{{ letter }}">{{ letter }}</h2>
    {% for term in letter_terms %}
    <div class="term">
        <h3 id="{{ term.term|lower|replace(' ', '-') }}">{{ term.term }}</h3>
        <div class="term-type">Type: {{ term.type }}</div>
        <div class="term-definition">{{ term.definition }}</div>
        
        {% if term.context %}
        <div class="term-context">{{ term.context }}</div>
        {% endif %}
        
        {% if term.examples %}
        <div class="term-examples">
        {% for example in term.examples %}
{{ example }}
        {% endfor %}
        </div>
        {% endif %}
        
        {% if term.related_terms %}
        <div class="term-related">
            Related terms:
            {% for related in term.related_terms %}
            <a href="#{{ related|lower|replace(' ', '-') }}">{{ related }}</a>
            {% endfor %}
        </div>
        {% endif %}
    </div>
    {% endfor %}
    <p><a href="#top">Back to top</a></p>
    {% endfor %}
    
    <a href="#top" class="back-to-top">↑</a>
</body>
</html>"""
            with open(self.template_dir / 'glossary.html.j2', 'w') as f:
                f.write(default_template)
            template = self.env.get_template('glossary.html.j2')
        
        # Group terms by first letter
        terms_by_letter = {}
        for term in glossary_data['terms']:
            first_letter = term['term'][0].upper()
            if first_letter not in terms_by_letter:
                terms_by_letter[first_letter] = []
            terms_by_letter[first_letter].append(term)
        
        # Sort terms within each letter
        for letter in terms_by_letter:
            terms_by_letter[letter].sort(key=lambda x: x['term'].lower())
        
        # Get sorted list of letters
        alphabet = sorted(terms_by_letter.keys())
        
        # Render template
        html = template.render(
            metadata=glossary_data['metadata'],
            terms=glossary_data['terms'],
            terms_by_letter=terms_by_letter,
            alphabet=alphabet
        )
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"HTML glossary generated at {output_file}")
    
    def generate_markdown(self, glossary_data, output_file):
        """Generate Markdown glossary."""
        # Group terms by first letter
        terms_by_letter = {}
        for term in glossary_data['terms']:
            first_letter = term['term'][0].upper()
            if first_letter not in terms_by_letter:
                terms_by_letter[first_letter] = []
            terms_by_letter[first_letter].append(term)
        
        # Sort terms within each letter
        for letter in terms_by_letter:
            terms_by_letter[letter].sort(key=lambda x: x['term'].lower())
        
        # Get sorted list of letters
        alphabet = sorted(terms_by_letter.keys())
        
        # Build markdown content
        md = ["# Glossary of Terms\n"]
        
        # Add metadata
        if glossary_data['metadata']:
            md.append(f"*Total terms: {len(glossary_data['terms'])}*\n")
            if 'extraction_date' in glossary_data['metadata']:
                md.append(f"*Last updated: {glossary_data['metadata']['extraction_date']}*\n")
            if 'source_directory' in glossary_data['metadata']:
                md.append(f"*Source: {glossary_data['metadata']['source_directory']}*\n")
        
        # Add alphabet navigation
        md.append("## Contents\n")
        for letter in alphabet:
            md.append(f"[{letter}](#{letter.lower()}) ")
        md.append("\n\n")
        
        # Add terms by letter
        for letter in alphabet:
            md.append(f"## {letter}\n")
            
            for term in terms_by_letter[letter]:
                md.append(f"### {term['term']}\n")
                md.append(f"**Type**: {term['type']}\n\n")
                md.append(f"**Definition**: {term['definition']}\n\n")
                
                if term.get('context'):
                    md.append(f"**Context**: {term['context']}\n\n")
                
                if term.get('examples'):
                    md.append("**Examples**:\n")
                    for example in term['examples']:
                        md.append(f"```\n{example}\n```\n\n")
                
                if term.get('related_terms'):
                    md.append("**Related terms**: ")
                    related_links = []
                    for related in term['related_terms']:
                        related_slug = related.lower().replace(' ', '-')
                        related_links.append(f"[{related}](#{related_slug})")
                    md.append(", ".join(related_links))
                    md.append("\n\n")
                
                md.append("---\n\n")
            
            md.append("[Back to top](#contents)\n\n")
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(md))
        
        print(f"Markdown glossary generated at {output_file}")
    
    def generate_json(self, glossary_data, output_file):
        """Generate JSON glossary."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(glossary_data, f, indent=2)
        
        print(f"JSON glossary generated at {output_file}")
    
    def generate_yaml(self, glossary_data, output_file):
        """Generate YAML glossary."""
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(glossary_data, f, sort_keys=False)
        
        print(f"YAML glossary generated at {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate formatted glossary")
    parser.add_argument("input_file", help="Input glossary file (JSON or YAML)")
    parser.add_argument("--output", help="Output file")
    parser.add_argument("--format", choices=["html", "markdown", "json", "yaml"], default="html",
                        help="Output format (default: html)")
    parser.add_argument("--template-dir", help="Directory containing templates")
    args = parser.parse_args()
    
    generator = GlossaryGenerator(template_dir=args.template_dir)
    
    try:
        # Load glossary data
        glossary_data = generator.load_glossary(args.input_file)
        
        # Determine output file if not specified
        if not args.output:
            input_path = Path(args.input_file)
            if args.format == 'html':
                output_file = input_path.with_suffix('.html')
            elif args.format == 'markdown':
                output_file = input_path.with_suffix('.md')
            elif args.format == 'json':
                output_file = input_path.with_suffix('.json')
            elif args.format == 'yaml':
                output_file = input_path.with_suffix('.yaml')
        else:
            output_file = args.output
        
        # Generate output
        if args.format == 'html':
            generator.generate_html(glossary_data, output_file)
        elif args.format == 'markdown':
            generator.generate_markdown(glossary_data, output_file)
        elif args.format == 'json':
            generator.generate_json(glossary_data, output_file)
        elif args.format == 'yaml':
            generator.generate_yaml(glossary_data, output_file)
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 