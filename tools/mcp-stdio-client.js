#!/usr/bin/env node

/**
 * MCP Stdio Client
 * 
 * A simple client that communicates with an MCP server via stdio.
 * This client supports connecting to a server, executing tasks, and
 * using fallback mechanisms when needed.
 * 
 * Features:
 * - Automatic session management
 * - Redis connectivity detection
 * - Fallback to local operations when server is unavailable
 * - Context generation for AI tools
 */

import path from 'path';
import { spawn, exec as execCallback } from 'child_process';
import fs from 'fs/promises';
import { v4 as uuidv4 } from 'uuid';
import { createRequire } from 'module';
import { fileURLToPath } from 'url';
import net from 'net';
import { promisify } from 'util';

// Setup ES modules compatibility
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const require = createRequire(import.meta.url);
const exec = promisify(execCallback);

// Constants
const WAIT_FOR_TOOLS_RESPONSE = 3000; // ms
const PROJECT_ROOT = path.resolve(__dirname, '..');

/**
 * Check if Redis is available at the given URL
 * 
 * @param {string} redisUrl - Redis URL to check
 * @returns {Promise<boolean>} - Whether Redis is available
 */
async function isRedisAvailable(redisUrl = 'redis://localhost:6379') {
  return new Promise((resolve) => {
    try {
      // Extract host and port from Redis URL
      let host = 'localhost';
      let port = 6379;

      try {
        const url = new URL(redisUrl);
        host = url.hostname;
        port = url.port || 6379;
      } catch (e) {
        console.warn(`Invalid Redis URL: ${redisUrl}`);
      }

      // Create a socket and try to connect
      const socket = new net.Socket();
      
      // Set a timeout (2 seconds)
      socket.setTimeout(2000);
      
      socket.on('connect', () => {
        socket.destroy();
        resolve(true);
      });
      
      socket.on('timeout', () => {
        socket.destroy();
        resolve(false);
      });
      
      socket.on('error', () => {
        socket.destroy();
        resolve(false);
      });
      
      // Try to connect
      socket.connect(port, host);
    } catch (error) {
      console.warn(`Error checking Redis: ${error.message}`);
      resolve(false);
    }
  });
}

/**
 * Call an MCP tool using JSON-RPC 2.0 format
 * 
 * @param {Object} serverProcess - Child process running the MCP server
 * @param {string} method - Method name
 * @param {Object} params - Parameters for the method
 * @returns {Promise<Object>} - Response from the server
 */
function callMcpTool(serverProcess, method, params = {}) {
  return new Promise((resolve, reject) => {
    const requestId = uuidv4();
    const jsonRpcRequest = {
      jsonrpc: '2.0',
      id: requestId,
      method,
      params
    };
    
    // Send the request to the server
    serverProcess.stdin.write(JSON.stringify(jsonRpcRequest) + '\n');
    
    // Set up timeout
    const timeout = setTimeout(() => {
      reject(new Error(`Request timed out after 5000ms: ${method}`));
    }, 5000);
    
    // Handler for server responses
    const responseHandler = (data) => {
      try {
        const lines = data.toString().trim().split('\n');
        
        for (const line of lines) {
          if (!line.trim()) continue;
          
          try {
            const response = JSON.parse(line);
            
            // Check if this is the response to our request
            if (response.id === requestId) {
              clearTimeout(timeout);
              
              // Handle error responses
              if (response.error) {
                reject(new Error(`Server error: ${JSON.stringify(response.error)}`));
                return;
              }
              
              // Successful response
              resolve(response.result);
              return;
            }
          } catch (e) {
            // Not JSON or not for us, ignore
          }
        }
      } catch (error) {
        reject(error);
      }
    };
    
    // Listen for the response
    serverProcess.stdout.on('data', responseHandler);
  });
}

/**
 * Create a text file from the given options
 * 
 * @param {Object} options - Options for text generation
 * @param {string} options.filePath - Path to write to
 * @param {string|Object} options.content - Content to write
 * @returns {Promise<void>}
 */
async function createTextFile(options) {
  const { filePath, content } = options;
  
  let textContent = content;
  if (typeof content === 'object') {
    textContent = JSON.stringify(content, null, 2);
  }
  
  await fs.writeFile(filePath, textContent, 'utf8');
  console.log(`Created file: ${filePath}`);
}

/**
 * Grep for files matching a pattern
 * 
 * @param {string} searchPattern - Pattern to search for
 * @param {string} fileGlob - Files to search in 
 * @returns {Promise<string[]>} - Matching files
 */
async function grepFiles(searchPattern, fileGlob) {
  try {
    // Build the grep command
    const command = `grep -l "${searchPattern}" ${fileGlob} || echo ""`;
    
    const { stdout } = await exec(command, { maxBuffer: 1024 * 1024 * 10 });
    const results = stdout.trim()
      .split('\n')
      .filter(line => line.trim() !== '');
      
    return results;
  } catch (error) {
    // Ignore grep "no match" errors
    if (error && error.code !== 1) {
      throw error;
    }
    return [];
  }
}

/**
 * Main function
 */
async function main() {
  // Parse command line arguments
  const args = process.argv.slice(2);
  const options = {};
  
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      const value = args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true;
      options[key] = value;
      if (value !== true) i++;
    }
  }
  
  // Required options
  const task = options.task || 'Analyze code';
  const files = options.files || '**/*.{js,ts,jsx,tsx}';
  const searchTerm = options.search || '';
  
  console.log(`Task: ${task}`);
  console.log(`Files: ${files}`);
  console.log(`Search: ${searchTerm || '(None)'}`);
  
  // Spawn the MCP server process
  console.log('Starting MCP server...');
  const serverProcess = spawn('node', ['src/server.js'], {
    env: {
      ...process.env,
      STDIO_TRANSPORT: 'true',
      FORCE_MEMORY_SESSION: 'true', // Start with memory session by default
    },
    stdio: ['pipe', 'pipe', 'pipe']
  });
  
  // Track if the server is ready
  let serverReady = false;
  
  // Handle server output
  serverProcess.stderr.on('data', (data) => {
    const text = data.toString();
    console.error(`Server error: ${text}`);
  });
  
  // Wait for the server to be ready
  const waitForServer = new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error('Server initialization timed out after 10 seconds'));
    }, 10000);
    
    serverProcess.stdout.on('data', (data) => {
      const text = data.toString();
      
      // Check if server is ready
      if (text.includes('ready to handle stdio requests')) {
        clearTimeout(timeout);
        serverReady = true;
        resolve();
      }
    });
  });
  
  try {
    // Wait for server to be ready
    await waitForServer;
    console.log('Server ready');
    
    // Check if Redis is available
    console.log('Checking Redis availability...');
    const redisAvailable = await isRedisAvailable();
    console.log(`Redis available: ${redisAvailable}`);
    
    // Generate a session ID
    let sessionId;
    
    try {
      // Try to create a session using the server
      console.log('Creating session...');
      const result = await callMcpTool(serverProcess, 'create-session', {
        description: task
      });
      
      // Extract session ID from response
      if (result && result.content && result.content[0] && result.content[0].text) {
        try {
          const parsed = JSON.parse(result.content[0].text);
          sessionId = parsed.data?.sessionId;
          console.log(`Session created: ${sessionId}`);
        } catch (e) {
          console.warn('Failed to parse session creation response:', e);
        }
      }
    } catch (error) {
      console.warn(`Failed to create session: ${error.message}`);
    }
    
    // If we failed to create a session, use a temporary one
    if (!sessionId) {
      sessionId = `temp-${uuidv4()}`;
      console.log(`Using temporary session ID: ${sessionId}`);
    }
    
    // Find relevant files
    let relevantFiles = [];
    
    if (searchTerm) {
      try {
        // Try to use the analyze-repository tool
        console.log(`Searching for files with "${searchTerm}"...`);
        try {
          const result = await callMcpTool(serverProcess, 'search-codebase', {
            query: searchTerm,
            filePatterns: files.split(',').map(f => f.trim())
          });
          
          if (result && result.content && result.content[0] && result.content[0].text) {
            try {
              const parsed = JSON.parse(result.content[0].text);
              if (parsed.data && parsed.data.results) {
                relevantFiles = parsed.data.results.map(r => r.filePath);
                console.log(`Found ${relevantFiles.length} files using MCP search`);
              }
            } catch (e) {
              console.warn('Failed to parse search results:', e);
            }
          }
        } catch (error) {
          console.warn(`Failed to search with MCP: ${error.message}`);
        }
        
        // If MCP search failed, fall back to grep
        if (relevantFiles.length === 0) {
          console.log('Falling back to grep search...');
          relevantFiles = await grepFiles(searchTerm, files);
          console.log(`Found ${relevantFiles.length} files using grep`);
        }
      } catch (error) {
        console.warn(`Search error: ${error.message}`);
      }
    } else {
      // If no search term, use glob matching
      console.log('Using specified files without search');
      relevantFiles = files.split(',').map(f => f.trim());
    }
    
    // Generate context data
    const contextData = {
      task,
      sessionId,
      timestamp: new Date().toISOString(),
      files: relevantFiles
    };
    
    // Write the context file
    await createTextFile({
      filePath: 'ai-context.json',
      content: contextData
    });
    
    console.log('Context generated successfully');
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  } finally {
    // Clean up
    serverProcess.kill();
  }
}

// Run the main function
main().catch(error => {
  console.error(`Unhandled error: ${error.message}`);
  process.exit(1);
}); 
main(); 