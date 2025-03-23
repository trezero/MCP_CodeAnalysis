# MCP Session Store

The MCP Session Store provides a modular interface for storing session data with different backend implementations. It's designed to support both production and development environments with automatic backend detection and fallback mechanisms.

## Features

- **Multiple Backends**: Redis for production, Memory for development
- **Automatic Detection**: Fall back to memory store if Redis is unavailable
- **TTL Management**: Supports session expiration with configurable TTL
- **Session Locking**: Provides distributed locking mechanism for concurrent access
- **Consistent Interface**: All implementations share the same SessionStore interface

## Installation

To use the Redis backend (recommended for production):

```bash
npm install redis
# OR
npm install ioredis
```

For development and testing, no additional dependencies are required as the memory store is built-in.

## Usage

### Creating a Session Store with Automatic Detection

The session store factory will automatically detect available backends and use the most appropriate one:

```typescript
import { createSessionStore } from "./state/services/sessionStoreFactory";

// Create a session store with automatic backend detection
const sessionStore = await createSessionStore({
  redisUrl: "redis://localhost:6379", // Optional for development
  prefix: "mcp:", // Optional prefix for keys
  defaultTtl: 3600, // Default TTL in seconds
  verbose: true, // Log store selection
});

// Use the session store
await sessionStore.setSession("session-123", {
  toolName: "my-tool",
  result: "success",
});

const session = await sessionStore.getSession("session-123");
console.log(session);
```

### Explicitly Creating a Memory Store

For development environments without Redis:

```typescript
import { createMemorySessionStore } from "./state/services/sessionStoreFactory";

const memoryStore = createMemorySessionStore({
  prefix: "dev:",
  defaultTtl: 3600,
});

// Use just like any other session store
await memoryStore.setSession("test-session", { data: "test" });
```

### Redis Availability Check

Check if Redis is available before attempting to use it:

```typescript
import { isRedisAvailable } from "./state/services/sessionStoreFactory";

const redisAvailable = await isRedisAvailable("redis://localhost:6379");
if (redisAvailable) {
  console.log("Redis is available");
} else {
  console.log("Redis is not available, will use memory store");
}
```

## Configuration Options

The session store accepts the following configuration options:

| Option         | Description                    | Default                    |
| -------------- | ------------------------------ | -------------------------- |
| `redisUrl`     | Redis connection URL           | `"redis://localhost:6379"` |
| `prefix`       | Key prefix for session storage | `"mcp:session:"`           |
| `defaultTtl`   | Default TTL in seconds         | `3600` (1 hour)            |
| `lockTimeout`  | Lock timeout in milliseconds   | `30000` (30 seconds)       |
| `preferMemory` | Force use of memory store      | `false`                    |
| `verbose`      | Enable verbose logging         | `false`                    |

## Implementation Details

### Redis Backend

For production environments, the Redis backend provides:

- Persistent storage across server restarts
- Ability to share sessions across multiple server instances
- Automatic session expiration using Redis TTL
- Distributed locking for concurrent access

### Memory Backend

For development and testing, the memory backend provides:

- No external dependencies
- Fast in-memory storage
- Simulated TTL behavior
- Simulated locking mechanism

## Integration with MCP Server

The session store is integrated with the MCP server through the `registerRedisBackedServices` function, which automatically selects the appropriate store:

```typescript
import { registerRedisBackedServices } from "./server/registerRedisBackedServices.js";

const server = new McpServer();

const services = await registerRedisBackedServices(server, {
  redisUrl: process.env.REDIS_URL,
  forceMemorySessionStore: process.env.NODE_ENV === "development",
});
```

## Best Practices

1. **Production Environments**: Always use Redis in production for persistence and scalability
2. **Development Environments**: Use memory store for simplicity and no dependencies
3. **Docker Environments**: Ensure Redis is available in your container setup
4. **Testing**: Use memory store for faster tests and no external dependencies
5. **Graceful Disconnection**: Always call `disconnect()` when done with a session store
