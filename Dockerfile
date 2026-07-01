# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 1 — install production dependencies in an isolated layer
# ---------------------------------------------------------------------------
FROM node:20-alpine AS deps
WORKDIR /usr/src/app
COPY package*.json ./
# Reproducible, production-only install (no dev deps in the runtime image).
RUN npm ci --omit=dev

# ---------------------------------------------------------------------------
# Stage 2 — minimal runtime image
# ---------------------------------------------------------------------------
FROM node:20-alpine AS runtime

# wget (busybox) is used by the container HEALTHCHECK below.
ENV NODE_ENV=production
WORKDIR /usr/src/app

# Copy pre-built node_modules, then application source.
COPY --from=deps /usr/src/app/node_modules ./node_modules
COPY package*.json ./
COPY app.js server.js proxy.js featureFlags.js ./
COPY config ./config

# Run as the unprivileged user that ships with the node image (security).
USER node

EXPOSE 3000

# Container-level health probe consumed by `docker compose` and orchestrators.
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -q -O- http://127.0.0.1:3000/health || exit 1

CMD ["node", "server.js"]
