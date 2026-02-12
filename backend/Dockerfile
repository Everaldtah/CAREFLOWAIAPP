# =============================================================================
# CareFlow AI - Backend Dockerfile
# =============================================================================

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Set work directory
WORKDIR /app

# =============================================================================
# Development Stage
# =============================================================================
FROM base as development

# Copy poetry files
COPY pyproject.toml ./

# Generate poetry.lock if it doesn't exist
RUN poetry lock --no-update || true

# Configure poetry to install to .venv
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true

# Install dependencies (including dev)
RUN poetry install --no-root --no-interaction --with dev

# Copy application code
COPY . .

# Pre-create directories
RUN mkdir -p logs uploads

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# =============================================================================
# Production Stage
# =============================================================================
FROM base as production

# Copy poetry files
COPY pyproject.toml ./

# Generate poetry.lock if it doesn't exist
RUN poetry lock --no-update || true

# Configure poetry
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true

# Install dependencies (without dev)
RUN poetry install --no-root --no-interaction --only main

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Create directories
RUN mkdir -p logs uploads && \
    chown -R appuser:appuser logs uploads

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with gunicorn
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]

# =============================================================================
# Tests Stage
# =============================================================================
FROM base as test

# Copy poetry files
COPY pyproject.toml ./

# Generate poetry.lock if it doesn't exist
RUN poetry lock --no-update || true

# Configure poetry
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true

# Install dependencies (with dev and test)
RUN poetry install --no-root --no-interaction --with dev,test

# Copy application code
COPY . .

# Run tests
CMD ["pytest", "-v", "--cov=app", "--cov-report=html"]
