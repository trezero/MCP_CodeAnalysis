import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { analyzeRepository, analyzeCode, getMetrics } from "./analyzer.js";
import path from "path";
import fs from "fs";
import { getRepository } from "../../utils/repository-analyzer.js";
import { createSuccessResponse, createErrorResponse } from "../../utils/responses.js";
import { CodeAnalysisResult } from "../../types/responses.js";

/**
 * Register basic code analysis features with the MCP server
 * 
 * This function registers a set of tools for analyzing code structure, dependencies,
 * and metrics. These tools provide the foundation for understanding code repositories
 * and individual files, which can be used by AI agents to gain insights into codebases.
 * 
 * Registered tools:
 * - analyze-dependencies: Analyzes dependencies between components in code
 * - calculate-metrics: Calculates various code quality and complexity metrics
 * - analysis-results: A resource for accessing detailed analysis results by URL
 * - review-code: A prompt for requesting human-like code reviews
 * 
 * @param server - The MCP server instance to register tools with
 * @example
 * ```typescript
 * import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
 * import { registerBasicAnalysisFeatures } from "./features/basic-analysis/index.js";
 * 
 * const server = new McpServer({ name: "code-analyzer", version: "1.0.0" });
 * registerBasicAnalysisFeatures(server);
 * ```
 */
export function registerBasicAnalysisFeatures(server: McpServer) {
  // Tool for analyzing code dependencies
  server.tool(
    "analyze-dependencies",
    {
      repositoryUrl: z.string().optional().describe("URL of the repository to analyze (e.g., 'https://github.com/username/repo')"),
      fileContent: z.string().optional().describe("Source code content to analyze directly instead of from a repository"),
      language: z.string().optional().describe("Programming language of the code (e.g., 'javascript', 'python', 'typescript', 'rust')")
    },
    async ({ repositoryUrl, fileContent, language }) => {
      try {
        const results = await analyzeRepository(repositoryUrl, fileContent, language);
        
        // Return standardized response
        return {
          content: [{
            type: "text",
            text: JSON.stringify(results, null, 2)
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error analyzing dependencies: ${(error as Error).message}`
          }],
          isError: true
        };
      }
    }
  );

  // Tool for calculating code metrics
  server.tool(
    "calculate-metrics",
    {
      repositoryUrl: z.string().optional().describe("URL of the repository to analyze (e.g., 'https://github.com/username/repo')"),
      filePath: z.string().optional().describe("Path to the file within the repository (e.g., 'src/main.ts')"),
      fileContent: z.string().optional().describe("Source code content to analyze directly instead of from a repository"),
      language: z.string().optional().describe("Programming language of the code (e.g., 'javascript', 'python', 'typescript', 'rust')"),
      metrics: z.array(z.string()).optional().describe("Specific metrics to calculate, such as 'complexity', 'linesOfCode', 'maintainability', 'functions', 'classes'")
    },
    async ({ repositoryUrl, filePath, fileContent, language, metrics }) => {
      try {
        const results = await getMetrics({
          repositoryUrl,
          filePath,
          fileContent,
          language,
          metrics: metrics || ["complexity", "linesOfCode", "maintainability"]
        });
        
        return {
          content: [{
            type: "text",
            text: JSON.stringify(results, null, 2)
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error calculating metrics: ${(error as Error).message}`
          }],
          isError: true
        };
      }
    }
  );

  // Resource for accessing detailed analysis results
  server.resource(
    "analysis-results",
    "analysis://:repo/:path",
    async (href) => {
      // href is now a URL object
      const repoUrl = href.pathname.split('/')[1];
      const filePath = href.pathname.split('/')[2];
      
      if (!repoUrl || !filePath) {
        throw new Error(`Invalid analysis URL: ${href.toString()}`);
      }
      
      // Implement the actual fetching logic here
      const repoPath = await getRepository(repoUrl);
      const fullPath = path.join(repoPath, filePath);
      const content = fs.readFileSync(fullPath, 'utf8');
      const analysis = analyzeCode(content, path.extname(filePath).slice(1));
      
      return {
        contents: [{
          text: JSON.stringify(analysis, null, 2),
          uri: `analysis://${repoUrl}/${filePath}`,
          mimeType: "application/json"
        }]
      };
    }
  );

  // Prompt for requesting code review
  server.prompt(
    "review-code",
    {
      code: z.string().describe("The source code to review"),
      language: z.string().optional().describe("Programming language of the code (e.g., 'javascript', 'typescript', 'python')"),
      focus: z.enum(["security", "performance", "maintainability", "all"]).optional().describe("Aspect to focus the review on")
    },
    ({ code, language, focus }) => {
      return {
        messages: [{
          role: "user",
          content: {
            type: "text",
            text: `Please review this ${language || ""} code with a focus on ${focus || "all aspects"}:\n\n${code}`
          }
        }]
      };
    }
  );
}

/**
 * Register primary analysis tools with the MCP server
 * 
 * This function registers the core analysis tools, including the high-level
 * analyze-repository tool that combines multiple analysis capabilities.
 * It first registers the basic analysis features, then adds the composite
 * analyze-repository tool on top.
 * 
 * The analyze-repository tool is particularly useful for AI agents to quickly
 * understand the structure and characteristics of an entire codebase.
 * 
 * @param server - The MCP server instance to register tools with
 * @example
 * ```typescript
 * import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
 * import { registerAnalysisTools } from "./features/basic-analysis/index.js";
 * 
 * const server = new McpServer({ name: "code-analyzer", version: "1.0.0" });
 * registerAnalysisTools(server);
 * ```
 */
export function registerAnalysisTools(server: McpServer) {
  console.log("Registering analyze-repository tool directly");
  
  // First register the basic analysis features
  registerBasicAnalysisFeatures(server);
  
  // Then add analyze-repository tool - with explicit logging
  server.tool(
    "analyze-repository",
    {
      repositoryUrl: z.string().describe("URL of the repository to analyze (e.g., 'https://github.com/username/repo')"),
      depth: z.number().default(2).describe("Analysis depth - higher values analyze more deeply but take longer (1-5)"),
      includeDependencies: z.boolean().default(true).describe("Include dependency analysis in the results"),
      includeComplexity: z.boolean().default(true).describe("Include complexity metrics in the results"),
      specificFiles: z.array(z.string()).optional().describe("Specific files to analyze, can include glob patterns (e.g., ['src/*.ts', 'lib/utils.js'])")
    },
    async (args) => {
      try {
        console.log("analyze-repository called with:", args);
        
        // Perform the actual analysis
        const startTime = Date.now();
        const analysis = await analyzeRepository(args.repositoryUrl);
        
        // Create a standardized response with the results
        const responseData = {
          repository: args.repositoryUrl,
          result: {
            ...analysis.data,
            includedDependencies: args.includeDependencies,
            includedComplexity: args.includeComplexity,
            depth: args.depth,
            specificFiles: args.specificFiles || "all"
          }
        };
        
        // Return MCP-formatted response
        return {
          content: [{
            type: "text",
            text: JSON.stringify(responseData, null, 2)
          }]
        };
      } catch (error) {
        // Create a standardized error response
        const errorResponse = createErrorResponse(
          error instanceof Error ? error.message : String(error),
          "analyze-repository"
        );
        
        // Return MCP-formatted error response
        return {
          content: [{
            type: "text",
            text: JSON.stringify(errorResponse, null, 2)
          }],
          isError: true
        };
      }
    }
  );
}

export * from './analyzer.js'; 