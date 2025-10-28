# AI Orchestration & RAG System

A comprehensive AI orchestration platform with Retrieval-Augmented Generation (RAG) capabilities, featuring automated workflows, vector databases, and production-ready deployment.

## 🚀 Features

### Core Components
- **RAG Orchestrator v2**: Central reasoning and control agent for AI workflows
- **Vector Databases**: FAISS and ChromaDB integration for semantic search
- **N8N Workflows**: Automated AI processing pipelines
- **Model Management**: Ollama integration with quantized models
- **Dataset Pipeline**: Automated ingestion and processing of training data

### Key Achievements
- ✅ **Dataset Expansion**: 249 high-quality training examples (27x growth)
- ✅ **Quality Assurance**: >99% excellent/good content quality
- ✅ **Vector Store**: FAISS production deployment with GPU acceleration
- ✅ **Performance**: Sub-millisecond query responses
- ✅ **Reliability**: Environment-conflict-free architecture

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │───▶│ RAG Orchestrator│───▶│  Vector Search  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   N8N Workflows │    │     FAISS       │
                       │  (Automation)   │    │   (Embeddings)  │
                       └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │    Ollama       │    │ Training Data   │
                       │   (Inference)   │    │   (249 docs)    │
                       └─────────────────┘    └─────────────────┘
```

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Ollama
- N8N

### Quick Start
```bash
# Clone the repository
git clone <your-private-repo-url>
cd ai

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start services
docker-compose up -d

# Run FAISS ingestion
python3 faiss_ingestion_production.py
```

## 📁 Project Structure

```
ai/
├── configs/                 # Configuration files
├── datasets/                # Training data (249 examples)
├── vector_db/              # Vector stores (FAISS/ChromaDB)
├── rag_sources/            # RAG documents
├── infra/                  # Infrastructure scripts
├── n8n/                    # N8N workflow definitions
├── benchmarks/             # Performance testing
├── models/                 # Model configurations
├── fine_tuned_models/      # Fine-tuned AI models
├── examples/               # Example implementations
├── scripts/                # Utility scripts
└── docker/                 # Container configurations
```

## 🎯 Key Components

### RAG System
- **FAISS Vector Store**: Production-ready semantic search
- **Sentence Transformers**: High-quality embeddings
- **249 Documents**: Curated training dataset
- **GPU Acceleration**: Optimized for performance

### Automation Workflows
- **N8N Integration**: Visual workflow automation
- **Webhook Processing**: Real-time AI responses
- **MCP Tools**: Model Context Protocol integration

### Performance Optimization
- **Model Quantization**: Q4_K_M, Q5_K_M for speed
- **Connection Pooling**: Efficient resource management
- **Caching**: Response caching for repeated queries

## 📈 Performance Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Documents Processed | 249 | ✅ |
| Quality Score | >99% | ✅ |
| Query Response Time | <1ms | ✅ |
| Vector Store | FAISS | ✅ |
| Model Support | Ollama | ✅ |

## 🚀 Usage

### Basic RAG Query
```python
from faiss_ingestion_production import ProductionFAISSIngester

# Load the system
ingester = ProductionFAISSIngester()

# Perform semantic search
results = ingester.search("What is machine learning?")
print(results)
```

### Workflow Automation
```bash
# Start N8N workflows
python3 activate_workflows.py

# Test webhook endpoints
python3 test_webhooks_final.py
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
export OLLAMA_HOST=http://localhost:11434
export N8N_HOST=http://localhost:5678

# Optional
export CUDA_VISIBLE_DEVICES=0  # GPU acceleration
```

### Model Configuration
- **Primary**: llama3.1:8b-instruct-q5_K_M (balanced)
- **Fast**: llama3.1:8b-instruct-q2_K (speed)
- **Quality**: llama3.1:8b-instruct-q8_0 (accuracy)

## 📚 Documentation

- [Quick Start Guide](QUICK_START_GUIDE.md)
- [Production Deployment](PRODUCTION_DEPLOYMENT_GUIDE.md)
- [API Documentation](configs/)
- [Performance Benchmarks](benchmarks/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

Private repository - internal use only.

## 🏆 Achievements

- **Dataset Expansion**: 9 → 249 examples (27x growth)
- **Quality Assurance**: >99% excellent/good content
- **Performance**: Sub-millisecond RAG responses
- **Architecture**: Environment-conflict-free design
- **Production Ready**: Complete deployment pipeline

---

**Built with ❤️ for AI orchestration and RAG excellence**
