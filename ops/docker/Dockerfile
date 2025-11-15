FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create data directory
RUN mkdir -p /data/logs /data/config /data/reports

# Create non-root user
RUN useradd -m -u 1000 sira && chown -R sira:sira /app /data
USER sira

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Default command (overridden in compose files)
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
