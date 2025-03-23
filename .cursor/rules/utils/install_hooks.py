#!/usr/bin/env python3
"""
Install the Pine Script linter as a pre-commit hook.
"""

import os
import sys
import shutil
import stat

def main():
    """Install the Pine Script linter as a pre-commit hook."""
    # Get the root directory of the git repository
    try:
        import subprocess
        git_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], 
            universal_newlines=True
        ).strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: Could not determine git repository root.")
        print("Make sure you're in a git repository and git is installed.")
        sys.exit(1)
    
    # Path to the hooks directory
    hooks_dir = os.path.join(git_root, ".git", "hooks")
    
    # Path to the pre-commit hook
    pre_commit_path = os.path.join(hooks_dir, "pre-commit")
    
    # Path to the Pine Script linter
    linter_path = os.path.abspath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "pine_linter.py"
    ))
    
    # Create the pre-commit hook
    with open(pre_commit_path, "w") as f:
        f.write(f"""#!/bin/sh
# Pine Script linter pre-commit hook

# Get all staged Pine Script files
files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\\.(pine|pinescript)$')

if [ -n "$files" ]; then
    echo "Running Pine Script linter on staged files..."
    python "{linter_path}" $files
    if [ $? -ne 0 ]; then
        echo "Pine Script linter found issues. Please fix them before committing."
        exit 1
    fi
fi

exit 0
""")
    
    # Make the pre-commit hook executable
    os.chmod(pre_commit_path, os.stat(pre_commit_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    print(f"Pine Script linter pre-commit hook installed at {pre_commit_path}")
    print("The linter will run automatically when you commit Pine Script files.")

if __name__ == "__main__":
    main() 