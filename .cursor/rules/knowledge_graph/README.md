# Knowledge Graph

<!-- MEMORY_ANCHOR: knowledge_graph_documentation -->

This directory contains the centralized knowledge graph for the codebase, integrating data from `metadata/` and `code_index/` into a structured format.

## Why

A centralized knowledge graph provides a unified view of the codebase, making it easier to understand relationships between components, errors, and solutions. This approach was chosen over separate data stores to enable more powerful queries and visualizations.

## Contents

- `schema.json`: JSON Schema defining the structure of the knowledge graph
- `graph.json`: The generated knowledge graph (created by `generator.py`)
- `generator.py`: Script to generate the knowledge graph
- `visualize.py`: Script to visualize the knowledge graph
- `visualizations/`: Directory containing generated visualizations

## Usage

### Generating the Knowledge Graph

To generate the knowledge graph:

```bash
python claude/knowledge_graph/generator.py
```

This will create `graph.json` in the `knowledge_graph/` directory.

### Visualizing the Knowledge Graph

To visualize the knowledge graph:

```bash
python claude/knowledge_graph/visualize.py
```

This will create several visualizations in the `knowledge_graph/visualizations/` directory:

- `full_graph.png`: Visualization of the entire knowledge graph
- `component_dependencies.png`: Visualization of component dependencies
- `error_solutions.png`: Visualization of errors and their solutions

## Knowledge Graph Structure

The knowledge graph consists of nodes and edges:

### Nodes

Nodes represent entities in the codebase, such as:

- **Components**: High-level modules or features
- **Files**: Source code files
- **Functions**: Individual functions or methods
- **Classes**: Class definitions
- **Errors**: Error types encountered in the codebase
- **Solutions**: Solutions to errors
- **Patterns**: Implementation patterns
- **Concepts**: Abstract concepts or principles

Each node has properties such as:

- `id`: Unique identifier
- `type`: Type of node (component, file, function, etc.)
- `name`: Name of the entity
- `description`: Description of the entity
- `maturity`: Maturity level (for components)
- `why`: Explanation of the rationale behind the entity
- `tags`: Tags associated with the entity
- `memoryAnchors`: Semantic memory anchors associated with the entity

### Edges

Edges represent relationships between nodes, such as:

- **depends_on**: Component A depends on Component B
- **imports**: File A imports File B
- **calls**: Function A calls Function B
- **inherits_from**: Class A inherits from Class B
- **contains**: File A contains Function B
- **causes**: Component A causes Error B
- **solves**: Solution A solves Error B
- **implements**: Component A implements Pattern B
- **references**: Entity A references Entity B

## Integration with Other Components

The knowledge graph integrates with:

- **Metadata**: Component and file metadata from `metadata/`
- **Code Index**: Function and class definitions, call graphs, and dependencies from `code_index/`
- **Debug History**: Error and solution information from `debug_history/`
- **Patterns**: Implementation patterns from `patterns/`
- **Memory Anchors**: Semantic memory anchors throughout the codebase

## Extending the Knowledge Graph

To add new node or edge types:

1. Update `schema.json` with the new types
2. Modify `generator.py` to process the new data sources
3. Update `visualize.py` to visualize the new types

## Maturity

The knowledge graph component is currently in **beta** status. It is functional but may undergo changes as the codebase evolves. 