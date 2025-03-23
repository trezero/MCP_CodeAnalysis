# Style Guide

<!-- MEMORY_ANCHOR: style_guide_documentation -->

This directory contains the coding standards and documentation templates for the project.

## Why

Consistent code and documentation make it easier for developers to understand and maintain the codebase. By enforcing coding standards and providing templates, we reduce variability and improve readability.

## Contents

- `README.md`: This file
- `python_style_guide.md`: Python coding standards
- `javascript_style_guide.md`: JavaScript coding standards
- `documentation_templates/`: Templates for documentation
  - `component_template.md`: Template for component documentation
  - `function_template.md`: Template for function documentation
  - `api_template.md`: Template for API documentation
- `linters/`: Linter configurations
  - `.eslintrc.js`: ESLint configuration for JavaScript
  - `.pylintrc`: Pylint configuration for Python
  - `pyproject.toml`: Black configuration for Python
- `formatters/`: Formatter configurations
  - `.prettierrc`: Prettier configuration for JavaScript
  - `.editorconfig`: EditorConfig for all files

## Coding Standards

### Python

See [Python Style Guide](python_style_guide.md) for detailed Python coding standards.

Key points:
- Follow PEP 8 for code style
- Use Black for code formatting
- Use type hints for function parameters and return values
- Write docstrings for all modules, classes, and functions
- Include a "Why" section in docstrings for non-trivial functions

### JavaScript

See [JavaScript Style Guide](javascript_style_guide.md) for detailed JavaScript coding standards.

Key points:
- Use ESLint for code linting
- Use Prettier for code formatting
- Use TypeScript for type safety
- Write JSDoc comments for all functions and classes
- Include a "Why" section in JSDoc comments for non-trivial functions

## Documentation Templates

### Component Documentation

Use the [Component Template](documentation_templates/component_template.md) for documenting components.

Key sections:
- Overview
- Why
- Usage
- API
- Examples
- Integration with Other Components
- Maturity

### Function Documentation

Use the [Function Template](documentation_templates/function_template.md) for documenting functions.

Key sections:
- Description
- Why
- Parameters
- Returns
- Raises
- Examples

### API Documentation

Use the [API Template](documentation_templates/api_template.md) for documenting APIs.

Key sections:
- Endpoint
- Method
- Description
- Why
- Request Parameters
- Response
- Status Codes
- Examples

## Linters and Formatters

### Linters

- **ESLint**: JavaScript linter
  - Configuration: `.eslintrc.js`
  - Run: `eslint .`

- **Pylint**: Python linter
  - Configuration: `.pylintrc`
  - Run: `pylint your_module`

### Formatters

- **Prettier**: JavaScript formatter
  - Configuration: `.prettierrc`
  - Run: `prettier --write .`

- **Black**: Python formatter
  - Configuration: `pyproject.toml`
  - Run: `black .`

- **EditorConfig**: Editor-agnostic formatting
  - Configuration: `.editorconfig`
  - Supported by most editors and IDEs

## Integration with CI/CD

To enforce coding standards in your CI/CD pipeline:

1. Add the following step to your CI/CD configuration:

```yaml
- name: Lint and format code
  run: |
    pip install black pylint
    npm install -g eslint prettier
    black --check .
    pylint your_module
    eslint .
    prettier --check .
```

2. Fail the build if linting or formatting checks fail:

```yaml
- name: Check for linting errors
  run: |
    if [ $? -ne 0 ]; then
      echo "Linting errors found. Please fix them before merging."
      exit 1
    fi
```

## Maturity

The style guide component is currently in **stable** status. It is well-established and unlikely to change significantly. 