#!/usr/bin/env node

/**
 * AI Development Helper
 * 
 * This script helps prepare code context for AI interactions by using MCP tools
 * to gather relevant information about the current codebase and development task.
 * 
 * Usage:
 *   node tools/ai-dev-helper.js --task="Implement login feature" --files="src/auth/*.ts" --search="authentication"
 */

import { McpClient } from '@modelcontextprotocol/sdk/client/mcp.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { parseArgs } from 'node:util';

// Get the directory name of the current module
const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Parse command line arguments
const options = {
  task: { type: 'string', short: 't', default: '' },
  files: { type: 'string', short: 'f', default: '' },
  search: { type: 'string', short: 's', default: '' },
  output: { type: 'string', short: 'o', default: 'ai-context.json' },
  sessionId: { type: 'string', short: 'i', default: `dev-${Date.now()}` }
};

const { values: args } = parseArgs({ options, allowPositionals: true });

async function main() {
  console.log('🚀 AI Development Helper');
  console.log('------------------------');
  
  // Create an MCP client
  const client = new McpClient();
  const transport = new StdioClientTransport();
  
  try {
    // Connect to the MCP server
    console.log('Connecting to MCP server...');
    await client.connect(transport);
    console.log('✅ Connected to MCP server');
    
    // Create a new session
    console.log(`Creating session: ${args.sessionId}`);
    const sessionResponse = await client.executeTool('create-session', {
      sessionId: args.sessionId,
      metadata: {
        task: args.task || 'Development assistance',
        timestamp: new Date().toISOString()
      }
    });
    
    const sessionResult = JSON.parse(sessionResponse.content[0].text).result;
    console.log(`✅ Session created: ${sessionResult.sessionId}`);
    
    // Collect context data
    const context = {
      task: args.task,
      timestamp: new Date().toISOString(),
      sessionId: args.sessionId,
      projectInfo: null,
      codeSearchResults: null,
      relevantFiles: [],
      folderStructure: null
    };
    
    // Get project info
    console.log('Gathering project information...');
    const projectInfoResponse = await client.executeTool('project-info', {});
    context.projectInfo = JSON.parse(projectInfoResponse.content[0].text).result;
    console.log('✅ Project information collected');
    
    // Search for relevant code if search term provided
    if (args.search) {
      console.log(`Searching for code related to: ${args.search}`);
      const searchResponse = await client.executeTool('search-code', {
        query: args.search,
        maxResults: 20
      });
      context.codeSearchResults = JSON.parse(searchResponse.content[0].text).result;
      console.log(`✅ Found ${context.codeSearchResults.resultsCount} code references`);
    }
    
    // Get folder structure
    console.log('Collecting folder structure...');
    const folderResponse = await client.executeTool('folder-structure', {
      path: 'src',
      depth: 3
    });
    context.folderStructure = JSON.parse(folderResponse.content[0].text).result;
    console.log(`✅ Folder structure collected (${context.folderStructure.count} directories)`);
    
    // Get content of relevant files if specified
    if (args.files) {
      const filePatterns = args.files.split(',');
      console.log(`Collecting content from files matching: ${filePatterns.join(', ')}`);
      
      // This is a simplified approach - in a real implementation,
      // you would use a glob pattern matching library to find files
      const filesToGet = [
        // Example hardcoded files based on patterns
        // In a real implementation, these would be dynamically found
        'src/server.ts',
        'src/features/dev-tools/index.ts'
      ];
      
      for (const file of filesToGet) {
        console.log(`Getting content from: ${file}`);
        try {
          const fileResponse = await client.executeTool('get-file', {
            path: file
          });
          
          const fileResult = JSON.parse(fileResponse.content[0].text).result;
          context.relevantFiles.push({
            path: fileResult.path,
            totalLines: fileResult.totalLines,
            content: fileResult.content
          });
          console.log(`✅ Added ${file} (${fileResult.totalLines} lines)`);
        } catch (error) {
          console.error(`❌ Error getting file ${file}:`, error.message);
        }
      }
    }
    
    // Output the context
    const outputPath = path.resolve(process.cwd(), args.output);
    fs.writeFileSync(outputPath, JSON.stringify(context, null, 2));
    console.log(`\n✅ Context saved to: ${outputPath}`);
    console.log('\nAI context preparation complete!');
    console.log(`\nTo use this context in AI interactions, include the contents of ${args.output}`);
    console.log(`Or reference session ID: ${args.sessionId}`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  } finally {
    process.exit(0);
  }
}

main().catch(console.error); 