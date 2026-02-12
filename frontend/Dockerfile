# =============================================================================
# CareFlow AI - Frontend Dockerfile
# =============================================================================

FROM node:20-alpine AS base

WORKDIR /app

# =============================================================================
# Development Stage
# =============================================================================
FROM base AS development

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev"]

# =============================================================================
# Build Stage
# =============================================================================
FROM base AS build

COPY package*.json ./
RUN npm ci

COPY . .

# Build application
RUN npm run build

# =============================================================================
# Production Stage
# =============================================================================
FROM base AS production

ENV NODE_ENV=production

COPY package*.json ./
RUN npm install --production

COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/next.config.js ./

# Expose port
EXPOSE 3000

# Start production server
CMD ["npm", "run", "start"]
