#!/usr/bin/env python3

"""A/B Testing Analyzer

This script analyzes the codebase to identify opportunities for A/B testing
of monetization features and pricing strategies.

Maturity: beta

Why:
- A/B testing is critical for optimizing monetization
- This script helps identify testable elements in the codebase
- Suggests A/B testing experiments for pricing and features
- Helps maintain a data-driven approach to monetization
"""

import argparse
import json
import os
import re
from pathlib import Path
import yaml
from collections import defaultdict

class ABTestingAnalyzer:
    """Analyzes the codebase to identify A/B testing opportunities."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = {
            'testable_elements': [],
            'existing_tests': [],
            'test_opportunities': [],
            'summary': {
                'total_testable_elements': 0,
                'existing_tests': 0,
                'test_opportunities': 0
            }
        }
        
        # Patterns to identify testable elements
        self.testable_patterns = {
            'pricing_display': r'(price|cost|fee|charge|amount)\s*[=:]\s*[\'"]*(\d+(?:\.\d+)?)',
            'cta_button': r'(button|btn|cta)\s*[=:]\s*[\'"]*([^\'"]*(sign\s*up|subscribe|buy|purchase|upgrade|try)[^\'"]*)[\'"]',
            'feature_flag': r'(feature\s*flag|toggle|enabled?)\s*[=:]\s*[\'"]*(\w+)',
            'checkout_flow': r'(checkout|payment|billing|cart)\s*[=:]\s*[\'"]*(\w+)',
            'landing_page': r'(landing|homepage|sales\s*page)\s*[=:]\s*[\'"]*(\w+)',
            'onboarding': r'(onboarding|welcome|tutorial|guide)\s*[=:]\s*[\'"]*(\w+)',
            'upsell': r'(upsell|cross\s*sell|upgrade|premium)\s*[=:]\s*[\'"]*(\w+)'
        }
        
        # Patterns to identify existing A/B tests
        self.existing_test_patterns = [
            r'a\s*[/\\]\s*b\s*test',
            r'ab\s*test',
            r'split\s*test',
            r'experiment\s*[=:]\s*[\'"]*(\w+)',
            r'variant\s*[=:]\s*[\'"]*(\w+)',
            r'control\s*[=:]\s*[\'"]*(\w+)',
            r'treatment\s*[=:]\s*[\'"]*(\w+)'
        ]
        
        # A/B test experiment templates
        self.experiment_templates = {
            'pricing_display': {
                'name': 'Pricing Display Test',
                'description': 'Test different pricing displays to optimize conversion',
                'variants': [
                    'Control: Current pricing display',
                    'Variant A: Show annual pricing with monthly equivalent',
                    'Variant B: Emphasize value with "X per day" pricing',
                    'Variant C: Show competitor comparison'
                ],
                'metrics': [
                    'Click-through rate to checkout',
                    'Conversion rate',
                    'Average order value'
                ],
                'implementation_complexity': 'Low'
            },
            'cta_button': {
                'name': 'Call-to-Action Button Test',
                'description': 'Test different CTA button text, color, and placement',
                'variants': [
                    'Control: Current CTA',
                    'Variant A: Action-oriented text (e.g., "Start Saving Now")',
                    'Variant B: Value-oriented text (e.g., "Get Premium Features")',
                    'Variant C: Urgency-oriented text (e.g., "Limited Time Offer")'
                ],
                'metrics': [
                    'Button click-through rate',
                    'Conversion rate',
                    'Time to conversion'
                ],
                'implementation_complexity': 'Low'
            },
            'feature_flag': {
                'name': 'Feature Gating Test',
                'description': 'Test different approaches to gating premium features',
                'variants': [
                    'Control: Current feature gating',
                    'Variant A: Preview with upgrade prompt',
                    'Variant B: Limited free usage with counter',
                    'Variant C: Full access with time limit'
                ],
                'metrics': [
                    'Upgrade rate',
                    'Time to upgrade',
                    'User engagement with feature'
                ],
                'implementation_complexity': 'Medium'
            },
            'checkout_flow': {
                'name': 'Checkout Flow Test',
                'description': 'Test different checkout flow designs to reduce abandonment',
                'variants': [
                    'Control: Current checkout flow',
                    'Variant A: Single-page checkout',
                    'Variant B: Progress indicator with steps',
                    'Variant C: Simplified form with fewer fields'
                ],
                'metrics': [
                    'Checkout completion rate',
                    'Time to complete checkout',
                    'Cart abandonment rate'
                ],
                'implementation_complexity': 'High'
            },
            'landing_page': {
                'name': 'Landing Page Test',
                'description': 'Test different landing page designs to improve conversion',
                'variants': [
                    'Control: Current landing page',
                    'Variant A: Benefit-focused headline',
                    'Variant B: Social proof emphasis',
                    'Variant C: Problem-solution framing'
                ],
                'metrics': [
                    'Bounce rate',
                    'Time on page',
                    'Conversion rate'
                ],
                'implementation_complexity': 'Medium'
            },
            'onboarding': {
                'name': 'Onboarding Flow Test',
                'description': 'Test different onboarding approaches to improve activation',
                'variants': [
                    'Control: Current onboarding',
                    'Variant A: Interactive tutorial',
                    'Variant B: Use case selection',
                    'Variant C: Template-based quick start'
                ],
                'metrics': [
                    'Completion rate',
                    'Time to first value moment',
                    'Day 1/7/30 retention'
                ],
                'implementation_complexity': 'High'
            },
            'upsell': {
                'name': 'Upsell Prompt Test',
                'description': 'Test different upsell prompt timing and messaging',
                'variants': [
                    'Control: Current upsell approach',
                    'Variant A: Feature-triggered prompts',
                    'Variant B: Usage milestone prompts',
                    'Variant C: Time-based prompts'
                ],
                'metrics': [
                    'Prompt click-through rate',
                    'Upgrade conversion rate',
                    'User sentiment/feedback'
                ],
                'implementation_complexity': 'Medium'
            }
        }
    
    def analyze_directory(self, directory_path, exclude_patterns=None):
        """Analyze files in a directory to identify A/B testing opportunities."""
        if exclude_patterns is None:
            exclude_patterns = ['node_modules', 'dist', 'build', '.git']
        
        directory_path = Path(directory_path)
        
        if not directory_path.is_dir():
            print(f"Error: {directory_path} is not a directory")
            return
        
        # Walk through the directory
        for root, dirs, files in os.walk(directory_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(re.match(pattern, d) for pattern in exclude_patterns)]
            
            for file in files:
                # Only analyze certain file types
                if file.endswith(('.js', '.jsx', '.ts', '.tsx', '.py', '.html', '.css', '.scss')):
                    file_path = Path(root) / file
                    self._analyze_file(file_path)
        
        # Generate test opportunities based on testable elements and existing tests
        self._generate_test_opportunities()
        
        # Calculate summary
        self._calculate_summary()
        
        if self.verbose:
            print(f"Found {len(self.results['testable_elements'])} testable elements")
            print(f"Found {len(self.results['existing_tests'])} existing tests")
            print(f"Generated {len(self.results['test_opportunities'])} test opportunities")
    
    def _analyze_file(self, file_path):
        """Analyze a file to identify testable elements and existing tests."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for testable elements
            for element_type, pattern in self.testable_patterns.items():
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    # Get context (a few lines around the match)
                    start_pos = max(0, match.start() - 100)
                    end_pos = min(len(content), match.end() + 100)
                    context = content[start_pos:end_pos]
                    
                    # Get line number
                    line_number = content[:match.start()].count('\n') + 1
                    
                    self.results['testable_elements'].append({
                        'type': element_type,
                        'file': str(file_path),
                        'line': line_number,
                        'match': match.group(0),
                        'context': context,
                        'already_tested': False  # Will be updated later
                    })
            
            # Look for existing A/B tests
            for pattern in self.existing_test_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    # Get context (a few lines around the match)
                    start_pos = max(0, match.start() - 100)
                    end_pos = min(len(content), match.end() + 100)
                    context = content[start_pos:end_pos]
                    
                    # Get line number
                    line_number = content[:match.start()].count('\n') + 1
                    
                    self.results['existing_tests'].append({
                        'file': str(file_path),
                        'line': line_number,
                        'match': match.group(0),
                        'context': context
                    })
            
            if self.verbose and (len(self.results['testable_elements']) > 0 or len(self.results['existing_tests']) > 0):
                print(f"Analyzed {file_path}")
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _generate_test_opportunities(self):
        """Generate test opportunities based on testable elements and existing tests."""
        # Mark elements that are already being tested
        for element in self.results['testable_elements']:
            for test in self.results['existing_tests']:
                # If the element and test are in the same file and close to each other
                if element['file'] == test['file'] and abs(element['line'] - test['line']) < 10:
                    element['already_tested'] = True
                    break
        
        # Generate test opportunities for untested elements
        for element in self.results['testable_elements']:
            if not element['already_tested']:
                # Get the template for this element type
                template = self.experiment_templates.get(element['type'])
                
                if template:
                    self.results['test_opportunities'].append({
                        'element': element,
                        'experiment': {
                            'name': template['name'],
                            'description': template['description'],
                            'variants': template['variants'],
                            'metrics': template['metrics'],
                            'implementation_complexity': template['implementation_complexity']
                        }
                    })
    
    def _calculate_summary(self):
        """Calculate summary statistics."""
        total_testable_elements = len(self.results['testable_elements'])
        existing_tests = len(self.results['existing_tests'])
        test_opportunities = len(self.results['test_opportunities'])
        
        self.results['summary'] = {
            'total_testable_elements': total_testable_elements,
            'existing_tests': existing_tests,
            'test_opportunities': test_opportunities
        }
    
    def save_results(self, output_file, format='json'):
        """Save analysis results to a file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(self.results, f, indent=2)
            elif format == 'yaml':
                yaml.dump(self.results, f, sort_keys=False)
        
        print(f"Saved A/B testing analysis results to {output_file}")
    
    def generate_report(self, output_file):
        """Generate a human-readable report."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# A/B Testing Opportunities Report\n\n")
            
            # Write summary
            f.write("## Summary\n\n")
            f.write(f"- Total testable elements: {self.results['summary']['total_testable_elements']}\n")
            f.write(f"- Existing A/B tests: {self.results['summary']['existing_tests']}\n")
            f.write(f"- Test opportunities: {self.results['summary']['test_opportunities']}\n\n")
            
            # Write test opportunities by type
            f.write("## Test Opportunities by Type\n\n")
            
            # Group opportunities by type
            opportunities_by_type = defaultdict(list)
            for opportunity in self.results['test_opportunities']:
                opportunities_by_type[opportunity['element']['type']].append(opportunity)
            
            # Write each type
            for element_type, opportunities in opportunities_by_type.items():
                f.write(f"### {element_type.replace('_', ' ').title()} ({len(opportunities)})\n\n")
                
                # Take the first opportunity as an example
                example = opportunities[0]
                
                f.write(f"**Experiment**: {example['experiment']['name']}\n\n")
                f.write(f"**Description**: {example['experiment']['description']}\n\n")
                
                f.write("**Variants**:\n")
                for variant in example['experiment']['variants']:
                    f.write(f"- {variant}\n")
                
                f.write("\n**Metrics**:\n")
                for metric in example['experiment']['metrics']:
                    f.write(f"- {metric}\n")
                
                f.write(f"\n**Implementation Complexity**: {example['experiment']['implementation_complexity']}\n\n")
                
                f.write("**Example Locations**:\n")
                for opportunity in opportunities[:3]:  # Show up to 3 examples
                    element = opportunity['element']
                    f.write(f"- {element['file']}:{element['line']} - `{element['match']}`\n")
                
                if len(opportunities) > 3:
                    f.write(f"- ... and {len(opportunities) - 3} more\n")
                
                f.write("\n")
            
            # Write existing tests
            if self.results['existing_tests']:
                f.write("## Existing A/B Tests\n\n")
                
                for test in self.results['existing_tests']:
                    f.write(f"### {test['file']}:{test['line']}\n\n")
                    f.write(f"```\n{test['context']}\n```\n\n")
            
            # Write implementation guide
            f.write("## A/B Testing Implementation Guide\n\n")
            
            f.write("### General Implementation Steps\n\n")
            f.write("1. **Define the hypothesis**\n")
            f.write("   - What do you expect to improve?\n")
            f.write("   - What is the expected outcome?\n\n")
            f.write("2. **Determine sample size**\n")
            f.write("   - Use a sample size calculator\n")
            f.write("   - Consider statistical significance\n\n")
            f.write("3. **Implement the test**\n")
            f.write("   - Use a testing framework (e.g., Optimizely, Google Optimize)\n")
            f.write("   - Ensure proper tracking is in place\n\n")
            f.write("4. **Run the test**\n")
            f.write("   - Run until statistical significance is reached\n")
            f.write("   - Avoid making other changes during the test\n\n")
            f.write("5. **Analyze results**\n")
            f.write("   - Look at primary and secondary metrics\n")
            f.write("   - Segment results by user type if possible\n\n")
            f.write("6. **Implement the winner**\n")
            f.write("   - Roll out the winning variant\n")
            f.write("   - Document learnings for future tests\n\n")
            
            f.write("### Recommended Testing Tools\n\n")
            f.write("- **Client-side testing**: Google Optimize, Optimizely, VWO\n")
            f.write("- **Server-side testing**: LaunchDarkly, Split.io, Flagsmith\n")
            f.write("- **Mobile app testing**: Firebase A/B Testing, Apptimize\n")
            f.write("- **Analytics integration**: Google Analytics, Mixpanel, Amplitude\n\n")
            
            f.write("### Best Practices\n\n")
            f.write("- Test one thing at a time for clear results\n")
            f.write("- Run tests for at least 1-2 weeks to account for day-of-week effects\n")
            f.write("- Aim for at least 100 conversions per variant before concluding\n")
            f.write("- Document all tests, even failed ones, to build institutional knowledge\n")
            f.write("- Consider segmenting results by user type, device, or traffic source\n")
            f.write("- Prioritize tests with high potential impact and low implementation cost\n")
        
        print(f"Generated A/B testing report at {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Analyze A/B testing opportunities")
    parser.add_argument("source_dir", help="Source directory to analyze")
    parser.add_argument("--output", default="ab_testing_analysis.json", help="Output file")
    parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Output format")
    parser.add_argument("--report", help="Generate human-readable report")
    parser.add_argument("--exclude", nargs="+", default=["node_modules", "dist", "build", ".git"],
                        help="Patterns to exclude (default: node_modules dist build .git)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    analyzer = ABTestingAnalyzer(verbose=args.verbose)
    analyzer.analyze_directory(args.source_dir, exclude_patterns=args.exclude)
    analyzer.save_results(args.output, format=args.format)
    
    if args.report:
        analyzer.generate_report(args.report)

if __name__ == "__main__":
    main() 