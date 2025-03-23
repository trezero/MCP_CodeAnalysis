# Metadata Management Tools

This directory contains tools and resources for implementing and managing metadata standards in your codebase.

## Overview

Effective metadata provides context for code and improves discoverability, maintainability, and integration. These tools help establish, validate, and visualize metadata across your codebase.

## Contents

- **`metadata.mdc`**: Rule definitions for metadata standards
- **`example_config.json`**: Example configuration for metadata standards
- **`example_documentation.md`**: Example documentation with metadata
- **`TUTORIAL.md`**: Comprehensive guide to implementing metadata standards
- **`metadata_extractor.py`**: Tool for extracting and validating metadata
- **`metadata_dashboard.py`**: Dashboard for visualizing metadata coverage

## Usage

### Metadata Extractor

The extractor analyzes your codebase for metadata in various file types, validating against defined standards:

```bash
# Basic usage
python metadata_extractor.py --source ./src

# With custom configuration
python metadata_extractor.py --source ./src --config metadata_config.json --report

# Generate report and enable verbose logging
python metadata_extractor.py --source ./src --verbose --report
```

### Metadata Dashboard

The dashboard provides interactive visualizations of metadata coverage and quality:

```bash
# Start the dashboard with a report
python metadata_dashboard.py --report ./metadata-output/metadata_report_20231125_120000.json

# Specify port
python metadata_dashboard.py --report ./metadata-output/metadata_report_20231125_120000.json --port 8080
```

## Integration with MCP

These tools can be integrated with MCP (Model-Code-Prompt) to provide automated metadata analysis:

1. Use `/mcp/extract_metadata` endpoint to analyze codebase
2. Use `/mcp/metadata_dashboard` to visualize results

Example API usage:

```python
import requests

# Extract metadata
response = requests.post('http://localhost:5000/mcp/extract_metadata', json={
    'source_dir': './src',
    'config_path': './metadata_config.json'
})
report_path = response.json()['report_path']

# Launch dashboard
dashboard_response = requests.post('http://localhost:5000/mcp/metadata_dashboard', json={
    'report_path': report_path,
    'port': 8080
})
dashboard_url = dashboard_response.json()['dashboard_url']
```

## Requirements

- Python 3.7+
- Required packages:
  - For extractor: `pyyaml`, `colorama`
  - For dashboard: `dash`, `plotly`, `pandas`

Install with:

```bash
pip install pyyaml colorama dash plotly pandas
```

## Best Practices

1. **Define Standards**: Use `example_config.json` as a template to define metadata standards
2. **Automate Validation**: Add metadata checks to CI/CD pipelines
3. **Monitor Coverage**: Use the dashboard to track metadata completeness
4. **Educate Team**: Share the TUTORIAL.md with your team

## License

MIT
