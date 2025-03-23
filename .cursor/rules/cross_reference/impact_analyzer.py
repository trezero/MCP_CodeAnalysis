#!/usr/bin/env python3

"""Impact Analyzer

This script analyzes the potential impact of changes to specific files
by tracing dependencies through the cross-reference graph.

Maturity: beta

Why:
- Understanding the impact of changes is crucial for risk assessment
- Manual impact analysis is time-consuming and error-prone
- This script automates the process of identifying affected components
- Helps developers make more informed decisions about changes
"""

import argparse
import json
import os
from pathlib import Path
import networkx as nx
import yaml
from collections import defaultdict

class ImpactAnalyzer:
    """Analyzes the impact of changes to specific files."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.graph = nx.DiGraph()
    
    def load_references(self, reference_file):
        """Load cross-references from a file."""
        try:
            with open(reference_file, 'r', encoding='utf-8') as f:
                if reference_file.endswith('.json'):
                    data = json.load(f)
                elif reference_file.endswith(('.yaml', '.yml')):
                    data = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported file format: {reference_file}")
            
            # Extract references
            if 'references' in data:
                references = data['references']
            else:
                references = data
            
            return references
        
        except Exception as e:
            print(f"Error loading references: {e}")
            return []
    
    def build_graph(self, references):
        """Build a directed graph from cross-references."""
        # Clear existing graph
        self.graph.clear()
        
        # Process each reference
        for ref in references:
            source = ref.get('source', '')
            target = ref.get('target', '')
            ref_type = ref.get('type', 'unknown')
            
            if not source or not target:
                continue
            
            # Add nodes if they don't exist
            if source not in self.graph:
                self.graph.add_node(source)
            
            if target not in self.graph:
                self.graph.add_node(target)
            
            # Add edge with reference type as attribute
            self.graph.add_edge(source, target, type=ref_type)
        
        # Build reverse graph for impact analysis
        self.reverse_graph = self.graph.reverse()
        
        if self.verbose:
            print(f"Built graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
    
    def analyze_impact(self, target_files, max_depth=None):
        """Analyze the impact of changes to target files."""
        if not isinstance(target_files, list):
            target_files = [target_files]
        
        # Normalize file paths
        target_files = [str(Path(f)) for f in target_files]
        
        # Check if all target files exist in the graph
        missing_files = [f for f in target_files if f not in self.reverse_graph]
        if missing_files:
            print(f"Warning: The following files are not in the dependency graph: {missing_files}")
            # Remove missing files from the target list
            target_files = [f for f in target_files if f not in missing_files]
        
        if not target_files:
            print("Error: No valid target files to analyze")
            return {}
        
        # Find all affected files
        affected_files = {}
        for target in target_files:
            if self.verbose:
                print(f"Analyzing impact of changes to {target}")
            
            # Find all files that depend on the target
            if max_depth is None:
                # Get all reachable nodes
                affected = set(nx.descendants(self.reverse_graph, target))
                affected.add(target)  # Include the target itself
            else:
                # Limited BFS to find nodes within max_depth
                affected = {target}  # Start with the target
                current_level = {target}
                for depth in range(max_depth):
                    next_level = set()
                    for node in current_level:
                        next_level.update(self.reverse_graph.neighbors(node))
                    affected.update(next_level)
                    current_level = next_level
            
            # Store affected files with their paths
            affected_files[target] = sorted(list(affected))
        
        return affected_files
    
    def analyze_impact_with_paths(self, target_files, max_depth=None):
        """Analyze impact with dependency paths."""
        if not isinstance(target_files, list):
            target_files = [target_files]
        
        # Normalize file paths
        target_files = [str(Path(f)) for f in target_files]
        
        # Check if all target files exist in the graph
        missing_files = [f for f in target_files if f not in self.reverse_graph]
        if missing_files:
            print(f"Warning: The following files are not in the dependency graph: {missing_files}")
            # Remove missing files from the target list
            target_files = [f for f in target_files if f not in missing_files]
        
        if not target_files:
            print("Error: No valid target files to analyze")
            return {}
        
        # Find all affected files with paths
        impact_results = {}
        for target in target_files:
            if self.verbose:
                print(f"Analyzing impact of changes to {target}")
            
            # Find all files that depend on the target
            affected_with_paths = {}
            
            if max_depth is None:
                max_search_depth = float('inf')
            else:
                max_search_depth = max_depth
            
            # BFS to find paths
            visited = {target: [[target]]}  # node -> list of paths to node
            queue = [target]
            
            while queue:
                current = queue.pop(0)
                current_paths = visited[current]
                
                # Skip if we've reached max depth
                if len(current_paths[0]) > max_search_depth:
                    continue
                
                # Process neighbors
                for neighbor in self.reverse_graph.neighbors(current):
                    # Create new paths by extending current paths
                    new_paths = [path + [neighbor] for path in current_paths]
                    
                    if neighbor not in visited:
                        visited[neighbor] = new_paths
                        queue.append(neighbor)
                    else:
                        # Add new paths to existing paths
                        visited[neighbor].extend(new_paths)
            
            # Remove the target from visited
            if target in visited:
                del visited[target]
            
            # Format the results
            for affected, paths in visited.items():
                # Sort paths by length (shortest first)
                paths.sort(key=len)
                
                # Keep only unique paths
                unique_paths = []
                path_strings = set()
                for path in paths:
                    path_str = '->'.join(path)
                    if path_str not in path_strings:
                        path_strings.add(path_str)
                        unique_paths.append(path)
                
                affected_with_paths[affected] = unique_paths
            
            impact_results[target] = affected_with_paths
        
        return impact_results
    
    def generate_impact_report(self, impact_results, output_file):
        """Generate a report of impact analysis results."""
        # Prepare report data
        report = {
            'summary': {
                'targets': list(impact_results.keys()),
                'total_affected_files': sum(len(affected) for affected in impact_results.values())
            },
            'details': {}
        }
        
        # Add details for each target
        for target, affected in impact_results.items():
            report['details'][target] = {
                'affected_count': len(affected),
                'affected_files': affected
            }
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"Impact report saved to {output_file}")
        
        # Print summary
        print("\nImpact Analysis Summary:")
        print(f"  Target files: {len(report['summary']['targets'])}")
        print(f"  Total affected files: {report['summary']['total_affected_files']}")
        for target, details in report['details'].items():
            print(f"  {target}: {details['affected_count']} affected files")
    
    def generate_detailed_impact_report(self, impact_results, output_file):
        """Generate a detailed report with dependency paths."""
        # Prepare report data
        report = {
            'summary': {
                'targets': list(impact_results.keys()),
                'total_affected_files': sum(len(affected) for affected in impact_results.values())
            },
            'details': {}
        }
        
        # Add details for each target
        for target, affected_with_paths in impact_results.items():
            affected_details = {}
            
            for affected, paths in affected_with_paths.items():
                # Format paths for readability
                formatted_paths = []
                for path in paths:
                    formatted_paths.append(' -> '.join(path))
                
                affected_details[affected] = {
                    'path_count': len(paths),
                    'shortest_path_length': len(paths[0]) if paths else 0,
                    'paths': formatted_paths
                }
            
            report['details'][target] = {
                'affected_count': len(affected_with_paths),
                'affected_files': affected_details
            }
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"Detailed impact report saved to {output_file}")
        
        # Print summary
        print("\nDetailed Impact Analysis Summary:")
        print(f"  Target files: {len(report['summary']['targets'])}")
        print(f"  Total affected files: {report['summary']['total_affected_files']}")
        for target, details in report['details'].items():
            print(f"  {target}: {details['affected_count']} affected files")

def main():
    parser = argparse.ArgumentParser(description="Analyze the impact of changes to specific files")
    parser.add_argument("reference_file", help="Cross-reference file (JSON or YAML)")
    parser.add_argument("target_files", nargs='+', help="Target files to analyze")
    parser.add_argument("--output", default="impact_report.json", help="Output report file")
    parser.add_argument("--detailed", action="store_true", help="Generate detailed report with paths")
    parser.add_argument("--max-depth", type=int, help="Maximum depth for impact analysis")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = ImpactAnalyzer(verbose=args.verbose)
    
    # Load references
    references = analyzer.load_references(args.reference_file)
    
    # Build graph
    analyzer.build_graph(references)
    
    # Analyze impact
    if args.detailed:
        impact_results = analyzer.analyze_impact_with_paths(args.target_files, max_depth=args.max_depth)
        analyzer.generate_detailed_impact_report(impact_results, args.output)
    else:
        impact_results = analyzer.analyze_impact(args.target_files, max_depth=args.max_depth)
        analyzer.generate_impact_report(impact_results, args.output)

if __name__ == "__main__":
    main() 