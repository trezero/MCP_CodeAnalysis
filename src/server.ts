import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import express from "express";

import { registerAnalysisTools } from "./features/basic-analysis/index.js";
import { registerCodeMetricsTools } from "./features/code-metrics/index.js";
import { registerDependencyAnalysisTools } from "./features/dependency-analysis/index.js";
import { registerIdeTools } from "./features/basic-analysis/ide-analyzer.js";
import { registerCodeQualityTools } from "./features/code-quality/index.js";
import { registerKnowledgeGraphFeatures } from "./features/knowledge-graph/index.js";
import { registerVisualizationFeatures } from "./features/visualization/index.js";
import { registerMemoryFeatures } from "./features/memory/index.js";
import { registerSocioTechnicalFeatures } from "./features/socio-technical/index.js";
import { registerMultiRepoFeatures } from "./features/multi-repo/index.js";
import { registerEvolutionFeatures } from "./features/evolution/index.js";
import { registerSessionTools } from "./features/session-manager/index.js";
import { registerDevTools } from "./features/dev-tools/index.js";

// Create a new server instance with a name and version
const server = new McpServer({
  name: "codeanalysis-mcp",
  version: "1.0.0",
});

// Track registered tools to avoid duplicates
const registeredTools = new Set<string>();

// Helper function to register tools only once
function registerToolsOnce(registerFn: (server: McpServer) => void) {
  try {
    // Register the tools
    registerFn(server);
  } catch (error) {
    console.error(`Error registering tools: ${error}`);
  }
}

// Register all features
console.log("• Registering analysis features...");
registerToolsOnce(registerAnalysisTools);
console.log("✓");

console.log("• Registering code metrics features...");
registerToolsOnce(registerCodeMetricsTools);
console.log("✓");

console.log("• Registering dependency analysis features...");
registerToolsOnce(registerDependencyAnalysisTools);
console.log("✓");

console.log("• Registering IDE tools features...");
registerToolsOnce(registerIdeTools);
console.log("✓");

console.log("• Registering code quality features...");
registerToolsOnce(registerCodeQualityTools);
console.log("✓");

console.log("• Registering knowledge graph features...");
registerToolsOnce(registerKnowledgeGraphFeatures);
console.log("✓");

console.log("• Registering visualization features...");
registerToolsOnce(registerVisualizationFeatures);
console.log("✓");

console.log("• Registering memory features...");
registerToolsOnce(registerMemoryFeatures);
console.log("✓");

console.log("• Registering socio-technical features...");
registerToolsOnce(registerSocioTechnicalFeatures);
console.log("✓");

console.log("• Registering multi-repo features...");
registerToolsOnce(registerMultiRepoFeatures);
console.log("✓");

console.log("• Registering evolution features...");
registerToolsOnce(registerEvolutionFeatures);
console.log("✓");

console.log("• Registering session manager features...");
registerToolsOnce(registerSessionTools);
console.log("✓");

console.log("• Registering developer tools features...");
registerToolsOnce(registerDevTools);
console.log("✓");

console.log("✓ Tool registration complete");

// Use HTTP transport with SSE by default, with fallback to stdio if STDIO_TRANSPORT is set
const useStdio = process.env.STDIO_TRANSPORT === "true";
const port = process.env.PORT ? parseInt(process.env.PORT, 10) : 3000;

if (useStdio) {
  // For stdio transport
  console.log("Server configured for stdio transport");
  const transport = new StdioServerTransport();

  // Connect using stdio transport
  server
    .connect(transport)
    .then(() => {
      console.log("✓ Server connected and ready to handle stdio requests");
    })
    .catch((err) => {
      console.error("Failed to start server with stdio transport:", err);
    });
} else {
  // For HTTP transport with SSE
  console.log(`Server configured for HTTP transport on port ${port}`);

  // Create Express app
  const app = express();
  app.use(express.json());

  // Set up SSE endpoint for client connections
  app.get("/sse", (req, res) => {
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");

    const transport = new SSEServerTransport("/messages", res);

    // Connect the MCP server to this transport
    server.connect(transport).catch((err) => {
      console.error("Failed to connect server to SSE transport:", err);
      res.end();
    });
  });

  // Set up endpoint for client messages
  app.post("/messages", express.json(), async (req, res) => {
    try {
      // Forward message to the server
      const transport = new SSEServerTransport("/messages", res);
      await transport.handlePostMessage(req, res);
    } catch (error) {
      console.error("Error handling client message:", error);
      res.status(500).json({ error: "Internal server error" });
    }
  });

  // Simple health check endpoint
  app.get("/", (req, res) => {
    res.status(200).json({
      status: "ok",
      server: "MCP Code Analysis Server",
      version: "1.0.0",
    });
  });

  // Start the HTTP server
  app.listen(port, () => {
    console.log(`✓ Server listening on port ${port}`);
    console.log("✓ MCP server ready to handle HTTP requests");
  });
}
