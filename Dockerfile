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

# Install dependencies
WORKDIR /app/masidy_frontend
RUN npm ci --only=production

# Copy frontend source
COPY masidy_frontend/ ./

# Build frontend
RUN npm run build

# =============================================================================
# Stage 3: Production Backend
# =============================================================================
FROM python:3.11-slim AS backend

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend code
COPY backend_api/ ./backend_api/
COPY masidy_agent_runtime/ ./masidy_agent_runtime/

# Create non-root user
RUN useradd -m -u 1000 masidy && chown -R masidy:masidy /app
USER masidy

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

EXPOSE 8000

WORKDIR /app/backend_api

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# Stage 4: Production Frontend
# =============================================================================
FROM node:18-alpine AS frontend

WORKDIR /app

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

CMD ["npm", "start"]
