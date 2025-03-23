#!/usr/bin/env python3
# pine_test_cleanup.py - Tool to identify Pine Script test files that are candidates for cleanup

import os
import re
import subprocess
from datetime import datetime, timedelta
import sys
import difflib
import hashlib

def is_git_repository(directory="."):
    """Check if the directory is a git repository."""
    return os.path.isdir(os.path.join(directory, ".git"))

def get_git_last_modified(file_path):
    """Get the date when a file was last modified in git."""
    if not is_git_repository():
        return None
        
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%at", file_path],
            capture_output=True, text=True, check=True
        )
        if result.stdout.strip():
            timestamp = int(result.stdout.strip())
            return datetime.fromtimestamp(timestamp)
        return None
    except subprocess.CalledProcessError:
        return None

def is_referenced_in_code(file_name, extensions=['.ts', '.js', '.sh', '.md']):
    """Check if a file is referenced in other code files."""
    file_base = os.path.basename(file_name)
    search_pattern = re.escape(file_base)
    
    for ext in extensions:
        try:
            result = subprocess.run(
                ["grep", "-r", search_pattern, "--include", f"*{ext}", "."],
                capture_output=True, text=True
            )
            if result.stdout:
                return True
        except subprocess.CalledProcessError:
            pass
    return False

def is_essential_test_file(file_name):
    """Check if the file is one of the essential test files we want to keep."""
    essential_files = [
        "array_destructuring_test.pine",
        "array_type_test.pine",
        "function_params_test.pine",
        "max_bars_back_test.pine",
        "string_literals_test.pine", 
        "balance_test.pine",
        "user_example_test.pine",
        "test_linter.pine"
    ]
    return os.path.basename(file_name) in essential_files

def calculate_file_similarity(file1, file2):
    """Calculate similarity between two files."""
    try:
        with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
            content1 = f1.read()
            content2 = f2.read()
            
            # Calculate similarity using difflib
            seq = difflib.SequenceMatcher(None, content1, content2)
            return seq.ratio()
    except Exception as e:
        print(f"Error comparing files {file1} and {file2}: {e}")
        return 0.0

def find_similar_files(files, threshold=0.7):
    """Find files that are similar above a certain threshold."""
    similar_groups = []
    
    for i, file1 in enumerate(files):
        current_group = [file1]
        for j, file2 in enumerate(files):
            if i != j:  # Don't compare a file with itself
                similarity = calculate_file_similarity(file1, file2)
                if similarity > threshold:
                    current_group.append(file2)
        
        if len(current_group) > 1:  # If we found similar files
            similar_groups.append(current_group)
    
    # Remove duplicates (a file can be in multiple groups)
    unique_groups = []
    for group in similar_groups:
        if not any(set(group).issubset(set(existing_group)) for existing_group in unique_groups):
            unique_groups.append(group)
    
    return unique_groups

def is_single_purpose_test(file_path):
    """Check if a file is likely a single-purpose test."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            
            # Check for indicators of a single-purpose test
            single_purpose_indicators = [
                "simple test",
                "specific test",
                "single test",
                "test case",
                "test for issue",
                "fix for",
                "minimal test"
            ]
            
            # Check if file is very small (likely a simple test)
            is_small = len(content.splitlines()) < 20
            
            # Check for indicators in content
            has_indicators = any(indicator in content for indicator in single_purpose_indicators)
            
            # Check if it has a highly specific name
            specific_name_patterns = [
                r"simple_.*test",
                r".*_simple_test",
                r"minimal_.*",
                r"test_.*_detection",
                r".*broken.*",
                r".*excessive.*"
            ]
            is_specific_name = any(re.match(pattern, os.path.basename(file_path).lower()) for pattern in specific_name_patterns)
            
            return is_small or has_indicators or is_specific_name
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return False

def is_duplicate_of_essential(file_path, essential_files):
    """Check if a file is a duplicate or subset of an essential file."""
    if is_essential_test_file(file_path):
        return False
        
    # Get absolute paths of essential files
    essential_paths = []
    for root, _, files in os.walk("."):
        for file in files:
            if is_essential_test_file(file):
                essential_paths.append(os.path.join(root, file))
    
    # Check similarity with each essential file
    for essential_path in essential_paths:
        if os.path.exists(essential_path):
            similarity = calculate_file_similarity(file_path, essential_path)
            if similarity > 0.6:  # 60% similar is likely covering the same functionality
                return True
    
    return False

def find_cleanup_candidates(directory=".", days_threshold=None):
    """Find Pine Script test files that are candidates for cleanup."""
    cleanup_candidates = []
    test_patterns = [
        r".*_test\.pine$", 
        r"test_.*\.pine$",
        r".*example.*\.pine$",
        r".*debug.*\.pine$",
        r".*format.*\.pine$",
        r".*simple.*\.pine$",
        r".*broken.*\.pine$"
    ]
    
    # Combined pattern for all test files
    combined_pattern = re.compile("|".join(test_patterns))
    
    cutoff_date = datetime.now() - timedelta(days=days_threshold) if days_threshold else None
    
    # First, collect all test files
    test_files = []
    for root, _, files in os.walk(directory):
        # Skip the .cursor directory
        if ".cursor" in root:
            continue
            
        for file in files:
            if combined_pattern.match(file) and file.endswith('.pine'):
                file_path = os.path.join(root, file)
                if not is_essential_test_file(file):
                    test_files.append(file_path)
    
    # Find duplicate files
    similar_groups = find_similar_files(test_files, threshold=0.7)
    
    # Process each test file
    for file_path in test_files:
        # Skip essential test files (double-check)
        if is_essential_test_file(file_path):
            continue
            
        # Get last modified date
        last_modified = get_git_last_modified(file_path)
        
        # If no git history (or not a git repo), use file system modified time
        if last_modified is None:
            try:
                mtime = os.path.getmtime(file_path)
                last_modified = datetime.fromtimestamp(mtime)
            except OSError:
                last_modified = datetime.now()  # Fallback
        
        # Check if file is old enough (if threshold provided)
        is_old = cutoff_date and last_modified < cutoff_date
        
        # Check if file is referenced elsewhere
        referenced = is_referenced_in_code(file_path)
        
        # Check if it's a single-purpose test
        single_purpose = is_single_purpose_test(file_path)
        
        # Check if it's a duplicate or similar to an essential file
        duplicate_of_essential = is_duplicate_of_essential(file_path, test_files)
        
        # Check if it's in a similarity group
        in_similarity_group = any(file_path in group for group in similar_groups)
        
        # If the file is a duplicate, a single-purpose test, or old and not referenced,
        # consider it a cleanup candidate
        if duplicate_of_essential or single_purpose or in_similarity_group or (is_old and not referenced):
            reasons = []
            if is_old:
                reasons.append("old")
            if not referenced:
                reasons.append("not referenced")
            if single_purpose:
                reasons.append("single purpose")
            if duplicate_of_essential:
                reasons.append("duplicate of essential file")
            if in_similarity_group:
                reasons.append("similar to other files")
                
            cleanup_candidates.append({
                'path': file_path,
                'last_modified': last_modified,
                'referenced': referenced,
                'reasons': reasons,
                'similarity_group': next((group for group in similar_groups if file_path in group), None)
            })
    
    return cleanup_candidates, similar_groups

def analyze_file_content(file_path):
    """Analyze the file content to determine if it's a test file that might be obsolete."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Look for indicators that this is a test created for a specific fix
        indicators = {
            'test_purpose': re.search(r'Test for|Test file for|Testing|This file tests', content, re.IGNORECASE) is not None,
            'specific_bug': re.search(r'bug|issue|fix|problem', content, re.IGNORECASE) is not None,
            'temporary': re.search(r'temporary|temp|just for testing', content, re.IGNORECASE) is not None,
            'cleanup_candidate': re.search(r'CLEANUP-CANDIDATE', content) is not None
        }
        
        return indicators
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return {}

def count_test_files(directory="."):
    """Count the number of test files in the root directory."""
    count = 0
    test_pattern = re.compile(r".*test.*\.pine$|.*example.*\.pine$", re.IGNORECASE)
    
    for item in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, item)) and test_pattern.match(item):
            count += 1
    
    return count

def create_cleanup_script(candidates, is_git_repo):
    """Create a cleanup script based on the candidates."""
    cleanup_script = "cleanup_test_files.sh"
    backup_dir = "old_test_files_backup_" + datetime.now().strftime('%Y%m%d')
    
    with open(cleanup_script, 'w') as f:
        f.write("#!/bin/bash\n\n")
        f.write("# Auto-generated cleanup script for Pine Script test files\n")
        f.write("# Generated on: " + datetime.now().strftime('%Y-%m-%d') + "\n\n")
        
        if is_git_repo:
            # Git repository commands
            f.write("# Create a cleanup branch\n")
            f.write("git checkout -b cleanup/pine-test-files-" + datetime.now().strftime('%Y%m%d') + "\n\n")
            f.write("# Remove cleanup candidates\n")
            for candidate in candidates:
                reason_str = ", ".join(candidate['reasons'])
                f.write(f"# Reason: {reason_str}\n")
                f.write(f"git rm {candidate['path']}\n\n")
            f.write("# Commit the changes\n")
            f.write('git commit -m "Cleanup obsolete Pine Script test files"\n\n')
            f.write("# Push the branch\n")
            f.write("git push origin cleanup/pine-test-files-" + datetime.now().strftime('%Y%m%d') + "\n")
        else:
            # Non-git repository commands
            f.write("# Create backup directory\n")
            f.write(f"mkdir -p {backup_dir}\n\n")
            f.write("# Move cleanup candidates to backup directory\n")
            for candidate in candidates:
                reason_str = ", ".join(candidate['reasons'])
                f.write(f"# Reason: {reason_str}\n")
                f.write(f"mv {candidate['path']} {backup_dir}/\n\n")
            f.write(f"echo \"Files have been moved to backup directory: {backup_dir}\"\n")
            f.write(f"echo \"To delete them permanently, run: rm -rf {backup_dir}\"\n")
    
    return cleanup_script

def main():
    days = 30
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
            print(f"Looking for files older than {days} days...")
        except ValueError:
            print(f"Invalid days value: {sys.argv[1]}. Using no age threshold.")
            days = None
    else:
        print("No age threshold specified. Considering all test files...")
        days = None
    
    # Check if this is a git repository
    is_git_repo = is_git_repository()
    if is_git_repo:
        print("Git repository detected. Using git commands for cleanup.")
    else:
        print("Not a git repository. Using standard file operations for cleanup.")
    
    # Count test files in root directory
    root_test_count = count_test_files()
    print(f"Found {root_test_count} test files in the root directory.")
    if root_test_count > 20:
        print("⚠️ The number of test files exceeds the recommended limit (20).")
        print("   Consider cleaning up some of these files.")
    
    candidates, similar_groups = find_cleanup_candidates(days_threshold=days)
    
    print(f"\nFound {len(candidates)} potential cleanup candidates:")
    
    # Group candidates by reason
    by_reason = {}
    for candidate in candidates:
        for reason in candidate['reasons']:
            if reason not in by_reason:
                by_reason[reason] = []
            by_reason[reason].append(candidate)
    
    # Print similar file groups
    if similar_groups:
        print("\n🔍 Similar File Groups (likely duplicates):")
        for i, group in enumerate(similar_groups):
            print(f"  Group {i+1}:")
            for file in group:
                print(f"    - {file}")
    
    # Print by reason
    for reason, files in by_reason.items():
        print(f"\n🔶 Files that are {reason}:")
        for candidate in files:
            content_analysis = analyze_file_content(candidate['path'])
            indicators = []
            if content_analysis.get('test_purpose', False):
                indicators.append("Test purpose")
            if content_analysis.get('specific_bug', False):
                indicators.append("Specific bug/fix")
            if content_analysis.get('temporary', False):
                indicators.append("Temporary file")
            if content_analysis.get('cleanup_candidate', False):
                indicators.append("Already marked for cleanup")
            
            indicators_str = ", ".join(indicators) if indicators else "No specific indicators"
            print(f"  - {candidate['path']} (Last modified: {candidate['last_modified'].strftime('%Y-%m-%d')}) - {indicators_str}")
    
    if not candidates:
        print("\n✅ No cleanup candidates found. Your codebase is clean!")
        return
        
    # Create the cleanup script
    cleanup_script = create_cleanup_script(candidates, is_git_repo)
        
    print(f"\n📝 Created cleanup script: {cleanup_script}")
    print("To make it executable: chmod +x " + cleanup_script)
    print("\nReview the script carefully before running it!")
    print("And remember to check each file manually before removing it.")
    
    # Show helper commands for manual review
    print("\n🔍 Helper commands for manually reviewing files:")
    for candidate in candidates[:3]:  # Show for the first few candidates
        print(f"  cat {candidate['path']} | less")
        print(f"  grep -r \"{os.path.basename(candidate['path'])}\" --include=\"*.sh\" --include=\"*.md\" --include=\"*.js\" --include=\"*.ts\" .")
        print()

if __name__ == "__main__":
    main() 