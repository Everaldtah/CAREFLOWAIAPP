# =============================================================================
# CareFlow AI - Backend Dockerfile (Improved)
# =============================================================================

FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry globally (not in virtualenv)
RUN pip install --no-cache-dir poetry==1.7.1

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# =============================================================================
# Development Stage
# =============================================================================
FROM base AS development

# Install dependencies with development packages
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy application code
COPY . .

# Expose port
EXPOSE ${PORT}

# Start FastAPI with hot reload for development
CMD ["sh", "-c", "poetry run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --reload"]

# =============================================================================
# Production Stage
# =============================================================================
FROM base AS production

# Install production dependencies only (no dev packages)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-dev

# Copy application code
COPY . .

# Create logs and uploads directories
RUN mkdir -p /app/logs /app/uploads && chmod -R 755 /app/logs /app/uploads

# Expose port
EXPOSE ${PORT}

# Start FastAPI using Gunicorn with Uvicorn workers
CMD ["sh", "-c", "gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT:-8000} --access-logfile /app/logs/access.log --error-logfile /app/logs/error.log --log-level info"]