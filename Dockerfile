FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# libpq-dev is needed for psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and config
COPY src/ src/
COPY tests/ tests/
COPY .env .env

# Set python path
ENV PYTHONPATH=/app/src

# Baked-in credentials (DEMO ONLY)
ENV REDSHIFT_HOST=daplabs.955954582473.us-east-1.redshift-serverless.amazonaws.com
ENV REDSHIFT_PORT=5439
ENV REDSHIFT_DATABASE=prod
ENV REDSHIFT_USER=moonshoot_dev
ENV REDSHIFT_PASSWORD=n!ua8y5Z
ENV GEMINI_API_KEY=AIzaSyBeIVrGGHipv9pjuXSDHmrGhCJ88v60QEI
ENV MAX_ROWS=1000

# Default command (can be overridden)
CMD ["python3", "-m", "redshift_nl_agent"]
