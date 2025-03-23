#!/usr/bin/env python3

"""Memory Anchor Visualizer

This script generates visualizations of memory anchors and their relationships,
making it easier to understand the semantic structure of the codebase.

Maturity: beta

Why:
- Visual representation makes semantic structure more apparent
- Helps developers navigate and understand the codebase
- Provides a high-level view of the codebase organization
- Makes it easier to identify related components
"""

import argparse
import json
import os
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
import yaml
from pyvis.network import Network

class AnchorVisualizer:
    """Generates visualizations of memory anchors."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.graph = nx.Graph()
    
    def load_anchors(self, anchor_file):
        """Load memory anchors from a file."""
        try:
            with open(anchor_file, 'r', encoding='utf-8') as f:
                if anchor_file.endswith('.json'):
                    data = json.load(f)
                elif anchor_file.endswith(('.yaml', '.yml')):
                    data = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported file format: {anchor_file}")
            
            # Extract anchors
            if 'anchors' in data:
                anchors = data['anchors']
            else:
                anchors = data
            
            return anchors
        
        except Exception as e:
            print(f"Error loading anchors: {e}")
            return []
    
    def build_graph(self, anchors, group_by_type=True):
        """Build a graph from memory anchors."""
        # Clear existing graph
        self.graph.clear()
        
        # Process each anchor
        for anchor in anchors:
            file_path = anchor.get('file', '')
            anchor_type = anchor.get('type', 'unknown')
            description = anchor.get('description', '')
            
            # Create a unique node ID
            node_id = f"{file_path}:{anchor.get('line', 0)}"
            
            # Add node with attributes
            self.graph.add_node(node_id, 
                               file=file_path,
                               type=anchor_type,
                               description=description,
                               line=anchor.get('line', 0),
                               context=anchor.get('context', ''))
        
        # Connect anchors of the same type
        if group_by_type:
            # Group nodes by type
            nodes_by_type = {}
            for node, attrs in self.graph.nodes(data=True):
                anchor_type = attrs.get('type', 'unknown')
                if anchor_type not in nodes_by_type:
                    nodes_by_type[anchor_type] = []
                nodes_by_type[anchor_type].append(node)
            
            # Connect nodes of the same type
            for anchor_type, nodes in nodes_by_type.items():
                for i in range(len(nodes)):
                    for j in range(i+1, len(nodes)):
                        self.graph.add_edge(nodes[i], nodes[j], type='same_type')
        
        if self.verbose:
            print(f"Built graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
    
    def generate_matplotlib_graph(self, output_file, layout='spring'):
        """Generate a static graph visualization using matplotlib."""
        if self.graph.number_of_nodes() == 0:
            print("Error: Graph is empty")
            return
        
        # Create figure
        plt.figure(figsize=(12, 10))
        
        # Get node attributes
        node_colors = []
        node_sizes = []
        node_labels = {}
        
        # Get unique anchor types
        anchor_types = set()
        for _, attrs in self.graph.nodes(data=True):
            anchor_types.add(attrs.get('type', 'unknown'))
        
        # Create a color map for anchor types
        color_map = plt.cm.get_cmap('tab10', len(anchor_types))
        type_to_color = {t: color_map(i) for i, t in enumerate(anchor_types)}
        
        for node, attrs in self.graph.nodes(data=True):
            # Set node color based on anchor type
            anchor_type = attrs.get('type', 'unknown')
            node_colors.append(type_to_color[anchor_type])
            
            # Set node size
            node_sizes.append(100)
            
            # Set node label (file name and description)
            file_name = Path(attrs.get('file', '')).name
            description = attrs.get('description', '')
            node_labels[node] = f"{file_name}\n{description}"
        
        # Choose layout
        if layout == 'spring':
            pos = nx.spring_layout(self.graph)
        elif layout == 'circular':
            pos = nx.circular_layout(self.graph)
        elif layout == 'shell':
            pos = nx.shell_layout(self.graph)
        elif layout == 'spectral':
            pos = nx.spectral_layout(self.graph)
        else:
            pos = nx.spring_layout(self.graph)
        
        # Draw graph
        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8)
        nx.draw_networkx_edges(self.graph, pos, alpha=0.5)
        nx.draw_networkx_labels(self.graph, pos, labels=node_labels, font_size=8, font_family='sans-serif')
        
        # Add legend for anchor types
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                     label=anchor_type,
                                     markerfacecolor=type_to_color[anchor_type], 
                                     markersize=10)
                          for anchor_type in anchor_types]
        
        plt.legend(handles=legend_elements, title="Anchor Types")
        
        # Remove axis
        plt.axis('off')
        
        # Save figure
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Static graph saved to {output_file}")
    
    def generate_interactive_graph(self, output_file):
        """Generate an interactive graph visualization using pyvis."""
        if self.graph.number_of_nodes() == 0:
            print("Error: Graph is empty")
            return
        
        # Create network
        net = Network(height="800px", width="100%", notebook=False)
        
        # Get unique anchor types
        anchor_types = set()
        for _, attrs in self.graph.nodes(data=True):
            anchor_types.add(attrs.get('type', 'unknown'))
        
        # Create a color map for anchor types
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", 
                 "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
        type_to_color = {t: colors[i % len(colors)] for i, t in enumerate(anchor_types)}
        
        # Add nodes
        for node, attrs in self.graph.nodes(data=True):
            # Get attributes
            file_path = attrs.get('file', '')
            file_name = Path(file_path).name
            anchor_type = attrs.get('type', 'unknown')
            description = attrs.get('description', '')
            line = attrs.get('line', 0)
            context = attrs.get('context', '')
            
            # Create label
            label = f"{file_name}:{line}\n{description}"
            
            # Create title (tooltip)
            title = f"File: {file_path}\nLine: {line}\nType: {anchor_type}\nDescription: {description}\nContext: {context}"
            
            # Add node
            net.add_node(node, 
                        label=label, 
                        title=title, 
                        color=type_to_color[anchor_type],
                        shape='dot',
                        size=10)
        
        # Add edges
        for source, target, attrs in self.graph.edges(data=True):
            edge_type = attrs.get('type', '')
            
            # Add edge
            net.add_edge(source, target, title=edge_type)
        
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

def main():
    parser = argparse.ArgumentParser(description="Visualize memory anchors")
    parser.add_argument("anchor_file", help="Memory anchor file (JSON or YAML)")
    parser.add_argument("--output-dir", default="anchor_visualizations", help="Output directory")
    parser.add_argument("--static", action="store_true", help="Generate static graph (matplotlib)")
    parser.add_argument("--interactive", action="store_true", help="Generate interactive graph (pyvis)")
    parser.add_argument("--group-by-type", action="store_true", help="Group anchors by type")
    parser.add_argument("--layout", choices=["spring", "circular", "shell", "spectral"], 
                        default="spring", help="Layout for static graph")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create visualizer
    visualizer = AnchorVisualizer(verbose=args.verbose)
    
    # Load anchors
    anchors = visualizer.load_anchors(args.anchor_file)
    
    # Build graph
    visualizer.build_graph(anchors, group_by_type=args.group_by_type)
    
    # Generate outputs
    if args.static or not args.interactive:  # Default to static if nothing specified
        static_output = output_dir / "anchor_graph.png"
        visualizer.generate_matplotlib_graph(static_output, layout=args.layout)
    
    if args.interactive:
        interactive_output = output_dir / "anchor_graph.html"
        visualizer.generate_interactive_graph(interactive_output)

if __name__ == "__main__":
    main() 