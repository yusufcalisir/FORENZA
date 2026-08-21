# ==============================================================================
# FORENZA: Forensic Evidence Operating System
# Frontend Workstation UI - Multi-Stage Air-Gapped Production Dockerfile
# ==============================================================================

# --- Stage 1: Dependency Caching ---
FROM node:20-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --prefer-offline --no-audit

# --- Stage 2: Production Build ---
FROM node:20-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production

RUN npm run build

# --- Stage 3: Lightweight Production Runtime ---
FROM node:20-alpine AS runner
WORKDIR /app

LABEL maintainer="FORENZA Biocomputational Intelligence Team <forenza@yusufcalisir.dev>"
LABEL description="FORENZA Air-Gapped Next.js 16 Forensic Workstation UI"
LABEL version="2.0.0"

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME="0.0.0.0"

# Install curl for health checking
RUN apk add --no-cache curl

# Create unprivileged system user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy built standalone bundle and static assets
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

# Health check endpoint
HEALTHCHECK --interval=20s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

CMD ["node", "server.js"]
