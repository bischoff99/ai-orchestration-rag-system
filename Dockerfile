# Development container for AI Orchestration & RAG System
FROM mcr.microsoft.com/devcontainers/python:3.11

# Install system dependencies for AI/ML
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Set working directory
WORKDIR /workspaces

# Create non-root user for development
RUN useradd -m -s /bin/bash vscode && \
    chown -R vscode:vscode /workspaces

USER vscode

# Environment variables
ENV PYTHONPATH=/workspaces
ENV OLLAMA_HOST=http://localhost:11434
ENV N8N_HOST=http://localhost:5678

# Default command
CMD ["sleep", "infinity"]