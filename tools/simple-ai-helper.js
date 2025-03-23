#!/usr/bin/env node

// A simpler AI context helper that uses HTTP fetch instead of MCP client SDK
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Parse command line arguments
const args = process.argv.slice(2);
let taskDescription = '';
let filePattern = '';
let searchTerm = '';
let outputPath = 'ai-context.json';

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
  } else if (args[i] === '--output' && i + 1 < args.length) {
    outputPath = args[i + 1];
    i++;
  }
}

// Validate required parameters
if (!taskDescription) {
  console.error('Error: --task parameter is required');
  process.exit(1);
}

// Create session ID
const sessionId = `ai-helper-${Date.now()}`;

// Get project directory
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, '..');

async function getFolderStructure(depth = 2) {
  try {
    const { stdout } = await execAsync(`find . -type d -not -path "*/\\.*" -not -path "*/node_modules/*" -maxdepth ${depth} | sort`);
    return stdout.trim().split('\n');
  } catch (error) {
    console.error('Error getting folder structure:', error);
    return [];
  }
}

async function getMatchingFiles() {
  if (!filePattern) return [];
  
  try {
    const { stdout } = await execAsync(`find ${filePattern} -type f 2>/dev/null || echo ""`);
    return stdout.trim() ? stdout.trim().split('\n') : [];
  } catch (error) {
    console.error('Error finding files:', error);
    return [];
  }
}

async function getFileContents(filePath) {
  try {
    return fs.readFileSync(path.join(projectRoot, filePath), 'utf8');
  } catch (error) {
    console.error(`Error reading file ${filePath}:`, error);
    return '';
  }
}

async function searchInCode() {
  if (!searchTerm) return [];
  
  try {
    const { stdout } = await execAsync(`grep -r "${searchTerm}" --include="*.ts" --include="*.js" src 2>/dev/null || echo ""`);
    return stdout.trim() ? stdout.trim().split('\n') : [];
  } catch (error) {
    console.error('Error searching code:', error);
    return [];
  }
}

async function getProjectInfo() {
  try {
    // Read package.json
    const packageJson = JSON.parse(fs.readFileSync(path.join(projectRoot, 'package.json'), 'utf8'));
    
    // Get Git info if available
    let gitInfo = {};
    try {
      const { stdout: gitBranch } = await execAsync('git branch --show-current');
      const { stdout: gitCommit } = await execAsync('git rev-parse HEAD');
      gitInfo = {
        branch: gitBranch.trim(),
        commit: gitCommit.trim()
      };
    } catch (e) {
      // Git might not be available or not a git repo
      gitInfo = { error: 'Git information not available' };
    }
    
    return {
      name: packageJson.name,
      version: packageJson.version,
      description: packageJson.description,
      dependencies: packageJson.dependencies,
      git: gitInfo
    };
  } catch (error) {
    console.error('Error getting project info:', error);
    return { error: 'Failed to get project information' };
  }
}

async function generateContext() {
  console.log('Generating AI context...');
  
  // Get project info
  const projectInfo = await getProjectInfo();
  console.log('✓ Collected project information');
  
  // Get folder structure
  const folderStructure = await getFolderStructure();
  console.log('✓ Collected folder structure');
  
  // Get matching files
  const matchingFiles = await getMatchingFiles();
  console.log(`✓ Found ${matchingFiles.length} files matching pattern "${filePattern || 'none'}"`);
  
  // Get file contents
  const fileContents = {};
  for (const file of matchingFiles) {
    fileContents[file] = await getFileContents(file);
  }
  console.log(`✓ Collected contents of ${Object.keys(fileContents).length} files`);
  
  // Search code
  const searchResults = await searchInCode();
  console.log(`✓ Found ${searchResults.length} matches for search term "${searchTerm || 'none'}"`);
  
  // Assemble context
  const context = {
    task: taskDescription,
    sessionId,
    timestamp: new Date().toISOString(),
    projectInfo,
    folderStructure,
    relevantFiles: matchingFiles,
    fileContents,
    searchResults
  };
  
  // Write to file
  fs.writeFileSync(outputPath, JSON.stringify(context, null, 2));
  console.log(`✓ Context saved to ${outputPath}`);
  
  console.log('\nSuccess! Use this context in your AI prompt to provide codebase information.');
  console.log(`Tip: You can reference this JSON file in your prompt or use the content directly.`);
}

// Run the context generation
generateContext().catch(error => {
  console.error('Error generating context:', error);
  process.exit(1);
}); 