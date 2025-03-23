#!/bin/bash

# Colors for better output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}TypeScript Compiler Check for Pine Script Extension${NC}"
echo -e "This script verifies that TypeScript is properly set up for the Pine Script extension."

# Navigate to the pine-script-syntax directory
cd ../../pine-script-syntax

# Check if TypeScript is installed
if ! command -v tsc &> /dev/null; then
    echo -e "${RED}TypeScript compiler not found! Installing TypeScript...${NC}"
    npm install -g typescript
fi

# Check if the TypeScript config file exists
if [ ! -f "tsconfig.json" ]; then
    echo -e "${RED}Error: tsconfig.json not found!${NC}"
    exit 1
fi

echo -e "${GREEN}TypeScript configuration found.${NC}"

# Run TypeScript compiler
echo -e "${YELLOW}Compiling TypeScript files...${NC}"
tsc

# Check if compilation was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}TypeScript compilation successful!${NC}"
else
    echo -e "${RED}TypeScript compilation failed. Please fix the errors and try again.${NC}"
    exit 1
fi

# Create a simple test file to verify our formatter
echo -e "${YELLOW}Creating a test file to verify the formatter...${NC}"
cat > temp-test-formatting.pine << EOL
//@version=5
indicator("Format Test", overlay=true)

// Test excessive spaces
if volume         <= volume[1]
    alert("Volume decreasing")

// Test compound operator in ternary
test() =>
    count       == 0 ? 0.0 : 1.0
EOL

# Create a simple test script
cat > temp-test-formatter.js << EOL
const fs = require('fs');
const { formatPineScriptText } = require('./out/formatter/pineFormatter');

// Read test file
const content = fs.readFileSync('temp-test-formatting.pine', 'utf8');

// Format the content
const formattedContent = formatPineScriptText(content);

// Output the before and after
console.log('=== ORIGINAL ===');
console.log(content);
console.log('\n=== FORMATTED ===');
console.log(formattedContent);

// Verify the fix for excessive spaces
const fixWorking = 
    !formattedContent.includes('volume         <=') && 
    !formattedContent.includes('count       ==');

console.log('\n=== TEST RESULT ===');
if (fixWorking) {
    console.log('✓ Fix for excessive spaces is working correctly!');
} else {
    console.log('✗ Fix for excessive spaces is NOT working correctly!');
}
EOL

# Run the test
echo -e "${YELLOW}Running the formatter test...${NC}"
node temp-test-formatter.js

# Clean up
echo -e "${YELLOW}Cleaning up test files...${NC}"
rm temp-test-formatting.pine temp-test-formatter.js

echo -e "${GREEN}TypeScript compiler check completed.${NC}" 