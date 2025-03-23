#!/usr/bin/env python3

"""
@file metadata_dashboard.py
@version 1.0.0
@author MetadataTeam
@date 2023-11-25
@license MIT

@description
A dashboard for visualizing metadata extraction results.
This script creates an interactive web dashboard using Dash/Plotly
to display metadata coverage, quality, and trends from extraction reports.

@example
```bash
python metadata_dashboard.py --report ./metadata-output/metadata_report_20231125_120000.json
```

@dependencies
- dash
- plotly
- pandas
- json
- argparse
- os
"""

import os
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

try:
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from dash import Dash, html, dcc, callback, Output, Input
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("Warning: Dashboard dependencies not available. Please install with:")
    print("pip install dash plotly pandas")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class MetadataDashboard:
    """
    @class MetadataDashboard
    @description Dashboard for visualizing metadata extraction results
    
    This class provides methods to create an interactive web dashboard
    for visualizing and exploring metadata extraction reports.
    
    @stability beta
    @since 1.0.0
    @author MetadataTeam
    """
    
    def __init__(self, report_path: str):
        """
        @method __init__
        @description Initialize the dashboard with a report
        
        @param report_path Path to the metadata extraction report (JSON)
        """
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Required dependencies not available. Please install dash, plotly, and pandas.")
        
        self.report_path = report_path
        self.report_data = self._load_report(report_path)
        self.app = None
        
        logger.info(f"Initialized MetadataDashboard with report from {report_path}")
    
    def _load_report(self, report_path: str) -> Dict[str, Any]:
        """
        @method _load_report
        @description Load the metadata extraction report
        
        @param report_path Path to the report file
        @return Dictionary containing the report data
        
        @private
        """
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded report from {report_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to load report: {str(e)}")
            raise
    
    def _prepare_summary_data(self) -> pd.DataFrame:
        """
        @method _prepare_summary_data
        @description Prepare summary data for visualization
        
        @return DataFrame containing summary metrics
        
        @private
        """
        summary = self.report_data['summary']
        
        # Create a DataFrame for the summary metrics
        metrics = [
            {"Metric": "Total Files", "Value": summary['processed_files']},
            {"Metric": "Files with Metadata", "Value": summary['files_with_metadata']},
            {"Metric": "Files with Complete Metadata", "Value": summary['files_with_complete_metadata']},
            {"Metric": "Metadata Coverage (%)", "Value": round(summary['metadata_coverage'], 1)},
            {"Metric": "Complete Metadata Coverage (%)", "Value": round(summary['complete_metadata_coverage'], 1)}
        ]
        
        return pd.DataFrame(metrics)
    
    def _prepare_language_data(self) -> pd.DataFrame:
        """
        @method _prepare_language_data
        @description Prepare language data for visualization
        
        @return DataFrame containing language distribution
        
        @private
        """
        by_language = self.report_data['by_language']
        
        # Create a DataFrame for the language distribution
        language_data = [
            {"Language": lang, "Files": count}
            for lang, count in by_language.items()
        ]
        
        return pd.DataFrame(language_data)
    
    def _prepare_extension_data(self) -> pd.DataFrame:
        """
        @method _prepare_extension_data
        @description Prepare file extension data for visualization
        
        @return DataFrame containing file extension distribution
        
        @private
        """
        by_extension = self.report_data['by_file_extension']
        
        # Create a DataFrame for the extension distribution
        extension_data = [
            {"Extension": f".{ext}", "Files": count}
            for ext, count in by_extension.items()
        ]
        
        return pd.DataFrame(extension_data)
    
    def _prepare_missing_fields_data(self) -> pd.DataFrame:
        """
        @method _prepare_missing_fields_data
        @description Prepare missing fields data for visualization
        
        @return DataFrame containing missing fields
        
        @private
        """
        missing_fields = self.report_data['most_common_missing_fields']
        
        # Create a DataFrame for the missing fields
        missing_fields_data = [
            {"Field": field, "Count": count}
            for field, count in missing_fields.items()
        ]
        
        return pd.DataFrame(missing_fields_data)
    
    def _prepare_file_data(self) -> pd.DataFrame:
        """
        @method _prepare_file_data
        @description Prepare detailed file data for visualization
        
        @return DataFrame containing file-level data
        
        @private
        """
        file_results = self.report_data['file_results']
        
        # Create a DataFrame for the file results
        file_data = []
        
        for path, data in file_results.items():
            # Extract filename from path
            filename = os.path.basename(path)
            
            # Count total metadata fields
            total_fields = len(data['metadata'])
            
            # Count missing and invalid fields
            missing_fields = len(data['validation']['missing_fields'])
            invalid_fields = len(data['validation']['invalid_formats'])
            
            # Calculate completeness score (0-100)
            completeness = 100 if data['validation']['valid'] else (
                100 - (missing_fields + invalid_fields) * 10
            )
            completeness = max(0, min(100, completeness))
            
            file_data.append({
                "Filename": filename,
                "Path": path,
                "Fields": total_fields,
                "Missing": missing_fields,
                "Invalid": invalid_fields,
                "Completeness": completeness,
                "Valid": data['validation']['valid']
            })
        
        return pd.DataFrame(file_data)
    
    def create_dashboard(self) -> Dash:
        """
        @method create_dashboard
        @description Create the Dash application for the dashboard
        
        @return Dash application object
        """
        # Prepare data for visualizations
        summary_df = self._prepare_summary_data()
        language_df = self._prepare_language_data()
        extension_df = self._prepare_extension_data()
        missing_fields_df = self._prepare_missing_fields_data()
        file_df = self._prepare_file_data()
        
        # Create the Dash app
        app = Dash(__name__, title="Metadata Dashboard")
        
        # Define layout
        app.layout = html.Div([
            # Header
            html.Div([
                html.H1("Metadata Dashboard", className="dashboard-title"),
                html.H3(f"Report: {os.path.basename(self.report_path)}", className="report-title"),
                html.P(f"Generated on: {datetime.fromisoformat(self.report_data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
            ], className="header"),
            
            # Summary stats
            html.Div([
                html.H2("Summary", className="section-title"),
                html.Div([
                    # Coverage gauge
                    html.Div([
                        dcc.Graph(
                            figure=go.Figure(
                                go.Indicator(
                                    mode="gauge+number",
                                    value=summary_df[summary_df["Metric"] == "Metadata Coverage (%)"]["Value"].iloc[0],
                                    title={"text": "Metadata Coverage (%)"},
                                    gauge={
                                        "axis": {"range": [0, 100]},
                                        "bar": {"color": "green"},
                                        "steps": [
                                            {"range": [0, 50], "color": "red"},
                                            {"range": [50, 80], "color": "orange"},
                                            {"range": [80, 100], "color": "lightgreen"}
                                        ],
                                        "threshold": {
                                            "line": {"color": "green", "width": 4},
                                            "thickness": 0.75,
                                            "value": 95
                                        }
                                    }
                                )
                            )
                        )
                    ], className="summary-gauge"),
                    
                    # Completeness gauge
                    html.Div([
                        dcc.Graph(
                            figure=go.Figure(
                                go.Indicator(
                                    mode="gauge+number",
                                    value=summary_df[summary_df["Metric"] == "Complete Metadata Coverage (%)"]["Value"].iloc[0],
                                    title={"text": "Complete Metadata Coverage (%)"},
                                    gauge={
                                        "axis": {"range": [0, 100]},
                                        "bar": {"color": "green"},
                                        "steps": [
                                            {"range": [0, 50], "color": "red"},
                                            {"range": [50, 80], "color": "orange"},
                                            {"range": [80, 100], "color": "lightgreen"}
                                        ],
                                        "threshold": {
                                            "line": {"color": "green", "width": 4},
                                            "thickness": 0.75,
                                            "value": 90
                                        }
                                    }
                                )
                            )
                        )
                    ], className="summary-gauge")
                ], className="summary-gauges"),
                
                # Summary table
                html.Div([
                    html.Table([
                        html.Thead(
                            html.Tr([html.Th(col) for col in summary_df.columns])
                        ),
                        html.Tbody([
                            html.Tr([
                                html.Td(summary_df.iloc[i][col]) for col in summary_df.columns
                            ]) for i in range(len(summary_df))
                        ])
                    ], className="summary-table")
                ], className="summary-table-container")
            ], className="summary-section"),
            
            # Language and extension distribution
            html.Div([
                html.Div([
                    html.H2("Language Distribution", className="section-title"),
                    dcc.Graph(
                        figure=px.pie(
                            language_df, 
                            values="Files", 
                            names="Language",
                            title="Files by Language",
                            hole=0.3
                        )
                    )
                ], className="chart-container"),
                
                html.Div([
                    html.H2("File Extension Distribution", className="section-title"),
                    dcc.Graph(
                        figure=px.bar(
                            extension_df,
                            x="Extension",
                            y="Files",
                            title="Files by Extension",
                            color="Files",
                            color_continuous_scale="Viridis"
                        )
                    )
                ], className="chart-container")
            ], className="chart-row"),
            
            # Missing fields
            html.Div([
                html.H2("Missing Fields", className="section-title"),
                dcc.Graph(
                    figure=px.bar(
                        missing_fields_df,
                        x="Field",
                        y="Count",
                        title="Most Common Missing Fields",
                        color="Count",
                        color_continuous_scale="Reds"
                    )
                )
            ], className="chart-container"),
            
            # File details
            html.Div([
                html.H2("File Details", className="section-title"),
                html.P("Filter by completeness:"),
                dcc.RangeSlider(
                    id='completeness-slider',
                    min=0,
                    max=100,
                    step=5,
                    marks={i: f'{i}%' for i in range(0, 101, 10)},
                    value=[0, 100]
                ),
                html.Div(id='file-table-container')
            ], className="file-details-section"),
            
            # CSS for styling
            html.Style("""
                .dashboard-title { color: #2c3e50; text-align: center; margin-bottom: 10px; }
                .report-title { color: #7f8c8d; text-align: center; margin-top: 0; }
                .header { padding: 20px; background-color: #f8f9fa; border-bottom: 1px solid #dee2e6; margin-bottom: 20px; }
                .section-title { color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px; }
                .summary-section { margin-bottom: 30px; }
                .summary-gauges { display: flex; justify-content: space-around; flex-wrap: wrap; }
                .summary-gauge { width: 45%; min-width: 300px; }
                .summary-table { width: 100%; border-collapse: collapse; }
                .summary-table th, .summary-table td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                .summary-table th { background-color: #f2f2f2; }
                .summary-table-container { margin-top: 20px; }
                .chart-row { display: flex; flex-wrap: wrap; justify-content: space-between; margin-bottom: 30px; }
                .chart-container { width: 48%; min-width: 450px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); padding: 15px; border-radius: 5px; }
                .file-details-section { margin-top: 30px; }
                .file-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                .file-table th, .file-table td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                .file-table th { background-color: #f2f2f2; position: sticky; top: 0; }
                .file-table-container { height: 400px; overflow-y: auto; margin-top: 20px; }
                
                @media (max-width: 992px) {
                    .chart-container { width: 100%; }
                    .summary-gauge { width: 100%; }
                }
            """)
        ])
        
        # Define callback for file table filtering
        @app.callback(
            Output('file-table-container', 'children'),
            [Input('completeness-slider', 'value')]
        )
        def update_file_table(completeness_range):
            filtered_df = file_df[
                (file_df['Completeness'] >= completeness_range[0]) & 
                (file_df['Completeness'] <= completeness_range[1])
            ]
            
            # Sort by completeness descending
            filtered_df = filtered_df.sort_values('Completeness', ascending=False)
            
            # Create the table
            return html.Div([
                html.P(f"Showing {len(filtered_df)} files"),
                html.Div([
                    html.Table([
                        html.Thead(
                            html.Tr([html.Th(col) for col in ['Filename', 'Fields', 'Missing', 'Invalid', 'Completeness', 'Valid']])
                        ),
                        html.Tbody([
                            html.Tr([
                                html.Td(filtered_df.iloc[i]['Filename']),
                                html.Td(filtered_df.iloc[i]['Fields']),
                                html.Td(filtered_df.iloc[i]['Missing']),
                                html.Td(filtered_df.iloc[i]['Invalid']),
                                html.Td(f"{filtered_df.iloc[i]['Completeness']}%"),
                                html.Td("✓" if filtered_df.iloc[i]['Valid'] else "✗")
                            ]) for i in range(len(filtered_df))
                        ])
                    ], className="file-table")
                ], className="file-table-container")
            ])
        
        self.app = app
        return app
    
    def run_server(self, debug: bool = False, port: int = 8050) -> None:
        """
        @method run_server
        @description Run the dashboard server
        
        @param debug Whether to run in debug mode
        @param port Port number to run the server on
        """
        if self.app is None:
            self.create_dashboard()
        
        logger.info(f"Starting dashboard server on port {port}")
        print(f"Dashboard is running at http://localhost:{port}/")
        
        self.app.run_server(debug=debug, port=port)


def main():
    """
    @function main
    @description Main entry point for the script
    """
    if not DEPENDENCIES_AVAILABLE:
        print("Required dependencies not available. Please install with:")
        print("pip install dash plotly pandas")
        return
    
    parser = argparse.ArgumentParser(description='Visualize metadata extraction results')
    parser.add_argument('--report', '-r', help='Path to the metadata report file', required=True)
    parser.add_argument('--port', '-p', type=int, default=8050, help='Port to run the dashboard on')
    parser.add_argument('--debug', '-d', action='store_true', help='Run in debug mode')
    args = parser.parse_args()
    
    try:
        dashboard = MetadataDashboard(args.report)
        dashboard.run_server(debug=args.debug, port=args.port)
    except Exception as e:
        logger.error(f"Error running dashboard: {str(e)}")
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main() 