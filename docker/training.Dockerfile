FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install MLX for Apple Silicon (if needed)
RUN pip install --no-cache-dir mlx mlx-lm

# Copy application code
COPY scripts/ /app/scripts/
COPY datasets/ /app/datasets/
COPY configs/ /app/configs/

# Create models directory
RUN mkdir -p /app/models

# Set Python path
ENV PYTHONPATH=/app
ENV MLX_DEVICE=mps

# Default command (can be overridden)
CMD ["python", "scripts/fine_tune_qlora.py", "--help"]