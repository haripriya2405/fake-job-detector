# ==============================================================================
# SentinelJob AI — Production Frontend Dockerfile (Phase 18)
# Multi-stage Node.js build + Nginx static serving
# ==============================================================================

# Stage 1: Build production React bundle
FROM node:20-alpine AS builder

WORKDIR /app

# Install build dependencies with clean npm cache
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy frontend source code and configs
COPY frontend/ ./

# Pass environment variables for production build
ENV VITE_API_URL=/api/v1 \
    VITE_USE_MOCK_DATA=false \
    VITE_APP_ENV=production

# Compile optimized static bundle
RUN npm run build

# Stage 2: Production Nginx static server
FROM nginx:1.27-alpine AS runtime

# Remove default nginx static index
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom frontend nginx configuration
COPY docker/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf

# Expose HTTP port
EXPOSE 80

# Health check
HEALTHCHECK --interval=20s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
