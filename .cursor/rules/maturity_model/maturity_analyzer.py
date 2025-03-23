#!/usr/bin/env python3

"""Maturity Model Analyzer

This script analyzes the codebase to identify, track, and report on the 
maturity levels of components based on their documentation.

Maturity: beta

Why:
- Tracking component maturity helps set proper expectations for usage
- Provides visibility into the stability of different parts of the codebase
- Helps plan development efforts to mature experimental components
- Identifies deprecated components that should be migrated away from
"""

import argparse
import json
import os
import re
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

# Define maturity levels and their order
MATURITY_LEVELS = ["experimental", "beta", "stable", "deprecated"]
MATURITY_LEVEL_MAP = {level: idx for idx, level in enumerate(MATURITY_LEVELS)}

class MaturityAnalyzer:
    """Analyzes component maturity throughout the codebase."""
    
    def __init__(self, output_dir=None):
        """Initialize the maturity analyzer."""
        if output_dir is None:
            # Default to a maturity directory at the script location
            self.output_dir = Path(__file__).parent / "output"
        else:
            self.output_dir = Path(output_dir)
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize data structures
        self.components = {}
        self.maturity_stats = {level: 0 for level in MATURITY_LEVELS}
        
        # Define regex patterns for extracting maturity info
        self.patterns = {
            # JavaScript/TypeScript JSDoc pattern
            "js_ts": re.compile(r'@maturity\s+(experimental|beta|stable|deprecated)'),
            
            # Python docstring pattern
            "py": re.compile(r'Maturity:\s+(experimental|beta|stable|deprecated)', re.IGNORECASE),
            
            # Pine Script comment pattern
            "pine": re.compile(r'@maturity=(experimental|beta|stable|deprecated)'),
            
            # Solidity NatSpec pattern
            "sol": re.compile(r'@maturity\s+(experimental|beta|stable|deprecated)')
        }

    def analyze_file(self, file_path):
        """Analyze a single file for component maturity information."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_ext = file_path.suffix.lower()
            component_name = file_path.stem
            
            # Determine which pattern to use based on file extension
            if file_ext in ['.js', '.jsx', '.ts', '.tsx']:
                pattern = self.patterns["js_ts"]
            elif file_ext == '.py':
                pattern = self.patterns["py"]
            elif file_ext in ['.pine', '.pinescript']:
                pattern = self.patterns["pine"]
            elif file_ext == '.sol':
                pattern = self.patterns["sol"]
            else:
                # Unsupported file type
                return None
            
            # Extract maturity level
            match = pattern.search(content)
            if match:
                maturity = match.group(1).lower()
                
                # Extract component name from file content if available
                name_match = re.search(r'(?:class|function|component|contract)\s+(\w+)', content)
                if name_match:
                    component_name = name_match.group(1)
                
                # Extract since version if available
                since_match = re.search(r'@since\s+([\d\.]+)', content)
                since_version = since_match.group(1) if since_match else "unknown"
                
                # Extract expected next level if available (mainly for experimental/beta)
                next_level = None
                next_level_match = re.search(r'@next\s+(beta|stable)', content)
                if next_level_match:
                    next_level = next_level_match.group(1)
                
                # Create component entry
                self.components[str(file_path)] = {
                    "name": component_name,
                    "path": str(file_path),
                    "maturity": maturity,
                    "since_version": since_version,
                    "next_level": next_level,
                    "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }
                
                # Update statistics
                self.maturity_stats[maturity] += 1
                
                return maturity
            
            return None
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None

    def analyze_directory(self, directory_path, exclude_patterns=None):
        """Analyze all relevant files in a directory for maturity information."""
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
                if file_path.suffix.lower() in ['.js', '.jsx', '.ts', '.tsx', '.py', '.pine', '.pinescript', '.sol']:
                    self.analyze_file(file_path)
    
    def generate_report(self):
        """Generate a JSON report of component maturity."""
        report = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_components": len(self.components),
                "maturity_stats": self.maturity_stats
            },
            "components": self.components
        }
        
        # Save to file
        report_path = self.output_dir / "maturity_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"Maturity report generated at {report_path}")
        return report

    def generate_visualizations(self):
        """Generate visualizations of component maturity."""
        if not self.components:
            print("No components found. Run analyze_directory() first.")
            return
        
        # Create a DataFrame for easier visualization
        df = pd.DataFrame.from_dict(self.components, orient='index')
        
        # Maturity distribution pie chart
        plt.figure(figsize=(10, 6))
        maturity_counts = df['maturity'].value_counts()
        plt.pie(maturity_counts, labels=maturity_counts.index, autopct='%1.1f%%', 
                colors=['#FF9999', '#66B2FF', '#99FF99', '#FFCC99'])
        plt.title('Component Maturity Distribution')
        plt.savefig(self.output_dir / "maturity_distribution.png")
        plt.close()
        
        # Maturity by file type bar chart
        plt.figure(figsize=(12, 6))
        file_types = df['path'].apply(lambda x: os.path.splitext(x)[1][1:])
        maturity_by_filetype = pd.crosstab(file_types, df['maturity'])
        maturity_by_filetype.plot(kind='bar', stacked=True, 
                                  color=['#FF9999', '#66B2FF', '#99FF99', '#FFCC99'])
        plt.title('Component Maturity by File Type')
        plt.xlabel('File Type')
        plt.ylabel('Number of Components')
        plt.legend(title='Maturity Level')
        plt.tight_layout()
        plt.savefig(self.output_dir / "maturity_by_filetype.png")
        plt.close()
        
        print(f"Visualizations saved to {self.output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Analyze component maturity")
    parser.add_argument("--directory", help="Directory to analyze", default=".")
    parser.add_argument("--output", help="Output directory for reports and visualizations")
    parser.add_argument("--exclude", help="Comma-separated list of directories to exclude")
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = MaturityAnalyzer(output_dir=args.output)
    
    # Set up exclude patterns
    exclude_patterns = ['node_modules', 'dist', 'build', '.git']
    if args.exclude:
        exclude_patterns.extend(args.exclude.split(','))
    
    # Analyze directory
    analyzer.analyze_directory(args.directory, exclude_patterns=exclude_patterns)
    
    # Generate report and visualizations
    analyzer.generate_report()
    analyzer.generate_visualizations()

if __name__ == "__main__":
    main() 