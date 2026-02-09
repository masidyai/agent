# Multi-stage Dockerfile for Masidy AI Agent Platform

# =============================================================================
# Stage 1: Backend Builder
# =============================================================================
FROM python:3.11-slim AS backend-builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend_api/requirements.txt ./backend_api/
RUN pip install --no-cache-dir -r backend_api/requirements.txt

# =============================================================================
# Stage 2: Frontend Builder
# =============================================================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# Copy frontend package files
COPY masidy_frontend/package*.json ./masidy_frontend/

# Install dependencies (including devDependencies needed for build)
WORKDIR /app/masidy_frontend
RUN npm ci

# Copy frontend source
COPY masidy_frontend/ ./

# Build frontend
RUN npm run build

# =============================================================================
# Stage 3: Production Backend
# =============================================================================
FROM python:3.11-slim AS backend

WORKDIR /app

# Install runtime dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend code
COPY backend_api/ ./backend_api/
COPY masidy_agent_runtime/ ./masidy_agent_runtime/

# Copy entrypoint script
COPY backend_api/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create data directories and set permissions
RUN mkdir -p /app/backend_api/data /app/backend_api/projects

# Create non-root user and change ownership
RUN useradd -m -u 1000 masidy && \
    chown -R masidy:masidy /app

# Set working directory before switching user
WORKDIR /app/backend_api

# Switch to non-root user
USER masidy

# Set environment variables with defaults
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    DATABASE_URL=sqlite+aiosqlite:///./data/masidy.db \
    SECRET_KEY=change-this-in-production-use-build-arg \
    CORS_ORIGINS=http://localhost:3000

EXPOSE 8000

# Health check (using existing /health endpoint)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use entrypoint script to run migrations before starting server
ENTRYPOINT ["/app/entrypoint.sh"]

# =============================================================================
# Stage 4: Production Frontend
# =============================================================================
FROM node:18-alpine AS frontend

WORKDIR /app

# Install wget for healthcheck
RUN apk add --no-cache wget

# Copy built frontend
COPY --from=frontend-builder /app/masidy_frontend/.next ./.next
COPY --from=frontend-builder /app/masidy_frontend/node_modules ./node_modules
COPY --from=frontend-builder /app/masidy_frontend/package.json ./
COPY --from=frontend-builder /app/masidy_frontend/public ./public

# Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
USER nextjs

ENV NODE_ENV=production \
    PORT=3000

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

CMD ["npm", "run", "start"]
