#!/usr/bin/env python3
# MEMORY_ANCHOR: debug_history_vector_db

"""Debug History Vector Database

This script implements a vector database for debug history using Faiss,
enabling semantic search for similar issues.

Maturity: beta

Why:
Traditional text-based search is limited when searching for similar errors
because it relies on exact keyword matches. A vector database allows for
semantic search, finding conceptually similar errors even when the wording
is different, which speeds up debugging by helping developers find and
apply solutions to similar problems.
"""

import os
import json
import glob
import argparse
import numpy as np
import faiss
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Define paths
BASE_DIR = Path(__file__).parent.parent
DEBUG_HISTORY_DIR = BASE_DIR / "debug_history"
INDEX_FILE = DEBUG_HISTORY_DIR / "vector_index.faiss"
METADATA_FILE = DEBUG_HISTORY_DIR / "vector_metadata.pkl"

# Initialize sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def ensure_directories():
    """Ensure all necessary directories exist."""
    DEBUG_HISTORY_DIR.mkdir(parents=True, exist_ok=True)

def load_debug_history():
    """Load all debug history files."""
    debug_files = glob.glob(str(DEBUG_HISTORY_DIR / "**" / "*.json"), recursive=True)
    debug_entries = []
    
    for file_path in debug_files:
        try:
            with open(file_path, 'r') as f:
                entry = json.load(f)
                entry["file_path"] = file_path
                debug_entries.append(entry)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return debug_entries

def create_index(debug_entries):
    """Create a Faiss index from debug entries."""
    # Extract text to embed
    texts = []
    metadata = []
    
    for entry in debug_entries:
        # Combine error message and description for better semantic matching
        error_text = f"{entry.get('error_message', '')} {entry.get('error_description', '')}"
        solution_text = entry.get('solution_description', '')
        
        # Add error text
        texts.append(error_text)
        metadata.append({
            "id": entry.get("id"),
            "type": "error",
            "error_type": entry.get("error_type"),
            "component": entry.get("component"),
            "file_path": entry.get("file_path")
        })
        
        # Add solution text
        texts.append(solution_text)
        metadata.append({
            "id": entry.get("id"),
            "type": "solution",
            "error_type": entry.get("error_type"),
            "component": entry.get("component"),
            "file_path": entry.get("file_path")
        })
    
    # Generate embeddings
    embeddings = model.encode(texts)
    
    # Create Faiss index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    
    return index, metadata

def save_index(index, metadata):
    """Save the Faiss index and metadata."""
    # Save Faiss index
    faiss.write_index(index, str(INDEX_FILE))
    
    # Save metadata
    with open(METADATA_FILE, 'wb') as f:
        pickle.dump(metadata, f)
    
    print(f"Index saved to {INDEX_FILE}")
    print(f"Metadata saved to {METADATA_FILE}")

def load_index():
    """Load the Faiss index and metadata."""
    if not os.path.exists(INDEX_FILE) or not os.path.exists(METADATA_FILE):
        print("Index or metadata file not found.")
        return None, None
    
    # Load Faiss index
    index = faiss.read_index(str(INDEX_FILE))
    
    # Load metadata
    with open(METADATA_FILE, 'rb') as f:
        metadata = pickle.load(f)
    
    return index, metadata

def search(query, index, metadata, k=5):
    """Search the index for similar entries."""
    if not index or not metadata:
        print("Index or metadata not loaded.")
        return []
    
    # Encode query
    query_embedding = model.encode([query])
    
    # Search index
    distances, indices = index.search(np.array(query_embedding).astype('float32'), k)
    
    # Get results
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(metadata):
            result = metadata[idx].copy()
            result["distance"] = float(distances[0][i])
            results.append(result)
    
    return results

def load_entry(file_path):
    """Load a debug entry from a file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def format_search_results(results):
    """Format search results for display."""
    formatted_results = []
    
    for i, result in enumerate(results):
        entry_id = result.get("id")
        entry_type = result.get("type")
        error_type = result.get("error_type")
        component = result.get("component")
        distance = result.get("distance")
        file_path = result.get("file_path")
        
        # Load the full entry
        entry = load_entry(file_path)
        
        if entry:
            if entry_type == "error":
                text = entry.get("error_message", "")
                description = entry.get("error_description", "")
            else:
                text = "Solution"
                description = entry.get("solution_description", "")
            
            formatted_results.append({
                "rank": i + 1,
                "id": entry_id,
                "type": entry_type,
                "error_type": error_type,
                "component": component,
                "similarity": 1.0 - min(distance / 10.0, 1.0),  # Convert distance to similarity score
                "text": text,
                "description": description,
                "file_path": file_path
            })
    
    return formatted_results

def build_index():
    """Build the vector index from debug history."""
    ensure_directories()
    
    print("Loading debug history...")
    debug_entries = load_debug_history()
    
    if not debug_entries:
        print("No debug entries found.")
        return
    
    print(f"Creating index from {len(debug_entries)} entries...")
    index, metadata = create_index(debug_entries)
    
    print("Saving index...")
    save_index(index, metadata)
    
    print("Index built successfully.")

def search_index(query, k=5):
    """Search the vector index for similar issues."""
    ensure_directories()
    
    print("Loading index...")
    index, metadata = load_index()
    
    if not index or not metadata:
        print("Index not found. Building index...")
        build_index()
        index, metadata = load_index()
    
    if not index or not metadata:
        print("Failed to load or build index.")
        return []
    
    print(f"Searching for: {query}")
    results = search(query, index, metadata, k)
    
    return format_search_results(results)

def main():
    parser = argparse.ArgumentParser(description="Debug History Vector Database")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Build index command
    build_parser = subparsers.add_parser("build", help="Build the vector index")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search the vector index")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--k", type=int, default=5, help="Number of results to return")
    
    args = parser.parse_args()
    
    if args.command == "build":
        build_index()
    elif args.command == "search":
        results = search_index(args.query, args.k)
        
        print("\nSearch Results:")
        print("==============")
        
        for result in results:
            print(f"\nRank: {result['rank']}")
            print(f"ID: {result['id']}")
            print(f"Type: {result['type']}")
            print(f"Error Type: {result['error_type']}")
            print(f"Component: {result['component']}")
            print(f"Similarity: {result['similarity']:.2f}")
            print(f"Text: {result['text']}")
            print(f"Description: {result['description'][:100]}...")
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 