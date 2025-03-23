#!/usr/bin/env python3

"""Duplication Detector

This script detects code duplication in the codebase,
identifying opportunities for refactoring and code reuse.

Maturity: beta

Why:
- Duplicated code increases maintenance burden
- This script helps identify areas where code can be refactored
- Promotes code reuse and DRY (Don't Repeat Yourself) principles
- Helps maintain code quality over time
"""

import argparse
import json
import os
import re
from pathlib import Path
import yaml
from collections import defaultdict
import difflib
import hashlib

class DuplicationDetector:
    """Detects code duplication in the codebase."""
    
    def __init__(self, min_lines=5, similarity_threshold=0.8, verbose=False):
        self.min_lines = min_lines
        self.similarity_threshold = similarity_threshold
        self.verbose = verbose
        self.results = {
            'duplicates': [],
            'summary': {
                'total_files': 0,
                'total_duplicates': 0,
                'total_duplicate_lines': 0,
                'duplicate_percentage': 0
            }
        }
        self.file_contents = {}
        self.total_lines = 0
    
    def detect_duplicates(self, directory_path, exclude_patterns=None):
        """Detect code duplication in files in a directory."""
        if exclude_patterns is None:
            exclude_patterns = ['node_modules', 'dist', 'build', '.git']
        
        directory_path = Path(directory_path)
        
        if not directory_path.is_dir():
            print(f"Error: {directory_path} is not a directory")
            return
        
        # First pass: collect file contents
        self._collect_file_contents(directory_path, exclude_patterns)
        
        # Second pass: detect duplicates
        self._detect_duplicates()
        
        # Calculate summary
        self._calculate_summary()
    
    def _collect_file_contents(self, directory_path, exclude_patterns):
        """Collect contents of all relevant files."""
        for root, dirs, files in os.walk(directory_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in str(Path(root) / d) for pattern in exclude_patterns)]
            
            for file in files:
                file_path = Path(root) / file
                
                # Only process relevant file types
                if file.endswith(('.js', '.jsx', '.ts', '.tsx', '.py', '.pine', '.pinescript')):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Store file content
                        self.file_contents[str(file_path)] = content
                        
                        # Count lines
                        self.total_lines += len(content.split('\n'))
                        
                        if self.verbose:
                            print(f"Collected {file_path}")
                    
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
    
    def _detect_duplicates(self):
        """Detect duplicates in collected files."""
        # Extract code blocks from files
        code_blocks = self._extract_code_blocks()
        
        # Group similar code blocks
        duplicate_groups = self._group_similar_blocks(code_blocks)
        
        # Format results
        self.results['duplicates'] = [
            {
                'group_id': i,
                'block_count': len(group),
                'line_count': len(group[0]['lines']),
                'similarity': self._calculate_group_similarity(group),
                'blocks': group
            }
            for i, group in enumerate(duplicate_groups)
        ]
        
        # Sort by line count (descending)
        self.results['duplicates'].sort(key=lambda x: x['line_count'] * x['block_count'], reverse=True)
    
    def _extract_code_blocks(self):
        """Extract code blocks from files."""
        code_blocks = []
        
        for file_path, content in self.file_contents.items():
            lines = content.split('\n')
            
            # Extract blocks of minimum size
            for i in range(len(lines) - self.min_lines + 1):
                block_lines = lines[i:i+self.min_lines]
                
                # Skip blocks that are mostly whitespace or comments
                if self._is_meaningful_block(block_lines):
                    block_hash = self._hash_block(block_lines)
                    
                    code_blocks.append({
                        'file': file_path,
                        'start_line': i + 1,
                        'end_line': i + self.min_lines,
                        'lines': block_lines,
                        'hash': block_hash
                    })
        
        return code_blocks
    
    def _is_meaningful_block(self, lines):
        """Check if a block contains meaningful code (not just comments or whitespace)."""
        meaningful_lines = 0
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip comment lines
            if line.startswith('//') or line.startswith('#') or line.startswith('/*') or line.startswith('*'):
                continue
            
            meaningful_lines += 1
        
        # At least 50% of lines should be meaningful
        return meaningful_lines >= len(lines) / 2
    
    def _hash_block(self, lines):
        """Create a hash for a code block."""
        # Normalize whitespace and join lines
        normalized = '\n'.join(line.strip() for line in lines)
        
        # Create hash
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def _group_similar_blocks(self, code_blocks):
        """Group similar code blocks together."""
        # First, group by exact hash matches
        hash_groups = defaultdict(list)
        
        for block in code_blocks:
            hash_groups[block['hash']].append(block)
        
        # Filter groups with only one block
        hash_groups = {h: blocks for h, blocks in hash_groups.items() if len(blocks) > 1}
        
        # For each hash group, further group by similarity
        duplicate_groups = []
        
        for hash_value, blocks in hash_groups.items():
            # If all blocks in this hash group are from the same file, skip
            if len(set(block['file'] for block in blocks)) <= 1:
                continue
            
            duplicate_groups.append(blocks)
        
        # Sort groups by size (descending)
        duplicate_groups.sort(key=lambda g: len(g), reverse=True)
        
        return duplicate_groups
    
    def _calculate_group_similarity(self, group):
        """Calculate the average similarity within a group of blocks."""
        if len(group) <= 1:
            return 1.0
        
        total_similarity = 0
        comparisons = 0
        
        for i in range(len(group)):
            for j in range(i+1, len(group)):
                block1 = '\n'.join(group[i]['lines'])
                block2 = '\n'.join(group[j]['lines'])
                
                similarity = difflib.SequenceMatcher(None, block1, block2).ratio()
                total_similarity += similarity
                comparisons += 1
        
        return total_similarity / comparisons if comparisons > 0 else 1.0
    
    def _calculate_summary(self):
        """Calculate summary statistics."""
        total_files = len(self.file_contents)
        total_duplicates = len(self.results['duplicates'])
        
        # Calculate total duplicate lines
        duplicate_line_count = sum(
            group['line_count'] * (group['block_count'] - 1)  # Count only redundant copies
            for group in self.results['duplicates']
        )
        
        # Calculate duplicate percentage
        duplicate_percentage = (duplicate_line_count / self.total_lines * 100) if self.total_lines > 0 else 0
        
        self.results['summary'] = {
            'total_files': total_files,
            'total_duplicates': total_duplicates,
            'total_duplicate_lines': duplicate_line_count,
            'duplicate_percentage': duplicate_percentage
        }
    
    def save_results(self, output_file, format='json'):
        """Save detection results to a file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(self.results, f, indent=2)
            elif format == 'yaml':
                yaml.dump(self.results, f, sort_keys=False)
        
        print(f"Saved duplication detection results to {output_file}")
    
    def generate_report(self, output_file):
        """Generate a human-readable report."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Code Duplication Report\n\n")
            
            # Write summary
            f.write("## Summary\n\n")
            f.write(f"- Total files analyzed: {self.results['summary']['total_files']}\n")
            f.write(f"- Total duplicate groups: {self.results['summary']['total_duplicates']}\n")
            f.write(f"- Total duplicate lines: {self.results['summary']['total_duplicate_lines']}\n")
            f.write(f"- Duplicate percentage: {self.results['summary']['duplicate_percentage']:.2f}%\n\n")
            
            # Write top duplicates
            f.write("## Top Duplicate Groups\n\n")
            
            for i, group in enumerate(self.results['duplicates'][:10]):  # Show top 10
                f.write(f"### Group {i+1}\n\n")
                f.write(f"- Blocks: {group['block_count']}\n")
                f.write(f"- Lines per block: {group['line_count']}\n")
                f.write(f"- Similarity: {group['similarity']:.2f}\n")
                f.write(f"- Total duplicate lines: {group['line_count'] * (group['block_count'] - 1)}\n\n")
                
                f.write("#### Locations\n\n")
                for block in group['blocks']:
                    f.write(f"- {block['file']}:{block['start_line']}-{block['end_line']}\n")
                
                f.write("\n#### Sample Code\n\n")
                f.write("```\n")
                f.write('\n'.join(group['blocks'][0]['lines']))
                f.write("\n```\n\n")
        
        print(f"Generated duplication report at {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Detect code duplication")
    parser.add_argument("source_dir", help="Source directory to analyze")
    parser.add_argument("--output", default="duplication_analysis.json", help="Output file")
    parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Output format")
    parser.add_argument("--report", help="Generate human-readable report")
    parser.add_argument("--min-lines", type=int, default=5, help="Minimum lines for a duplicate block")
    parser.add_argument("--similarity", type=float, default=0.8,
                        help="Similarity threshold for duplicate blocks")
    args = parser.parse_args()
    
    detector = DuplicationDetector(min_lines=args.min_lines, similarity_threshold=args.similarity, verbose=True)
    detector.detect_duplicates(args.source_dir)
    detector.save_results(args.output, format=args.format)
    
    if args.report:
        detector.generate_report(args.report)

if __name__ == "__main__":
    main() 