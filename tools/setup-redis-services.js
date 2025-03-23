/**
 * Script to set up Redis-backed services for the MCP server
 * 
 * This script demonstrates:
 * 1. Starting a server with Redis integration
 * 2. Using Redis session management
 * 3. Using Redis caching for performance improvements
 * 4. Configuring tools with Redis backing
 * 
 * Usage:
 * node tools/setup-redis-services.js
 */

const { startServer } = require('../dist/server/startServer');
const { registerRedisBackedServices } = require('../dist/server/registerRedisBackedServices');

async function main() {
  try {
    console.log('Setting up MCP server with Redis services...');
    
    // Configure Redis connection
    const redisConfig = {
      redisUrl: process.env.REDIS_URL || 'redis://localhost:6379',
      prefix: 'mcp:',
      defaultTtl: 3600, // 1 hour
      useMemoryCache: true
    };
    
    // Start the MCP server
    const server = await startServer({
      port: 3000, 
      host: 'localhost',
      transport: 'http'
    });
    
    // Register Redis-backed services
    const { sessionStore, cacheStore, toolService } = await registerRedisBackedServices(
      server,
      redisConfig
    );
    
    // Test session functionality
    const testSessionId = `test-session-${Date.now()}`;
    await sessionStore.setSession(testSessionId, { 
      created: new Date().toISOString(),
      metadata: {
        type: 'test-session',
        description: 'Session for testing Redis integration'
      }
    });
    
    const session = await sessionStore.getSession(testSessionId);
    console.log('Test session created:', session);
    
    // Test cache functionality
    await cacheStore.set('test-key', { 
      message: 'Hello from Redis cache!',
      timestamp: Date.now()
    });
    
    const cachedItem = await cacheStore.get('test-key');
    console.log('Cache item retrieved:', cachedItem);
    
    // Register shutdown handlers
    process.on('SIGINT', async () => {
      console.log('Shutting down Redis services...');
      await sessionStore.clearSession(testSessionId);
      await cacheStore.disconnect();
      await toolService.disconnect();
      server.stop();
      process.exit(0);
    });
    
    console.log('\nMCP server with Redis services is running');
    console.log('Press Ctrl+C to shut down the server');
    
  } catch (error) {
    console.error('Error setting up Redis services:', error);
    process.exit(1);
  }
}

main(); 