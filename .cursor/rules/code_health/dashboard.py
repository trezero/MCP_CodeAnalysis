#!/usr/bin/env python3
# MEMORY_ANCHOR: code_health_dashboard

"""Code Health Dashboard Generator

This script generates an HTML dashboard for code health metrics.

Maturity: beta

Why:
A visual dashboard makes it easier to monitor code health metrics over time
and identify areas that need attention. HTML format allows for easy sharing
and viewing in any browser.
"""

import os
import json
import datetime
import argparse
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Define paths
BASE_DIR = Path(__file__).parent.parent
METRICS_FILE = BASE_DIR / "code_health" / "metrics.json"
HISTORY_FILE = BASE_DIR / "code_health" / "history.json"
OUTPUT_FILE = BASE_DIR / "code_health" / "dashboard.html"

def load_metrics():
    """Load metrics from file."""
    if not os.path.exists(METRICS_FILE):
        print(f"Metrics file {METRICS_FILE} not found.")
        return None
    
    with open(METRICS_FILE, 'r') as f:
        return json.load(f)

def load_history():
    """Load metrics history from file."""
    if not os.path.exists(HISTORY_FILE):
        print(f"History file {HISTORY_FILE} not found.")
        return []
    
    with open(HISTORY_FILE, 'r') as f:
        return json.load(f)

def create_summary_section(metrics):
    """Create summary section for the dashboard."""
    overall = metrics["overall"]
    
    # Create summary figure
    fig = go.Figure()
    
    # Add summary metrics
    fig.add_trace(go.Indicator(
        mode="number+gauge+delta",
        value=overall["complexity"]["average"],
        title={"text": "Avg. Complexity"},
        domain={"x": [0, 0.3], "y": [0, 0.5]},
        gauge={
            "axis": {"range": [0, 10]},
            "bar": {"color": "darkblue"},
            "steps": [
                {"range": [0, 5], "color": "lightgreen"},
                {"range": [5, 7], "color": "yellow"},
                {"range": [7, 10], "color": "red"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 7
            }
        }
    ))
    
    fig.add_trace(go.Indicator(
        mode="number+gauge+delta",
        value=overall["maintainability"]["average"],
        title={"text": "Maintainability"},
        domain={"x": [0.35, 0.65], "y": [0, 0.5]},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "darkblue"},
            "steps": [
                {"range": [0, 40], "color": "red"},
                {"range": [40, 60], "color": "yellow"},
                {"range": [60, 100], "color": "lightgreen"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 40
            }
        }
    ))
    
    fig.add_trace(go.Indicator(
        mode="number+gauge+delta",
        value=overall["coverage"]["total"],
        title={"text": "Test Coverage (%)"},
        domain={"x": [0.7, 1], "y": [0, 0.5]},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "darkblue"},
            "steps": [
                {"range": [0, 50], "color": "red"},
                {"range": [50, 80], "color": "yellow"},
                {"range": [80, 100], "color": "lightgreen"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 80
            }
        }
    ))
    
    # Add code size metrics
    fig.add_trace(go.Indicator(
        mode="number",
        value=overall["raw"]["total_sloc"],
        title={"text": "Total SLOC"},
        domain={"x": [0, 0.3], "y": [0.6, 1]}
    ))
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=overall["raw"]["comment_ratio"],
        title={"text": "Comment Ratio"},
        number={"suffix": "x"},
        domain={"x": [0.35, 0.65], "y": [0.6, 1]}
    ))
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=overall["churn"]["average_churn_rate"],
        title={"text": "Avg. Churn Rate"},
        domain={"x": [0.7, 1], "y": [0.6, 1]}
    ))
    
    fig.update_layout(
        title="Code Health Summary",
        height=400
    )
    
    return fig

def create_metrics_over_time_section(history):
    """Create metrics over time section for the dashboard."""
    if not history:
        return None
    
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
    
    # Create figure
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Average Complexity", "Maintainability", "Test Coverage (%)", "Average Churn Rate")
    )
    
    fig.add_trace(
        go.Scatter(x=df["timestamp"], y=df["complexity"], mode="lines+markers", name="Complexity"),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df["timestamp"], y=df["maintainability"], mode="lines+markers", name="Maintainability"),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Scatter(x=df["timestamp"], y=df["coverage"], mode="lines+markers", name="Coverage"),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df["timestamp"], y=df["churn_rate"], mode="lines+markers", name="Churn Rate"),
        row=2, col=2
    )
    
    fig.update_layout(
        title="Metrics Over Time",
        height=600,
        showlegend=False
    )
    
    return fig

def create_file_metrics_section(metrics):
    """Create file metrics section for the dashboard."""
    files = metrics["files"]
    
    # Prepare data for complexity
    complexity_data = {
        file_path: data["complexity"]["average"]
        for file_path, data in files.items()
    }
    
    # Sort by complexity and get top 20
    complexity_data = dict(sorted(complexity_data.items(), key=lambda x: x[1], reverse=True)[:20])
    
    # Create complexity figure
    complexity_fig = px.bar(
        x=list(complexity_data.keys()),
        y=list(complexity_data.values()),
        title="Top 20 Files by Complexity",
        labels={"x": "File", "y": "Average Complexity"}
    )
    complexity_fig.update_layout(height=400, xaxis_tickangle=-45)
    
    # Prepare data for maintainability
    maintainability_data = {
        file_path: data["maintainability"]["maintainability_index"]
        for file_path, data in files.items()
    }
    
    # Sort by maintainability (ascending) and get bottom 20
    maintainability_data = dict(sorted(maintainability_data.items(), key=lambda x: x[1])[:20])
    
    # Create maintainability figure
    maintainability_fig = px.bar(
        x=list(maintainability_data.keys()),
        y=list(maintainability_data.values()),
        title="Bottom 20 Files by Maintainability",
        labels={"x": "File", "y": "Maintainability Index"}
    )
    maintainability_fig.update_layout(height=400, xaxis_tickangle=-45)
    
    # Prepare data for churn
    churn_data = {
        file_path: data["churn"]["churn_rate"]
        for file_path, data in files.items()
        if data["churn"]["commits"] > 0
    }
    
    # Sort by churn rate and get top 20
    churn_data = dict(sorted(churn_data.items(), key=lambda x: x[1], reverse=True)[:20])
    
    # Create churn figure
    churn_fig = px.bar(
        x=list(churn_data.keys()),
        y=list(churn_data.values()),
        title="Top 20 Files by Churn Rate",
        labels={"x": "File", "y": "Churn Rate"}
    )
    churn_fig.update_layout(height=400, xaxis_tickangle=-45)
    
    # Prepare data for coverage
    coverage_data = {
        file_path: data["coverage"]
        for file_path, data in files.items()
        if data["coverage"] > 0
    }
    
    # Sort by coverage (ascending) and get bottom 20
    coverage_data = dict(sorted(coverage_data.items(), key=lambda x: x[1])[:20])
    
    # Create coverage figure
    coverage_fig = px.bar(
        x=list(coverage_data.keys()),
        y=list(coverage_data.values()),
        title="Bottom 20 Files by Test Coverage",
        labels={"x": "File", "y": "Coverage (%)"}
    )
    coverage_fig.update_layout(height=400, xaxis_tickangle=-45)
    
    return complexity_fig, maintainability_fig, churn_fig, coverage_fig

def create_dashboard(metrics, history):
    """Create the dashboard HTML."""
    # Create summary section
    summary_fig = create_summary_section(metrics)
    
    # Create metrics over time section
    history_fig = create_metrics_over_time_section(history)
    
    # Create file metrics section
    complexity_fig, maintainability_fig, churn_fig, coverage_fig = create_file_metrics_section(metrics)
    
    # Create HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Code Health Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                padding: 20px;
                font-family: Arial, sans-serif;
            }}
            .dashboard-header {{
                margin-bottom: 30px;
            }}
            .dashboard-section {{
                margin-bottom: 30px;
                padding: 20px;
                border-radius: 5px;
                background-color: #f8f9fa;
            }}
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <div class="dashboard-header">
                <h1>Code Health Dashboard</h1>
                <p>Generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            
            <div class="dashboard-section">
                <div id="summary-chart"></div>
            </div>
            
            <div class="dashboard-section">
                <div id="history-chart"></div>
            </div>
            
            <div class="dashboard-section">
                <div class="row">
                    <div class="col-md-6">
                        <div id="complexity-chart"></div>
                    </div>
                    <div class="col-md-6">
                        <div id="maintainability-chart"></div>
                    </div>
                </div>
            </div>
            
            <div class="dashboard-section">
                <div class="row">
                    <div class="col-md-6">
                        <div id="churn-chart"></div>
                    </div>
                    <div class="col-md-6">
                        <div id="coverage-chart"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Summary chart
            var summaryData = {summary_fig.to_json()};
            Plotly.newPlot('summary-chart', summaryData.data, summaryData.layout);
            
            // History chart
            {"var historyData = " + history_fig.to_json() + ";" if history_fig else ""}
            {"Plotly.newPlot('history-chart', historyData.data, historyData.layout);" if history_fig else ""}
            
            // Complexity chart
            var complexityData = {complexity_fig.to_json()};
            Plotly.newPlot('complexity-chart', complexityData.data, complexityData.layout);
            
            // Maintainability chart
            var maintainabilityData = {maintainability_fig.to_json()};
            Plotly.newPlot('maintainability-chart', maintainabilityData.data, maintainabilityData.layout);
            
            // Churn chart
            var churnData = {churn_fig.to_json()};
            Plotly.newPlot('churn-chart', churnData.data, churnData.layout);
            
            // Coverage chart
            var coverageData = {coverage_fig.to_json()};
            Plotly.newPlot('coverage-chart', coverageData.data, coverageData.layout);
        </script>
    </body>
    </html>
    """
    
    return html

def main():
    parser = argparse.ArgumentParser(description="Generate code health dashboard")
    parser.add_argument("--output", help="Output file path", default=str(OUTPUT_FILE))
    args = parser.parse_args()
    
    output_file = Path(args.output)
    
    # Load metrics
    metrics = load_metrics()
    if not metrics:
        return
    
    # Load history
    history = load_history()
    
    # Create dashboard
    print("Generating dashboard...")
    dashboard_html = create_dashboard(metrics, history)
    
    # Save dashboard
    with open(output_file, 'w') as f:
        f.write(dashboard_html)
    
    print(f"Dashboard saved to {output_file}")

if __name__ == "__main__":
    main() 