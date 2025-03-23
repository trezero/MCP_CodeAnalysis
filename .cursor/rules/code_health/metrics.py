#!/usr/bin/env python3
# MEMORY_ANCHOR: code_health_metrics

"""Code Health Metrics Calculator

This script calculates various code health metrics including complexity,
test coverage, and code churn.

Maturity: beta

Why:
Tracking code health metrics helps identify areas of the codebase that
need attention, ensuring the codebase remains maintainable and robust.
Automated metrics provide an objective measure of code quality that can
be tracked over time.
"""

import os
import json
import glob
import subprocess
import datetime
import argparse
import re
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from radon.complexity import cc_visit
from radon.metrics import h_visit
from radon.raw import analyze

# Define paths
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "code_health"
METRICS_FILE = OUTPUT_DIR / "metrics.json"
HISTORY_FILE = OUTPUT_DIR / "history.json"
VISUALIZATIONS_DIR = OUTPUT_DIR / "visualizations"

def ensure_directories():
    """Ensure all necessary directories exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    VISUALIZATIONS_DIR.mkdir(parents=True, exist_ok=True)

def get_git_files():
    """Get all files tracked by git."""
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            check=True
        )
        return [file for file in result.stdout.splitlines() if os.path.exists(file)]
    except subprocess.CalledProcessError as e:
        print(f"Error getting git files: {e}")
        return []

def filter_files(files, extensions):
    """Filter files by extension."""
    return [file for file in files if any(file.endswith(ext) for ext in extensions)]

def calculate_complexity(file_path):
    """Calculate cyclomatic complexity for a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Use radon to calculate complexity
        results = cc_visit(content)
        
        # Calculate average complexity
        if results:
            total_complexity = sum(result.complexity for result in results)
            avg_complexity = total_complexity / len(results)
            max_complexity = max(result.complexity for result in results)
            return {
                "average": avg_complexity,
                "maximum": max_complexity,
                "total": total_complexity,
                "functions": len(results)
            }
        return {
            "average": 0,
            "maximum": 0,
            "total": 0,
            "functions": 0
        }
    except Exception as e:
        print(f"Error calculating complexity for {file_path}: {e}")
        return {
            "average": 0,
            "maximum": 0,
            "total": 0,
            "functions": 0
        }

def calculate_maintainability(file_path):
    """Calculate maintainability index for a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Use radon to calculate maintainability
        result = h_visit(content)
        
        if result:
            return {
                "maintainability_index": result.mi,
                "rank": result.rank
            }
        return {
            "maintainability_index": 0,
            "rank": "F"
        }
    except Exception as e:
        print(f"Error calculating maintainability for {file_path}: {e}")
        return {
            "maintainability_index": 0,
            "rank": "F"
        }

def calculate_raw_metrics(file_path):
    """Calculate raw metrics for a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Use radon to calculate raw metrics
        result = analyze(content)
        
        return {
            "loc": result.loc,
            "lloc": result.lloc,
            "sloc": result.sloc,
            "comments": result.comments,
            "multi": result.multi,
            "blank": result.blank,
            "single_comments": result.single_comments
        }
    except Exception as e:
        print(f"Error calculating raw metrics for {file_path}: {e}")
        return {
            "loc": 0,
            "lloc": 0,
            "sloc": 0,
            "comments": 0,
            "multi": 0,
            "blank": 0,
            "single_comments": 0
        }

def calculate_test_coverage():
    """Calculate test coverage using coverage.py."""
    try:
        # Run coverage
        subprocess.run(
            ["coverage", "run", "-m", "pytest"],
            capture_output=True,
            check=False
        )
        
        # Get coverage report
        result = subprocess.run(
            ["coverage", "json", "-o", "coverage.json"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Load coverage data
        if os.path.exists("coverage.json"):
            with open("coverage.json", 'r') as f:
                coverage_data = json.load(f)
            
            # Clean up
            os.remove("coverage.json")
            
            return {
                "total": coverage_data.get("totals", {}).get("percent_covered", 0),
                "files": {
                    file: data.get("summary", {}).get("percent_covered", 0)
                    for file, data in coverage_data.get("files", {}).items()
                }
            }
        
        return {
            "total": 0,
            "files": {}
        }
    except Exception as e:
        print(f"Error calculating test coverage: {e}")
        return {
            "total": 0,
            "files": {}
        }

def calculate_code_churn():
    """Calculate code churn (changes over time)."""
    try:
        # Get git log with stats
        result = subprocess.run(
            ["git", "log", "--numstat", "--format=%H,%at"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse git log
        commits = []
        current_commit = None
        current_timestamp = None
        
        for line in result.stdout.splitlines():
            if line.strip() == "":
                continue
            
            # Check if this is a commit line
            if "," in line and len(line.split(",")) == 2:
                if current_commit is not None:
                    commits.append({
                        "hash": current_commit,
                        "timestamp": current_timestamp,
                        "files": []
                    })
                
                parts = line.split(",")
                current_commit = parts[0]
                current_timestamp = int(parts[1])
                continue
            
            # Parse file stats
            parts = line.split("\t")
            if len(parts) == 3:
                try:
                    added = int(parts[0]) if parts[0] != "-" else 0
                    deleted = int(parts[1]) if parts[1] != "-" else 0
                    filename = parts[2]
                    
                    if current_commit is not None:
                        commits[-1]["files"].append({
                            "filename": filename,
                            "added": added,
                            "deleted": deleted
                        })
                except ValueError:
                    continue
        
        # Add the last commit
        if current_commit is not None and current_commit not in [c["hash"] for c in commits]:
            commits.append({
                "hash": current_commit,
                "timestamp": current_timestamp,
                "files": []
            })
        
        # Calculate churn by file
        file_churn = {}
        for commit in commits:
            for file_data in commit["files"]:
                filename = file_data["filename"]
                if filename not in file_churn:
                    file_churn[filename] = {
                        "added": 0,
                        "deleted": 0,
                        "commits": 0,
                        "last_modified": 0
                    }
                
                file_churn[filename]["added"] += file_data["added"]
                file_churn[filename]["deleted"] += file_data["deleted"]
                file_churn[filename]["commits"] += 1
                file_churn[filename]["last_modified"] = max(
                    file_churn[filename]["last_modified"],
                    commit["timestamp"]
                )
        
        # Calculate churn rate (changes per day)
        for filename, data in file_churn.items():
            # Convert timestamp to days since epoch
            days_since_epoch = data["last_modified"] / (60 * 60 * 24)
            
            # Calculate churn rate (changes per day)
            total_changes = data["added"] + data["deleted"]
            data["churn_rate"] = total_changes / max(1, data["commits"])
        
        return file_churn
    except Exception as e:
        print(f"Error calculating code churn: {e}")
        return {}

def calculate_metrics():
    """Calculate all metrics for the codebase."""
    # Get all files
    files = get_git_files()
    
    # Filter Python files
    python_files = filter_files(files, [".py"])
    
    # Calculate metrics for each file
    file_metrics = {}
    for file_path in python_files:
        print(f"Processing {file_path}...")
        file_metrics[file_path] = {
            "complexity": calculate_complexity(file_path),
            "maintainability": calculate_maintainability(file_path),
            "raw": calculate_raw_metrics(file_path)
        }
    
    # Calculate test coverage
    coverage = calculate_test_coverage()
    
    # Calculate code churn
    churn = calculate_code_churn()
    
    # Add churn and coverage to file metrics
    for file_path, metrics in file_metrics.items():
        metrics["coverage"] = coverage.get("files", {}).get(file_path, 0)
        metrics["churn"] = churn.get(file_path, {
            "added": 0,
            "deleted": 0,
            "commits": 0,
            "churn_rate": 0,
            "last_modified": 0
        })
    
    # Calculate overall metrics
    overall_metrics = {
        "complexity": {
            "average": sum(m["complexity"]["average"] for m in file_metrics.values()) / max(1, len(file_metrics)),
            "maximum": max((m["complexity"]["maximum"] for m in file_metrics.values()), default=0)
        },
        "maintainability": {
            "average": sum(m["maintainability"]["maintainability_index"] for m in file_metrics.values()) / max(1, len(file_metrics))
        },
        "raw": {
            "total_loc": sum(m["raw"]["loc"] for m in file_metrics.values()),
            "total_lloc": sum(m["raw"]["lloc"] for m in file_metrics.values()),
            "total_sloc": sum(m["raw"]["sloc"] for m in file_metrics.values()),
            "total_comments": sum(m["raw"]["comments"] for m in file_metrics.values()),
            "comment_ratio": sum(m["raw"]["comments"] for m in file_metrics.values()) / max(1, sum(m["raw"]["sloc"] for m in file_metrics.values()))
        },
        "coverage": {
            "total": coverage.get("total", 0)
        },
        "churn": {
            "total_added": sum(m["churn"]["added"] for m in file_metrics.values()),
            "total_deleted": sum(m["churn"]["deleted"] for m in file_metrics.values()),
            "total_commits": max((m["churn"]["commits"] for m in file_metrics.values()), default=0),
            "average_churn_rate": sum(m["churn"]["churn_rate"] for m in file_metrics.values()) / max(1, len(file_metrics))
        }
    }
    
    # Create final metrics object
    metrics = {
        "timestamp": datetime.datetime.now().isoformat(),
        "overall": overall_metrics,
        "files": file_metrics
    }
    
    return metrics

def save_metrics(metrics):
    """Save metrics to a file."""
    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    # Update history
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    
    # Add current metrics to history
    history_entry = {
        "timestamp": metrics["timestamp"],
        "overall": metrics["overall"]
    }
    history.append(history_entry)
    
    # Save history
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def generate_visualizations(metrics):
    """Generate visualizations from metrics."""
    # Create directory for visualizations
    os.makedirs(VISUALIZATIONS_DIR, exist_ok=True)
    
    # 1. Complexity by file
    complexity_data = {
        file_path: data["complexity"]["average"]
        for file_path, data in metrics["files"].items()
    }
    
    # Sort by complexity
    complexity_data = dict(sorted(complexity_data.items(), key=lambda x: x[1], reverse=True)[:20])
    
    plt.figure(figsize=(12, 8))
    plt.bar(complexity_data.keys(), complexity_data.values())
    plt.xticks(rotation=90)
    plt.title("Average Cyclomatic Complexity by File (Top 20)")
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_DIR / "complexity.png")
    plt.close()
    
    # 2. Maintainability by file
    maintainability_data = {
        file_path: data["maintainability"]["maintainability_index"]
        for file_path, data in metrics["files"].items()
    }
    
    # Sort by maintainability (ascending)
    maintainability_data = dict(sorted(maintainability_data.items(), key=lambda x: x[1])[:20])
    
    plt.figure(figsize=(12, 8))
    plt.bar(maintainability_data.keys(), maintainability_data.values())
    plt.xticks(rotation=90)
    plt.title("Maintainability Index by File (Bottom 20)")
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_DIR / "maintainability.png")
    plt.close()
    
    # 3. Code churn by file
    churn_data = {
        file_path: data["churn"]["churn_rate"]
        for file_path, data in metrics["files"].items()
        if data["churn"]["commits"] > 0
    }
    
    # Sort by churn rate
    churn_data = dict(sorted(churn_data.items(), key=lambda x: x[1], reverse=True)[:20])
    
    plt.figure(figsize=(12, 8))
    plt.bar(churn_data.keys(), churn_data.values())
    plt.xticks(rotation=90)
    plt.title("Code Churn Rate by File (Top 20)")
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_DIR / "churn.png")
    plt.close()
    
    # 4. Test coverage by file
    coverage_data = {
        file_path: data["coverage"]
        for file_path, data in metrics["files"].items()
        if data["coverage"] > 0
    }
    
    # Sort by coverage (ascending)
    coverage_data = dict(sorted(coverage_data.items(), key=lambda x: x[1])[:20])
    
    plt.figure(figsize=(12, 8))
    plt.bar(coverage_data.keys(), coverage_data.values())
    plt.xticks(rotation=90)
    plt.title("Test Coverage by File (Bottom 20)")
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_DIR / "coverage.png")
    plt.close()
    
    # 5. Metrics over time
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                "timestamp": entry["timestamp"],
                "complexity": entry["overall"]["complexity"]["average"],
                "maintainability": entry["overall"]["maintainability"]["average"],
                "coverage": entry["overall"]["coverage"]["total"],
                "churn_rate": entry["overall"]["churn"]["average_churn_rate"]
            }
            for entry in history
        ])
        
        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Sort by timestamp
        df = df.sort_values("timestamp")
        
        # Plot metrics over time
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        plt.plot(df["timestamp"], df["complexity"])
        plt.title("Average Complexity Over Time")
        plt.xticks(rotation=45)
        
        plt.subplot(2, 2, 2)
        plt.plot(df["timestamp"], df["maintainability"])
        plt.title("Average Maintainability Over Time")
        plt.xticks(rotation=45)
        
        plt.subplot(2, 2, 3)
        plt.plot(df["timestamp"], df["coverage"])
        plt.title("Test Coverage Over Time")
        plt.xticks(rotation=45)
        
        plt.subplot(2, 2, 4)
        plt.plot(df["timestamp"], df["churn_rate"])
        plt.title("Average Churn Rate Over Time")
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(VISUALIZATIONS_DIR / "metrics_over_time.png")
        plt.close()

def main():
    parser = argparse.ArgumentParser(description="Calculate code health metrics")
    parser.add_argument("--visualize-only", action="store_true", help="Only generate visualizations")
    args = parser.parse_args()
    
    ensure_directories()
    
    if not args.visualize_only:
        print("Calculating metrics...")
        metrics = calculate_metrics()
        save_metrics(metrics)
        print(f"Metrics saved to {METRICS_FILE}")
    else:
        # Load existing metrics
        if os.path.exists(METRICS_FILE):
            with open(METRICS_FILE, 'r') as f:
                metrics = json.load(f)
        else:
            print(f"Metrics file {METRICS_FILE} not found. Run without --visualize-only first.")
            return
    
    print("Generating visualizations...")
    generate_visualizations(metrics)
    print(f"Visualizations saved to {VISUALIZATIONS_DIR}")

if __name__ == "__main__":
    main() 