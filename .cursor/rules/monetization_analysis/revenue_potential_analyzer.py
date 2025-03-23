#!/usr/bin/env python3

"""Revenue Potential Analyzer

This script analyzes the codebase to identify potential monetization opportunities,
focusing on freemium features, subscription models, and marketplace integration.

Maturity: beta

Why:
- Identifying monetization opportunities early helps guide development
- This script helps identify features that could be monetized
- Promotes a focus on revenue-generating features
- Helps maintain a sustainable business model
"""

import argparse
import json
import os
import re
from pathlib import Path
import yaml
from collections import defaultdict

class RevenuePotentialAnalyzer:
    """Analyzes the codebase for monetization opportunities."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = {
            'opportunities': [],
            'summary': {
                'total_opportunities': 0,
                'by_type': {},
                'by_priority': {}
            }
        }
        
        # Patterns to identify potential monetization opportunities
        self.monetization_patterns = {
            'freemium': [
                r'(free|premium|upgrade|subscribe|subscription|plan|tier|limit)',
                r'(trial|demo|basic|pro|enterprise|business)',
                r'(feature\s+flag|feature\s+toggle|paywall)'
            ],
            'subscription': [
                r'(subscribe|subscription|recurring|monthly|yearly|annual)',
                r'(payment|billing|invoice|charge|credit\s+card)',
                r'(cancel|renew|auto\s*renew|expire|extend)'
            ],
            'marketplace': [
                r'(marketplace|store|shop|vendor|seller|buyer|purchase)',
                r'(listing|product|item|inventory|catalog)',
                r'(commission|fee|transaction|payment\s+processing)'
            ],
            'api': [
                r'(api\s+key|api\s+token|api\s+limit|rate\s+limit)',
                r'(api\s+usage|api\s+call|api\s+request|api\s+response)',
                r'(api\s+version|api\s+endpoint|api\s+service)'
            ],
            'ads': [
                r'(ad|ads|advert|advertisement|banner|display\s+ad)',
                r'(impression|click|ctr|cpm|cpc|ad\s+network)',
                r'(ad\s+block|ad\s+blocker|ad\s+free)'
            ],
            'data': [
                r'(data\s+export|data\s+import|data\s+access)',
                r'(analytics|insights|reports|dashboard)',
                r'(data\s+processing|data\s+storage|data\s+retention)'
            ]
        }
        
        # Feature patterns to identify potential features
        self.feature_patterns = {
            'authentication': r'(auth|login|signup|register|user)',
            'dashboard': r'(dashboard|overview|summary|stats|analytics)',
            'profile': r'(profile|account|settings|preferences)',
            'notification': r'(notification|alert|message|email)',
            'search': r'(search|filter|sort|query|find)',
            'upload': r'(upload|file|image|video|document)',
            'social': r'(share|follow|like|comment|friend)',
            'payment': r'(payment|checkout|cart|order|purchase)',
            'integration': r'(integration|connect|sync|import|export)'
        }
    
    def analyze_directory(self, directory_path, exclude_patterns=None):
        """Analyze files in a directory for monetization opportunities."""
        if exclude_patterns is None:
            exclude_patterns = ['node_modules', 'dist', 'build', '.git']
        
        directory_path = Path(directory_path)
        
        if not directory_path.is_dir():
            print(f"Error: {directory_path} is not a directory")
            return
        
        # Walk through the directory
        for root, dirs, files in os.walk(directory_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in str(Path(root) / d) for pattern in exclude_patterns)]
            
            for file in files:
                file_path = Path(root) / file
                
                # Only process relevant file types
                if file.endswith(('.js', '.jsx', '.ts', '.tsx', '.py', '.md')):
                    self._analyze_file(file_path)
        
        # Calculate summary
        self._calculate_summary()
    
    def _analyze_file(self, file_path):
        """Analyze a file for monetization opportunities."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for monetization patterns
            for monetization_type, patterns in self.monetization_patterns.items():
                for pattern in patterns:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        context_start = max(0, match.start() - 100)
                        context_end = min(len(content), match.end() + 100)
                        context = content[context_start:context_end]
                        
                        # Find the line number
                        line_number = content[:match.start()].count('\n') + 1
                        
                        # Determine priority based on context
                        priority = self._determine_priority(context, monetization_type)
                        
                        # Identify associated feature
                        feature = self._identify_feature(context)
                        
                        # Extract a description from the context
                        description = self._extract_description(context, match.group(0))
                        
                        self.results['opportunities'].append({
                            'type': monetization_type,
                            'file': str(file_path),
                            'line': line_number,
                            'match': match.group(0),
                            'context': context,
                            'priority': priority,
                            'feature': feature,
                            'description': description
                        })
            
            if self.verbose:
                print(f"Analyzed {file_path}")
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _determine_priority(self, context, monetization_type):
        """Determine the priority of a monetization opportunity."""
        # Count the number of monetization-related terms in the context
        term_count = sum(
            1 for pattern in self.monetization_patterns[monetization_type]
            for match in re.finditer(pattern, context, re.IGNORECASE)
        )
        
        # Check for specific high-priority indicators
        high_priority_indicators = [
            r'revenue',
            r'monetize',
            r'profit',
            r'income',
            r'earn',
            r'conversion',
            r'upsell',
            r'ROI',
            r'customer\s+value'
        ]
        
        has_high_priority = any(
            re.search(pattern, context, re.IGNORECASE)
            for pattern in high_priority_indicators
        )
        
        # Determine priority
        if has_high_priority or term_count >= 3:
            return 'high'
        elif term_count >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _identify_feature(self, context):
        """Identify the feature associated with a monetization opportunity."""
        for feature, pattern in self.feature_patterns.items():
            if re.search(pattern, context, re.IGNORECASE):
                return feature
        
        return 'unknown'
    
    def _extract_description(self, context, match_text):
        """Extract a description from the context."""
        # Look for comments or documentation near the match
        comment_patterns = [
            r'\/\*\*\s*(.*?)\s*\*\/',  # JSDoc comment
            r'\/\/\s*(.*?)$',          # Single-line comment
            r'#\s*(.*?)$',             # Python comment
            r'"""\s*(.*?)\s*"""',      # Python docstring
            r'<!--\s*(.*?)\s*-->'      # HTML/Markdown comment
        ]
        
        for pattern in comment_patterns:
            for comment_match in re.finditer(pattern, context, re.MULTILINE):
                comment_text = comment_match.group(1)
                if match_text.lower() in comment_text.lower():
                    return comment_text.strip()
        
        # If no comment found, extract a sentence containing the match
        sentences = re.split(r'[.!?]', context)
        for sentence in sentences:
            if match_text.lower() in sentence.lower():
                return sentence.strip()
        
        # If all else fails, return a generic description
        return f"Potential {match_text} monetization opportunity"
    
    def _calculate_summary(self):
        """Calculate summary statistics."""
        total_opportunities = len(self.results['opportunities'])
        
        # Count by type
        by_type = defaultdict(int)
        for opportunity in self.results['opportunities']:
            by_type[opportunity['type']] += 1
        
        # Count by priority
        by_priority = defaultdict(int)
        for opportunity in self.results['opportunities']:
            by_priority[opportunity['priority']] += 1
        
        self.results['summary'] = {
            'total_opportunities': total_opportunities,
            'by_type': dict(by_type),
            'by_priority': dict(by_priority)
        }
    
    def save_results(self, output_file, format='json'):
        """Save analysis results to a file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(self.results, f, indent=2)
            elif format == 'yaml':
                yaml.dump(self.results, f, sort_keys=False)
        
        print(f"Saved revenue potential analysis results to {output_file}")
    
    def generate_report(self, output_file):
        """Generate a human-readable report."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Revenue Potential Analysis Report\n\n")
            
            # Write summary
            f.write("## Summary\n\n")
            f.write(f"- Total monetization opportunities: {self.results['summary']['total_opportunities']}\n\n")
            
            # Write by type
            f.write("### By Type\n\n")
            for type_name, count in self.results['summary']['by_type'].items():
                f.write(f"- {type_name}: {count}\n")
            
            f.write("\n")
            
            # Write by priority
            f.write("### By Priority\n\n")
            for priority, count in self.results['summary']['by_priority'].items():
                f.write(f"- {priority}: {count}\n")
            
            f.write("\n")
            
            # Write high-priority opportunities
            f.write("## High-Priority Opportunities\n\n")
            
            high_priority = [o for o in self.results['opportunities'] if o['priority'] == 'high']
            
            for opportunity in high_priority:
                f.write(f"### {opportunity['type'].capitalize()} - {opportunity['feature'].capitalize()}\n\n")
                f.write(f"- **File**: {opportunity['file']}\n")
                f.write(f"- **Line**: {opportunity['line']}\n")
                f.write(f"- **Description**: {opportunity['description']}\n")
                f.write(f"- **Match**: {opportunity['match']}\n\n")
                
                f.write("```\n")
                f.write(opportunity['context'])
                f.write("\n```\n\n")
            
            # Write by monetization type
            for monetization_type in self.monetization_patterns.keys():
                type_opportunities = [o for o in self.results['opportunities'] if o['type'] == monetization_type]
                
                if type_opportunities:
                    f.write(f"## {monetization_type.capitalize()} Opportunities\n\n")
                    
                    # Group by feature
                    by_feature = defaultdict(list)
                    for opportunity in type_opportunities:
                        by_feature[opportunity['feature']].append(opportunity)
                    
                    for feature, opportunities in by_feature.items():
                        f.write(f"### {feature.capitalize()}\n\n")
                        
                        for opportunity in opportunities:
                            f.write(f"- **{opportunity['priority'].upper()}**: {opportunity['description']} ({opportunity['file']}:{opportunity['line']})\n")
                        
                        f.write("\n")
        
        print(f"Generated revenue potential report at {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Analyze revenue potential")
    parser.add_argument("source_dir", help="Source directory to analyze")
    parser.add_argument("--output", default="revenue_potential_analysis.json", help="Output file")
    parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Output format")
    parser.add_argument("--report", help="Generate human-readable report")
    parser.add_argument("--exclude", nargs="+", default=["node_modules", "dist", "build", ".git"],
                        help="Patterns to exclude (default: node_modules dist build .git)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    analyzer = RevenuePotentialAnalyzer(verbose=args.verbose)
    analyzer.analyze_directory(args.source_dir, exclude_patterns=args.exclude)
    analyzer.save_results(args.output, format=args.format)
    
    if args.report:
        analyzer.generate_report(args.report)

if __name__ == "__main__":
    main() 