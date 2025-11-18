# Fantasy Football Backend - Docker Image
# ======================================
# Multi-stage build for Python FastAPI backend

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libpq-dev \
        gcc \
        g++ \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs backups data temp

# Create non-root user
RUN groupadd -r ffapp && useradd -r -g ffapp ffapp
RUN chown -R ffapp:ffapp /app
USER ffapp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "src/main.py"]

# ======================================
# Development stage
# ======================================
FROM base as development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    pytest-asyncio \
    black \
    flake8 \
    mypy

# Install debugging tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        vim \
        htop \
        telnet \
    && rm -rf /var/lib/apt/lists/*

# Switch back to app user
USER ffapp

# Development server with hot reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]

# ======================================
# Production stage
# ======================================
FROM base as production

# Copy only production files
COPY --chown=ffapp:ffapp src/ src/
COPY --chown=ffapp:ffapp alembic/ alembic/
COPY --chown=ffapp:ffapp alembic.ini .

# Production server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]