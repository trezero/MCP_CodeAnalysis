# Use official Node.js image
FROM node:18-alpine

# Create app directory
WORKDIR /usr/src/app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install pnpm and dependencies
RUN npm install -g pnpm && pnpm install

# Copy source files
COPY . .

# Build the project
RUN pnpm build

# Expose the server port
EXPOSE 3005

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3005

# Run the server
CMD ["pnpm", "start"]
