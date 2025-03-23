#!/usr/bin/env python3

"""Memory Anchor Search Tool

This script provides a command-line interface for searching memory anchors
and navigating to their locations in the codebase.

Maturity: beta

Why:
- Memory anchors are only useful if they can be easily found
- This tool makes it easy to search for anchors by type or description
- Helps developers quickly navigate to relevant parts of the codebase
- Enhances the value of memory anchors as a navigation aid
"""

import argparse
import json
import os
import re
from pathlib import Path
import yaml
import subprocess
import sys
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel

class AnchorSearchTool:
    """Provides search functionality for memory anchors."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.console = Console()
        self.anchors = []
    
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
                self.anchors = data['anchors']
            else:
                self.anchors = data
            
            if self.verbose:
                self.console.print(f"Loaded {len(self.anchors)} anchors from {anchor_file}")
            
            return True
        
        except Exception as e:
            self.console.print(f"[bold red]Error loading anchors:[/bold red] {e}")
            return False
    
    def search_anchors(self, query=None, anchor_type=None, file_pattern=None):
        """Search for anchors matching the given criteria."""
        results = []
        
        for anchor in self.anchors:
            # Check if anchor matches all specified criteria
            matches = True
            
            if query:
                # Search in description and context
                description = anchor.get('description', '').lower()
                context = anchor.get('context', '').lower()
                if query.lower() not in description and query.lower() not in context:
                    matches = False
            
            if anchor_type and matches:
                # Check anchor type
                if anchor.get('type', '').lower() != anchor_type.lower():
                    matches = False
            
            if file_pattern and matches:
                # Check file path
                file_path = anchor.get('file', '')
                if not re.search(file_pattern, file_path):
                    matches = False
            
            if matches:
                results.append(anchor)
        
        return results
    
    def display_results(self, results, show_context=True):
        """Display search results in a formatted table."""
        if not results:
            self.console.print("[yellow]No matching anchors found.[/yellow]")
            return
        
        table = Table(title=f"Found {len(results)} Memory Anchors")
        
        table.add_column("Type", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("File", style="blue")
        table.add_column("Line", style="magenta")
        if show_context:
            table.add_column("Context", style="dim")
        
        for i, anchor in enumerate(results):
            row = [
                anchor.get('type', ''),
                anchor.get('description', ''),
                Path(anchor.get('file', '')).name,
                str(anchor.get('line', 0))
            ]
            
            if show_context:
                row.append(anchor.get('context', ''))
            
            table.add_row(*row)
        
        self.console.print(table)
    
    def display_anchor_details(self, anchor):
        """Display detailed information about a specific anchor."""
        file_path = anchor.get('file', '')
        line_number = anchor.get('line', 0)
        
        # Display anchor information
        self.console.print(Panel(
            f"[bold cyan]Type:[/bold cyan] {anchor.get('type', '')}\n"
            f"[bold green]Description:[/bold green] {anchor.get('description', '')}\n"
            f"[bold blue]File:[/bold blue] {file_path}\n"
            f"[bold magenta]Line:[/bold magenta] {line_number}\n"
            f"[bold yellow]Context:[/bold yellow] {anchor.get('context', '')}"
        ))
        
        # Try to display file content around the anchor
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.readlines()
            
            # Get content around the anchor (5 lines before and after)
            start_line = max(0, line_number - 6)
            end_line = min(len(content), line_number + 5)
            
            # Extract the relevant lines
            code_snippet = ''.join(content[start_line:end_line])
            
            # Determine the language for syntax highlighting
            if file_path.endswith(('.js', '.jsx')):
                language = 'javascript'
            elif file_path.endswith(('.ts', '.tsx')):
                language = 'typescript'
            elif file_path.endswith('.py'):
                language = 'python'
            elif file_path.endswith(('.pine', '.pinescript')):
                language = 'pine'
            elif file_path.endswith('.md'):
                language = 'markdown'
            else:
                language = 'text'
            
            # Display the code snippet with syntax highlighting
            syntax = Syntax(
                code_snippet,
                language,
                line_numbers=True,
                start_line=start_line + 1,
                highlight_lines=[line_number]
            )
            
            self.console.print("\n[bold]Code Snippet:[/bold]")
            self.console.print(syntax)
        
        except Exception as e:
            self.console.print(f"[yellow]Could not display file content: {e}[/yellow]")
    
    def open_in_editor(self, anchor, editor_command=None):
        """Open the anchor location in an editor."""
        file_path = anchor.get('file', '')
        line_number = anchor.get('line', 0)
        
        if not os.path.exists(file_path):
            self.console.print(f"[bold red]Error:[/bold red] File {file_path} does not exist")
            return False
        
        try:
            # Determine editor command
            if editor_command:
                cmd = editor_command.split()
            elif 'EDITOR' in os.environ:
                cmd = [os.environ['EDITOR']]
            elif sys.platform == 'win32':
                cmd = ['notepad']
            else:
                cmd = ['vim']
            
            # Add file path and line number
            cmd.append(file_path)
            
            # Add line number parameter for common editors
            editor_name = os.path.basename(cmd[0]).lower()
            if editor_name in ['vim', 'vi', 'nvim']:
                cmd[0] = f"{cmd[0]} +{line_number}"
            elif editor_name in ['code', 'codium', 'vscode']:
                cmd.append(f"--goto")
                cmd.append(f"{file_path}:{line_number}")
            elif editor_name in ['subl', 'sublime_text']:
                cmd.append(f"{file_path}:{line_number}")
            
            # Execute command
            self.console.print(f"Opening {file_path}:{line_number} with {cmd[0]}...")
            subprocess.run(cmd)
            
            return True
        
        except Exception as e:
            self.console.print(f"[bold red]Error opening editor:[/bold red] {e}")
            return False
    
    def interactive_search(self, anchor_file):
        """Provide an interactive search interface."""
        # Load anchors
        if not self.load_anchors(anchor_file):
            return
        
        # Get unique anchor types
        anchor_types = set()
        for anchor in self.anchors:
            anchor_types.add(anchor.get('type', ''))
        
        # Display welcome message
        self.console.print(Panel(
            "[bold]Memory Anchor Search Tool[/bold]\n\n"
            f"Loaded {len(self.anchors)} anchors from {anchor_file}\n"
            f"Available anchor types: {', '.join(sorted(anchor_types))}\n\n"
            "Type 'help' for available commands, 'exit' to quit"
        ))
        
        # Interactive loop
        while True:
            try:
                command = self.console.input("\n[bold green]anchor-search>[/bold green] ")
                
                if command.lower() in ['exit', 'quit', 'q']:
                    break
                
                elif command.lower() in ['help', '?', 'h']:
                    self.console.print(Panel(
                        "[bold]Available Commands:[/bold]\n\n"
                        "search QUERY            - Search for anchors containing QUERY\n"
                        "type TYPE               - List anchors of a specific TYPE\n"
                        "file PATTERN            - List anchors in files matching PATTERN\n"
                        "list                    - List all anchors\n"
                        "show INDEX              - Show details for anchor at INDEX\n"
                        "open INDEX              - Open anchor at INDEX in editor\n"
                        "types                   - List all anchor types\n"
                        "help                    - Show this help message\n"
                        "exit                    - Exit the program"
                    ))
                
                elif command.lower() == 'list':
                    self.display_results(self.anchors, show_context=False)
                
                elif command.lower() == 'types':
                    self.console.print(", ".join(sorted(anchor_types)))
                
                elif command.lower().startswith('search '):
                    query = command[7:].strip()
                    results = self.search_anchors(query=query)
                    self.display_results(results)
                
                elif command.lower().startswith('type '):
                    anchor_type = command[5:].strip()
                    results = self.search_anchors(anchor_type=anchor_type)
                    self.display_results(results)
                
                elif command.lower().startswith('file '):
                    file_pattern = command[5:].strip()
                    results = self.search_anchors(file_pattern=file_pattern)
                    self.display_results(results)
                
                elif command.lower().startswith('show '):
                    try:
                        index = int(command[5:].strip())
                        if 0 <= index < len(self.anchors):
                            self.display_anchor_details(self.anchors[index])
                        else:
                            self.console.print("[bold red]Error:[/bold red] Invalid index")
                    except ValueError:
                        self.console.print("[bold red]Error:[/bold red] Invalid index")
                
                elif command.lower().startswith('open '):
                    try:
                        index = int(command[5:].strip())
                        if 0 <= index < len(self.anchors):
                            self.open_in_editor(self.anchors[index])
                        else:
                            self.console.print("[bold red]Error:[/bold red] Invalid index")
                    except ValueError:
                        self.console.print("[bold red]Error:[/bold red] Invalid index")
                
                else:
                    self.console.print("[yellow]Unknown command. Type 'help' for available commands.[/yellow]")
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.console.print(f"[bold red]Error:[/bold red] {e}")

def main():
    parser = argparse.ArgumentParser(description="Search for memory anchors")
    parser.add_argument("anchor_file", help="Memory anchor file (JSON or YAML)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # Create AnchorSearchTool instance
    tool = AnchorSearchTool(verbose=args.verbose)
    
    # Perform interactive search
    tool.interactive_search(args.anchor_file)

if __name__ == "__main__":
    main() 