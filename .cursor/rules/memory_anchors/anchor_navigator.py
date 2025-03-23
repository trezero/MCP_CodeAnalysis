#!/usr/bin/env python3

"""Memory Anchor Navigator

This script provides a web-based interface for navigating memory anchors,
making it easy to explore the semantic structure of the codebase.

Maturity: beta

Why:
- Visual navigation makes it easier to understand code structure
- Web interface is accessible to all team members
- Interactive exploration helps discover relationships between components
- Enhances the value of memory anchors as a documentation tool
"""

import argparse
import json
import os
from pathlib import Path
import yaml
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import threading
import tempfile
import shutil

class AnchorNavigator:
    """Provides a web-based interface for navigating memory anchors."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.temp_dir = None
    
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
    
    def generate_html(self, anchors, output_dir):
        """Generate HTML files for navigating anchors."""
        # Create output directory
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy static assets
        self._create_static_assets(output_dir)
        
        # Generate index.html
        self._generate_index_html(anchors, output_dir)
        
        # Generate type pages
        self._generate_type_pages(anchors, output_dir)
        
        # Generate file pages
        self._generate_file_pages(anchors, output_dir)
        
        return output_dir
    
    def _create_static_assets(self, output_dir):
        """Create static assets for the web interface."""
        # Create CSS file
        css_dir = output_dir / 'css'
        css_dir.mkdir(parents=True, exist_ok=True)
        
        with open(css_dir / 'style.css', 'w', encoding='utf-8') as f:
            f.write("""
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
}
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}
.header {
    background-color: #2196F3;
    color: white;
    padding: 20px;
    text-align: center;
    margin-bottom: 20px;
}
.nav {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
}
.nav a {
    margin: 0 10px;
    color: #2196F3;
    text-decoration: none;
    font-weight: bold;
}
.nav a:hover {
    text-decoration: underline;
}
.card {
    background-color: white;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    margin-bottom: 20px;
    padding: 20px;
}
.anchor-list {
    list-style-type: none;
    padding: 0;
}
.anchor-item {
    border-bottom: 1px solid #eee;
    padding: 10px 0;
}
.anchor-type {
    display: inline-block;
    background-color: #E3F2FD;
    color: #1976D2;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    margin-right: 5px;
}
.anchor-description {
    font-weight: bold;
}
.anchor-file {
    color: #757575;
    font-size: 0.9em;
}
.anchor-line {
    color: #757575;
    font-size: 0.9em;
}
.anchor-context {
    margin-top: 5px;
    padding: 5px;
    background-color: #f5f5f5;
    border-radius: 3px;
    font-family: monospace;
    white-space: pre-wrap;
}
.search-container {
    margin-bottom: 20px;
}
.search-input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 1em;
}
.type-list, .file-list {
    display: flex;
    flex-wrap: wrap;
}
.type-item, .file-item {
    margin: 5px;
}
.type-link, .file-link {
    display: inline-block;
    background-color: #E3F2FD;
    color: #1976D2;
    padding: 5px 10px;
    border-radius: 5px;
    text-decoration: none;
}
.type-link:hover, .file-link:hover {
    background-color: #BBDEFB;
}
            """)
        
        # Create JavaScript file
        js_dir = output_dir / 'js'
        js_dir.mkdir(parents=True, exist_ok=True)
        
        with open(js_dir / 'script.js', 'w', encoding='utf-8') as f:
            f.write("""
document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            const anchorItems = document.querySelectorAll('.anchor-item');
            
            anchorItems.forEach(function(item) {
                const description = item.querySelector('.anchor-description').textContent.toLowerCase();
                const context = item.querySelector('.anchor-context').textContent.toLowerCase();
                const file = item.querySelector('.anchor-file').textContent.toLowerCase();
                
                if (description.includes(query) || context.includes(query) || file.includes(query)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
});
            """)
    
    def _generate_index_html(self, anchors, output_dir):
        """Generate the index.html file."""
        # Get unique anchor types
        anchor_types = set()
        for anchor in anchors:
            anchor_types.add(anchor.get('type', 'unknown'))
        
        # Get unique files
        files = set()
        for anchor in anchors:
            files.add(anchor.get('file', ''))
        
        # Generate HTML
        with open(output_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Memory Anchor Navigator</title>
    <link rel="stylesheet" href="css/style.css">
    <script src="js/script.js"></script>
</head>
<body>
    <div class="header">
        <h1>Memory Anchor Navigator</h1>
        <p>Explore the semantic structure of your codebase</p>
    </div>
    
    <div class="container">
        <div class="nav">
            <a href="index.html">Home</a>
            <a href="#types">Types</a>
            <a href="#files">Files</a>
        </div>
        
        <div class="card">
            <h2>Overview</h2>
            <p>Total anchors: {len(anchors)}</p>
            <p>Anchor types: {len(anchor_types)}</p>
            <p>Files: {len(files)}</p>
        </div>
        
        <div class="card" id="types">
            <h2>Anchor Types</h2>
            <div class="type-list">
                {' '.join(f'<div class="type-item"><a href="types/{anchor_type}.html" class="type-link">{anchor_type}</a></div>' for anchor_type in sorted(anchor_types))}
            </div>
        </div>
        
        <div class="card" id="files">
            <h2>Files</h2>
            <div class="file-list">
                {' '.join(f'<div class="file-item"><a href="files/{self._file_to_html_name(file)}.html" class="file-link">{Path(file).name}</a></div>' for file in sorted(files))}
            </div>
        </div>
        
        <div class="card">
            <h2>All Anchors</h2>
            <div class="search-container">
                <input type="text" id="search-input" class="search-input" placeholder="Search anchors...">
            </div>
            <ul class="anchor-list">
                {self._generate_anchor_list_html(anchors)}
            </ul>
        </div>
    </div>
</body>
</html>""")
    
    def _generate_type_pages(self, anchors, output_dir):
        """Generate pages for each anchor type."""
        # Create types directory
        types_dir = output_dir / 'types'
        types_dir.mkdir(parents=True, exist_ok=True)
        
        # Group anchors by type
        anchors_by_type = {}
        for anchor in anchors:
            anchor_type = anchor.get('type', 'unknown')
            if anchor_type not in anchors_by_type:
                anchors_by_type[anchor_type] = []
            anchors_by_type[anchor_type].append(anchor)
        
        # Generate a page for each type
        for anchor_type, type_anchors in anchors_by_type.items():
            with open(types_dir / f'{anchor_type}.html', 'w', encoding='utf-8') as f:
                f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{anchor_type} Anchors - Memory Anchor Navigator</title>
    <link rel="stylesheet" href="../css/style.css">
    <script src="../js/script.js"></script>
</head>
<body>
    <div class="header">
        <h1>{anchor_type} Anchors</h1>
        <p>Memory anchors of type '{anchor_type}'</p>
    </div>
    
    <div class="container">
        <div class="nav">
            <a href="../index.html">Home</a>
            <a href="../index.html#types">Types</a>
            <a href="../index.html#files">Files</a>
        </div>
        
        <div class="card">
            <h2>Overview</h2>
            <p>Total {anchor_type} anchors: {len(type_anchors)}</p>
        </div>
        
        <div class="card">
            <h2>{anchor_type} Anchors</h2>
            <div class="search-container">
                <input type="text" id="search-input" class="search-input" placeholder="Search anchors...">
            </div>
            <ul class="anchor-list">
                {self._generate_anchor_list_html(type_anchors)}
            </ul>
        </div>
    </div>
</body>
</html>""")
    
    def _generate_file_pages(self, anchors, output_dir):
        """Generate pages for each file."""
        # Create files directory
        files_dir = output_dir / 'files'
        files_dir.mkdir(parents=True, exist_ok=True)
        
        # Group anchors by file
        anchors_by_file = {}
        for anchor in anchors:
            file_path = anchor.get('file', '')
            if file_path not in anchors_by_file:
                anchors_by_file[file_path] = []
            anchors_by_file[file_path].append(anchor)
        
        # Generate a page for each file
        for file_path, file_anchors in anchors_by_file.items():
            file_name = Path(file_path).name
            html_name = self._file_to_html_name(file_path)
            
            with open(files_dir / f'{html_name}.html', 'w', encoding='utf-8') as f:
                f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{file_name} Anchors - Memory Anchor Navigator</title>
    <link rel="stylesheet" href="../css/style.css">
    <script src="../js/script.js"></script>
</head>
<body>
    <div class="header">
        <h1>{file_name} Anchors</h1>
        <p>Memory anchors in '{file_path}'</p>
    </div>
    
    <div class="container">
        <div class="nav">
            <a href="../index.html">Home</a>
            <a href="../index.html#types">Types</a>
            <a href="../index.html#files">Files</a>
        </div>
        
        <div class="card">
            <h2>Overview</h2>
            <p>Total anchors in this file: {len(file_anchors)}</p>
        </div>
        
        <div class="card">
            <h2>Anchors in {file_name}</h2>
            <div class="search-container">
                <input type="text" id="search-input" class="search-input" placeholder="Search anchors...">
            </div>
            <ul class="anchor-list">
                {self._generate_anchor_list_html(file_anchors)}
            </ul>
        </div>
    </div>
</body>
</html>""")
    
    def _generate_anchor_list_html(self, anchors):
        """Generate HTML for a list of anchors."""
        html = ""
        for anchor in sorted(anchors, key=lambda a: (a.get('file', ''), a.get('line', 0))):
            file_path = anchor.get('file', '')
            file_name = Path(file_path).name
            anchor_type = anchor.get('type', 'unknown')
            description = anchor.get('description', '')
            line = anchor.get('line', 0)
            context = anchor.get('context', '')
            
            html += f"""
                <li class="anchor-item">
                    <span class="anchor-type">{anchor_type}</span>
                    <span class="anchor-description">{description}</span>
                    <div>
                        <span class="anchor-file">{file_path}</span>
                        <span class="anchor-line">Line {line}</span>
                    </div>
                    <div class="anchor-context">{context}</div>
                </li>"""
        
        return html
    
    def _file_to_html_name(self, file_path):
        """Convert a file path to a valid HTML file name."""
        # Replace invalid characters with underscores
        return re.sub(r'[^\w\-]', '_', file_path)
    
    def start_server(self, directory, port=8000):
        """Start a local HTTP server to serve the navigator."""
        os.chdir(directory)
        
        handler = SimpleHTTPRequestHandler
        httpd = socketserver.TCPServer(("", port), handler)
        
        print(f"Serving at http://localhost:{port}")
        print("Press Ctrl+C to stop the server")
        
        # Open browser
        webbrowser.open(f"http://localhost:{port}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped")
    
    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None

def main():
    parser = argparse.ArgumentParser(description="Navigate memory anchors in a web interface")
    parser.add_argument("anchor_file", help="Memory anchor file (JSON or YAML)")
    parser.add_argument("--output-dir", help="Output directory for generated files")
    parser.add_argument("--port", type=int, default=8000, help="Port for the HTTP server")
    parser.add_argument("--no-server", action="store_true", help="Generate files but don't start server")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    navigator = AnchorNavigator(verbose=args.verbose)
    
    try:
        # Load anchors
        anchors = navigator.load_anchors(args.anchor_file)
        
        if not anchors:
            print("No anchors found")
            return
        
        # Determine output directory
        if args.output_dir:
            output_dir = args.output_dir
        else:
            # Create temporary directory
            navigator.temp_dir = tempfile.mkdtemp(prefix="anchor_navigator_")
            output_dir = navigator.temp_dir
        
        # Generate HTML
        output_dir = navigator.generate_html(anchors, output_dir)
        
        print(f"Generated navigator files in {output_dir}")
        
        # Start server if requested
        if not args.no_server:
            navigator.start_server(output_dir, port=args.port)
    
    finally:
        # Clean up
        navigator.cleanup()

if __name__ == "__main__":
    main() 