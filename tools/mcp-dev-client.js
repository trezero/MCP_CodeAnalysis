#!/usr/bin/env node

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { HttpClientTransport } from '@modelcontextprotocol/sdk/client/http.js';
import fs from 'fs';

// Configuration
const SERVER_URL = 'http://localhost:3000';
const OUTPUT_FILE = 'ai-context.json';

async function main() {
  // Parse command line arguments
  const args = process.argv.slice(2);
  let taskDescription = '';
  let filePattern = '';
  let searchTerm = '';
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--task' && i + 1 < args.length) {
      taskDescription = args[i + 1];
      i++;
    } else if (args[i] === '--files' && i + 1 < args.length) {
      filePattern = args[i + 1];
      i++;
    } else if (args[i] === '--search' && i + 1 < args.length) {
      searchTerm = args[i + 1];
      i++;
    }
  }
  
  if (!taskDescription) {
    console.error('Error: --task parameter is required');
    console.error('Usage: node mcp-dev-client.js --task="Your task" --files="src/path/*.ts" --search="keyword"');
    process.exit(1);
  }
  
  // Create the client and connect to the server
  console.log('Connecting to MCP server at', SERVER_URL);
  const client = new Client({ 
    name: 'mcp-dev-client', 
    version: '1.0.0'
  });
  
  const transport = new HttpClientTransport({
    serverUrl: SERVER_URL
  });
  
  try {
    await client.connect(transport);
    console.log('Connected to MCP server');
    
    // Create a session
    const sessionResponse = await client.callTool({
      name: 'create-session',
      arguments: {
        name: `ai-task-${Date.now()}`
      }
    });
    
    const sessionId = sessionResponse.content[0].text;
    console.log(`Created session with ID: ${sessionId}`);
    
    // Get project info
    console.log('\nGetting project information...');
    const projectInfoResponse = await client.callTool({
      name: 'project-info',
      arguments: {
        sessionId
      }
    });
    
    const projectInfo = JSON.parse(projectInfoResponse.content[0].text);
    console.log('✓ Collected project information');
    
    // Get folder structure
    console.log('\nFetching folder structure...');
    const folderResponse = await client.callTool({
      name: 'folder-structure',
      arguments: {
        sessionId,
        path: '.',
        depth: 2,
        excludePatterns: ['node_modules', '.git']
      }
    });
    
    const folderStructure = JSON.parse(folderResponse.content[0].text);
    console.log('✓ Collected folder structure');
    
    // Search for code if search term is provided
    let searchResults = [];
    if (searchTerm) {
      console.log(`\nSearching for "${searchTerm}" in code...`);
      const searchResponse = await client.callTool({
        name: 'search-code',
        arguments: {
          sessionId,
          query: searchTerm,
          filePatterns: ['**/*.ts', '**/*.js'],
          excludePatterns: ['node_modules/**', 'dist/**']
        }
      });
      
      searchResults = JSON.parse(searchResponse.content[0].text);
      console.log(`✓ Found ${searchResults.length} matches`);
    }
    
    // Get file contents if pattern is provided
    let fileContents = {};
    if (filePattern) {
      console.log(`\nCollecting files matching pattern "${filePattern}"...`);
      // First find matching files
      const searchResponse = await client.callTool({
        name: 'search-code',
        arguments: {
          sessionId,
          query: '*',
          filePatterns: [filePattern],
          excludePatterns: ['node_modules/**', 'dist/**']
        }
      });
      
      const files = JSON.parse(searchResponse.content[0].text);
      console.log(`✓ Found ${files.length} matching files`);
      
      // Then get the content of each file
      for (const file of files) {
        const filePathMatch = file.path || file.file || file.filename;
        if (filePathMatch) {
          console.log(`  Getting contents of ${filePathMatch}...`);
          const fileResponse = await client.callTool({
            name: 'get-file',
            arguments: {
              sessionId,
              path: filePathMatch
            }
          });
          
          fileContents[filePathMatch] = fileResponse.content[0].text;
        }
      }
      console.log(`✓ Collected contents of ${Object.keys(fileContents).length} files`);
    }
    
    // Assemble and save context
    const context = {
      task: taskDescription,
      sessionId,
      timestamp: new Date().toISOString(),
      projectInfo,
      folderStructure,
      searchResults,
      relevantFiles: Object.keys(fileContents),
      fileContents
    };
    
    // Write context to file
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(context, null, 2));
    console.log(`\n✓ Context saved to ${OUTPUT_FILE}`);
    
    // Clean up the session
    await client.callTool({
      name: 'clear-session',
      arguments: {
        sessionId
      }
    });
    console.log('✓ Session cleared');
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    // Close the client connection
    await client.close();
  }
}

main().catch(error => {
  console.error('Error running client:', error);
  process.exit(1);
}); 