#!/usr/bin/env node

import fetch from 'node-fetch';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

// Default values
const DEFAULT_SERVER = 'http://localhost:3000';
const DEFAULT_OUTPUT_FILE = 'ai-context.json';

// Parse command line args
const args = process.argv.slice(2);
const taskIndex = args.indexOf('--task');
const filesIndex = args.indexOf('--files');
const serverIndex = args.indexOf('--server');

const task = taskIndex !== -1 && taskIndex + 1 < args.length ? args[taskIndex + 1] : null;
const filesPattern = filesIndex !== -1 && filesIndex + 1 < args.length ? args[filesIndex + 1] : '*';
const serverUrl = serverIndex !== -1 && serverIndex + 1 < args.length ? args[serverIndex + 1] : DEFAULT_SERVER;

// Validate required args
if (!task) {
  console.error('Error: --task parameter is required');
  console.log('Usage: node http-client.js --task "Your task description" [--files "glob/pattern/*.js"] [--server "http://localhost:3000"]');
  process.exit(1);
}

// Helper function to make JSON-RPC requests
async function jsonRpcRequest(method, params = {}) {
  try {
    // Use the /messages endpoint for all JSON-RPC requests
    const response = await fetch(`${serverUrl}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: Date.now(),
        method,
        params,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.error) {
      throw new Error(`JSON-RPC error: ${data.error.message}`);
    }
    
    return data.result;
  } catch (error) {
    throw new Error(`Failed to connect to MCP server: ${error.message}`);
  }
}

// Main function
async function main() {
  try {
    console.log(`Task: ${task}`);
    console.log(`Connecting to MCP server at ${serverUrl}...`);
    
    // First check if server is running with a basic health check
    try {
      const response = await fetch(serverUrl);
      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }
      const data = await response.json();
      console.log(`Connected to server: ${data.server} v${data.version}`);
    } catch (error) {
      throw new Error(`Server not reachable: ${error.message}`);
    }
    
    // Collect available data for the context
    try {
      const serverInfo = {
        name: "MCP Code Analysis Server",
        version: "1.0.0"
      };
      
      // For a future improvement, we could implement proper JSON-RPC over HTTP
      // Currently just creating a simple context with the task and files pattern
      console.log('Preparing context data...');
      
      // Prepare context object with available data
      const context = {
        server: serverInfo,
        task: task,
        files: filesPattern,
        timestamp: new Date().toISOString()
      };
      
      // Write context to file
      await fs.writeFile(
        DEFAULT_OUTPUT_FILE,
        JSON.stringify(context, null, 2),
        'utf-8'
      );
      
      console.log(`✓ Context saved to ${DEFAULT_OUTPUT_FILE}`);
      
    } catch (error) {
      throw new Error(`Failed to prepare context data: ${error.message}`);
    }
    
  } catch (error) {
    console.error(`Error: ${error.message}`);
    console.error('Make sure the server is running with HTTP transport enabled on port 3000');
    process.exit(1);
  }
}

main(); 