#!/usr/bin/env node

import { spawn } from 'child_process';
import readline from 'readline';
import path from 'path';
import fs from 'fs';

// Process arguments
const args = process.argv.slice(2);
const serverScript = args[0] || 'dist/server.js';

console.log(`Starting MCP client - connecting to ${serverScript}`);

// Spawn the server process
const serverProcess = spawn('node', [serverScript], {
  stdio: ['pipe', 'pipe', 'inherit']
});

// Create readline interface for reading server output
const rl = readline.createInterface({
  input: serverProcess.stdout,
  terminal: false
});

// Track if we're receiving JSON or debug output
let inJsonMode = false;
let jsonBuffer = '';

// Handle server output
rl.on('line', (line) => {
  const trimmedLine = line.trim();
  
  // Skip empty lines
  if (!trimmedLine) return;
  
  // Check if this looks like JSON
  if (trimmedLine.startsWith('{') || trimmedLine.startsWith('[')) {
    try {
      const parsed = JSON.parse(trimmedLine);
      console.log('\n🔄 MCP Message:');
      console.log(JSON.stringify(parsed, null, 2));
      
      // If this is a successful response with implementation info, the server is ready
      if (parsed.result && parsed.result.implementation) {
        console.log('\n✅ MCP Server initialized successfully!');
        console.log(`   Name: ${parsed.result.implementation.name}`);
        console.log(`   Version: ${parsed.result.implementation.version}`);
        
        // Now let's discover available tools
        sendJsonRpc('rpc.discover', { method: 'tools.list' });
      }
      
      // If we get tools back, show them
      if (parsed.result && parsed.result.tools) {
        console.log('\n🧰 Available Tools:');
        parsed.result.tools.forEach(tool => {
          console.log(`   • ${tool.name}${tool.description ? `: ${tool.description}` : ''}`);
        });
        
        // Optionally, you could auto-call a tool here if needed
      }
    } catch (error) {
      // Not valid JSON, treat as debug output
      console.log(`🔍 Server: ${line}`);
    }
  } else {
    // Regular output
    console.log(`🔍 Server: ${line}`);
  }
});

// Send a JSON-RPC request to the server
function sendJsonRpc(method, params = {}) {
  const request = {
    jsonrpc: '2.0',
    id: Date.now(),
    method,
    params
  };
  
  const requestStr = JSON.stringify(request) + '\n';
  console.log('\n📤 Sending request:');
  console.log(JSON.stringify(request, null, 2));
  
  serverProcess.stdin.write(requestStr);
}

// Handle process exit
serverProcess.on('close', (code) => {
  console.log(`\n👋 Server process exited with code ${code}`);
  process.exit(0);
});

// Initial discovery request
setTimeout(() => {
  console.log('\n🚀 Discovering server capabilities...');
  sendJsonRpc('rpc.discover');
}, 2000); // Wait for server to initialize

// Handle ctrl+c to exit gracefully
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down...');
  serverProcess.kill();
  process.exit(0);
}); 