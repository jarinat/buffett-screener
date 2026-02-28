# Multi-stage build for optimized production image

# Stage 1: Dependencies installation
FROM node:18-alpine AS deps

# Install system dependencies for node-gyp
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies (FIXED: removed --only=production)
RUN npm ci


# Stage 2: Development stage with hot reload
FROM node:18-alpine AS development

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache libc6-compat

# Copy package files
COPY package.json package-lock.json* ./

# Install all dependencies (including dev)
RUN npm ci

# Copy application files
COPY . .

# Set environment
ENV NODE_ENV=development \
    NEXT_TELEMETRY_DISABLED=1

# Expose port
EXPOSE 3000

# Run development server with hot reload
CMD ["npm", "run", "dev"]


# Stage 3: Builder stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application files
COPY . .

# Set Next.js telemetry to disabled
ENV NEXT_TELEMETRY_DISABLED=1

# Build the application (standalone output configured in next.config.js)
RUN npm run build


# Stage 4: Runtime stage
FROM node:18-alpine AS runner

WORKDIR /app

# Set production environment
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy standalone output from builder
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Set port environment variable
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})" || exit 1

# Run the application
CMD ["node", "server.js"]
