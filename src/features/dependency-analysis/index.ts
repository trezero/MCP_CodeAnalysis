import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { analyzeDependencies } from "./dependency-analyzer.js";

export function registerDependencyAnalysisTools(server: McpServer) {
  server.tool(
    "analyze-dependencies",
    {
      repositoryUrl: z.string().optional().describe("URL or path to the repository to analyze"),
      repositoryPath: z.string().optional().describe("Path to the repository to analyze"),
      fileContent: z.string().optional().describe("File content to analyze"),
      format: z.enum(["json", "mermaid", "dot"]).optional().describe("Output format for the dependency graph")
    },
    async ({ repositoryUrl, repositoryPath, fileContent, format = "json" }) => {
      try {
        const repoPath = repositoryPath || repositoryUrl; // Use either one
        if (!repoPath && !fileContent) {
          throw new Error("Either repositoryUrl, repositoryPath, or fileContent must be provided");
        }
        
        console.log(`Analyzing dependencies in: ${repoPath || 'provided content'}`);
        
        // Perform the analysis
        const analysis = await analyzeDependencies(repoPath || '.');
        
        // Format the result based on requested format
        let formattedResult;
        switch (format) {
          case "mermaid":
            formattedResult = generateMermaidGraph(analysis.graph);
            break;
          case "dot":
            formattedResult = generateDotGraph(analysis.graph);
            break;
          default:
            formattedResult = JSON.stringify(analysis, null, 2);
        }
        
        return {
          content: [{
            type: "text",
            text: formattedResult
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
}

/**
 * Generate a Mermaid graph from dependency data
 */
function generateMermaidGraph(graph: any): string {
  let mermaid = "graph TD;\n";
  
  // Add nodes
  for (const node of graph.nodes) {
    mermaid += `  ${formatNodeId(node.name)}["${node.name}${node.version ? ` (${node.version})` : ''}"`;
    
    // Style nodes based on type
    if (node.type === 'direct') {
      mermaid += ' style="fill:#a8d08d"';
    } else if (node.type === 'dev') {
      mermaid += ' style="fill:#ffcc99"';
    } else if (node.type === 'internal') {
      mermaid += ' style="fill:#a4c2f4"';
    }
    
    mermaid += "];\n";
  }
  
  // Add edges
  for (const edge of graph.edges) {
    mermaid += `  ${formatNodeId(edge.source)} --> ${formatNodeId(edge.target)};\n`;
  }
  
  return mermaid;
}

/**
 * Generate a DOT graph from dependency data
 */
function generateDotGraph(graph: any): string {
  let dot = "digraph Dependencies {\n";
  
  // Add graph settings
  dot += "  rankdir=TD;\n";
  dot += "  node [shape=box, style=filled, fontname=Arial];\n";
  
  // Add nodes
  for (const node of graph.nodes) {
    dot += `  "${node.name}" [label="${node.name}${node.version ? `\\n${node.version}` : ''}"`;
    
    // Style nodes based on type
    if (node.type === 'direct') {
      dot += ', fillcolor="#a8d08d"';
    } else if (node.type === 'dev') {
      dot += ', fillcolor="#ffcc99"';
    } else if (node.type === 'internal') {
      dot += ', fillcolor="#a4c2f4"';
    } else {
      dot += ', fillcolor="#f5f5f5"';
    }
    
    dot += "];\n";
  }
  
  // Add edges
  for (const edge of graph.edges) {
    dot += `  "${edge.source}" -> "${edge.target}";\n`;
  }
  
  dot += "}\n";
  return dot;
}

/**
 * Format a node name to be valid in Mermaid
 */
function formatNodeId(name: string): string {
  // Replace characters that are problematic in Mermaid IDs
  return name.replace(/[^a-zA-Z0-9]/g, '_');
} 