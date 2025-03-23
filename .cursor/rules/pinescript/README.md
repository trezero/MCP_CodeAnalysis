# Pine Script Rules for Cursor

This directory contains rules and guidelines for writing Pine Script code in the Cursor editor, following TradingView's official style guide.

## How to Use These Rules

1. **Automatic Enforcement**: Cursor will automatically apply these rules when you're editing `.pine` or `.pinescript` files.

2. **Manual Checking**: You can also run the linter manually to check your Pine Script files:
   ```bash
   python ../utils/pine_linter.py your_script.pine
   ```

3. **Automatic Fixing**: Fix common issues automatically with the fixer:
   ```bash
   python ../utils/pine_fixer.py your_script.pine
   ```

4. **Rule References**: 
   - [Structure Guidelines](./structure.mdc) - How to organize your Pine Script files
   - [Example Code](./example.mdc) - Example of properly structured Pine Script
   - [Refactoring Guidelines](./refactoring.mdc) - How to refactor disorganized code
   - [Section Headers](./headers.mdc) - Standardized section headers to use

## Key Principles

1. **Consistent Structure**: All Pine Script files should follow the same structure with standard sections:
   - METADATA
   - INPUT GROUPS
   - INPUT PARAMETERS
   - VARIABLE DECLARATIONS
   - FUNCTION DEFINITIONS
   - MAIN CALCULATIONS
   - VISUALIZATION
   - ALERTS

2. **Function Organization**: Functions should be defined in the function definitions section, not scattered throughout the code.

3. **Input Parameter Grouping**: Input parameters should be grouped logically and placed in the input parameters section.

4. **Memory Management**: Cleanup operations should be part of the main calculation section.

5. **Naming Conventions** (Following TradingView's Style Guide):
   - Functions: `camelCase` (e.g., `calculateAverage`)
   - Variables: `camelCase` (e.g., `result`)
   - Inputs: `camelCase` (e.g., `length`)
   - Constants: `SNAKE_CASE` (e.g., `MAX_LOOKBACK`)
   - Input groups: `gCamelCase` (e.g., `gAppearance`)

## Getting Started

If you're starting a new Pine Script file, you can use the template file as a starting point:
```bash
cp template.pine your_new_script.pine
```

For existing files that need refactoring, follow the guidelines in [refactoring.mdc](./refactoring.mdc) or use the automatic fixer:
```bash
python ../utils/pine_fixer.py your_script.pine
```

## Linter Features

The Pine Script linter checks for:

1. **Version Declaration**: Ensures the script has a version declaration (`//@version=X`).
2. **Required Sections**: Verifies all standard sections are present.
3. **Section Order**: Checks that sections are in the correct order.
4. **Function Placement**: Ensures functions are defined in the function definitions section.
5. **Input Placement**: Ensures inputs are defined in the input parameters section.
6. **Variable Declaration Placement**: Ensures variables are declared in the variable declarations section.
7. **Naming Conventions**: Checks that functions, inputs, variables, and constants follow TradingView's naming conventions.

## Fixer Features

The Pine Script fixer automatically fixes:

1. **Missing Version Declaration**: Adds `//@version=6` if missing.
2. **Missing Section Headers**: Adds any missing standard section headers.
3. **Naming Conventions**: Converts identifiers to follow TradingView's naming conventions.
4. **Code Organization**: Moves functions, inputs, and variables to their correct sections.

## Troubleshooting

If you're having issues with the rules or linter, please check:
- That your file has the `.pine` or `.pinescript` extension
- That you've included all the required section headers
- That functions are defined in the function definitions section
- That you're following the naming conventions

For more help, refer to the [example.mdc](./example.mdc) file for a complete example of a properly structured Pine Script file or the [TradingView Pine Script Style Guide](https://www.tradingview.com/pine-script-docs/writing/style-guide/). 