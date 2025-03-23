#!/usr/bin/env python3

"""Maturity Model Dashboard Generator

This script generates an interactive HTML dashboard for visualizing
component maturity across the codebase.

Maturity: beta

Why:
- Visual representation makes maturity patterns more apparent
- Interactive dashboard allows exploration of maturity data
- Timeline view shows progression of components through maturity levels
- Helps plan development efforts to mature experimental components
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from jinja2 import Environment, FileSystemLoader

class MaturityDashboard:
    """Generates an interactive dashboard for maturity visualization."""
    
    def __init__(self, template_dir=None):
        if template_dir is None:
            # Use default templates directory relative to this script
            template_dir = Path(__file__).parent / "templates"
        
        self.template_dir = Path(template_dir)
        
        # Create template directory if it doesn't exist
        if not self.template_dir.exists():
            self.template_dir.mkdir(parents=True)
            self._create_default_template()
        
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
    
    def _create_default_template(self):
        """Create a default HTML template if none exists."""
        template_path = self.template_dir / "dashboard_template.html"
        
        default_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Component Maturity Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .dashboard-title {
            text-align: center;
            margin-bottom: 30px;
        }
        .dashboard-container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .dashboard-summary {
            margin-bottom: 30px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }
        .chart-container {
            margin-bottom: 40px;
        }
        .component-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .component-table th, .component-table td {
            padding: 8px 12px;
            border: 1px solid #ddd;
            text-align: left;
        }
        .component-table th {
            background-color: #f2f2f2;
        }
        .component-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .experimental {
            background-color: #ffebee !important;
        }
        .beta {
            background-color: #e3f2fd !important;
        }
        .stable {
            background-color: #e8f5e9 !important;
        }
        .deprecated {
            background-color: #fff3e0 !important;
        }
        .filter-controls {
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f2f2f2;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="dashboard-title">
            <h1>Component Maturity Dashboard</h1>
            <p>Generated on {{ generated_date }}</p>
        </div>
        
        <div class="dashboard-summary">
            <h2>Summary</h2>
            <p>Total Components: {{ total_components }}</p>
            <p>Components by Maturity Level:</p>
            <ul>
                <li>Experimental: {{ experimental_count }} ({{ experimental_percent }}%)</li>
                <li>Beta: {{ beta_count }} ({{ beta_percent }}%)</li>
                <li>Stable: {{ stable_count }} ({{ stable_percent }}%)</li>
                <li>Deprecated: {{ deprecated_count }} ({{ deprecated_percent }}%)</li>
            </ul>
        </div>
        
        <div class="filter-controls">
            <h3>Filter Components</h3>
            <div id="maturity-filter"></div>
            <div id="filetype-filter"></div>
        </div>
        
        <div class="chart-container">
            <h2>Maturity Distribution</h2>
            {{ maturity_distribution_chart|safe }}
        </div>
        
        <div class="chart-container">
            <h2>Maturity by File Type</h2>
            {{ file_type_chart|safe }}
        </div>
        
        <div class="chart-container">
            <h2>Component Maturity Timeline</h2>
            <p>Shows when components were last modified, grouped by maturity level.</p>
            {{ timeline_chart|safe }}
        </div>
        
        <div class="component-table-container">
            <h2>Component Details</h2>
            <table class="component-table" id="componentTable">
                <thead>
                    <tr>
                        <th>Component Name</th>
                        <th>Maturity</th>
                        <th>File Type</th>
                        <th>Since Version</th>
                        <th>Next Level</th>
                        <th>Last Modified</th>
                    </tr>
                </thead>
                <tbody>
                    {% for component in components %}
                    <tr class="{{ component.maturity }}">
                        <td>{{ component.name }}</td>
                        <td>{{ component.maturity }}</td>
                        <td>{{ component.file_type }}</td>
                        <td>{{ component.since_version }}</td>
                        <td>{{ component.next_level if component.next_level else "N/A" }}</td>
                        <td>{{ component.last_modified }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        // Simple table filtering functionality
        document.addEventListener('DOMContentLoaded', function() {
            const table = document.getElementById('componentTable');
            const rows = table.getElementsByTagName('tr');
            
            // Add more sophisticated filtering if needed
        });
    </script>
</body>
</html>
"""
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(default_template)
    
    def generate_dashboard(self, maturity_report_path, output_path=None):
        """Generate an HTML dashboard from a maturity report."""
        # Load the maturity report
        try:
            with open(maturity_report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
        except Exception as e:
            print(f"Error loading maturity report: {e}")
            return
        
        if output_path is None:
            output_path = Path(maturity_report_path).parent / "maturity_dashboard.html"
        
        # Convert components to DataFrame for easier manipulation
        components_df = pd.DataFrame.from_dict(report['components'], orient='index')
        
        # Extract file types
        components_df['file_type'] = components_df['path'].apply(
            lambda x: os.path.splitext(x)[1][1:] if os.path.splitext(x)[1] else "unknown"
        )
        
        # Format dates for display
        components_df['last_modified'] = pd.to_datetime(components_df['last_modified']).dt.strftime('%Y-%m-%d')
        
        # Calculate summary statistics
        total_components = len(components_df)
        maturity_counts = components_df['maturity'].value_counts()
        
        # Create visualizations
        maturity_distribution_chart = self._create_maturity_distribution_chart(components_df)
        file_type_chart = self._create_file_type_chart(components_df)
        timeline_chart = self._create_timeline_chart(components_df)
        
        # Prepare template variables
        template_vars = {
            'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_components': total_components,
            'experimental_count': maturity_counts.get('experimental', 0),
            'beta_count': maturity_counts.get('beta', 0),
            'stable_count': maturity_counts.get('stable', 0),
            'deprecated_count': maturity_counts.get('deprecated', 0),
            'experimental_percent': round((maturity_counts.get('experimental', 0) / total_components) * 100 if total_components > 0 else 0, 1),
            'beta_percent': round((maturity_counts.get('beta', 0) / total_components) * 100 if total_components > 0 else 0, 1),
            'stable_percent': round((maturity_counts.get('stable', 0) / total_components) * 100 if total_components > 0 else 0, 1),
            'deprecated_percent': round((maturity_counts.get('deprecated', 0) / total_components) * 100 if total_components > 0 else 0, 1),
            'maturity_distribution_chart': maturity_distribution_chart,
            'file_type_chart': file_type_chart,
            'timeline_chart': timeline_chart,
            'components': components_df.to_dict('records')
        }
        
        # Render the template
        template = self.env.get_template('dashboard_template.html')
        output_html = template.render(**template_vars)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_html)
        
        print(f"Maturity dashboard generated at {output_path}")
    
    def _create_maturity_distribution_chart(self, df):
        """Create a pie chart of maturity distribution."""
        maturity_counts = df['maturity'].value_counts()
        
        fig = px.pie(
            names=maturity_counts.index,
            values=maturity_counts.values,
            color=maturity_counts.index,
            color_discrete_map={
                'experimental': '#ffcdd2',
                'beta': '#bbdefb',
                'stable': '#c8e6c9',
                'deprecated': '#ffe0b2'
            },
            title="Component Maturity Distribution"
        )
        
        fig.update_traces(textinfo='percent+label')
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def _create_file_type_chart(self, df):
        """Create a stacked bar chart of maturity by file type."""
        # Create a cross-tabulation of file type and maturity
        file_type_maturity = pd.crosstab(df['file_type'], df['maturity'])
        
        # Create stacked bar chart
        fig = px.bar(
            file_type_maturity,
            barmode='stack',
            color_discrete_map={
                'experimental': '#ffcdd2',
                'beta': '#bbdefb',
                'stable': '#c8e6c9',
                'deprecated': '#ffe0b2'
            },
            title="Component Maturity by File Type"
        )
        
        fig.update_layout(
            xaxis_title="File Type",
            yaxis_title="Number of Components",
            legend_title="Maturity Level"
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def _create_timeline_chart(self, df):
        """Create a timeline chart of component modifications by maturity level."""
        # Convert last_modified to datetime
        df['last_modified_dt'] = pd.to_datetime(df['last_modified'])
        
        # Sort by date
        df_sorted = df.sort_values('last_modified_dt')
        
        # Create a figure with subplots
        fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                            subplot_titles=("Experimental", "Beta", "Stable", "Deprecated"))
        
        # Colors for each maturity level
        colors = {
            'experimental': '#ffcdd2',
            'beta': '#bbdefb',
            'stable': '#c8e6c9',
            'deprecated': '#ffe0b2'
        }
        
        # Create a trace for each maturity level
        for i, maturity in enumerate(['experimental', 'beta', 'stable', 'deprecated']):
            level_df = df_sorted[df_sorted['maturity'] == maturity]
            
            if not level_df.empty:
                fig.add_trace(
                    go.Scatter(
                        x=level_df['last_modified_dt'],
                        y=[1] * len(level_df),  # All points on same y-level
                        mode='markers',
                        marker=dict(
                            size=12,
                            color=colors[maturity],
                            line=dict(width=1, color='gray')
                        ),
                        text=level_df['name'],
                        hovertemplate='<b>%{text}</b><br>Last Modified: %{x}<extra></extra>'
                    ),
                    row=i+1, col=1
                )
        
        # Update layout
        fig.update_layout(
            height=600,
            showlegend=False,
            hovermode='closest'
        )
        
        # Update y-axes to hide ticks and labels
        for i in range(1, 5):
            fig.update_yaxes(showticklabels=False, row=i, col=1)
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')

def main():
    parser = argparse.ArgumentParser(description="Generate maturity dashboard")
    parser.add_argument("report", help="Path to the maturity report JSON file")
    parser.add_argument("--output", help="Output HTML file path")
    parser.add_argument("--template-dir", help="Directory containing templates")
    args = parser.parse_args()
    
    dashboard = MaturityDashboard(template_dir=args.template_dir)
    dashboard.generate_dashboard(args.report, output_path=args.output)

if __name__ == "__main__":
    main() 