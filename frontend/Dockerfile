FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Set production API URL for build
ENV VITE_API_URL=https://blue-lotus-seo-production.up.railway.app
ENV VITE_ENVIRONMENT=production

# Build for production
RUN npm run build

# Production stage
FROM node:18-alpine AS production

WORKDIR /app

# Copy built assets and server
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/server.js ./server.js

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S react -u 1001 && \
    chown -R react:nodejs /app

USER react

# Railway provides PORT env var
ENV PORT=3000

# Health check using the PORT variable
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:${PORT} || exit 1

# Start server
CMD ["node", "server.js"]
