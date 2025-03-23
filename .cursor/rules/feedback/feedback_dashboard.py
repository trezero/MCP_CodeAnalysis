#!/usr/bin/env python3

"""Feedback Dashboard Generator

This script generates an interactive HTML dashboard for visualizing
feedback data, sentiment analysis, and trends over time.

Maturity: beta

Why:
- Visual representation makes feedback patterns more apparent
- Interactive dashboard allows exploration of feedback data
- Centralized view helps prioritize actions based on feedback
- Trends over time show the impact of product changes
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

class FeedbackDashboard:
    """Generates an interactive dashboard for feedback visualization."""
    
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
        """Create a default dashboard template."""
        template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Feedback Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #2196F3;
            color: white;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
        }
        .card {
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            padding: 20px;
        }
        .summary {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
        }
        .summary-item {
            flex: 1;
            min-width: 200px;
            text-align: center;
            padding: 20px;
        }
        .summary-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .summary-label {
            color: #757575;
        }
        .chart {
            width: 100%;
            height: 400px;
        }
        .positive { color: #4CAF50; }
        .neutral { color: #FFC107; }
        .negative { color: #F44336; }
        .feedback-list {
            max-height: 500px;
            overflow-y: auto;
        }
        .feedback-item {
            border-bottom: 1px solid #eee;
            padding: 10px 0;
        }
        .feedback-meta {
            color: #757575;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        .feedback-content {
            margin-bottom: 5px;
        }
        .feedback-sentiment {
            font-weight: bold;
        }
        .theme-tag {
            display: inline-block;
            background-color: #E3F2FD;
            color: #1976D2;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-right: 5px;
            margin-bottom: 5px;
        }
    </style>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div class="header">
        <h1>Feedback Dashboard</h1>
        <p>Generated on {{ timestamp }}</p>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>Summary</h2>
            <div class="summary">
                <div class="summary-item">
                    <div class="summary-value">{{ total_items }}</div>
                    <div class="summary-label">Total Feedback Items</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value positive">{{ positive_count }}</div>
                    <div class="summary-label">Positive</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value neutral">{{ neutral_count }}</div>
                    <div class="summary-label">Neutral</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value negative">{{ negative_count }}</div>
                    <div class="summary-label">Negative</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value">{{ average_sentiment_score }}</div>
                    <div class="summary-label">Average Sentiment Score</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>Sentiment Distribution</h2>
            <div id="sentiment-chart" class="chart"></div>
        </div>
        
        <div class="card">
            <h2>Sentiment Trend</h2>
            <div id="trend-chart" class="chart"></div>
        </div>
        
        <div class="card">
            <h2>Theme Distribution</h2>
            <div id="theme-chart" class="chart"></div>
        </div>
        
        <div class="card">
            <h2>Recent Feedback</h2>
            <div class="feedback-list">
                {% for item in recent_feedback %}
                <div class="feedback-item">
                    <div class="feedback-meta">
                        {{ item.date }} | {{ item.source }} | User: {{ item.user }}
                    </div>
                    <div class="feedback-content">
                        {{ item.content }}
                    </div>
                    <div class="feedback-sentiment {{ item.sentiment }}">
                        Sentiment: {{ item.sentiment }} ({{ item.sentiment_score }})
                    </div>
                    <div>
                        {% for theme in item.themes %}
                        <span class="theme-tag">{{ theme }}</span>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <script>
        // Sentiment Distribution Chart
        var sentimentData = [
            {
                values: [{{ positive_count }}, {{ neutral_count }}, {{ negative_count }}],
                labels: ['Positive', 'Neutral', 'Negative'],
                type: 'pie',
                marker: {
                    colors: ['#4CAF50', '#FFC107', '#F44336']
                }
            }
        ];
        
        var sentimentLayout = {
            margin: {t: 30, b: 30, l: 30, r: 30}
        };
        
        Plotly.newPlot('sentiment-chart', sentimentData, sentimentLayout);
        
        // Sentiment Trend Chart
        var trendData = [
            {
                x: {{ trend_dates|safe }},
                y: {{ trend_scores|safe }},
                type: 'scatter',
                mode: 'lines+markers',
                line: {color: '#2196F3'}
            }
        ];
        
        var trendLayout = {
            margin: {t: 30, b: 50, l: 50, r: 30},
            xaxis: {title: 'Date'},
            yaxis: {title: 'Average Sentiment Score'}
        };
        
        Plotly.newPlot('trend-chart', trendData, trendLayout);
        
        // Theme Distribution Chart
        var themeData = [
            {
                x: {{ theme_names|safe }},
                y: {{ theme_counts|safe }},
                type: 'bar',
                marker: {color: '#2196F3'}
            }
        ];
        
        var themeLayout = {
            margin: {t: 30, b: 100, l: 50, r: 30},
            xaxis: {title: 'Theme', tickangle: 45},
            yaxis: {title: 'Count'}
        };
        
        Plotly.newPlot('theme-chart', themeData, themeLayout);
    </script>
</body>
</html>
"""
        with open(self.template_dir / "dashboard.html", "w", encoding="utf-8") as f:
            f.write(template)
    
    def load_data(self, input_file):
        """Load feedback data from a file."""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract feedback items
            if isinstance(data, list):
                feedback_items = data
                metadata = {}
                summary = {}
            elif isinstance(data, dict):
                if 'items' in data:
                    feedback_items = data['items']
                    metadata = data.get('metadata', {})
                    summary = data.get('summary', {})
                elif 'summary' in data and 'items' in data:
                    # This is likely a sentiment analysis result
                    feedback_items = data['items']
                    metadata = data.get('metadata', {})
                    summary = data.get('summary', {})
                else:
                    raise ValueError("Invalid data format")
            else:
                raise ValueError("Invalid data format")
            
            return feedback_items, metadata, summary
        
        except Exception as e:
            raise Exception(f"Error loading data: {e}")
    
    def generate_dashboard(self, input_file, output_file):
        """Generate a feedback dashboard."""
        try:
            # Load data
            feedback_items, metadata, summary = self.load_data(input_file)
            
            # If summary is not provided, generate it
            if not summary:
                summary = self._generate_summary(feedback_items)
            
            # Prepare template data
            template_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_items': summary.get('total_items', len(feedback_items)),
                'positive_count': summary.get('sentiment_distribution', {}).get('positive', 0),
                'neutral_count': summary.get('sentiment_distribution', {}).get('neutral', 0),
                'negative_count': summary.get('sentiment_distribution', {}).get('negative', 0),
                'average_sentiment_score': f"{summary.get('average_sentiment_score', 0):.2f}",
                'trend_dates': json.dumps(list(summary.get('sentiment_trend', {}).keys())),
                'trend_scores': json.dumps(list(summary.get('sentiment_trend', {}).values())),
                'theme_names': json.dumps(list(summary.get('theme_distribution', {}).keys())),
                'theme_counts': json.dumps(list(summary.get('theme_distribution', {}).values())),
                'recent_feedback': sorted(feedback_items, key=lambda x: x.get('date', ''), reverse=True)[:20]
            }
            
            # Render template
            template = self.env.get_template('dashboard.html')
            html = template.render(**template_data)
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"Dashboard generated at {output_file}")
        
        except Exception as e:
            print(f"Error generating dashboard: {e}")
    
    def _generate_summary(self, feedback_items):
        """Generate a summary from feedback items."""
        # This is a simplified summary generator
        # For a more comprehensive analysis, use the SentimentAnalyzer
        
        sentiment_distribution = {'positive': 0, 'neutral': 0, 'negative': 0}
        sentiment_scores = []
        sentiment_by_date = {}
        themes = Counter()
        
        for item in feedback_items:
            # Count sentiment
            sentiment = item.get('sentiment', 'neutral')
            sentiment_distribution[sentiment] = sentiment_distribution.get(sentiment, 0) + 1
            
            # Collect sentiment scores
            score = item.get('sentiment_score', 0)
            sentiment_scores.append(score)
            
            # Group by date
            date = item.get('date', '')[:10]  # Get just the date part
            if date:
                if date not in sentiment_by_date:
                    sentiment_by_date[date] = []
                sentiment_by_date[date].append(score)
            
            # Count themes
            for theme in item.get('themes', []):
                themes[theme] += 1
        
        # Calculate average sentiment score
        average_sentiment_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        # Calculate sentiment trend (average by date)
        sentiment_trend = {
            date: sum(scores) / len(scores)
            for date, scores in sentiment_by_date.items()
        }
        
        # Sort dates
        sentiment_trend = {k: sentiment_trend[k] for k in sorted(sentiment_trend.keys())}
        
        return {
            'total_items': len(feedback_items),
            'sentiment_distribution': sentiment_distribution,
            'average_sentiment_score': average_sentiment_score,
            'sentiment_trend': sentiment_trend,
            'theme_distribution': dict(themes.most_common(10))
        }

def main():
    parser = argparse.ArgumentParser(description="Generate feedback dashboard")
    parser.add_argument("input_file", help="Input feedback file (JSON)")
    parser.add_argument("--output", help="Output HTML file")
    parser.add_argument("--template-dir", help="Directory containing templates")
    args = parser.parse_args()
    
    # Determine output file if not specified
    if not args.output:
        input_path = Path(args.input_file)
        output_file = input_path.with_suffix('.html')
    else:
        output_file = args.output
    
    # Create dashboard generator
    dashboard = FeedbackDashboard(template_dir=args.template_dir)
    
    # Generate dashboard
    dashboard.generate_dashboard(args.input_file, output_file)

if __name__ == "__main__":
    main() 