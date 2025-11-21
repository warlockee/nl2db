# Multi-stage build for Redshift Natural Language Agent
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ ./src/

# Set Python path to find the package
ENV PYTHONPATH=/app/src

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from redshift_nl_agent.database import RedshiftCLI; print('OK')" || exit 1

# Default command - run interactive CLI
CMD ["python", "-m", "redshift_nl_agent"]
