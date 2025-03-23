#!/usr/bin/env node

import { spawn } from 'child_process';
import readline from 'readline';

// Path to the server script
const serverPath = process.argv[2] || "dist/server.js";

// Spawn the server process
const serverProcess = spawn("node", [serverPath], {
  stdio: ["pipe", "pipe", "pipe"],
});

// Create readline interface for reading server output
const rl = readline.createInterface({
  input: serverProcess.stdout,
  terminal: false,
});

// Set up error handling
serverProcess.stderr.on("data", (data) => {
  console.error(`Server error: ${data.toString()}`);
});

// Handle server process exit
serverProcess.on("close", (code) => {
  console.log(`Server process exited with code ${code}`);
  process.exit(code);
});

// Initialize message ID counter
let messageId = 1;

// Function to send a request to the server
function sendRequest(method, params = {}) {
  const request = {
    jsonrpc: "2.0",
    id: messageId++,
    method,
    params,
  };
  
  const requestStr = JSON.stringify(request) + "\n";
  serverProcess.stdin.write(requestStr);
  console.log("Sent request:", requestStr);
}

// Parse and handle server responses
rl.on("line", (line) => {
  try {
    const response = JSON.parse(line);
    console.log("Received response:", JSON.stringify(response, null, 2));
    
    // If this is the server initialization response, list available tools
    if (response.result && response.result.implementation) {
      console.log("Server initialized, listing tools...");
      sendRequest("rpc.discover", { method: "tools.list" });
    }
    
    // If we received the list of tools, try calling the first tool
    if (response.result && response.result.tools && response.result.tools.length > 0) {
      const firstTool = response.result.tools[0];
      console.log(`Found tool: ${firstTool.name}`);
      if (firstTool.name) {
        console.log(`Calling tool: ${firstTool.name}`);
        sendRequest("tools.call", { 
          name: firstTool.name,
          arguments: {},
        });
      }
    }
  } catch (error) {
    console.error("Error parsing server response:", error);
    console.error("Raw line:", line);
  }
});

// Send initial request to get server info
console.log("Connecting to server...");
sendRequest("rpc.discover");

// Handle process termination
process.on("SIGINT", () => {
  console.log("Terminating server...");
  serverProcess.kill();
  process.exit(0);
}); 