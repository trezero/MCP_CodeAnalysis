// MCP Server entry point
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { fileURLToPath } from 'url';
import path from 'path';

// Import all feature modules
import { registerAnalysisTools } from './features/basic-analysis/index.js';
import { registerDependencyTools } from './features/dependencies/dependency-analyzer.js';
import { registerMetricsTools } from './features/metrics/metrics-calculator.js';
import { registerInsightTools } from './features/insights/insight-manager.js';
import { registerVisualizationTools } from './features/visualization/visualizer.js';
import { registerKnowledgeGraphTools } from './features/knowledge-graph/graph-manager.js';
import { registerSocioTechnicalTools } from './features/socio-technical/st-analyzer.js';
import { registerIdeTools } from './features/basic-analysis/ide-analyzer.js';

// Get the directory name of the current module
const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Create MCP server with stdio transport by default
// Can be overridden with HTTP_TRANSPORT env var for HTTP mode
const useHttpTransport = process.env.HTTP_TRANSPORT === 'true';
const port = process.env.PORT || 3000;
const host = process.env.HOST || 'localhost';

let server;

console.log("Starting server...");

if (useHttpTransport) {
  server = new McpServer({
    transport: {
      type: "http",
      port: port,
      host: host
    }
  });
  
  console.log(`Server running on http://${host}:${port}`);
} else {
  server = new McpServer({
    transport: {
      type: "stdio"
    }
  });
  
  console.log("Server running with stdio transport");
}

// Before registering tools
console.log("About to register tools...");

// Register all tools with the server
console.log("Registering analysis tools...");
try {
  registerAnalysisTools(server);
  console.log("Analysis tools registered successfully");
} catch (error) {
  console.error("Error registering analysis tools:", error);
}

registerDependencyTools(server);
registerMetricsTools(server);
registerInsightTools(server);
registerVisualizationTools(server);
registerKnowledgeGraphTools(server);
registerSocioTechnicalTools(server);
registerIdeTools(server);

// Add this after all registerXTools calls but before server.start()
console.log("Registered tools:", Object.keys(server._registry?.tools || {}));

// After all tools are registered
console.log("All tools registered, starting server...");

// Start the server
server.start(); 