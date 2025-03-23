# Cursor Rules and Scripts Integration

This document explains how the Cursor rules (`.mdc` files) and Python scripts work together to provide a comprehensive code analysis and assistance system.

## Integration Architecture

The integration between rules and scripts is managed through these key components:

1. **Central Configuration** (`config.py`): Provides shared settings and integration points
2. **Rule Loader** (`rule_loader.py`): Allows Python scripts to access rule definitions
3. **Integration Test** (`integration_test.py`): Verifies proper integration
4. **Documentation Generator** (`doc_generator.py`): Creates comprehensive documentation

## How Rules and Scripts Work Together

1. **Rules define patterns and configurations**:
   - `.mdc` files contain YAML frontmatter with configuration
   - They specify which files to analyze (via glob patterns)
   - They define how the AI should interpret and process code

2. **Scripts implement analysis logic**:
   - Python scripts perform actual code analysis
   - They use rule definitions to determine what to analyze
   - They generate reports and insights based on analysis

3. **Integration points**:
   - Scripts can access rule metadata through the rule loader
   - Rules can reference script capabilities in their descriptions
   - Both contribute to a unified understanding of the codebase

## Using the Integration

### For Developers

When creating new scripts or rules:

1. Use the rule loader to access rule definitions
2. Follow the established patterns for script arguments and output
3. Run the integration test to verify proper integration
4. Update documentation using the doc generator

### For Users

When using the system:

1. Configure rules to match your project's needs
2. Run scripts to analyze your codebase
3. Review generated reports for insights
4. Use the AI with confidence that it understands your codebase

## Example Integration Flow

1. A rule in `code_quality/complexity.mdc` defines patterns for identifying complex code
2. The script `code_quality/complexity_analyzer.py` uses these patterns to analyze code
3. The script generates a report highlighting areas of high complexity
4. The AI uses both the rule definitions and script results to provide targeted suggestions 