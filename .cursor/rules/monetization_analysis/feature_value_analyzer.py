#!/usr/bin/env python3

"""Feature Value Analyzer

This script analyzes features in the codebase to estimate their potential value,
helping prioritize development efforts based on monetization potential.

Maturity: beta

Why:
- Not all features have equal monetization potential
- This script helps identify high-value features to prioritize
- Promotes focus on features that drive revenue
- Helps maintain a sustainable business model
"""

import argparse
import json
import os
import re
from pathlib import Path
import yaml
from collections import defaultdict

class FeatureValueAnalyzer:
    """Analyzes features in the codebase to estimate their potential value."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = {
            'features': [],
            'summary': {
                'total_features': 0,
                'high_value_features': 0,
                'medium_value_features': 0,
                'low_value_features': 0
            }
        }
        
        # Patterns to identify features
        self.feature_patterns = {
            'authentication': {
                'pattern': r'(auth|login|signup|register|user)',
                'value_factors': {
                    'conversion_impact': 'medium',
                    'retention_impact': 'high',
                    'monetization_potential': 'low',
                    'development_cost': 'medium'
                }
            },
            'dashboard': {
                'pattern': r'(dashboard|overview|summary|stats|analytics)',
                'value_factors': {
                    'conversion_impact': 'medium',
                    'retention_impact': 'high',
                    'monetization_potential': 'medium',
                    'development_cost': 'high'
                }
            },
            'profile': {
                'pattern': r'(profile|account|settings|preferences)',
                'value_factors': {
                    'conversion_impact': 'low',
                    'retention_impact': 'medium',
                    'monetization_potential': 'low',
                    'development_cost': 'medium'
                }
            },
            'notification': {
                'pattern': r'(notification|alert|message|email)',
                'value_factors': {
                    'conversion_impact': 'medium',
                    'retention_impact': 'high',
                    'monetization_potential': 'low',
                    'development_cost': 'medium'
                }
            },
            'search': {
                'pattern': r'(search|filter|sort|query|find)',
                'value_factors': {
                    'conversion_impact': 'high',
                    'retention_impact': 'high',
                    'monetization_potential': 'medium',
                    'development_cost': 'high'
                }
            },
            'upload': {
                'pattern': r'(upload|file|image|video|document)',
                'value_factors': {
                    'conversion_impact': 'medium',
                    'retention_impact': 'medium',
                    'monetization_potential': 'high',
                    'development_cost': 'medium'
                }
            },
            'social': {
                'pattern': r'(share|follow|like|comment|friend)',
                'value_factors': {
                    'conversion_impact': 'medium',
                    'retention_impact': 'high',
                    'monetization_potential': 'medium',
                    'development_cost': 'high'
                }
            },
            'payment': {
                'pattern': r'(payment|checkout|cart|order|purchase)',
                'value_factors': {
                    'conversion_impact': 'high',
                    'retention_impact': 'medium',
                    'monetization_potential': 'high',
                    'development_cost': 'high'
                }
            },
            'integration': {
                'pattern': r'(integration|connect|sync|import|export)',
                'value_factors': {
                    'conversion_impact': 'medium',
                    'retention_impact': 'high',
                    'monetization_potential': 'high',
                    'development_cost': 'high'
                }
            },
            'subscription': {
                'pattern': r'(subscription|plan|tier|billing|renew)',
                'value_factors': {
                    'conversion_impact': 'high',
                    'retention_impact': 'high',
                    'monetization_potential': 'high',
                    'development_cost': 'medium'
                }
            },
            'api': {
                'pattern': r'(api|endpoint|request|response)',
                'value_factors': {
                    'conversion_impact': 'low',
                    'retention_impact': 'medium',
                    'monetization_potential': 'high',
                    'development_cost': 'high'
                }
            },
            'marketplace': {
                'pattern': r'(marketplace|store|product|listing|seller)',
                'value_factors': {
                    'conversion_impact': 'high',
                    'retention_impact': 'high',
                    'monetization_potential': 'high',
                    'development_cost': 'very_high'
                }
            }
        }
        
        # Value factor weights
        self.value_factor_weights = {
            'conversion_impact': 0.3,
            'retention_impact': 0.3,
            'monetization_potential': 0.4,
            'development_cost': -0.2  # Negative weight because higher cost reduces value
        }
        
        # Value factor scores
        self.value_factor_scores = {
            'very_low': 1,
            'low': 2,
            'medium': 3,
            'high': 4,
            'very_high': 5
        }
    
    def analyze_directory(self, directory_path, exclude_patterns=None):
        """Analyze files in a directory to identify and value features."""
        if exclude_patterns is None:
            exclude_patterns = ['node_modules', 'dist', 'build', '.git']
        
        directory_path = Path(directory_path)
        
        if not directory_path.is_dir():
            print(f"Error: {directory_path} is not a directory")
            return
        
        # First pass: collect all files
        files = []
        
        for root, dirs, filenames in os.walk(directory_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in str(Path(root) / d) for pattern in exclude_patterns)]
            
            for file in filenames:
                file_path = Path(root) / file
                
                # Only process relevant file types
                if file.endswith(('.js', '.jsx', '.ts', '.tsx', '.py', '.md')):
                    files.append(file_path)
        
        # Second pass: identify features
        self._identify_features(files)
        
        # Third pass: calculate feature values
        self._calculate_feature_values()
        
        # Calculate summary
        self._calculate_summary()
    
    def _identify_features(self, files):
        """Identify features in files."""
        # Initialize feature occurrences
        feature_occurrences = defaultdict(list)
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for feature patterns
                for feature_name, feature_info in self.feature_patterns.items():
                    pattern = feature_info['pattern']
                    
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        context_start = max(0, match.start() - 100)
                        context_end = min(len(content), match.end() + 100)
                        context = content[context_start:context_end]
                        
                        # Find the line number
                        line_number = content[:match.start()].count('\n') + 1
                        
                        feature_occurrences[feature_name].append({
                            'file': str(file_path),
                            'line': line_number,
                            'match': match.group(0),
                            'context': context
                        })
                
                if self.verbose:
                    print(f"Analyzed {file_path}")
            
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
        
        # Process feature occurrences
        for feature_name, occurrences in feature_occurrences.items():
            # Skip features with too few occurrences (likely false positives)
            if len(occurrences) < 3:
                continue
            
            # Get value factors for the feature
            value_factors = self.feature_patterns[feature_name]['value_factors']
            
            # Calculate implementation completeness based on occurrences
            implementation_completeness = min(1.0, len(occurrences) / 20)  # Cap at 20 occurrences
            
            self.results['features'].append({
                'name': feature_name,
                'occurrences': occurrences,
                'occurrence_count': len(occurrences),
                'value_factors': value_factors,
                'implementation_completeness': implementation_completeness
            })
    
    def _calculate_feature_values(self):
        """Calculate the value of each feature."""
        for feature in self.results['features']:
            # Calculate raw value score
            value_score = 0
            
            for factor, rating in feature['value_factors'].items():
                factor_weight = self.value_factor_weights.get(factor, 0)
                factor_score = self.value_factor_scores.get(rating, 3)  # Default to medium (3)
                
                value_score += factor_weight * factor_score
            
            # Adjust for implementation completeness
            adjusted_value_score = value_score * (0.5 + 0.5 * feature['implementation_completeness'])
            
            # Determine value category
            if adjusted_value_score >= 3.5:
                value_category = 'high'
            elif adjusted_value_score >= 2.5:
                value_category = 'medium'
            else:
                value_category = 'low'
            
            feature['value_score'] = adjusted_value_score
            feature['value_category'] = value_category
    
    def _calculate_summary(self):
        """Calculate summary statistics."""
        total_features = len(self.results['features'])
        high_value_features = sum(1 for feature in self.results['features'] if feature['value_category'] == 'high')
        medium_value_features = sum(1 for feature in self.results['features'] if feature['value_category'] == 'medium')
        low_value_features = sum(1 for feature in self.results['features'] if feature['value_category'] == 'low')
        
        self.results['summary'] = {
            'total_features': total_features,
            'high_value_features': high_value_features,
            'medium_value_features': medium_value_features,
            'low_value_features': low_value_features
        }
    
    def save_results(self, output_file, format='json'):
        """Save analysis results to a file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(self.results, f, indent=2)
            elif format == 'yaml':
                yaml.dump(self.results, f, sort_keys=False)
        
        print(f"Saved feature value analysis results to {output_file}")
    
    def generate_report(self, output_file):
        """Generate a human-readable report."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Feature Value Analysis Report\n\n")
            
            # Write summary
            f.write("## Summary\n\n")
            f.write(f"- Total features identified: {self.results['summary']['total_features']}\n")
            f.write(f"- High-value features: {self.results['summary']['high_value_features']}\n")
            f.write(f"- Medium-value features: {self.results['summary']['medium_value_features']}\n")
            f.write(f"- Low-value features: {self.results['summary']['low_value_features']}\n\n")
            
            # Write high-value features
            f.write("## High-Value Features\n\n")
            
            high_value_features = [feature for feature in self.results['features'] if feature['value_category'] == 'high']
            high_value_features.sort(key=lambda x: x['value_score'], reverse=True)
            
            for feature in high_value_features:
                f.write(f"### {feature['name'].capitalize()}\n\n")
                f.write(f"- **Value Score**: {feature['value_score']:.2f}\n")
                f.write(f"- **Occurrences**: {feature['occurrence_count']}\n")
                f.write(f"- **Implementation Completeness**: {feature['implementation_completeness'] * 100:.0f}%\n\n")
                
                f.write("#### Value Factors\n\n")
                for factor, rating in feature['value_factors'].items():
                    f.write(f"- {factor.replace('_', ' ').capitalize()}: {rating}\n")
                
                f.write("\n#### Key Occurrences\n\n")
                for occurrence in feature['occurrences'][:3]:  # Show top 3 occurrences
                    f.write(f"- {occurrence['file']}:{occurrence['line']}\n")
                
                f.write("\n")
            
            # Write medium-value features
            f.write("## Medium-Value Features\n\n")
            
            medium_value_features = [feature for feature in self.results['features'] if feature['value_category'] == 'medium']
            medium_value_features.sort(key=lambda x: x['value_score'], reverse=True)
            
            for feature in medium_value_features:
                f.write(f"### {feature['name'].capitalize()}\n\n")
                f.write(f"- **Value Score**: {feature['value_score']:.2f}\n")
                f.write(f"- **Occurrences**: {feature['occurrence_count']}\n")
                f.write(f"- **Implementation Completeness**: {feature['implementation_completeness'] * 100:.0f}%\n\n")
                
                f.write("#### Value Factors\n\n")
                for factor, rating in feature['value_factors'].items():
                    f.write(f"- {factor.replace('_', ' ').capitalize()}: {rating}\n")
                
                f.write("\n")
            
            # Write low-value features
            f.write("## Low-Value Features\n\n")
            
            low_value_features = [feature for feature in self.results['features'] if feature['value_category'] == 'low']
            low_value_features.sort(key=lambda x: x['value_score'], reverse=True)
            
            for feature in low_value_features:
                f.write(f"### {feature['name'].capitalize()}\n\n")
                f.write(f"- **Value Score**: {feature['value_score']:.2f}\n")
                f.write(f"- **Occurrences**: {feature['occurrence_count']}\n\n")
            
            # Write recommendations
            f.write("## Recommendations\n\n")
            
            # Recommend focusing on high-value features
            if high_value_features:
                f.write("### Focus on High-Value Features\n\n")
                f.write("Consider prioritizing development efforts on these high-value features:\n\n")
                
                for feature in high_value_features[:3]:
                    f.write(f"1. **{feature['name'].capitalize()}** - Value Score: {feature['value_score']:.2f}\n")
                
                f.write("\n")
            
            # Recommend improving medium-value features
            if medium_value_features:
                f.write("### Improve Medium-Value Features\n\n")
                f.write("These features have potential but may need improvements to increase their value:\n\n")
                
                for feature in medium_value_features[:3]:
                    f.write(f"1. **{feature['name'].capitalize()}** - Consider enhancing monetization potential\n")
                
                f.write("\n")
            
            # Recommend reconsidering low-value features
            if low_value_features:
                f.write("### Reconsider Low-Value Features\n\n")
                f.write("These features may not be worth significant investment:\n\n")
                
                for feature in low_value_features[:3]:
                    f.write(f"1. **{feature['name'].capitalize()}** - Value Score: {feature['value_score']:.2f}\n")
        
        print(f"Generated feature value report at {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Analyze feature value")
    parser.add_argument("source_dir", help="Source directory to analyze")
    parser.add_argument("--output", default="feature_value_analysis.json", help="Output file")
    parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Output format")
    parser.add_argument("--report", help="Generate human-readable report")
    parser.add_argument("--exclude", nargs="+", default=["node_modules", "dist", "build", ".git"],
                        help="Patterns to exclude (default: node_modules dist build .git)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    analyzer = FeatureValueAnalyzer(verbose=args.verbose)
    analyzer.analyze_directory(args.source_dir, exclude_patterns=args.exclude)
    analyzer.save_results(args.output, format=args.format)
    
    if args.report:
        analyzer.generate_report(args.report)

if __name__ == "__main__":
    main() 