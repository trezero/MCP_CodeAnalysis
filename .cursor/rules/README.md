# Cursor AI Rules

This directory contains scripts and rules that help the AI assistant understand and analyze your codebase. These scripts serve as a structured framework for the AI to provide more relevant and targeted suggestions.

## Purpose

These scripts define patterns, rules, and analysis methods that the AI can use to:

1. **Understand your code organization** - Help the AI grasp how your project is structured
2. **Identify important parts of your codebase** - Highlight critical components and features
3. **Make consistent recommendations aligned with your priorities** - Ensure AI suggestions match your goals
4. **Focus on areas that matter most to you** (monetization, testing, etc.) - Direct AI attention to your priorities

## How It Works

When you interact with AI tools in Cursor, these rules act as a knowledge base and guidance system. The AI reads these files to understand:

- What patterns to look for in your code
- Which areas of your codebase deserve special attention
- What kinds of recommendations would be most valuable to you
- How to analyze your code for specific qualities (complexity, test coverage, etc.)

Think of these rules as "configuration files" that customize how the AI understands and interacts with your codebase.

## Directory Structure

## Why

Custom rules for Cursor AI enable more efficient and context-aware assistance, tailored to specific tasks and file types. This approach was chosen over generic AI settings to provide more targeted help for each enhancement.

## Rule Files

### Main Rules

- `main.rules`: Main rules for the repository, integrating all enhancements.

### Enhancement-Specific Rules

- `knowledge_graph.rules`: Rules for the Centralized Knowledge Graph.

  - Creates a connected network of concepts, functions, and components in your codebase
  - Helps the AI understand relationships between different parts of your code
  - Makes it easier to navigate complex codebases by following concept connections
  - Example: Links authentication functions with user profile components and permission checks

- `code_health.rules`: Rules for Automated Code Health Metrics.

  - Defines standards for measuring code quality (complexity, test coverage, etc.)
  - Helps identify problematic code that needs refactoring
  - Tracks improvements or degradations in code quality over time
  - Example: Flags functions with high cyclomatic complexity or insufficient test coverage

- `code_health/test_file_cleanup.mdc`: Rules for Test File Cleanup.

  - Defines criteria for identifying test files that are no longer needed
  - Provides a process for safely removing obsolete test files
  - Helps keep the codebase organized and lean
  - Example: Identifies test files that are older than 30 days and no longer referenced

- `pinescript/test_cleanup.mdc`: Rules for Pine Script Test File Cleanup.

  - Pine Script specific guidelines for test file management
  - Includes a helper script for identifying cleanup candidates
  - Lists standard test files that should be kept
  - Example: Organizes test files by category and provides cleanup recommendations

- `debug_history.rules`: Rules for Enhanced Debug History.

  - Tracks patterns in debugging sessions to improve future troubleshooting
  - Records common errors and their solutions
  - Helps identify recurring issues that might indicate deeper problems
  - Example: Recognizes that a particular component frequently causes memory leaks

- `style_guide.rules`: Rules for the Living Style Guide.

  - Maintains consistent coding practices across your project
  - Adapts to your team's evolving coding standards
  - Ensures new code follows established patterns
  - Example: Enforces consistent naming conventions or component structure

- `onboarding.rules`: Rules for Interactive Onboarding Materials.

  - Helps new developers understand your codebase more quickly
  - Identifies key components and concepts that newcomers should learn first
  - Creates guided paths through complex systems
  - Example: Provides a step-by-step introduction to your authentication flow

- `feedback.rules`: Rules for the Feedback Loop.

  - Establishes patterns for collecting and responding to user feedback
  - Helps prioritize improvements based on user input
  - Tracks sentiment changes over time
  - Example: Identifies features that consistently receive negative feedback

- `memory_anchors.rules`: Rules for Semantic Memory Anchors.

  - Defines important reference points in your codebase
  - Helps the AI remember critical components and their purposes
  - Creates stable points of reference even as code evolves
  - Example: Marks core business logic functions that rarely change but are frequently referenced

- `maturity_model.rules`: Rules for the Component Maturity Model.

  - Tracks the development stage of different components (experimental, stable, legacy, etc.)
  - Helps set appropriate expectations for different parts of the codebase
  - Guides refactoring and improvement efforts
  - Example: Identifies which components are production-ready vs. still in development

- `cross_reference.rules`: Rules for the Cross-Reference Index.

  - Creates connections between related code elements
  - Helps understand how changes in one area might affect others
  - Identifies implicit dependencies that might not be obvious
  - Example: Links a database schema change to all queries that might be affected

- `why_documentation.rules`: Rules for 'Why' in Documentation.

  - Ensures documentation explains not just how but why code works
  - Preserves design decisions and their rationales
  - Helps prevent accidental breaking changes
  - Example: Explains why a particular authentication approach was chosen over alternatives

- `sandbox.rules`: Rules for the Sandbox Environment.

  - Defines safe areas for experimentation
  - Helps isolate experimental code from production systems
  - Encourages innovation while managing risk
  - Example: Identifies components that can be modified freely vs. those requiring careful testing

- `glossary.rules`: Rules for the Glossary of Terms.
  - Maintains consistent terminology throughout your project
  - Defines domain-specific language used in your codebase
  - Helps new team members understand specialized vocabulary
  - Example: Ensures that terms like "user," "customer," and "account" are used consistently

## Rule Structure

Each rule file specifies:

- `path_pattern`: Which files or directories the rule applies to (e.g., "src/_.js", "components/_.tsx").
- `model`: Which AI model to use for this rule (e.g., fusion for complex understanding, standard for simpler tasks).
- `context_window`: How much surrounding code the AI should consider when applying the rule (small for focused tasks, large for understanding broader patterns).
- `completion_style`: What style of suggestions the AI should provide (documentation for explanatory text, code for implementation suggestions, etc.).
- `description`: Human-readable explanation of what the rule does and why it matters.

## Usage

Cursor AI automatically applies these rules when working with files that match the path patterns. No additional configuration is needed.

## Extending the Rules

To add a new rule or analysis script:

1. Decide which category your rule belongs to (code_quality, monetization_analysis, etc.) or create a new directory if needed.

2. Create a new Python script (`.py`) in the appropriate directory following the naming pattern of existing scripts.

   - Implement your analysis logic following the pattern of other scripts
   - Include a descriptive docstring explaining the purpose
   - Create a main class that implements the analysis
   - Add command-line argument handling
   - Implement methods for analyzing, saving results, and generating reports

3. Create documentation in one of these formats:

   - `.md` (Markdown): For standard documentation that explains the rule
   - `.mdc` (Markdown with Configuration): For documentation that includes metadata and configuration
     - The `.mdc` format includes a YAML frontmatter section at the top with configuration parameters
     - These files define rule behavior, file patterns, and AI model preferences
     - They serve as both documentation and configuration for the rule system

4. Update this README.md to include your new script in the appropriate category.

### Example: Adding a New Code Quality Rule

#### 1. Create the Python script (security_analyzer.py):

```python
#!/usr/bin/env python3

"""Security Vulnerability Analyzer

This script analyzes the codebase for potential security vulnerabilities.

Maturity: beta

Why:
- Security is critical for user trust
- This script helps identify common security issues
- Promotes secure coding practices
- Helps prevent data breaches and attacks
"""

import argparse
# ... rest of implementation ...

class SecurityVulnerabilityAnalyzer:
    # ... implementation ...

def main():
    # ... command-line handling ...

if __name__ == "__main__":
    main()
```

#### 2. Create the documentation and configuration (security_analyzer.mdc):

```
---
Description: Rules for identifying and remediating security vulnerabilities in the codebase.
Globs: src/**/*.{js,ts,jsx,tsx,py}
Model: standard
Context_window: medium
Completion_style: security
---

# Security Vulnerability Analyzer

This rule helps identify potential security vulnerabilities in your codebase.

## Purpose

The security vulnerability analyzer scans code for common security issues such as:

- SQL Injection
- Cross-Site Scripting (XSS)
- Insecure Direct Object References
- Cross-Site Request Forgery (CSRF)
- Security Misconfiguration

## Usage

Run the analyzer with:

python .cursor/rules/code_quality/security_analyzer.py ./src --report security_report.md

## Remediation Strategies

For each vulnerability type, consider these best practices:

### SQL Injection
Use parameterized queries instead of string concatenation.

### XSS
Always sanitize user input before rendering it in HTML.

### CSRF
Implement anti-CSRF tokens for all state-changing operations.
```

#### 3. Update the README.md to include your new script in the Code Quality section.

## Rule File Structure

Each rule file must include a frontmatter metadata section at the top of the file with the following structure:

```yaml
---
Description: A clear description of what this rule covers
Globs: **/* or specific file patterns
Model: fusion
Context_window: medium or large
Includes:
  - path/to/included/rule.mdc  # Optional, for rules that include other rules
---
```

### Required Fields:

- `Description`: A clear, concise description of what the rule covers
- `Globs`: File patterns this rule applies to (e.g., `**/*` for all files, `**/*.ts` for TypeScript files)
- `Model`: The AI model to use (typically "fusion")
- `Context_window`: Size of context window ("medium" or "large")

### Optional Fields:

- `Includes`: List of other rule files to include
- `Completion_style`: Style of completion (e.g., "analytics")

### Example:

```yaml
---
Description: Guidelines for maintaining code quality and testing standards
Globs: **/*.ts
Model: fusion
Context_window: medium
Includes:
  - testing/testing.mdc
  - quality/quality.mdc
---
```
