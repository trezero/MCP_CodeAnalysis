# API Contract Verification Process

This document outlines the process for verifying that all components adhere to the established API contracts. Ensuring contract compliance is crucial for maintainability, interoperability, and enabling future extensions.

## Core API Contracts

### 1. Tool Response Contract

All tools must return responses that conform to the `ToolResponse` type:

```typescript
type ToolResponse<T> = {
  data: T;
  metadata: {
    tool: string;
    version: string;
    executionTime: number;
    timestamp: string;
  };
  status: {
    success: boolean;
    code: number;
    message?: string;
  };
  context?: {
    sessionId?: string;
    relatedResults?: string[];
  };
};
```

### 2. Tool Registration Contract

All tools must be registered using the MCP server's `tool` method with proper parameter schemas:

```typescript
server.tool(
  toolName: string,
  paramSchema: z.ZodRawShape,
  handler: (params: any) => Promise<any>
): void
```

### 3. State Machine Contract

State machines must adhere to the standard event types and context structure:

```typescript
interface ToolMachineContext {
  toolName: string | null;
  parameters: Record<string, any> | null;
  result: any | null;
  error: Error | null;
  sessionId: string | null;
  selectedTool: string | null;
  history: Array<{
    tool: string;
    result: any;
    timestamp: string;
  }>;
}

type ToolMachineEvent =
  | { type: "SELECT_TOOL"; toolName: string }
  | { type: "SET_PARAMETERS"; parameters: Record<string, any> }
  | { type: "EXECUTE" }
  | { type: "RECEIVED_RESULT"; result: any }
  | { type: "ERROR"; error: Error }
  | { type: "CANCEL" }
  | { type: "RESET" };
```

## Verification Methods

### 1. Static Analysis Verification

We use TypeScript's type system to verify API contracts at compile time.

#### Required Checks:

- Type compatibility for all tool responses
- Proper use of generic type parameters
- Correct implementation of interfaces
- Proper handling of optional fields

#### Implementation:

```typescript
// Add a script to package.json that runs type checking
// "verify-types": "tsc --noEmit"
```

### 2. Runtime Schema Validation

We use Zod schemas to validate structures at runtime.

#### Required Tests:

- Verify tool responses against ToolResponseSchema
- Test parameter validation for all tools
- Ensure proper error handling for invalid inputs

#### Example Test:

```typescript
it("should validate tool responses against schema", () => {
  const response = createSuccessResponse("test data", "test-tool");
  const result = ToolResponseSchema.safeParse(response);
  expect(result.success).toBe(true);
});
```

### 3. Integration Testing

Integration tests verify that components work together correctly.

#### Required Tests:

- End-to-end tests for tool registration and execution
- State machine integration with tool execution service
- Session management across multiple tool calls

#### Example Test:

```typescript
it("should maintain state across multiple tool calls", async () => {
  // Create a stateful tool
  createStatefulTool(
    mockServer,
    "stateful-tool",
    { param: z.string() },
    async (params) => {
      return params.param;
    }
  );

  // Execute the tool twice with the same session ID
  const firstCall = await mockServer.lastHandler({
    param: "first",
    sessionId: "test-session",
  });
  const secondCall = await mockServer.lastHandler({
    param: "second",
    sessionId: "test-session",
  });

  // Verify session state was maintained
  expect(firstCall.context.sessionId).toBe("test-session");
  expect(secondCall.context.sessionId).toBe("test-session");
});
```

### 4. Documentation Verification

Verify that all components have proper documentation that matches implementation.

#### Required Checks:

- JSDoc comments for all public functions and methods
- Parameter descriptions for all tool parameters
- Examples for complex parameters and return values
- Descriptions of error conditions and handling

#### Example Check:

```typescript
it('should include parameter descriptions', () => {
  // Extract parameter schema from tool registration
  const toolParams = /* extract parameter schema */;

  // Verify all parameters have descriptions
  Object.entries(toolParams).forEach(([name, schema]) => {
    expect(schema.description).toBeDefined();
  });
});
```

## Verification Process

### Pre-Commit Verification

1. Run static type checking:

   ```bash
   npm run verify-types
   ```

2. Run unit tests with contract verification:

   ```bash
   npm run test:contracts
   ```

3. Verify documentation coverage:
   ```bash
   npm run verify-docs
   ```

### Continuous Integration Verification

Our CI pipeline runs the following checks:

1. Static type analysis with strict mode
2. Full test suite including contract tests
3. Documentation coverage analysis
4. Integration test suite

## Adding New Components

When adding new components:

1. Define clear API contracts using TypeScript interfaces
2. Create Zod schemas for runtime validation
3. Write tests that verify contract compliance
4. Add comprehensive documentation that matches implementation

### Component Checklist

- [ ] TypeScript interfaces and types defined
- [ ] Zod schemas for runtime validation
- [ ] Helper functions for common operations
- [ ] Unit tests for individual functions
- [ ] Integration tests with dependent components
- [ ] Contract verification tests
- [ ] JSDoc documentation with examples

## Enforcing Contracts

### Code Review Guidelines

When reviewing code that implements or modifies API contracts:

1. Verify type safety and proper use of generics
2. Check for runtime validation of inputs and outputs
3. Ensure proper error handling for contract violations
4. Confirm documentation is updated to match implementation

### Automated Enforcement

We use the following tools to enforce API contracts:

1. ESLint with TypeScript plugin
2. Custom rules for ensuring proper JSDoc documentation
3. Husky pre-commit hooks for running verification scripts
4. CI/CD pipelines that block merges on contract violations

## Tool-Specific Contracts

### Code Analysis Tools

All code analysis tools must:

1. Accept file paths in a consistent format
2. Return analysis results in a structured format
3. Handle errors for file not found, parsing errors, etc.
4. Include metadata about analysis run time and versions

### State Management Tools

All stateful tools must:

1. Support the sessionId parameter
2. Maintain state between calls with the same sessionId
3. Handle expired or invalid sessions gracefully
4. Clear state when requested

## Contract Versioning

When making changes to API contracts:

1. Document the changes in a changelog
2. Update version numbers according to semver principles
3. Provide migration guides for breaking changes
4. Maintain backward compatibility when possible

## Next Steps for Phase 2

1. Create additional contract verification tests for Redis integration
2. Develop contract specifications for tool discovery mechanism
3. Define interface contracts for Rust-based analysis tools
4. Expand contract verification to cover all API endpoints
