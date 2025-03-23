import { getRepository, listFiles } from "../../utils/repository-analyzer.js";
import fs from "fs";
import path from "path";
import { v4 as uuidv4 } from "uuid";
import { z } from "zod";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { CodeAnalysisResult } from "../../types/responses.js";
import { executeWithTiming, createErrorResponse } from "../../utils/responses.js";

// In-memory cache for analysis results
const analysisCache = new Map<string, any>();

/**
 * Analyze a repository's dependencies and structure
 */
export async function analyzeRepository(
  repositoryUrl?: string,
  fileContent?: string,
  language?: string
): Promise<any> {
  return executeWithTiming('analyze-repository', async () => {
    if (repositoryUrl) {
      const repoPath = await getRepository(repositoryUrl);
      const files = listFiles(repoPath);
      const analysisId = uuidv4();
      
      // Perform dependency analysis
      const dependencies = extractDependencies(repoPath, files, language);
      
      // Store results in cache
      const results = {
        repositoryUrl,
        analysisId,
        dependencies,
        fileCount: files.length,
        timestamp: new Date().toISOString()
      };
      
      analysisCache.set(analysisId, results);
      return results;
    } else if (fileContent) {
      // Analyze single file content
      const dependencies = analyzeCode(fileContent, language);
      return {
        analysisId: uuidv4(),
        dependencies,
        timestamp: new Date().toISOString()
      };
    } else {
      throw new Error("Either repositoryUrl or fileContent must be provided");
    }
  });
}

/**
 * Analyze a single code snippet
 */
export function analyzeCode(code: string, language?: string): CodeAnalysisResult {
  // This would ideally use a language-specific parser
  // For demonstration, we'll do a simple analysis
  
  // Mock implementation - would be replaced with actual parsing
  const imports = extractImports(code, language);
  const functions = extractFunctions(code, language);
  const classes = extractClasses(code, language);
  
  return {
    imports,
    functions,
    classes,
    complexity: calculateComplexity(code, language)
  };
}

/**
 * Get metrics for files or a previous analysis
 */
export async function getMetrics(options: {
  repositoryUrl?: string;
  filePath?: string;
  fileContent?: string;
  language?: string;
  metrics?: string[];
  analysisId?: string;
  type?: string;
}): Promise<any> {
  const { repositoryUrl, filePath, fileContent, language, metrics, analysisId, type } = options;
  
  // If analysisId is provided, retrieve from cache
  if (analysisId) {
    const cachedAnalysis = analysisCache.get(analysisId);
    if (!cachedAnalysis) {
      throw new Error(`Analysis not found: ${analysisId}`);
    }
    
    if (type) {
      return cachedAnalysis[type] || {};
    }
    
    return cachedAnalysis;
  }
  
  // Otherwise perform new analysis
  if (repositoryUrl) {
    const repoPath = await getRepository(repositoryUrl);
    
    if (filePath) {
      // Analyze specific file
      const fullPath = path.join(repoPath, filePath);
      const code = fs.readFileSync(fullPath, 'utf8');
      return calculateMetrics(code, language, metrics);
    } else {
      // Analyze entire repository
      const files = listFiles(repoPath);
      const allMetrics: Record<string, any> = {};
      
      for (const file of files) {
        const fullPath = path.join(repoPath, file);
        const code = fs.readFileSync(fullPath, 'utf8');
        allMetrics[file] = calculateMetrics(code, path.extname(file).slice(1), metrics);
      }
      
      return allMetrics;
    }
  } else if (fileContent) {
    // Analyze provided code content
    return calculateMetrics(fileContent, language, metrics);
  } else {
    throw new Error("Either repositoryUrl, filePath, or fileContent must be provided");
  }
}

/**
 * Extract imported modules from code
 */
function extractImports(code: string, language?: string): string[] {
  // Basic implementation - would be replaced with language-specific parsers
  const imports: string[] = [];
  
  if (language === 'javascript' || language === 'typescript' || !language) {
    // Simple regex to find import statements (not comprehensive)
    const importRegex = /import\s+(?:{[^}]*}|\*\s+as\s+\w+|\w+)\s+from\s+['"]([^'"]+)['"]/g;
    let match;
    while ((match = importRegex.exec(code)) !== null) {
      imports.push(match[1]);
    }
  }
  
  return imports;
}

/**
 * Extract function names from code
 */
function extractFunctions(code: string, language?: string): string[] {
  // Basic implementation - would be replaced with language-specific parsers
  const functions: string[] = [];
  
  if (language === 'javascript' || language === 'typescript' || !language) {
    // Simple regex to find function declarations (not comprehensive)
    const funcRegex = /function\s+(\w+)\s*\(/g;
    let match;
    while ((match = funcRegex.exec(code)) !== null) {
      functions.push(match[1]);
    }
    
    // Arrow functions with names
    const arrowFuncRegex = /const\s+(\w+)\s*=\s*(?:\([^)]*\)|\w+)\s*=>/g;
    while ((match = arrowFuncRegex.exec(code)) !== null) {
      functions.push(match[1]);
    }
  }
  
  return functions;
}

/**
 * Extract class names from code
 */
function extractClasses(code: string, language?: string): string[] {
  // Basic implementation - would be replaced with language-specific parsers
  const classes: string[] = [];
  
  if (language === 'javascript' || language === 'typescript' || !language) {
    // Simple regex to find class declarations (not comprehensive)
    const classRegex = /class\s+(\w+)(?:\s+extends\s+\w+)?/g;
    let match;
    while ((match = classRegex.exec(code)) !== null) {
      classes.push(match[1]);
    }
  }
  
  return classes;
}

/**
 * Extract dependencies from a repository
 */
function extractDependencies(repoPath: string, files: string[], language?: string): Record<string, string[]> {
  const dependencies: Record<string, string[]> = {};
  
  for (const file of files) {
    const fullPath = path.join(repoPath, file);
    try {
      const code = fs.readFileSync(fullPath, 'utf8');
      const fileLanguage = language || path.extname(file).slice(1);
      dependencies[file] = extractImports(code, fileLanguage);
    } catch (error) {
      console.warn(`Error reading file ${file}: ${(error as Error).message}`);
    }
  }
  
  return dependencies;
}

/**
 * Calculate metrics for a code snippet
 */
function calculateMetrics(code: string, language?: string, metricTypes?: string[]): Record<string, any> {
  const result: Record<string, any> = {};
  
  if (!metricTypes || metricTypes.includes('linesOfCode')) {
    result.linesOfCode = code.split('\n').length;
  }
  
  if (!metricTypes || metricTypes.includes('complexity')) {
    // Simple complexity heuristic (would be replaced with actual analysis)
    const decisions = (code.match(/if|else|for|while|switch|case|try|catch/g) || []).length;
    result.complexity = decisions;
  }
  
  if (!metricTypes || metricTypes.includes('maintainability')) {
    // Simple maintainability heuristic
    const commentLines = (code.match(/\/\/.*$|\/*[\s\S]*?\*\//gm) || []).length;
    const codeLines = code.split('\n').length;
    
    // Calculate a simple maintainability index (higher is better)
    const commentRatio = commentLines / codeLines;
    const complexity = result.complexity || 0;
    
    result.maintainability = Math.max(0, 100 - (complexity * 0.25) + (commentRatio * 20));
  }
  
  return result;
}

/**
 * Calculate complexity for a code snippet
 */
function calculateComplexity(code: string, language?: string): number {
  // Simple complexity heuristic (would be replaced with actual analysis)
  const decisions = (code.match(/if|else|for|while|switch|case|try|catch/g) || []).length;
  return decisions;
}

export function registerAnalysisTools(server: McpServer) {
  // Make sure this exact tool name is registered
  server.tool(
    "analyze-repository",  // This name must match exactly what the CLI calls
    {
      repositoryUrl: z.string().describe("URL of the repository to analyze"),
      depth: z.number().default(2).describe("Analysis depth"),
      includeDependencies: z.boolean().default(true).describe("Include dependency analysis"),
      includeComplexity: z.boolean().default(true).describe("Include complexity analysis"),
      specificFiles: z.array(z.string()).optional().describe("Specific files to analyze")
    },
    async (args) => {
      // Basic implementation
      console.log("Analyzing repository:", args.repositoryUrl);
      
      // Handle specific files if provided
      if (args.specificFiles && args.specificFiles.length > 0) {
        console.log("Analyzing specific files:", args.specificFiles);
      }
      
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            repository: args.repositoryUrl,
            analysisDepth: args.depth,
            result: "Sample repository analysis results"
          }, null, 2)
        }]
      };
    }
  );
} 