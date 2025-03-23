#!/usr/bin/env python3

"""
Central configuration for Cursor rules and analysis scripts.
This provides shared settings and integration points.
"""

import os
import yaml
import json
from pathlib import Path

class CursorConfig:
    """Central configuration manager for Cursor rules and scripts."""
    
    def __init__(self, config_path=None):
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), 'config.yaml')
        self.config = self._load_config()
        self.rules_dir = os.path.dirname(__file__)
        
    def _load_config(self):
        """Load configuration from YAML file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def get_rule_files(self):
        """Get all rule files (.mdc) in the rules directory."""
        rule_files = []
        for root, _, files in os.walk(self.rules_dir):
            for file in files:
                if file.endswith('.mdc'):
                    rule_files.append(os.path.join(root, file))
        return rule_files
    
    def get_rule_metadata(self, rule_file):
        """Extract metadata from a rule file."""
        with open(rule_file, 'r') as f:
            content = f.read()
            
        # Extract YAML frontmatter
        if content.startswith('---'):
            end_idx = content.find('---', 3)
            if end_idx != -1:
                frontmatter = content[3:end_idx].strip()
                try:
                    return yaml.safe_load(frontmatter)
                except:
                    return {}
        return {}
    
    def get_all_rule_metadata(self):
        """Get metadata from all rule files."""
        metadata = {}
        for rule_file in self.get_rule_files():
            rel_path = os.path.relpath(rule_file, self.rules_dir)
            metadata[rel_path] = self.get_rule_metadata(rule_file)
        return metadata
    
    def get_script_paths(self):
        """Get all Python script paths."""
        script_paths = []
        for root, _, files in os.walk(self.rules_dir):
            for file in files:
                if file.endswith('.py') and file != '__init__.py' and file != 'config.py':
                    script_paths.append(os.path.join(root, file))
        return script_paths
    
    def get_integration_map(self):
        """Map rules to related scripts based on directory and content."""
        integration_map = {}
        rule_metadata = self.get_all_rule_metadata()
        
        for rule_path, metadata in rule_metadata.items():
            rule_dir = os.path.dirname(rule_path)
            rule_name = os.path.basename(rule_path).replace('.mdc', '')
            
            # Find related scripts in the same directory
            related_scripts = []
            for script_path in self.get_script_paths():
                script_dir = os.path.dirname(os.path.relpath(script_path, self.rules_dir))
                if script_dir == rule_dir or rule_name in os.path.basename(script_path):
                    related_scripts.append(script_path)
            
            integration_map[rule_path] = {
                'metadata': metadata,
                'related_scripts': related_scripts
            }
        
        return integration_map

# Singleton instance
config = CursorConfig() 