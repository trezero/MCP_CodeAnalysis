#!/usr/bin/env python3

"""
Rule loader for Python scripts.
This allows Python scripts to access and use rule definitions.
"""

import os
import yaml
from pathlib import Path
from .config import config

class RuleLoader:
    """Loads and provides access to rule definitions for Python scripts."""
    
    def __init__(self):
        self.rules_by_category = self._categorize_rules()
    
    def _categorize_rules(self):
        """Categorize rules by their parent directory."""
        rules_by_category = {}
        rule_metadata = config.get_all_rule_metadata()
        
        for rule_path, metadata in rule_metadata.items():
            category = os.path.dirname(rule_path)
            if category not in rules_by_category:
                rules_by_category[category] = []
            
            rules_by_category[category].append({
                'path': rule_path,
                'metadata': metadata
            })
        
        return rules_by_category
    
    def get_rules_for_category(self, category):
        """Get all rules for a specific category."""
        return self.rules_by_category.get(category, [])
    
    def get_rule_by_name(self, name):
        """Find a rule by name across all categories."""
        for category, rules in self.rules_by_category.items():
            for rule in rules:
                rule_name = os.path.basename(rule['path']).replace('.mdc', '')
                if rule_name == name:
                    return rule
        return None
    
    def get_globs_for_category(self, category):
        """Get all glob patterns for a category."""
        globs = []
        for rule in self.get_rules_for_category(category):
            if 'Globs' in rule['metadata']:
                if isinstance(rule['metadata']['Globs'], list):
                    globs.extend(rule['metadata']['Globs'])
                else:
                    globs.append(rule['metadata']['Globs'])
        return globs

# Singleton instance
rule_loader = RuleLoader() 