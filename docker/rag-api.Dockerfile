FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scripts/ /app/scripts/
COPY configs/ /app/configs/
COPY sample_docs/ /app/sample_docs/

# Create necessary directories
RUN mkdir -p /app/vector_db /app/logs

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Start command
CMD ["python", "-m", "uvicorn", "scripts.rag_api:app", "--host", "0.0.0.0", "--port", "8001"]