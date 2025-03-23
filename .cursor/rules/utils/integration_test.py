#!/usr/bin/env python3

"""
Integration test for Cursor rules and scripts.
This verifies that rules and scripts are properly integrated.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from config import config

def test_rule_script_integration():
    """Test integration between rules and scripts."""
    integration_map = config.get_integration_map()
    
    print(f"Found {len(integration_map)} rules with potential script integrations")
    
    for rule_path, integration_info in integration_map.items():
        print(f"\nTesting integration for rule: {rule_path}")
        
        metadata = integration_info['metadata']
        related_scripts = integration_info['related_scripts']
        
        print(f"  Rule metadata: {json.dumps(metadata, indent=2)}")
        print(f"  Related scripts: {len(related_scripts)}")
        
        for script_path in related_scripts:
            print(f"  Testing script: {script_path}")
            
            # Check if script is executable
            if not os.access(script_path, os.X_OK):
                print(f"    WARNING: Script is not executable")
                continue
            
            # Try to run script with --help to verify it works
            try:
                result = subprocess.run([script_path, '--help'], 
                                       capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"    SUCCESS: Script runs successfully")
                else:
                    print(f"    ERROR: Script returned non-zero exit code")
                    print(f"    {result.stderr.strip()}")
            except Exception as e:
                print(f"    ERROR: Failed to run script: {e}")

def main():
    test_rule_script_integration()

if __name__ == "__main__":
    main() 