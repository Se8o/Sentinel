# Multi-stage Dockerfile for Sentinel

# ============================================
# Base Stage - Common dependencies
# ============================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r sentinel && useradd -r -g sentinel sentinel

# Set working directory
WORKDIR /app

# ============================================
# Builder Stage - Install Python dependencies
# ============================================
FROM base as builder

# Install Poetry
RUN pip install poetry==1.7.1

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies (without dev dependencies for production)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main

# ============================================
# Development Stage
# ============================================
FROM base as development

# Install Poetry for development
RUN pip install poetry==1.7.1

# Copy dependency files
COPY pyproject.toml ./

# Install all dependencies including dev
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R sentinel:sentinel /app

USER sentinel

# Expose port
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================
# Production Stage
# ============================================
FROM base as production

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=sentinel:sentinel . .

# Change to non-root user
USER sentinel

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
