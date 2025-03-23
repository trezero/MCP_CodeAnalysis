#!/usr/bin/env python3

"""Pricing Strategy Analyzer

This script analyzes the codebase to identify pricing-related code and suggest
optimal pricing strategies based on feature value and market positioning.

Maturity: beta

Why:
- Pricing is critical to monetization success
- This script helps identify existing pricing structures
- Suggests optimal pricing strategies based on feature analysis
- Helps maintain a competitive and profitable pricing model
"""

import argparse
import json
import os
import re
from pathlib import Path
import yaml
from collections import defaultdict

class PricingStrategyAnalyzer:
    """Analyzes the codebase to identify and suggest pricing strategies."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = {
            'pricing_elements': [],
            'pricing_models': [],
            'recommendations': [],
            'summary': {
                'total_pricing_elements': 0,
                'identified_pricing_models': []
            }
        }
        
        # Patterns to identify pricing-related code
        self.pricing_patterns = {
            'price_point': r'(price|cost|fee|charge|amount)\s*[=:]\s*[\'"]*(\d+(?:\.\d+)?)',
            'subscription': r'(monthly|yearly|annual|quarterly|weekly)\s*[=:]\s*[\'"]*(\d+(?:\.\d+)?)',
            'discount': r'(discount|promo|coupon|sale)\s*[=:]\s*[\'"]*(\d+(?:\.\d+)?)',
            'tier': r'(tier|plan|level|package)\s*[=:]\s*[\'"]*(\w+)',
            'trial': r'(trial|free|demo)\s*[=:]\s*[\'"]*(\w+)',
            'currency': r'(currency|usd|eur|gbp|jpy|cny)\s*[=:]\s*[\'"]*(\w+)'
        }
        
        # Pricing models to identify
        self.pricing_models = {
            'freemium': [
                r'free\s+tier',
                r'premium\s+features',
                r'upgrade\s+to\s+pro',
                r'basic\s+plan.*?premium\s+plan'
            ],
            'subscription': [
                r'monthly\s+subscription',
                r'yearly\s+subscription',
                r'recurring\s+billing',
                r'cancel\s+subscription'
            ],
            'tiered': [
                r'(basic|starter|pro|premium|enterprise|business)\s+tier',
                r'(basic|starter|pro|premium|enterprise|business)\s+plan',
                r'pricing\s+tiers'
            ],
            'usage_based': [
                r'pay\s+per\s+(use|usage|call|request)',
                r'usage\s+limit',
                r'rate\s+limit',
                r'metered\s+billing'
            ],
            'one_time': [
                r'one[\s-]time\s+purchase',
                r'lifetime\s+access',
                r'buy\s+now',
                r'purchase\s+license'
            ],
            'marketplace': [
                r'commission\s+fee',
                r'transaction\s+fee',
                r'seller\s+fee',
                r'marketplace\s+fee'
            ]
        }
        
        # Pricing strategy recommendations
        self.pricing_strategies = {
            'freemium': {
                'description': 'Offer a free basic version with premium paid features',
                'suitable_for': ['consumer apps', 'SaaS products', 'content platforms'],
                'conversion_rate': '2-5%',
                'pros': ['Low barrier to entry', 'Viral growth potential', 'Upsell opportunities'],
                'cons': ['Need large user base', 'Free users may never convert', 'Support costs for free users']
            },
            'tiered_subscription': {
                'description': 'Multiple subscription tiers with increasing features and prices',
                'suitable_for': ['B2B SaaS', 'professional tools', 'content services'],
                'conversion_rate': '15-30%',
                'pros': ['Predictable revenue', 'Higher customer lifetime value', 'Clear upgrade path'],
                'cons': ['Churn risk', 'Need continuous value delivery', 'Price sensitivity']
            },
            'usage_based': {
                'description': 'Pay only for what you use (API calls, storage, etc.)',
                'suitable_for': ['APIs', 'infrastructure services', 'data processing'],
                'conversion_rate': '10-20%',
                'pros': ['Aligns with customer value', 'Scales with customer growth', 'Lower entry barrier'],
                'cons': ['Revenue unpredictability', 'Difficult forecasting', 'Customer budget concerns']
            },
            'hybrid': {
                'description': 'Combination of subscription base fee plus usage-based components',
                'suitable_for': ['enterprise SaaS', 'platform services', 'advanced tools'],
                'conversion_rate': '20-40%',
                'pros': ['Baseline predictable revenue', 'Captures value from power users', 'Flexible pricing model'],
                'cons': ['More complex to implement', 'Harder to communicate to customers', 'Billing complexity']
            },
            'marketplace': {
                'description': 'Platform fee or commission on transactions between users',
                'suitable_for': ['marketplaces', 'booking platforms', 'content creator platforms'],
                'conversion_rate': '30-70%',
                'pros': ['Scales with platform success', 'Aligns platform with user success', 'Network effects'],
                'cons': ['Need critical mass', 'Platform value must be clear', 'Competition may undercut fees']
            }
        }
    
    def analyze_directory(self, directory_path, exclude_patterns=None):
        """Analyze files in a directory to identify pricing-related code."""
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
                if file.endswith(('.js', '.jsx', '.ts', '.tsx', '.py', '.json', '.md')):
                    self._analyze_file(file_path)
        
        # Identify pricing models
        self._identify_pricing_models()
        
        # Generate recommendations
        self._generate_recommendations()
        
        # Calculate summary
        self._calculate_summary()
    
    def _analyze_file(self, file_path):
        """Analyze a file for pricing-related code."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for pricing patterns
            for pricing_type, pattern in self.pricing_patterns.items():
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    context_start = max(0, match.start() - 100)
                    context_end = min(len(content), match.end() + 100)
                    context = content[context_start:context_end]
                    
                    # Find the line number
                    line_number = content[:match.start()].count('\n') + 1
                    
                    # Extract the value
                    value = match.group(2) if match.lastindex >= 2 else None
                    
                    self.results['pricing_elements'].append({
                        'type': pricing_type,
                        'file': str(file_path),
                        'line': line_number,
                        'match': match.group(0),
                        'value': value,
                        'context': context
                    })
            
            if self.verbose:
                print(f"Analyzed {file_path}")
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _identify_pricing_models(self):
        """Identify pricing models based on pricing elements."""
        # Check for each pricing model
        for model_name, patterns in self.pricing_models.items():
            evidence = []
            
            # Check all pricing elements for evidence of this model
            for element in self.results['pricing_elements']:
                for pattern in patterns:
                    if re.search(pattern, element['context'], re.IGNORECASE):
                        evidence.append({
                            'element': element['type'],
                            'file': element['file'],
                            'line': element['line'],
                            'match': element['match']
                        })
            
            # If we have enough evidence, consider this model identified
            if len(evidence) >= 2:
                self.results['pricing_models'].append({
                    'model': model_name,
                    'confidence': min(1.0, len(evidence) / 5),  # Cap at 5 pieces of evidence
                    'evidence': evidence
                })
    
    def _generate_recommendations(self):
        """Generate pricing strategy recommendations."""
        # Identify existing models
        existing_models = [model['model'] for model in self.results['pricing_models']]
        
        # Generate recommendations based on existing models and pricing elements
        if not existing_models:
            # No clear pricing model detected, recommend based on pricing elements
            element_types = [element['type'] for element in self.results['pricing_elements']]
            
            if 'subscription' in element_types or 'tier' in element_types:
                self.results['recommendations'].append({
                    'strategy': 'tiered_subscription',
                    'reason': 'Subscription or tier elements detected, but no clear pricing model implemented',
                    'details': self.pricing_strategies['tiered_subscription']
                })
            
            elif 'price_point' in element_types:
                self.results['recommendations'].append({
                    'strategy': 'freemium',
                    'reason': 'Price points detected, but no clear pricing model implemented',
                    'details': self.pricing_strategies['freemium']
                })
            
            else:
                # Default recommendation
                self.results['recommendations'].append({
                    'strategy': 'hybrid',
                    'reason': 'No clear pricing elements or models detected',
                    'details': self.pricing_strategies['hybrid']
                })
        
        else:
            # Recommendations based on existing models
            if 'freemium' in existing_models and 'subscription' not in existing_models:
                self.results['recommendations'].append({
                    'strategy': 'tiered_subscription',
                    'reason': 'Freemium model detected, consider adding subscription tiers for premium features',
                    'details': self.pricing_strategies['tiered_subscription']
                })
            
            if 'subscription' in existing_models and 'usage_based' not in existing_models:
                self.results['recommendations'].append({
                    'strategy': 'hybrid',
                    'reason': 'Subscription model detected, consider adding usage-based components for power users',
                    'details': self.pricing_strategies['hybrid']
                })
            
            if 'one_time' in existing_models:
                self.results['recommendations'].append({
                    'strategy': 'tiered_subscription',
                    'reason': 'One-time purchase model detected, consider transitioning to subscription for recurring revenue',
                    'details': self.pricing_strategies['tiered_subscription']
                })
        
        # Add general recommendations
        if 'marketplace' not in existing_models and len(self.results['pricing_elements']) > 5:
            self.results['recommendations'].append({
                'strategy': 'marketplace',
                'reason': 'Consider marketplace model if your platform connects multiple user types',
                'details': self.pricing_strategies['marketplace']
            })
    
    def _calculate_summary(self):
        """Calculate summary statistics."""
        total_pricing_elements = len(self.results['pricing_elements'])
        identified_pricing_models = [model['model'] for model in self.results['pricing_models']]
        
        self.results['summary'] = {
            'total_pricing_elements': total_pricing_elements,
            'identified_pricing_models': identified_pricing_models
        }
    
    def save_results(self, output_file, format='json'):
        """Save analysis results to a file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(self.results, f, indent=2)
            elif format == 'yaml':
                yaml.dump(self.results, f, sort_keys=False)
        
        print(f"Saved pricing strategy analysis results to {output_file}")
    
    def generate_report(self, output_file):
        """Generate a human-readable report."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Pricing Strategy Analysis Report\n\n")
            
            # Write summary
            f.write("## Summary\n\n")
            f.write(f"- Total pricing elements identified: {self.results['summary']['total_pricing_elements']}\n")
            
            if self.results['summary']['identified_pricing_models']:
                f.write("- Identified pricing models:\n")
                for model in self.results['summary']['identified_pricing_models']:
                    f.write(f"  - {model}\n")
            else:
                f.write("- No clear pricing models identified\n")
            
            f.write("\n")
            
            # Write pricing elements
            if self.results['pricing_elements']:
                f.write("## Pricing Elements\n\n")
                
                # Group by type
                elements_by_type = defaultdict(list)
                for element in self.results['pricing_elements']:
                    elements_by_type[element['type']].append(element)
                
                for element_type, elements in elements_by_type.items():
                    f.write(f"### {element_type.replace('_', ' ').capitalize()}\n\n")
                    f.write("| File | Line | Value | Context |\n")
                    f.write("|------|------|-------|--------|\n")
                    
                    for element in elements:
                        context = element['context'].replace('\n', ' ')[:50] + '...'
                        f.write(f"| {element['file']} | {element['line']} | {element['value']} | {context} |\n")
                    
                    f.write("\n")
            
            # Write pricing models
            if self.results['pricing_models']:
                f.write("## Identified Pricing Models\n\n")
                
                for model in self.results['pricing_models']:
                    f.write(f"### {model['model'].replace('_', ' ').capitalize()}\n\n")
                    f.write(f"- Confidence: {model['confidence'] * 100:.0f}%\n")
                    f.write("- Evidence:\n")
                    
                    for evidence in model['evidence']:
                        f.write(f"  - {evidence['file']}:{evidence['line']} - {evidence['match']}\n")
                    
                    f.write("\n")
            
            # Write recommendations
            if self.results['recommendations']:
                f.write("## Pricing Strategy Recommendations\n\n")
                
                for recommendation in self.results['recommendations']:
                    f.write(f"### {recommendation['strategy'].replace('_', ' ').capitalize()}\n\n")
                    f.write(f"**Reason**: {recommendation['reason']}\n\n")
                    
                    details = recommendation['details']
                    f.write(f"**Description**: {details['description']}\n\n")
                    
                    f.write("**Suitable for**:\n")
                    for suitable in details['suitable_for']:
                        f.write(f"- {suitable}\n")
                    
                    f.write(f"\n**Typical conversion rate**: {details['conversion_rate']}\n\n")
                    
                    f.write("**Pros**:\n")
                    for pro in details['pros']:
                        f.write(f"- {pro}\n")
                    
                    f.write("\n**Cons**:\n")
                    for con in details['cons']:
                        f.write(f"- {con}\n")
                    
                    f.write("\n")
            
            # Write implementation guidance
            f.write("## Implementation Guidance\n\n")
            
            # Determine the most recommended strategy
            if self.results['recommendations']:
                top_strategy = self.results['recommendations'][0]['strategy']
                
                if top_strategy == 'freemium':
                    f.write("### Implementing Freemium\n\n")
                    f.write("1. **Identify core vs. premium features**\n")
                    f.write("   - Core features should provide real value but leave users wanting more\n")
                    f.write("   - Premium features should solve significant pain points\n\n")
                    f.write("2. **Implement feature flags**\n")
                    f.write("   - Use a consistent system for toggling features based on user tier\n")
                    f.write("   - Consider using a feature flag service for complex implementations\n\n")
                    f.write("3. **Design clear upgrade paths**\n")
                    f.write("   - Make premium features visible but clearly marked\n")
                    f.write("   - Provide contextual upgrade prompts when users hit limitations\n\n")
                    f.write("4. **Monitor conversion metrics**\n")
                    f.write("   - Track free-to-paid conversion rate (target: 2-5%)\n")
                    f.write("   - Measure time-to-conversion and optimize accordingly\n")
                
                elif top_strategy == 'tiered_subscription':
                    f.write("### Implementing Tiered Subscriptions\n\n")
                    f.write("1. **Design clear tier structure**\n")
                    f.write("   - Typically 3-4 tiers works best (e.g., Basic, Pro, Enterprise)\n")
                    f.write("   - Each tier should have clear value differentiation\n\n")
                    f.write("2. **Implement billing system**\n")
                    f.write("   - Consider using Stripe, Chargebee, or similar subscription billing service\n")
                    f.write("   - Support both monthly and annual billing (with discount for annual)\n\n")
                    f.write("3. **Create upgrade/downgrade flows**\n")
                    f.write("   - Make it easy to upgrade, slightly harder to downgrade\n")
                    f.write("   - Implement clear pro-ration policies\n\n")
                    f.write("4. **Monitor subscription metrics**\n")
                    f.write("   - Track MRR, churn rate, and LTV\n")
                    f.write("   - Analyze upgrade/downgrade patterns\n")
                
                elif top_strategy == 'usage_based':
                    f.write("### Implementing Usage-Based Pricing\n\n")
                    f.write("1. **Identify usage metrics**\n")
                    f.write("   - Choose metrics that align with customer value (API calls, storage, users, etc.)\n")
                    f.write("   - Ensure metrics are easily understood by customers\n\n")
                    f.write("2. **Implement usage tracking**\n")
                    f.write("   - Build robust tracking system with redundancy\n")
                    f.write("   - Provide real-time usage dashboards for customers\n\n")
                    f.write("3. **Design pricing tiers**\n")
                    f.write("   - Consider volume discounts for higher usage\n")
                    f.write("   - Implement soft and hard limits\n\n")
                    f.write("4. **Monitor usage patterns**\n")
                    f.write("   - Track usage distribution across customer base\n")
                    f.write("   - Identify opportunities for pricing optimization\n")
                
                elif top_strategy == 'hybrid':
                    f.write("### Implementing Hybrid Pricing\n\n")
                    f.write("1. **Balance base fee and usage components**\n")
                    f.write("   - Base fee should cover core functionality and minimum value\n")
                    f.write("   - Usage components should align with additional value\n\n")
                    f.write("2. **Implement tiered base pricing**\n")
                    f.write("   - Create 2-3 tiers with different feature sets\n")
                    f.write("   - Each tier can have different usage allowances\n\n")
                    f.write("3. **Design usage pricing**\n")
                    f.write("   - Implement fair overage pricing\n")
                    f.write("   - Consider package pricing for predictability\n\n")
                    f.write("4. **Provide billing transparency**\n")
                    f.write("   - Give customers clear visibility into both components\n")
                    f.write("   - Offer usage forecasting tools\n")
                
                elif top_strategy == 'marketplace':
                    f.write("### Implementing Marketplace Pricing\n\n")
                    f.write("1. **Determine fee structure**\n")
                    f.write("   - Consider percentage-based vs. fixed fees\n")
                    f.write("   - Decide which party pays (buyer, seller, or both)\n\n")
                    f.write("2. **Implement payment processing**\n")
                    f.write("   - Build or integrate payment processing system\n")
                    f.write("   - Ensure compliance with financial regulations\n\n")
                    f.write("3. **Design seller/buyer dashboards**\n")
                    f.write("   - Provide clear earnings/spending reports\n")
                    f.write("   - Implement transparent fee calculation\n\n")
                    f.write("4. **Monitor marketplace health**\n")
                    f.write("   - Track GMV, take rate, and transaction volume\n")
                    f.write("   - Monitor seller retention and buyer satisfaction\n")
            
            else:
                f.write("No specific pricing strategy recommendations available.\n")
        
        print(f"Generated pricing strategy report at {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Analyze pricing strategies")
    parser.add_argument("source_dir", help="Source directory to analyze")
    parser.add_argument("--output", default="pricing_strategy_analysis.json", help="Output file")
    parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Output format")
    parser.add_argument("--report", help="Generate human-readable report")
    parser.add_argument("--exclude", nargs="+", default=["node_modules", "dist", "build", ".git"],
                        help="Patterns to exclude (default: node_modules dist build .git)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    analyzer = PricingStrategyAnalyzer(verbose=args.verbose)
    analyzer.analyze_directory(args.source_dir, exclude_patterns=args.exclude)
    analyzer.save_results(args.output, format=args.format)
    
    if args.report:
        analyzer.generate_report(args.report)

if __name__ == "__main__":
    main() 