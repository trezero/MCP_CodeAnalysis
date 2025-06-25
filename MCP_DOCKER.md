# MCP CodeAnalysis Docker Deployment

This document provides instructions for deploying the MCP CodeAnalysis server using Docker.

## Prerequisites
- Docker Desktop installed on Windows
- WSL 2 configured (for Linux environments)
- At least 4GB RAM allocated to Docker

## Container Details
- **Container Name**: `mcp-code-analysis` (will appear in Docker Desktop)
- **Service Port**: 3005
- **Redis Connection**: Uses existing Redis from n8n stack
- **Data Volume**: Persists in `./data` directory

## Important Note
This setup connects to your existing Redis container from the LocalAI stack. Ensure:
1. Your LocalAI stack is running
2. The Redis container name is 'redis'
3. Both containers are on the localai_default network

## Deployment Steps

### 1. Build and Start Containers
```bash
docker-compose up -d --build
```

### 2. Verify in Docker Desktop
1. Open Docker Desktop application
2. Check "Containers" section
3. Look for `mcp-code-analysis` and `mcp-redis` containers
4. Verify both show "Running" status

### 3. Access the Server
- **From Windows**: http://localhost:3005
- **From WSL**: http://host.docker.internal:3005
- **From other containers**: http://mcp-code-analysis:3005

### 4. Management Commands
```bash
# Stop containers
docker-compose down

# Start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild containers
docker-compose up -d --build

# Remove all data (including Redis)
docker-compose down -v
```

## Configuration Options

### Environment Variables
Set these in `docker-compose.yml`:
- `PORT`: Server port (default: 3005)
- `REDIS_URL`: Redis connection string (default: redis://mcp-redis:6379)
- `FORCE_MEMORY_SESSION`: Force memory session store (bypass Redis)

### Volumes
- Server data: `./data` → `/usr/src/app/data`
- Redis data: Persistent Docker volume

## Troubleshooting

### Common Issues
1. **Port conflicts**: Ensure port 3005 is free
2. **Container not starting**: Check logs with `docker-compose logs`
3. **Redis connection issues**:
   ```bash
   # Verify Redis is running
   docker ps | grep redis
   
   # Test connection from MCP container
   docker exec -it mcp-code-analysis ping redis
   ```
4. **Network issues**: Ensure both containers are on localai_default network
   ```bash
   docker network inspect localai_default
   docker inspect redis --format '{{range .NetworkSettings.Networks}}{{.NetworkID}} {{end}}'
   ```

### Windows-Specific Notes
- First run may be slow as WSL initializes
- Allow Docker through Windows Firewall if connection issues occur
- Use `host.docker.internal` for WSL-to-container communication

## Development Workflow
```mermaid
graph TD
    A[Edit code] --> B[Rebuild containers]
    B --> C[Test changes]
    C --> D{Working?}
    D -->|Yes| E[Commit changes]
    D -->|No| A
