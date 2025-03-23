# Using the Pine Script Linter and Fixer

This document explains how to use the Pine Script linter and fixer to enforce and automatically fix coding standards in your Pine Script files according to TradingView's official style guide.

## Installation

1. Make sure you have Python 3.6+ installed.

2. Install the required dependencies:
   ```bash
   pip install -r ../utils/requirements.txt
   ```

3. (Optional) Install the linter as a pre-commit hook:
   ```bash
   python ../utils/install_hooks.py
   ```

## Running the Linter

### Command Line Usage

```bash
python ../utils/pine_linter.py [options] <file_or_directory>
```

#### Options:
- `-c, --config`: Path to configuration file (default: `config.json`)
- `-r, --recursive`: Recursively lint directories
- `-v, --verbose`: Verbose output

### Examples

Lint a single file:
```bash
python ../utils/pine_linter.py my_script.pine
```

Lint all Pine Script files in a directory:
```bash
python ../utils/pine_linter.py -r my_scripts_directory/
```

Use a custom configuration file:
```bash
python ../utils/pine_linter.py -c my_config.json my_script.pine
```

## Running the Fixer

The Pine Script fixer can automatically fix common issues in your Pine Script files, including:

1. Adding missing version declarations
2. Adding missing section headers
3. Renaming functions, inputs, and variables to follow TradingView's naming conventions:
   - Functions: `camelCase` (e.g., `calculateAverage`)
   - Variables: `camelCase` (e.g., `result`)
   - Inputs: `camelCase` (e.g., `length`)
   - Constants: `SNAKE_CASE` (e.g., `MAX_LOOKBACK`)
4. Moving functions, inputs, and variables to their correct sections

### Command Line Usage

```bash
python ../utils/pine_fixer.py [options] <file_or_directory>
```

#### Options:
- `-c, --config`: Path to configuration file (default: `config.json`)
- `-r, --recursive`: Recursively fix directories
- `-n, --no-backup`: Don't create backup files (default: create .bak files)
- `-v, --verbose`: Verbose output

### Examples

Fix a single file:
```bash
python ../utils/pine_fixer.py my_script.pine
```

Fix all Pine Script files in a directory:
```bash
python ../utils/pine_fixer.py -r my_scripts_directory/
```

Fix without creating backup files:
```bash
python ../utils/pine_fixer.py -n my_script.pine
```

## Configuration

The linter and fixer use a configuration file (`config.json`) to define the rules to enforce. You can customize this file to match your coding standards.

### Default Rules

- **Version Declaration**: Requires a version declaration at the top of the file (`//@version=X`).
- **Required Sections**: Checks for the presence of standard sections.
- **Section Order**: Ensures sections are in the correct order.
- **Function Placement**: Ensures functions are defined in the function definitions section.
- **Input Placement**: Ensures inputs are defined in the input parameters section.
- **Variable Declaration Placement**: Ensures variables are declared in the variable declarations section.
- **Naming Conventions**: Checks that functions, inputs, variables, and constants follow TradingView's naming conventions.

### Customizing Rules

You can customize the rules by editing the `config.json` file. Here's an example of how to disable a rule:

```json
{
  "rules": {
    "require_version_declaration": false
  }
}
```

Or change the naming conventions:

```json
{
  "rules": {
    "naming_conventions": {
      "functions": "f_*",
      "inputs": "i_*",
      "variables": "v_*",
      "constants": "c_*"
    }
  }
}
```

## Pine Script Template

A template Pine Script file (`template.pine`) is provided as an example of a file that follows all the rules and TradingView's style guide. You can use this as a starting point for your own scripts.

## Integration with Cursor

The Pine Script linter is integrated with the Cursor editor through the rules system. When you edit a Pine Script file in Cursor, the editor will automatically check your code against the rules and provide feedback.

## Troubleshooting

If you encounter issues with the linter or fixer:

1. Make sure you have the required dependencies installed.
2. Check that your configuration file is valid JSON.
3. Verify that your Pine Script files have the correct extension (`.pine` or `.pinescript`).
4. If using the pre-commit hook, make sure it has execute permissions.
5. If the fixer doesn't fix all issues, try running it multiple times or fix the remaining issues manually.

For more help, refer to the [README.md](./README.md) file or the [TradingView Pine Script Style Guide](https://www.tradingview.com/pine-script-docs/writing/style-guide/). 