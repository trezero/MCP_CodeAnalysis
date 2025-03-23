# MCP Code Analysis Project Overview

## Project Purpose

This project is focused on building AI-powered code analysis tools that enhance developer productivity, code quality, and monetization opportunities. The system integrates with various MCP (Machine Coded Programmer) services to provide intelligent code analysis.

## Core Components

### 1. Rule System

- Located in `.cursor/rules/`
- Provides guidelines and standards for different aspects of code
- Rule files use `.mdc` extension and contain frontmatter with metadata
- Rules can be applied based on file patterns through glob settings

### 2. Analysis Tools

- Located in corresponding tool directories under `.cursor/rules/`
- Implement various code analysis techniques including:
  - Memory anchor extraction and search
  - Metadata analysis and validation
  - Monetization opportunity identification
  - Code quality assessment
  - Security vulnerability detection

### 3. MCP Integration

- Located in `mcp_server.py` and `.cursor/mcp.json`
- Provides API endpoints for AI services to access analysis tools
- Follows a structured request/response pattern for tool invocation

## Key Conventions

### Memory Anchors

- Important code sections are marked with `MEMORY_ANCHOR: anchor_name`
- Anchors help AI and humans quickly locate and understand critical code sections
- Anchors should follow snake_case naming convention

### Metadata Headers

- All source files should include appropriate metadata in headers or frontmatter
- Metadata includes information about purpose, authors, version, and dependencies
- Standardized formats are used for different file types

### Monetization Features

- Monetization-related code follows specific patterns defined in monetization guidelines
- Revenue potential analysis identifies opportunities for feature monetization
- Pricing strategy analysis helps optimize revenue generation

### File Organization

- Tool-specific implementations are stored in their respective directories
- Supporting utilities are stored in `.cursor/rules/utils/`
- Integration code connects tools to MCP services

## Development Workflow

1. Create or update rule files to define standards
2. Implement analysis tools according to rule specifications
3. Integrate tools with MCP server through API endpoints
4. Test functionality through MCP client interactions
5. Iterate based on feedback and performance metrics

## Key Technologies

- Python for backend tool implementation
- Flask/FastAPI for API endpoint exposure
- JSON for configuration and data exchange
- Various language-specific analysis libraries
- Web technologies for visualization components
