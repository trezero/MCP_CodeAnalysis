#!/usr/bin/env python3

"""Dependency Graph Generator

This script generates a visual dependency graph from cross-reference data,
showing relationships between components in the codebase.

Maturity: beta

Why:
- Visual representation makes complex dependencies easier to understand
- Helps identify tightly coupled components that may need refactoring
- Provides insights into the architecture of the codebase
- Makes it easier to plan refactoring and understand impact of changes
"""

import argparse
import json
import os
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
import yaml
from pyvis.network import Network

class DependencyGraphGenerator:
    """Generates visual dependency graphs from cross-reference data."""
    
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
    
    def build_graph(self, references, simplify_paths=True, group_by_directory=False):
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
            
            # Simplify paths if requested
            if simplify_paths:
                source = self._simplify_path(source)
                if not target.startswith(('http://', 'https://')):  # Don't simplify URLs
                    target = self._simplify_path(target)
            
            # Add nodes if they don't exist
            if source not in self.graph:
                self.graph.add_node(source)
            
            if target not in self.graph:
                self.graph.add_node(target)
            
            # Add edge with reference type as attribute
            self.graph.add_edge(source, target, type=ref_type)
        
        # Group nodes by directory if requested
        if group_by_directory:
            self._group_by_directory()
        
        if self.verbose:
            print(f"Built graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
    
    def _simplify_path(self, path):
        """Simplify a file path for better visualization."""
        # Convert to Path object
        p = Path(path)
        
        # If it's a relative import path (no extension), return as is
        if '.' not in p.name:
            return path
        
        # Otherwise, return the relative path from the project root
        # This assumes the path is already relative to the project root
        return str(p)
    
    def _group_by_directory(self):
        """Group nodes by directory."""
        # Create a new graph
        grouped_graph = nx.DiGraph()
        
        # Map nodes to directories
        node_to_dir = {}
        for node in self.graph.nodes():
            directory = str(Path(node).parent)
            node_to_dir[node] = directory
            
            # Add directory node if it doesn't exist
            if directory not in grouped_graph:
                grouped_graph.add_node(directory, type='directory')
        
        # Add edges between directories
        for source, target, data in self.graph.edges(data=True):
            source_dir = node_to_dir[source]
            target_dir = node_to_dir[target]
            
            if source_dir != target_dir:  # Skip self-references
                # Add edge if it doesn't exist
                if not grouped_graph.has_edge(source_dir, target_dir):
                    grouped_graph.add_edge(source_dir, target_dir, weight=1, types=[data['type']])
                else:
                    # Increment weight and add reference type
                    grouped_graph[source_dir][target_dir]['weight'] += 1
                    if data['type'] not in grouped_graph[source_dir][target_dir]['types']:
                        grouped_graph[source_dir][target_dir]['types'].append(data['type'])
        
        # Replace the original graph
        self.graph = grouped_graph
    
    def generate_matplotlib_graph(self, output_file, layout='spring', node_size=1000, edge_width=1.0):
        """Generate a static graph visualization using matplotlib."""
        plt.figure(figsize=(12, 10))
        
        # Choose layout
        if layout == 'spring':
            pos = nx.spring_layout(self.graph, seed=42)
        elif layout == 'circular':
            pos = nx.circular_layout(self.graph)
        elif layout == 'shell':
            pos = nx.shell_layout(self.graph)
        elif layout == 'spectral':
            pos = nx.spectral_layout(self.graph)
        else:
            pos = nx.spring_layout(self.graph, seed=42)
        
        # Draw nodes
        nx.draw_networkx_nodes(self.graph, pos, node_size=node_size, 
                              node_color='lightblue', alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(self.graph, pos, width=edge_width, 
                              edge_color='gray', alpha=0.6, arrows=True)
        
        # Draw labels
        nx.draw_networkx_labels(self.graph, pos, font_size=8, font_family='sans-serif')
        
        # Save figure
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Static graph saved to {output_file}")
    
    def generate_interactive_graph(self, output_file, height='800px', width='100%'):
        """Generate an interactive graph visualization using pyvis."""
        # Create network
        net = Network(height=height, width=width, directed=True, notebook=False)
        
        # Add nodes
        for node in self.graph.nodes():
            # Determine node type
            if 'type' in self.graph.nodes[node] and self.graph.nodes[node]['type'] == 'directory':
                node_type = 'directory'
                title = f"Directory: {node}"
                color = '#FFA500'  # Orange for directories
            else:
                node_type = 'file'
                title = f"File: {node}"
                color = '#6BAED6'  # Blue for files
            
            # Add node with attributes
            net.add_node(node, label=str(Path(node).name), title=title, color=color)
        
        # Add edges
        for source, target, data in self.graph.edges(data=True):
            # Determine edge attributes
            if 'weight' in data:
                weight = data['weight']
                title = f"References: {weight}"
                width = min(weight, 10)  # Cap width at 10
            else:
                weight = 1
                title = f"Type: {data.get('type', 'unknown')}"
                width = 1
            
            # Add edge with attributes
            net.add_edge(source, target, title=title, width=width)
        
        # Set physics options for better visualization
        net.set_options("""
        {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.01,
              "springLength": 100,
              "springConstant": 0.08
            },
            "maxVelocity": 50,
            "solver": "forceAtlas2Based",
            "timestep": 0.35,
            "stabilization": {
              "enabled": true,
              "iterations": 1000
            }
          }
        }
        """)
        
        # Save to HTML file
        net.save_graph(output_file)
        
        print(f"Interactive graph saved to {output_file}")
    
    def generate_metrics(self, output_file=None):
        """Generate graph metrics and statistics."""
        metrics = {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'is_directed': nx.is_directed(self.graph),
            'is_connected': nx.is_weakly_connected(self.graph) if nx.is_directed(self.graph) else nx.is_connected(self.graph),
            'average_clustering': nx.average_clustering(self.graph.to_undirected()),
            'average_shortest_path_length': None,  # Will calculate if connected
            'diameter': None,  # Will calculate if connected
            'degree_centrality': None,  # Will calculate
            'betweenness_centrality': None,  # Will calculate
            'strongly_connected_components': None,  # Will calculate if directed
            'cycles': None  # Will calculate
        }
        
        # Calculate additional metrics
        try:
            # Average shortest path length (only for connected graphs)
            if metrics['is_connected']:
                metrics['average_shortest_path_length'] = nx.average_shortest_path_length(self.graph)
                metrics['diameter'] = nx.diameter(self.graph.to_undirected())
        except nx.NetworkXError:
            # Graph is not connected
            pass
        
        # Centrality measures
        metrics['degree_centrality'] = nx.degree_centrality(self.graph)
        metrics['betweenness_centrality'] = nx.betweenness_centrality(self.graph)
        
        # Strongly connected components (for directed graphs)
        if nx.is_directed(self.graph):
            metrics['strongly_connected_components'] = list(nx.strongly_connected_components(self.graph))
        
        # Find cycles
        try:
            metrics['cycles'] = list(nx.simple_cycles(self.graph))
        except:
            # Some graphs may not support cycle detection
            pass
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, default=str)
            
            print(f"Metrics saved to {output_file}")
        
        return metrics

def main():
    parser = argparse.ArgumentParser(description="Generate dependency graph from cross-references")
    parser.add_argument("reference_file", help="Cross-reference file (JSON or YAML)")
    parser.add_argument("--output-dir", default="dependency_graphs", help="Output directory")
    parser.add_argument("--static", action="store_true", help="Generate static graph (matplotlib)")
    parser.add_argument("--interactive", action="store_true", help="Generate interactive graph (pyvis)")
    parser.add_argument("--metrics", action="store_true", help="Generate graph metrics")
    parser.add_argument("--simplify-paths", action="store_true", help="Simplify file paths")
    parser.add_argument("--group-by-directory", action="store_true", help="Group nodes by directory")
    parser.add_argument("--layout", choices=["spring", "circular", "shell", "spectral"], 
                        default="spring", help="Layout for static graph")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create generator
    generator = DependencyGraphGenerator(verbose=args.verbose)
    
    # Load references
    references = generator.load_references(args.reference_file)
    
    # Build graph
    generator.build_graph(references, simplify_paths=args.simplify_paths, 
                         group_by_directory=args.group_by_directory)
    
    # Generate outputs
    if args.static or not args.interactive:  # Default to static if nothing specified
        static_output = output_dir / "dependency_graph.png"
        generator.generate_matplotlib_graph(static_output, layout=args.layout)
    
    if args.interactive:
        interactive_output = output_dir / "dependency_graph.html"
        generator.generate_interactive_graph(interactive_output)
    
    if args.metrics:
        metrics_output = output_dir / "graph_metrics.json"
        generator.generate_metrics(metrics_output)

if __name__ == "__main__":
    main() 