#!/usr/bin/env python3
# MEMORY_ANCHOR: debug_history_web_interface

"""Debug History Web Interface

This script implements a web interface for debug history using Flask,
allowing developers to search and browse debug history entries.

Maturity: beta

Why:
A web interface makes it easier to search, browse, and share debug history
entries. It provides a more user-friendly experience than command-line tools,
especially for complex searches and viewing detailed information.
"""

import os
import json
import glob
import datetime
import argparse
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for
from vector_db import search_index, build_index

# Define paths
BASE_DIR = Path(__file__).parent.parent
DEBUG_HISTORY_DIR = BASE_DIR / "debug_history"
TEMPLATES_DIR = DEBUG_HISTORY_DIR / "templates"
STATIC_DIR = DEBUG_HISTORY_DIR / "static"

# Create Flask app
app = Flask(__name__, 
            template_folder=str(TEMPLATES_DIR),
            static_folder=str(STATIC_DIR))

def ensure_directories():
    """Ensure all necessary directories exist."""
    DEBUG_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

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

def load_entry(entry_id):
    """Load a debug entry by ID."""
    debug_files = glob.glob(str(DEBUG_HISTORY_DIR / "**" / "*.json"), recursive=True)
    
    for file_path in debug_files:
        try:
            with open(file_path, 'r') as f:
                entry = json.load(f)
                if entry.get("id") == entry_id:
                    entry["file_path"] = file_path
                    return entry
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return None

def get_components():
    """Get a list of all components."""
    debug_entries = load_debug_history()
    components = set()
    
    for entry in debug_entries:
        component = entry.get("component")
        if component:
            components.add(component)
    
    return sorted(list(components))

def get_error_types():
    """Get a list of all error types."""
    debug_entries = load_debug_history()
    error_types = set()
    
    for entry in debug_entries:
        error_type = entry.get("error_type")
        if error_type:
            error_types.add(error_type)
    
    return sorted(list(error_types))

@app.route('/')
def index():
    """Render the index page."""
    components = get_components()
    error_types = get_error_types()
    
    return render_template('index.html', 
                          components=components,
                          error_types=error_types)

@app.route('/search')
def search():
    """Search debug history."""
    query = request.args.get('query', '')
    component = request.args.get('component', '')
    error_type = request.args.get('error_type', '')
    k = int(request.args.get('k', '10'))
    
    # Build search query
    search_query = query
    if component:
        search_query += f" component:{component}"
    if error_type:
        search_query += f" error_type:{error_type}"
    
    # Search index
    results = search_index(search_query, k)
    
    # Filter results by component and error type if specified
    if component or error_type:
        filtered_results = []
        for result in results:
            if component and result.get("component") != component:
                continue
            if error_type and result.get("error_type") != error_type:
                continue
            filtered_results.append(result)
        results = filtered_results
    
    components = get_components()
    error_types = get_error_types()
    
    return render_template('search.html', 
                          query=query,
                          component=component,
                          error_type=error_type,
                          results=results,
                          components=components,
                          error_types=error_types)

@app.route('/entry/<entry_id>')
def entry(entry_id):
    """View a debug entry."""
    entry = load_entry(entry_id)
    
    if not entry:
        return redirect(url_for('index'))
    
    return render_template('entry.html', entry=entry)

@app.route('/api/search')
def api_search():
    """API endpoint for searching debug history."""
    query = request.args.get('query', '')
    component = request.args.get('component', '')
    error_type = request.args.get('error_type', '')
    k = int(request.args.get('k', '10'))
    
    # Build search query
    search_query = query
    if component:
        search_query += f" component:{component}"
    if error_type:
        search_query += f" error_type:{error_type}"
    
    # Search index
    results = search_index(search_query, k)
    
    # Filter results by component and error type if specified
    if component or error_type:
        filtered_results = []
        for result in results:
            if component and result.get("component") != component:
                continue
            if error_type and result.get("error_type") != error_type:
                continue
            filtered_results.append(result)
        results = filtered_results
    
    return jsonify(results)

@app.route('/api/entry/<entry_id>')
def api_entry(entry_id):
    """API endpoint for getting a debug entry."""
    entry = load_entry(entry_id)
    
    if not entry:
        return jsonify({"error": "Entry not found"}), 404
    
    return jsonify(entry)

@app.route('/api/components')
def api_components():
    """API endpoint for getting all components."""
    components = get_components()
    return jsonify(components)

@app.route('/api/error_types')
def api_error_types():
    """API endpoint for getting all error types."""
    error_types = get_error_types()
    return jsonify(error_types)

def create_templates():
    """Create HTML templates for the web interface."""
    # Create base template
    base_template = """<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Debug History{% endblock %}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            padding: 20px;
            font-family: Arial, sans-serif;
        }
        .header {
            margin-bottom: 30px;
        }
        .search-form {
            margin-bottom: 30px;
        }
        .result-item {
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 5px;
            background-color: #f8f9fa;
        }
        .result-item:hover {
            background-color: #e9ecef;
        }
        .similarity-badge {
            float: right;
        }
        .entry-details {
            margin-top: 20px;
        }
        .entry-section {
            margin-bottom: 30px;
            padding: 20px;
            border-radius: 5px;
            background-color: #f8f9fa;
        }
    </style>
    {% block head %}{% endblock %}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Debug History</h1>
            <nav class="navbar navbar-expand-lg navbar-light bg-light">
                <div class="container-fluid">
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav">
                            <li class="nav-item">
                                <a class="nav-link" href="{{ url_for('index') }}">Home</a>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>
        </div>
        
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
"""
    
    # Create index template
    index_template = """{% extends "base.html" %}

{% block title %}Debug History{% endblock %}

{% block content %}
<div class="search-form">
    <h2>Search Debug History</h2>
    <form action="{{ url_for('search') }}" method="get">
        <div class="mb-3">
            <label for="query" class="form-label">Search Query</label>
            <input type="text" class="form-control" id="query" name="query" placeholder="Enter search query">
        </div>
        <div class="mb-3">
            <label for="component" class="form-label">Component</label>
            <select class="form-select" id="component" name="component">
                <option value="">All Components</option>
                {% for component in components %}
                <option value="{{ component }}">{{ component }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="mb-3">
            <label for="error_type" class="form-label">Error Type</label>
            <select class="form-select" id="error_type" name="error_type">
                <option value="">All Error Types</option>
                {% for error_type in error_types %}
                <option value="{{ error_type }}">{{ error_type }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="mb-3">
            <label for="k" class="form-label">Number of Results</label>
            <input type="number" class="form-control" id="k" name="k" value="10" min="1" max="100">
        </div>
        <button type="submit" class="btn btn-primary">Search</button>
    </form>
</div>
{% endblock %}
"""
    
    # Create search template
    search_template = """{% extends "base.html" %}

{% block title %}Search Results{% endblock %}

{% block content %}
<div class="search-form">
    <h2>Search Debug History</h2>
    <form action="{{ url_for('search') }}" method="get">
        <div class="mb-3">
            <label for="query" class="form-label">Search Query</label>
            <input type="text" class="form-control" id="query" name="query" value="{{ query }}" placeholder="Enter search query">
        </div>
        <div class="mb-3">
            <label for="component" class="form-label">Component</label>
            <select class="form-select" id="component" name="component">
                <option value="">All Components</option>
                {% for comp in components %}
                <option value="{{ comp }}" {% if comp == component %}selected{% endif %}>{{ comp }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="mb-3">
            <label for="error_type" class="form-label">Error Type</label>
            <select class="form-select" id="error_type" name="error_type">
                <option value="">All Error Types</option>
                {% for et in error_types %}
                <option value="{{ et }}" {% if et == error_type %}selected{% endif %}>{{ et }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="mb-3">
            <label for="k" class="form-label">Number of Results</label>
            <input type="number" class="form-control" id="k" name="k" value="10" min="1" max="100">
        </div>
        <button type="submit" class="btn btn-primary">Search</button>
    </form>
</div>

<div class="search-results">
    <h2>Search Results</h2>
    {% if results %}
        {% for result in results %}
        <div class="result-item">
            <h4>
                {{ result.text }}
                <span class="badge bg-primary similarity-badge">{{ "%.0f"|format(result.similarity * 100) }}% Match</span>
            </h4>
            <p>{{ result.description[:200] }}{% if result.description|length > 200 %}...{% endif %}</p>
            <div>
                <span class="badge bg-secondary">{{ result.type }}</span>
                <span class="badge bg-info">{{ result.error_type }}</span>
                <span class="badge bg-dark">{{ result.component }}</span>
            </div>
            <div class="mt-2">
                <a href="{{ url_for('entry', entry_id=result.id) }}" class="btn btn-sm btn-outline-primary">View Details</a>
            </div>
        </div>
        {% endfor %}
    {% else %}
        <div class="alert alert-info">No results found.</div>
    {% endif %}
</div>
{% endblock %}
"""
    
    # Create entry template
    entry_template = """{% extends "base.html" %}

{% block title %}{{ entry.error_type }} - Debug Entry{% endblock %}

{% block content %}
<div class="entry-details">
    <h2>Debug Entry: {{ entry.error_type }}</h2>
    
    <div class="entry-section">
        <h3>Error Information</h3>
        <div class="mb-3">
            <strong>ID:</strong> {{ entry.id }}
        </div>
        <div class="mb-3">
            <strong>Component:</strong> {{ entry.component }}
        </div>
        <div class="mb-3">
            <strong>Error Type:</strong> {{ entry.error_type }}
        </div>
        <div class="mb-3">
            <strong>Error Message:</strong>
            <pre class="bg-dark text-light p-3">{{ entry.error_message }}</pre>
        </div>
        <div class="mb-3">
            <strong>Error Description:</strong>
            <p>{{ entry.error_description }}</p>
        </div>
    </div>
    
    <div class="entry-section">
        <h3>Solution</h3>
        <div class="mb-3">
            <strong>Solution Description:</strong>
            <p>{{ entry.solution_description }}</p>
        </div>
        {% if entry.solution_code %}
        <div class="mb-3">
            <strong>Solution Code:</strong>
            <pre class="bg-dark text-light p-3">{{ entry.solution_code }}</pre>
        </div>
        {% endif %}
    </div>
    
    <div class="entry-section">
        <h3>Additional Information</h3>
        {% if entry.tags %}
        <div class="mb-3">
            <strong>Tags:</strong>
            {% for tag in entry.tags %}
            <span class="badge bg-secondary">{{ tag }}</span>
            {% endfor %}
        </div>
        {% endif %}
        {% if entry.created_at %}
        <div class="mb-3">
            <strong>Created At:</strong> {{ entry.created_at }}
        </div>
        {% endif %}
        {% if entry.file_path %}
        <div class="mb-3">
            <strong>File Path:</strong> {{ entry.file_path }}
        </div>
        {% endif %}
    </div>
    
    <a href="{{ url_for('index') }}" class="btn btn-primary">Back to Search</a>
</div>
{% endblock %}
"""
    
    # Create templates directory if it doesn't exist
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Write templates
    with open(TEMPLATES_DIR / "base.html", 'w') as f:
        f.write(base_template)
    
    with open(TEMPLATES_DIR / "index.html", 'w') as f:
        f.write(index_template)
    
    with open(TEMPLATES_DIR / "search.html", 'w') as f:
        f.write(search_template)
    
    with open(TEMPLATES_DIR / "entry.html", 'w') as f:
        f.write(entry_template)

def main():
    parser = argparse.ArgumentParser(description="Debug History Web Interface")
    parser.add_argument("--host", default="127.0.0.1", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the server on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()
    
    ensure_directories()
    create_templates()
    
    # Build index if it doesn't exist
    try:
        from vector_db import INDEX_FILE
        if not os.path.exists(INDEX_FILE):
            print("Building index...")
            build_index()
    except ImportError:
        print("Warning: vector_db module not found. Search functionality may not work.")
    
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main() 