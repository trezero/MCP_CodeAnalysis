#!/usr/bin/env python3

"""Feedback Collector

This script collects feedback from various sources (CSV files, JSON exports,
database dumps) and normalizes it into a standard format for analysis.

Maturity: beta

Why:
- Feedback comes from multiple sources in different formats
- Standardizing feedback makes analysis more consistent
- Centralized collection simplifies the feedback loop
- Automated collection reduces manual data entry errors
"""

import argparse
import csv
import json
import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path
import yaml

class FeedbackCollector:
    """Collects and normalizes feedback from various sources."""
    
    def __init__(self, output_dir, verbose=False):
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.feedback_items = []
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_from_csv(self, csv_file, mapping=None):
        """Collect feedback from a CSV file."""
        if mapping is None:
            # Default mapping assumes standard column names
            mapping = {
                'date': 'date',
                'source': 'source',
                'user': 'user',
                'category': 'category',
                'content': 'feedback',
                'rating': 'rating'
            }
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    feedback_item = self._normalize_feedback({
                        'date': row.get(mapping['date'], ''),
                        'source': row.get(mapping['source'], os.path.basename(csv_file)),
                        'user': row.get(mapping['user'], 'anonymous'),
                        'category': row.get(mapping['category'], 'uncategorized'),
                        'content': row.get(mapping['content'], ''),
                        'rating': row.get(mapping['rating'], '')
                    })
                    
                    self.feedback_items.append(feedback_item)
            
            if self.verbose:
                print(f"Collected {len(self.feedback_items)} items from {csv_file}")
        
        except Exception as e:
            print(f"Error collecting from CSV {csv_file}: {e}")
    
    def collect_from_json(self, json_file, mapping=None):
        """Collect feedback from a JSON file."""
        if mapping is None:
            # Default mapping assumes standard field names
            mapping = {
                'date': 'date',
                'source': 'source',
                'user': 'user',
                'category': 'category',
                'content': 'feedback',
                'rating': 'rating'
            }
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Handle different JSON structures
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict) and 'items' in data:
                    items = data['items']
                elif isinstance(data, dict) and 'feedback' in data:
                    items = data['feedback']
                else:
                    items = [data]  # Single item
                
                for item in items:
                    feedback_item = self._normalize_feedback({
                        'date': self._extract_nested(item, mapping['date']),
                        'source': self._extract_nested(item, mapping['source'], os.path.basename(json_file)),
                        'user': self._extract_nested(item, mapping['user'], 'anonymous'),
                        'category': self._extract_nested(item, mapping['category'], 'uncategorized'),
                        'content': self._extract_nested(item, mapping['content'], ''),
                        'rating': self._extract_nested(item, mapping['rating'], '')
                    })
                    
                    self.feedback_items.append(feedback_item)
            
            if self.verbose:
                print(f"Collected {len(self.feedback_items)} items from {json_file}")
        
        except Exception as e:
            print(f"Error collecting from JSON {json_file}: {e}")
    
    def collect_from_database(self, db_file, query, mapping=None):
        """Collect feedback from a SQLite database."""
        if mapping is None:
            # Default mapping assumes standard column names
            mapping = {
                'date': 'date',
                'source': 'source',
                'user': 'user',
                'category': 'category',
                'content': 'feedback',
                'rating': 'rating'
            }
        
        try:
            conn = sqlite3.connect(db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                row_dict = dict(row)
                feedback_item = self._normalize_feedback({
                    'date': row_dict.get(mapping['date'], ''),
                    'source': row_dict.get(mapping['source'], os.path.basename(db_file)),
                    'user': row_dict.get(mapping['user'], 'anonymous'),
                    'category': row_dict.get(mapping['category'], 'uncategorized'),
                    'content': row_dict.get(mapping['content'], ''),
                    'rating': row_dict.get(mapping['rating'], '')
                })
                
                self.feedback_items.append(feedback_item)
            
            conn.close()
            
            if self.verbose:
                print(f"Collected {len(self.feedback_items)} items from {db_file}")
        
        except Exception as e:
            print(f"Error collecting from database {db_file}: {e}")
    
    def _extract_nested(self, item, key_path, default=''):
        """Extract a value from a nested dictionary using a dot-separated path."""
        if '.' not in key_path:
            return item.get(key_path, default)
        
        parts = key_path.split('.')
        current = item
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        
        return current
    
    def _normalize_feedback(self, feedback_item):
        """Normalize a feedback item to a standard format."""
        # Normalize date
        if feedback_item['date']:
            try:
                # Try to parse various date formats
                date_formats = [
                    '%Y-%m-%d',
                    '%Y/%m/%d',
                    '%m/%d/%Y',
                    '%d/%m/%Y',
                    '%Y-%m-%d %H:%M:%S',
                    '%Y/%m/%d %H:%M:%S',
                    '%m/%d/%Y %H:%M:%S',
                    '%d/%m/%Y %H:%M:%S'
                ]
                
                parsed_date = None
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(feedback_item['date'], fmt)
                        break
                    except ValueError:
                        continue
                
                if parsed_date:
                    feedback_item['date'] = parsed_date.isoformat()
                else:
                    feedback_item['date'] = datetime.now().isoformat()
            except Exception:
                feedback_item['date'] = datetime.now().isoformat()
        else:
            feedback_item['date'] = datetime.now().isoformat()
        
        # Normalize rating
        if feedback_item['rating']:
            try:
                # Convert to a number between 1-5
                rating = float(feedback_item['rating'])
                
                # Handle different scales
                if 0 <= rating <= 1:  # 0-1 scale
                    rating = round(rating * 5)
                elif 0 <= rating <= 10:  # 0-10 scale
                    rating = round(rating / 2)
                
                # Ensure rating is between 1-5
                rating = max(1, min(5, rating))
                
                feedback_item['rating'] = rating
            except ValueError:
                # Handle text ratings
                text_rating = feedback_item['rating'].lower()
                if text_rating in ['excellent', 'very good', 'very satisfied']:
                    feedback_item['rating'] = 5
                elif text_rating in ['good', 'satisfied']:
                    feedback_item['rating'] = 4
                elif text_rating in ['average', 'neutral']:
                    feedback_item['rating'] = 3
                elif text_rating in ['poor', 'dissatisfied']:
                    feedback_item['rating'] = 2
                elif text_rating in ['very poor', 'very dissatisfied']:
                    feedback_item['rating'] = 1
                else:
                    feedback_item['rating'] = None
        else:
            feedback_item['rating'] = None
        
        # Add unique ID
        feedback_item['id'] = f"{feedback_item['source']}_{feedback_item['date']}_{hash(feedback_item['content'])}"
        
        return feedback_item
    
    def save_feedback(self, format='json'):
        """Save collected feedback to files."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            output_file = self.output_dir / f"feedback_{timestamp}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': {
                        'timestamp': datetime.now().isoformat(),
                        'count': len(self.feedback_items)
                    },
                    'items': self.feedback_items
                }, f, indent=2)
        
        elif format == 'csv':
            output_file = self.output_dir / f"feedback_{timestamp}.csv"
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                fieldnames = ['id', 'date', 'source', 'user', 'category', 'content', 'rating']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for item in self.feedback_items:
                    writer.writerow(item)
        
        elif format == 'yaml':
            output_file = self.output_dir / f"feedback_{timestamp}.yaml"
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump({
                    'metadata': {
                        'timestamp': datetime.now().isoformat(),
                        'count': len(self.feedback_items)
                    },
                    'items': self.feedback_items
                }, f)
        
        print(f"Saved {len(self.feedback_items)} feedback items to {output_file}")
        return output_file

def main():
    parser = argparse.ArgumentParser(description="Collect feedback from various sources")
    parser.add_argument("--output-dir", default="feedback_data", help="Output directory")
    parser.add_argument("--format", choices=["json", "csv", "yaml"], default="json",
                        help="Output format (default: json)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    subparsers = parser.add_subparsers(dest="source_type", help="Source type")
    
    # CSV source
    csv_parser = subparsers.add_parser("csv", help="Collect from CSV file")
    csv_parser.add_argument("file", help="CSV file path")
    csv_parser.add_argument("--mapping", type=json.loads, help="Column mapping (JSON)")
    
    # JSON source
    json_parser = subparsers.add_parser("json", help="Collect from JSON file")
    json_parser.add_argument("file", help="JSON file path")
    json_parser.add_argument("--mapping", type=json.loads, help="Field mapping (JSON)")
    
    # Database source
    db_parser = subparsers.add_parser("db", help="Collect from SQLite database")
    db_parser.add_argument("file", help="Database file path")
    db_parser.add_argument("--query", required=True, help="SQL query")
    db_parser.add_argument("--mapping", type=json.loads, help="Column mapping (JSON)")
    
    args = parser.parse_args()
    
    collector = FeedbackCollector(args.output_dir, verbose=args.verbose)
    
    if args.source_type == "csv":
        collector.collect_from_csv(args.file, mapping=args.mapping)
    elif args.source_type == "json":
        collector.collect_from_json(args.file, mapping=args.mapping)
    elif args.source_type == "db":
        collector.collect_from_database(args.file, args.query, mapping=args.mapping)
    else:
        parser.print_help()
        return
    
    collector.save_feedback(format=args.format)

if __name__ == "__main__":
    main() 