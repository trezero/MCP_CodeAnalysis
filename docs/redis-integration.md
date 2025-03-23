# Redis Integration

> **Note**: Redis is now an optional dependency for development but still recommended for production. The MCP server will automatically fall back to in-memory storage if Redis is unavailable. See [Session Store Architecture](./session-store.md) for more details.

This document outlines the Redis integration features for the Model Context Protocol (MCP) Code Analysis platform. Redis provides distributed caching, session management, and persistent storage capabilities to enhance performance and scalability.

## Features

- **Session Management**: Persistent session storage across server restarts and distributed deployment
- **Caching**: Two-level caching strategy (memory + Redis) for high-performance tool execution
- **Tool State**: Stateful tool execution with persistent state storage
- **Distributed Locks**: Concurrency control for distributed operations
- **TTL Management**: Automatic expiration of stale data

## Components

### Redis Session Store

The `RedisSessionStore` provides persistent session management for MCP:

```typescript
import { RedisSessionStore } from "../state/store/redisSessionStore";

// Initialize the store
const sessionStore = new RedisSessionStore({
  redisUrl: "redis://localhost:6379",
  prefix: "mcp:session:",
  defaultTtl: 3600, // 1 hour
  lockTimeout: 10000, // 10 seconds
});

// Create a session
await sessionStore.setSession("my-session", {
  userId: "user-123",
  context: {
    /* session context */
  },
});

// Retrieve a session
const session = await sessionStore.getSession("my-session");

// Get all active sessions
const sessions = await sessionStore.getSessions();

// Clear a session
await sessionStore.clearSession("my-session");

// Lock management for concurrent access
const lock = await sessionStore.acquireLock("my-session", 30000);
if (lock) {
  try {
    // Perform operations requiring exclusive access
    // ...
  } finally {
    await sessionStore.releaseLock("my-session", lock);
  }
}

// Extend session TTL
await sessionStore.extendSessionTtl("my-session", 7200); // 2 hours
```

### Redis Cache Store

The `RedisCacheStore` provides a tiered caching system with in-memory LRU cache backed by Redis:

```typescript
import { RedisCacheStore } from "../state/store/redisCacheStore";

// Initialize the store
const cacheStore = new RedisCacheStore({
  redisUrl: "redis://localhost:6379",
  prefix: "mcp:cache:",
  defaultTtl: 300, // 5 minutes
  useMemoryCache: true,
  memCacheSize: 1000,
});

// Cache an item
await cacheStore.set("my-key", { data: "value" }, 600); // 10 minutes TTL

// Cache an item with namespace
await cacheStore.set("my-key", { data: "value" }, 600, "user-123");

// Retrieve a cached item
const item = await cacheStore.get("my-key");

// Invalidate by key
await cacheStore.delete("my-key");

// Invalidate by namespace
await cacheStore.invalidateNamespace("user-123");

// Batch operations
await cacheStore.setMany(
  {
    key1: "value1",
    key2: "value2",
  },
  600
);

const items = await cacheStore.getMany(["key1", "key2"]);

// Get cache statistics
const stats = cacheStore.getStats();
```

### Redis Tool Execution Service

The `RedisToolExecutionService` provides persistent state for tool execution:

```typescript
import { RedisToolExecutionService } from "../state/services/redisToolExecutionService";

// Initialize the service
const toolExecutionService = new RedisToolExecutionService({
  redisUrl: "redis://localhost:6379",
  prefix: "mcp:toolexec:",
  defaultTtl: 3600,
  useMemoryCache: true,
  tools: toolRegistry.getAllTools(),
});

// Execute a tool with caching enabled
const result = await toolExecutionService.executeTool(
  "analyze-file-metrics",
  { filePath: "src/index.ts" },
  "user-session-123",
  true // use cached results if available
);

// Invalidate cache for a specific tool
await toolExecutionService.invalidateToolCache("analyze-file-metrics");

// Clear session data and cached results
await toolExecutionService.clearSession("user-session-123");
```

## Server Integration

The MCP server can be configured to use Redis-backed services:

```typescript
import { startServer } from "./server/startServer";
import { registerRedisBackedServices } from "./server/registerRedisBackedServices";

// Start the MCP server
const server = await startServer({
  port: 3000,
  host: "localhost",
});

// Register Redis-backed services
const { sessionStore, cacheStore, toolService } =
  await registerRedisBackedServices(server, {
    redisUrl: "redis://localhost:6379",
    prefix: "mcp:",
    defaultTtl: 3600,
    useMemoryCache: true,
  });
```

## Configuration

Redis integration can be configured using the following environment variables:

| Variable                  | Description                     | Default                  |
| ------------------------- | ------------------------------- | ------------------------ |
| `REDIS_URL`               | Redis connection string         | `redis://localhost:6379` |
| `REDIS_PREFIX`            | Key prefix for all Redis keys   | `mcp:`                   |
| `REDIS_TTL`               | Default TTL in seconds          | `3600` (1 hour)          |
| `REDIS_MEMORY_CACHE`      | Enable memory caching layer     | `true`                   |
| `REDIS_MEMORY_CACHE_SIZE` | Maximum entries in memory cache | `1000`                   |
| `REDIS_LOCK_TIMEOUT`      | Default lock timeout in ms      | `10000` (10 seconds)     |

## Performance Considerations

- **Memory Cache**: The in-memory cache layer provides ultra-fast access to frequent items
- **Batch Operations**: Use `getMany` and `setMany` for bulk operations to reduce network round-trips
- **TTL Strategy**: Customize TTL values based on data volatility and access patterns
- **Namespaces**: Use namespaces to group related cache items for efficient invalidation
- **Connection Pooling**: Redis connections are automatically pooled for optimal performance

## Security Considerations

- Use Redis AUTH for production deployments
- Consider enabling Redis TLS for sensitive data
- Implement proper network isolation for Redis servers
- Do not store sensitive information in cache without encryption

## Monitoring

Redis integration can be monitored through the provided statistics:

```typescript
// Get cache statistics
const cacheStats = cacheStore.getStats();
console.log(cacheStats);
// Example output:
// {
//   memoryCache: {
//     enabled: true,
//     size: 245,
//     maxSize: 1000,
//     hits: 1532,
//     misses: 423,
//     sets: 658,
//     hitRate: 0.78
//   }
// }

// Get tool execution statistics
const toolStats = await toolService.getStats();
console.log(toolStats);
```

## Error Handling

Redis integration includes graceful error handling:

- Connection failures are logged and do not crash the application
- Memory cache serves as a fallback when Redis is unavailable
- Automatic reconnection attempts
- Failed operations are logged for troubleshooting
