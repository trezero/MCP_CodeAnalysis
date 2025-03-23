#!/usr/bin/env python3

"""Feedback Sentiment Analyzer

This script analyzes the sentiment of feedback text, categorizing feedback
as positive, negative, or neutral, and identifying key themes.

Maturity: beta

Why:
- Manual sentiment analysis is subjective and time-consuming
- Automated analysis provides consistent categorization
- Identifying themes helps prioritize feedback
- Sentiment trends over time reveal the impact of changes
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter, defaultdict

# Note: This script uses simple rule-based sentiment analysis
# For production use, consider using a more sophisticated NLP library
# such as NLTK, spaCy, or a cloud-based sentiment analysis API

class SentimentAnalyzer:
    """Analyzes sentiment and themes in feedback text."""
    
    def __init__(self):
        # Simple sentiment lexicons
        self.positive_words = set([
            'good', 'great', 'excellent', 'amazing', 'awesome', 'fantastic',
            'wonderful', 'love', 'like', 'helpful', 'easy', 'useful', 'best',
            'perfect', 'happy', 'satisfied', 'impressive', 'intuitive', 'fast',
            'efficient', 'reliable', 'responsive', 'beautiful', 'clean', 'simple'
        ])
        
        self.negative_words = set([
            'bad', 'poor', 'terrible', 'awful', 'horrible', 'worst',
            'difficult', 'hard', 'confusing', 'confused', 'slow', 'buggy',
            'broken', 'error', 'issue', 'problem', 'fail', 'crash', 'hate',
            'dislike', 'disappointed', 'frustrating', 'annoying', 'useless',
            'complicated', 'inconsistent', 'unreliable', 'ugly', 'expensive'
        ])
        
        # Theme keywords
        self.themes = {
            'performance': ['slow', 'fast', 'speed', 'performance', 'lag', 'responsive', 'loading'],
            'usability': ['easy', 'intuitive', 'confusing', 'difficult', 'simple', 'complicated', 'user-friendly'],
            'reliability': ['crash', 'bug', 'error', 'reliable', 'stable', 'broken', 'issue', 'problem'],
            'design': ['design', 'layout', 'look', 'ui', 'interface', 'beautiful', 'ugly', 'clean'],
            'features': ['feature', 'functionality', 'capability', 'option', 'setting', 'missing'],
            'pricing': ['price', 'cost', 'expensive', 'cheap', 'affordable', 'worth', 'value'],
            'support': ['support', 'help', 'documentation', 'tutorial', 'guide', 'assistance']
        }
    
    def analyze_feedback(self, feedback_items):
        """Analyze sentiment and themes in a list of feedback items."""
        results = []
        
        for item in feedback_items:
            content = item.get('content', '')
            if not content:
                continue
            
            # Analyze sentiment
            sentiment_score, sentiment = self._analyze_sentiment(content)
            
            # Identify themes
            themes = self._identify_themes(content)
            
            # Extract key phrases
            key_phrases = self._extract_key_phrases(content)
            
            # Add analysis to results
            results.append({
                'id': item.get('id', ''),
                'date': item.get('date', ''),
                'source': item.get('source', ''),
                'user': item.get('user', ''),
                'category': item.get('category', ''),
                'content': content,
                'rating': item.get('rating', None),
                'sentiment_score': sentiment_score,
                'sentiment': sentiment,
                'themes': themes,
                'key_phrases': key_phrases
            })
        
        return results
    
    def _analyze_sentiment(self, text):
        """Analyze the sentiment of a text."""
        # Normalize text
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)
        
        # Count positive and negative words
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        # Calculate sentiment score (-1 to 1)
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            sentiment_score = 0
        else:
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
        
        # Determine sentiment category
        if sentiment_score > 0.2:
            sentiment = 'positive'
        elif sentiment_score < -0.2:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return sentiment_score, sentiment
    
    def _identify_themes(self, text):
        """Identify themes in a text."""
        text = text.lower()
        themes = []
        
        for theme, keywords in self.themes.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                    themes.append(theme)
                    break
        
        return themes
    
    def _extract_key_phrases(self, text):
        """Extract key phrases from a text."""
        # This is a simplified implementation
        # For production use, consider using a more sophisticated approach
        
        # Split into sentences
        sentences = re.split(r'[.!?]', text)
        key_phrases = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if sentence contains sentiment words
            words = re.findall(r'\b\w+\b', sentence.lower())
            has_sentiment = any(word in self.positive_words or word in self.negative_words for word in words)
            
            if has_sentiment and 3 <= len(words) <= 15:
                key_phrases.append(sentence)
        
        # Limit to top 3 key phrases
        return key_phrases[:3]
    
    def generate_summary(self, analysis_results):
        """Generate a summary of the sentiment analysis."""
        total_items = len(analysis_results)
        
        if total_items == 0:
            return {
                'total_items': 0,
                'sentiment_distribution': {},
                'theme_distribution': {},
                'average_sentiment_score': 0
            }
        
        # Count sentiments
        sentiment_counts = Counter(item['sentiment'] for item in analysis_results)
        
        # Count themes
        theme_counts = Counter()
        for item in analysis_results:
            for theme in item['themes']:
                theme_counts[theme] += 1
        
        # Calculate average sentiment score
        avg_sentiment_score = sum(item['sentiment_score'] for item in analysis_results) / total_items
        
        # Group by date
        sentiment_by_date = defaultdict(list)
        for item in analysis_results:
            date = item.get('date', '')
            if date:
                try:
                    # Extract just the date part if it's a datetime
                    if 'T' in date:
                        date = date.split('T')[0]
                    sentiment_by_date[date].append(item['sentiment_score'])
                except Exception:
                    pass
        
        # Calculate average sentiment by date
        sentiment_trend = {
            date: sum(scores) / len(scores)
            for date, scores in sentiment_by_date.items()
        }
        
        return {
            'total_items': total_items,
            'sentiment_distribution': {
                'positive': sentiment_counts.get('positive', 0),
                'neutral': sentiment_counts.get('neutral', 0),
                'negative': sentiment_counts.get('negative', 0)
            },
            'theme_distribution': dict(theme_counts),
            'average_sentiment_score': avg_sentiment_score,
            'sentiment_trend': dict(sorted(sentiment_trend.items()))
        }
    
    def generate_visualizations(self, summary, output_dir):
        """Generate visualizations of the sentiment analysis."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Sentiment distribution pie chart
        plt.figure(figsize=(10, 6))
        labels = ['Positive', 'Neutral', 'Negative']
        sizes = [
            summary['sentiment_distribution'].get('positive', 0),
            summary['sentiment_distribution'].get('neutral', 0),
            summary['sentiment_distribution'].get('negative', 0)
        ]
        colors = ['#4CAF50', '#FFC107', '#F44336']
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Feedback Sentiment Distribution')
        plt.savefig(output_dir / 'sentiment_distribution.png')
        plt.close()
        
        # Theme distribution bar chart
        if summary['theme_distribution']:
            plt.figure(figsize=(12, 6))
            themes = list(summary['theme_distribution'].keys())
            counts = list(summary['theme_distribution'].values())
            
            # Sort by count
            sorted_indices = np.argsort(counts)[::-1]
            themes = [themes[i] for i in sorted_indices]
            counts = [counts[i] for i in sorted_indices]
            
            plt.bar(themes, counts, color='#2196F3')
            plt.xlabel('Theme')
            plt.ylabel('Count')
            plt.title('Feedback Themes')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(output_dir / 'theme_distribution.png')
            plt.close()
        
        # Sentiment trend line chart
        if summary['sentiment_trend']:
            plt.figure(figsize=(12, 6))
            dates = list(summary['sentiment_trend'].keys())
            scores = list(summary['sentiment_trend'].values())
            
            plt.plot(dates, scores, marker='o', linestyle='-', color='#2196F3')
            plt.axhline(y=0, color='#757575', linestyle='--', alpha=0.7)
            plt.xlabel('Date')
            plt.ylabel('Average Sentiment Score')
            plt.title('Sentiment Trend Over Time')
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(output_dir / 'sentiment_trend.png')
            plt.close()

def main():
    parser = argparse.ArgumentParser(description="Analyze sentiment in feedback")
    parser.add_argument("input_file", help="Input feedback file (JSON)")
    parser.add_argument("--output-dir", default="sentiment_analysis", help="Output directory")
    args = parser.parse_args()
    
    try:
        # Load feedback data
        with open(args.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract feedback items
        if isinstance(data, list):
            feedback_items = data
        elif isinstance(data, dict) and 'items' in data:
            feedback_items = data['items']
        else:
            print("Error: Invalid feedback data format")
            return
        
        # Create analyzer
        analyzer = SentimentAnalyzer()
        
        # Analyze feedback
        print(f"Analyzing {len(feedback_items)} feedback items...")
        analysis_results = analyzer.analyze_feedback(feedback_items)
        
        # Generate summary
        summary = analyzer.generate_summary(analysis_results)
        
        # Save analysis results
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / 'sentiment_analysis.json', 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'source_file': args.input_file,
                    'item_count': len(analysis_results)
                },
                'summary': summary,
                'items': analysis_results
            }, f, indent=2)
        
        # Generate visualizations
        analyzer.generate_visualizations(summary, output_dir)
        
        # Print summary
        print("\nAnalysis Summary:")
        print(f"Total items: {summary['total_items']}")
        print("Sentiment distribution:")
        print(f"  Positive: {summary['sentiment_distribution'].get('positive', 0)} ({summary['sentiment_distribution'].get('positive', 0)/summary['total_items']*100:.1f}%)")
        print(f"  Neutral: {summary['sentiment_distribution'].get('neutral', 0)} ({summary['sentiment_distribution'].get('neutral', 0)/summary['total_items']*100:.1f}%)")
        print(f"  Negative: {summary['sentiment_distribution'].get('negative', 0)} ({summary['sentiment_distribution'].get('negative', 0)/summary['total_items']*100:.1f}%)")
        print(f"Average sentiment score: {summary['average_sentiment_score']:.2f}")
        print(f"Top themes: {', '.join(k for k, v in sorted(summary['theme_distribution'].items(), key=lambda x: x[1], reverse=True)[:3])}")
        print(f"\nResults saved to {output_dir}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 