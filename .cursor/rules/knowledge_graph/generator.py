#!/usr/bin/env python3
# MEMORY_ANCHOR: knowledge_graph_generator

"""Knowledge Graph Generator

This script generates a centralized knowledge graph by integrating data from
the metadata/ and code_index/ directories.

Maturity: beta

Why:
A centralized knowledge graph provides a unified view of the codebase,
making it easier to understand relationships between components, errors,
and solutions. This approach was chosen over separate data stores to
enable more powerful queries and visualizations.
"""

import os
import json
import glob
import yaml
import datetime
import argparse
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).parent.parent
METADATA_DIR = BASE_DIR / "metadata"
CODE_INDEX_DIR = BASE_DIR / "code_index"
OUTPUT_FILE = BASE_DIR / "knowledge_graph" / "graph.json"

def load_json_file(file_path):
    """Load a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def load_yaml_file(file_path):
    """Load a YAML file."""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def process_metadata_files():
    """Process files in the metadata directory."""
    nodes = []
    
    # Process component metadata
    component_files = glob.glob(str(METADATA_DIR / "components" / "*.json"))
    for file_path in component_files:
        data = load_json_file(file_path)
        if data:
            component_id = f"component:{data.get('name')}"
            nodes.append({
                "id": component_id,
                "type": "component",
                "name": data.get("name"),
                "maturity": data.get("maturity", "experimental"),
                "description": data.get("description", ""),
                "why": data.get("why", ""),
                "tags": data.get("tags", [])
            })
    
    # Process file metadata
    file_metadata_files = glob.glob(str(METADATA_DIR / "files" / "*.json"))
    for file_path in file_metadata_files:
        data = load_json_file(file_path)
        if data:
            file_id = f"file:{data.get('path')}"
            nodes.append({
                "id": file_id,
                "type": "file",
                "name": os.path.basename(data.get("path", "")),
                "path": data.get("path", ""),
                "description": data.get("description", ""),
                "tags": data.get("tags", [])
            })
    
    return nodes

def process_code_index_files():
    """Process files in the code_index directory."""
    nodes = []
    edges = []
    
    # Process function definitions
    function_files = glob.glob(str(CODE_INDEX_DIR / "functions" / "*.json"))
    for file_path in function_files:
        data = load_json_file(file_path)
        if data:
            function_id = f"function:{data.get('name')}:{data.get('file')}"
            nodes.append({
                "id": function_id,
                "type": "function",
                "name": data.get("name"),
                "path": data.get("file"),
                "description": data.get("description", "")
            })
            
            # Add edge to containing file
            if data.get("file"):
                edges.append({
                    "source": f"file:{data.get('file')}",
                    "target": function_id,
                    "type": "contains"
                })
    
    # Process class definitions
    class_files = glob.glob(str(CODE_INDEX_DIR / "classes" / "*.json"))
    for file_path in class_files:
        data = load_json_file(file_path)
        if data:
            class_id = f"class:{data.get('name')}:{data.get('file')}"
            nodes.append({
                "id": class_id,
                "type": "class",
                "name": data.get("name"),
                "path": data.get("file"),
                "description": data.get("description", "")
            })
            
            # Add edge to containing file
            if data.get("file"):
                edges.append({
                    "source": f"file:{data.get('file')}",
                    "target": class_id,
                    "type": "contains"
                })
    
    # Process function call graph
    call_graph_file = CODE_INDEX_DIR / "call_graph.json"
    if call_graph_file.exists():
        data = load_json_file(call_graph_file)
        if data and "calls" in data:
            for call in data["calls"]:
                caller = call.get("caller")
                callee = call.get("callee")
                if caller and callee:
                    caller_id = f"function:{caller.get('name')}:{caller.get('file')}"
                    callee_id = f"function:{callee.get('name')}:{callee.get('file')}"
                    edges.append({
                        "source": caller_id,
                        "target": callee_id,
                        "type": "calls"
                    })
    
    # Process dependency graph
    dependency_file = CODE_INDEX_DIR / "dependencies.json"
    if dependency_file.exists():
        data = load_json_file(dependency_file)
        if data and "dependencies" in data:
            for dep in data["dependencies"]:
                source = dep.get("source")
                target = dep.get("target")
                if source and target:
                    edges.append({
                        "source": f"component:{source}",
                        "target": f"component:{target}",
                        "type": "depends_on"
                    })
    
    return nodes, edges

def process_debug_history():
    """Process debug history to add error and solution nodes."""
    nodes = []
    edges = []
    
    debug_files = glob.glob(str(BASE_DIR / "debug_history" / "**" / "*.json"), recursive=True)
    for file_path in debug_files:
        data = load_json_file(file_path)
        if data:
            error_id = f"error:{data.get('error_type')}:{data.get('id')}"
            solution_id = f"solution:{data.get('id')}"
            
            # Add error node
            nodes.append({
                "id": error_id,
                "type": "error",
                "name": data.get("error_message", "Unknown error"),
                "description": data.get("error_description", "")
            })
            
            # Add solution node
            nodes.append({
                "id": solution_id,
                "type": "solution",
                "name": f"Solution for {data.get('error_type', 'unknown error')}",
                "description": data.get("solution_description", "")
            })
            
            # Add edge from error to solution
            edges.append({
                "source": error_id,
                "target": solution_id,
                "type": "solves"
            })
            
            # Add edge from error to component if available
            if data.get("component"):
                edges.append({
                    "source": f"component:{data.get('component')}",
                    "target": error_id,
                    "type": "causes"
                })
    
    return nodes, edges

def process_patterns():
    """Process implementation patterns."""
    nodes = []
    
    pattern_files = glob.glob(str(BASE_DIR / "patterns" / "**" / "*.json"), recursive=True)
    for file_path in pattern_files:
        data = load_json_file(file_path)
        if data:
            pattern_id = f"pattern:{data.get('name')}"
            nodes.append({
                "id": pattern_id,
                "type": "pattern",
                "name": data.get("name", "Unknown pattern"),
                "description": data.get("description", ""),
                "why": data.get("why", "")
            })
    
    return nodes

def process_memory_anchors():
    """Process semantic memory anchors in the codebase."""
    memory_anchors = []
    
    # This would typically involve parsing the actual code files
    # For demonstration, we'll just add a few example memory anchors
    memory_anchors.append({
        "node_id": "function:process_metadata_files:claude/knowledge_graph/generator.py",
        "type": "performance_bottleneck",
        "location": "claude/knowledge_graph/generator.py:45"
    })
    
    memory_anchors.append({
        "node_id": "component:knowledge_graph",
        "type": "architecture_decision",
        "location": "claude/knowledge_graph/generator.py:10"
    })
    
    return memory_anchors

def generate_knowledge_graph():
    """Generate the complete knowledge graph."""
    # Process all data sources
    metadata_nodes = process_metadata_files()
    code_index_nodes, code_index_edges = process_code_index_files()
    debug_nodes, debug_edges = process_debug_history()
    pattern_nodes = process_patterns()
    
    # Combine all nodes and edges
    all_nodes = metadata_nodes + code_index_nodes + debug_nodes + pattern_nodes
    all_edges = code_index_edges + debug_edges
    
    # Process memory anchors
    memory_anchors = process_memory_anchors()
    
    # Add memory anchors to nodes
    node_map = {node["id"]: node for node in all_nodes}
    for anchor in memory_anchors:
        node_id = anchor["node_id"]
        if node_id in node_map:
            if "memoryAnchors" not in node_map[node_id]:
                node_map[node_id]["memoryAnchors"] = []
            node_map[node_id]["memoryAnchors"].append({
                "type": anchor["type"],
                "location": anchor["location"]
            })
    
    # Create the final knowledge graph
    knowledge_graph = {
        "nodes": all_nodes,
        "edges": all_edges,
        "metadata": {
            "version": "1.0",
            "lastUpdated": datetime.datetime.now().isoformat(),
            "generatedBy": "knowledge_graph_generator.py"
        }
    }
    
    return knowledge_graph

def save_knowledge_graph(graph):
    """Save the knowledge graph to a file."""
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(graph, f, indent=2)
    print(f"Knowledge graph saved to {OUTPUT_FILE}")

def main():
    parser = argparse.ArgumentParser(description="Generate a centralized knowledge graph")
    parser.add_argument("--output", help="Output file path", default=str(OUTPUT_FILE))
    args = parser.parse_args()
    
    global OUTPUT_FILE
    OUTPUT_FILE = Path(args.output)
    
    print("Generating knowledge graph...")
    knowledge_graph = generate_knowledge_graph()
    save_knowledge_graph(knowledge_graph)
    print("Done!")

if __name__ == "__main__":
    main() 