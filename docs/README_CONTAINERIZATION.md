# AI System Containerization Guide

## 🐳 Overview

This guide covers the containerization of your AI agent system using Docker and Docker Compose. The system is designed as a collection of microservices that work together to provide RAG capabilities, model training, and workflow orchestration.

## 🏗️ Architecture

### Services

1. **ChromaDB** - Vector database for document storage and retrieval
2. **Ollama** - Model serving for LLM inference
3. **n8n** - Workflow orchestration and automation
4. **RAG API** - FastAPI service for RAG operations
5. **Training Service** - Model fine-tuning and training
6. **Monitoring** - System health monitoring and reporting
7. **Web Interface** - User interface for system interaction

### Network

All services communicate through a dedicated `ai-network` bridge network, ensuring secure and efficient inter-service communication.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- NVIDIA GPU support (for training and Ollama)
- At least 8GB RAM available
- 20GB+ disk space

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit configuration as needed
nano .env
```

### 2. Start the System

```bash
# Make scripts executable
chmod +x docker/*.sh

# Start all services
./docker/start-ai-system.sh
```

### 3. Verify Installation

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Test RAG API
curl http://localhost:8001/health
```

## 📋 Service Details

### ChromaDB (Port 8000)
- **Purpose**: Vector database for document storage
- **Data**: Persistent storage in `./vector_db/chroma`
- **API**: REST API for document operations

### Ollama (Port 11434)
- **Purpose**: LLM model serving
- **Models**: Stored in `./models` directory
- **GPU**: Requires NVIDIA GPU for optimal performance

### n8n (Port 5678)
- **Purpose**: Workflow orchestration
- **Data**: Persistent in `./n8n/data`
- **Webhooks**: Available at `/webhook/*` endpoints

### RAG API (Port 8001)
- **Purpose**: FastAPI service for RAG operations
- **Endpoints**:
  - `POST /api/search` - Search documents
  - `POST /api/ingest` - Ingest documents
  - `GET /api/collections` - List collections
  - `GET /health` - Health check

### Training Service
- **Purpose**: Model fine-tuning and training
- **GPU**: Requires NVIDIA GPU
- **Usage**: Run specific training commands

### Monitoring (Port 3000)
- **Purpose**: System health monitoring
- **Reports**: Saved to `./logs` directory
- **Alerts**: Console logging and file output

### Web Interface (Port 8080)
- **Purpose**: User interface for system interaction
- **Features**: Query interface, system status, configuration

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
CHROMA_HOST=chromadb
CHROMA_PORT=8000

# Ollama
OLLAMA_HOST=ollama
OLLAMA_PORT=11434

# n8n
N8N_HOST=n8n
N8N_PORT=5678

# GPU
CUDA_VISIBLE_DEVICES=0
MLX_DEVICE=mps
```

### Volume Mounts

- `./vector_db` - Vector database storage
- `./models` - Model files
- `./n8n/data` - n8n workflow data
- `./logs` - System logs
- `./configs` - Configuration files

## 🛠️ Development

### Building Custom Images

```bash
# Build specific service
docker-compose build rag-api

# Build all services
docker-compose build
```

### Running Individual Services

```bash
# Start only ChromaDB
docker-compose up -d chromadb

# Start RAG API with logs
docker-compose up rag-api
```

### Debugging

```bash
# Access service shell
docker-compose exec rag-api bash

# View service logs
docker-compose logs rag-api

# Check service health
docker-compose exec rag-api curl localhost:8001/health
```

## 📊 Monitoring

### Health Checks

All services include health check endpoints:

- ChromaDB: `GET /api/v1/heartbeat`
- Ollama: `GET /api/tags`
- n8n: `GET /api/v1/workflows`
- RAG API: `GET /health`
- Monitoring: `GET /health`

### Logs

Logs are available in multiple ways:

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs rag-api

# Follow logs
docker-compose logs -f monitoring
```

### Metrics

The monitoring service provides:

- Service health status
- Response times
- Error rates
- System resource usage

## 🔒 Security

### Network Security

- Services communicate through isolated Docker network
- No external access to internal services
- Only necessary ports exposed

### Data Security

- Persistent data stored in Docker volumes
- Environment variables for sensitive configuration
- API keys and secrets in `.env` file

## 🚨 Troubleshooting

### Common Issues

1. **Services not starting**
   ```bash
   # Check logs
   docker-compose logs
   
   # Check resource usage
   docker stats
   ```

2. **GPU not available**
   ```bash
   # Check NVIDIA Docker support
   docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
   ```

3. **Port conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :8000
   ```

4. **Memory issues**
   ```bash
   # Check memory usage
   docker stats
   
   # Increase Docker memory limit
   ```

### Reset System

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Start fresh
./docker/start-ai-system.sh
```

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale RAG API
docker-compose up -d --scale rag-api=3

# Scale with load balancer
# (Requires additional nginx configuration)
```

### Resource Limits

```yaml
# In docker-compose.yml
services:
  rag-api:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

## 🔄 Updates

### Updating Services

```bash
# Pull latest images
docker-compose pull

# Restart services
docker-compose up -d
```

### Updating Code

```bash
# Rebuild with new code
docker-compose build rag-api

# Restart service
docker-compose up -d rag-api
```

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Ollama Documentation](https://ollama.ai/docs)
- [n8n Documentation](https://docs.n8n.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Support

For issues and questions:

1. Check the troubleshooting section
2. Review service logs
3. Check system resources
4. Verify configuration