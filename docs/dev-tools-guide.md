# Developer Tools Guide

This guide explains how to leverage the MCP server's developer tools to enhance your AI-assisted development workflow.

## Overview

The Developer Tools feature provides specialized tools for developers working with this codebase. These tools are designed to enhance developer productivity by providing quick access to common tasks, code insights, and documentation.

## Available Tools

### `search-code`

Search for specific code patterns across the repository.

**Parameters:**

- `query` (string): The search query to find code in the repository
- `filePattern` (string, optional): Optional file pattern to limit search (e.g., '\*.ts')
- `maxResults` (number, default: 10): Maximum number of results to return

**Example:**

```javascript
const results = await client.executeTool("search-code", {
  query: "registerFeatures",
  filePattern: "*.ts",
  maxResults: 5,
});
```

### `project-info`

Get information about the current project, including package details, git status, and file statistics.

**Parameters:** None

**Example:**

```javascript
const info = await client.executeTool("project-info", {});
```

### `get-file`

Retrieve the contents of a specific file, with optional line range selection.

**Parameters:**

- `path` (string): Relative path to the file
- `startLine` (number, optional): Starting line number (1-based)
- `endLine` (number, optional): Ending line number (1-based)

**Example:**

```javascript
const fileContent = await client.executeTool("get-file", {
  path: "src/server.ts",
  startLine: 10,
  endLine: 20,
});
```

### `folder-structure`

Get the directory structure of a specified folder.

**Parameters:**

- `path` (string, default: "."): Relative path to the directory
- `depth` (number, default: 2): Depth of folders to show

**Example:**

```javascript
const structure = await client.executeTool("folder-structure", {
  path: "src/features",
  depth: 3,
});
```

## Using with AI Assistants

These tools are particularly useful when working with AI assistants to improve their understanding of your codebase. Here are some common scenarios:

### Helping AIs Understand Your Codebase

When working with an AI assistant, you can instruct it to use the MCP tools to better understand your codebase:

```
"Please use the MCP 'project-info' tool to understand the project structure,
then use 'search-code' to find implementations related to the feature I'm working on."
```

### Context Sharing Between Sessions

Combined with the Session Manager tools, you can maintain context across multiple AI interactions:

1. Create a session for a specific development task
2. Use dev tools to add code context to the session
3. Reference the session in future AI interactions

Example session creation:

```javascript
const session = await client.executeTool("create-session", {
  sessionId: "feature-login-dev",
  metadata: {
    purpose: "Login feature development",
    features: ["dev-tools"],
  },
});
```

## Integration Example

See the complete example in `examples/dev-tools-client.js` which demonstrates how to:

1. Connect to the MCP server
2. Execute various developer tools
3. Create and maintain development sessions

## Best Practices

1. **Targeted Searches**: When using `search-code`, be specific with your queries to avoid overwhelming results
2. **Session Naming**: Use descriptive session IDs that relate to specific features or tasks
3. **File Access**: Use line ranges when accessing large files to focus on relevant sections
4. **Context Management**: Create separate sessions for different development tasks

## Extending the Tools

If you need additional developer tools, you can extend the functionality by modifying `src/features/dev-tools/index.ts` and adding new tools following the existing patterns.
