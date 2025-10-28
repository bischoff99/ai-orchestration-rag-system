#!/usr/bin/env python3
"""
Complete RAG Setup Script
Sets up everything needed for RAG with vector databases
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "/Users/andrejsp/ai/vector_db",
        "/Users/andrejsp/ai/vector_db/chroma",
        "/Users/andrejsp/ai/vector_db/faiss",
        "/Users/andrejsp/ai/vector_db/qdrant",
        "/Users/andrejsp/ai/sample_docs",
        "/Users/andrejsp/ai/configs",
        "/Users/andrejsp/ai/scripts",
        "/Users/andrejsp/ai/examples"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Directories created")

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    
    packages = [
        "chromadb",
        "faiss-cpu", 
        "sentence-transformers",
        "langchain",
        "langchain-community",
        "requests",
        "numpy"
    ]
    
    for package in packages:
        if not run_command(f"cd /Users/andrejsp/ai && source envs/mlx_qlora/bin/activate && uv pip install {package}", f"Installing {package}"):
            return False
    
    return True

def create_sample_documents():
    """Create sample documents for testing"""
    print("📚 Creating sample documents...")
    
    documents = {
        "python_guide.txt": """Python Programming Guide

Python is a high-level, interpreted programming language known for its simplicity and readability.

Key Features:
- Simple and easy to learn syntax
- Cross-platform compatibility
- Extensive standard library
- Large ecosystem of third-party packages

Best Practices:
- Follow PEP 8 style guide
- Use meaningful variable names
- Write docstrings for functions and classes
- Use virtual environments for project isolation
- Handle exceptions properly with try-except blocks

Example Code:
def fibonacci(n):
    \"\"\"Calculate the nth Fibonacci number.\"\"\"
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# List comprehension example
squares = [x**2 for x in range(10)]
""",
        
        "machine_learning.txt": """Machine Learning Basics

Machine Learning (ML) is a subset of artificial intelligence that enables computers to learn from data.

Types of Machine Learning:

1. Supervised Learning:
   - Uses labeled training data
   - Examples: Classification, Regression
   - Algorithms: Linear Regression, Decision Trees, Random Forest

2. Unsupervised Learning:
   - Works with unlabeled data
   - Examples: Clustering, Dimensionality Reduction
   - Algorithms: K-Means, PCA

3. Reinforcement Learning:
   - Learns through interaction with environment
   - Examples: Game playing, Robotics

Popular Python Libraries:
- Scikit-learn: General purpose ML
- TensorFlow: Deep learning framework
- PyTorch: Deep learning with dynamic graphs
- Pandas: Data manipulation
- NumPy: Numerical computing

Evaluation Metrics:
- Classification: Accuracy, Precision, Recall, F1-Score
- Regression: MSE, RMSE, MAE, R²
""",
        
        "docker_guide.txt": """Docker Containerization Guide

Docker allows you to package applications and their dependencies into containers.

Key Concepts:
1. Dockerfile: Instructions to build a Docker image
2. Docker Image: A read-only template for creating containers
3. Docker Container: A running instance of an image
4. Docker Compose: Tool for multi-container applications

Basic Dockerfile:
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]

Common Commands:
- docker build -t myapp .
- docker run -p 8000:8000 myapp
- docker-compose up
- docker ps
- docker logs <container_id>
"""
    }
    
    for filename, content in documents.items():
        file_path = f"/Users/andrejsp/ai/sample_docs/{filename}"
        with open(file_path, 'w') as f:
            f.write(content)
    
    print("✅ Sample documents created")

def create_rag_scripts():
    """Create RAG utility scripts"""
    print("🛠️ Creating RAG scripts...")
    
    # Create a simple test script
    test_script = """#!/usr/bin/env python3
import sys
sys.path.append('/Users/andrejsp/ai/examples')
from unified_rag import UnifiedRAG

def test_rag():
    print("🧪 Testing RAG System")
    print("=" * 25)
    
    # Initialize RAG
    rag = UnifiedRAG(backend="chroma")
    
    # Test documents
    documents = [
        "Python is a programming language known for its simplicity and readability.",
        "Machine learning enables computers to learn from data without explicit programming.",
        "Docker containers package applications with their dependencies for easy deployment."
    ]
    
    metadatas = [
        {"title": "Python", "category": "programming"},
        {"title": "Machine Learning", "category": "ai"},
        {"title": "Docker", "category": "devops"}
    ]
    
    # Add documents
    rag.add_documents(documents, metadatas)
    
    # Test queries
    queries = [
        "What is Python?",
        "How does machine learning work?",
        "What is Docker used for?"
    ]
    
    for query in queries:
        print(f"\\n❓ Query: {query}")
        response = rag.query_ollama(query)
        print(f"🤖 Answer: {response['answer']}")
        print(f"📚 Sources: {len(response['sources'])} documents")

if __name__ == "__main__":
    test_rag()
"""
    
    with open("/Users/andrejsp/ai/scripts/test_rag.py", "w") as f:
        f.write(test_script)
    
    os.chmod("/Users/andrejsp/ai/scripts/test_rag.py", 0o755)
    
    print("✅ RAG scripts created")

def create_usage_guide():
    """Create usage guide"""
    print("📖 Creating usage guide...")
    
    guide = """# RAG Vector Database Setup Complete! 🎉

## What's Been Set Up

### Vector Databases
- **ChromaDB**: Easy-to-use, persistent storage
- **FAISS**: Fast, memory-efficient search
- **Qdrant**: Advanced features (optional)

### Files Created
- `/Users/andrejsp/ai/examples/unified_rag.py` - Main RAG implementation
- `/Users/andrejsp/ai/scripts/test_rag.py` - Test script
- `/Users/andrejsp/ai/sample_docs/` - Sample documents
- `/Users/andrejsp/ai/configs/rag_config.json` - Configuration

## Quick Start

### 1. Test the RAG System
```bash
cd /Users/andrejsp/ai
source envs/mlx_qlora/bin/activate
python scripts/test_rag.py
```

### 2. Add Your Own Documents
```bash
python scripts/ingest_documents.py your_documents/*.txt --backend chroma
```

### 3. Query the RAG System
```bash
python scripts/rag_query.py --query "Your question here" --backend chroma
```

### 4. Interactive Mode
```bash
python scripts/rag_query.py --backend chroma
```

## Available Backends

### ChromaDB (Recommended)
- Easy to use
- Persistent storage
- Good for development

### FAISS
- Very fast
- Memory efficient
- Good for production

## Integration with Ollama

The RAG system automatically integrates with your Ollama models:
- Uses `llama-assistant` by default
- Configurable in the scripts
- Supports any Ollama model

## Next Steps

1. **Add Your Documents**: Place your documents in `/Users/andrejsp/ai/sample_docs/`
2. **Ingest Documents**: Use the ingestion script to add them to the vector database
3. **Query**: Use the query interface to ask questions
4. **Customize**: Modify the configuration and scripts as needed

## Troubleshooting

- Make sure Ollama is running: `ollama serve`
- Check that your model is available: `ollama list`
- Verify the vector database is working with the test script

Happy RAG-ing! 🚀
"""
    
    with open("/Users/andrejsp/ai/RAG_SETUP_COMPLETE.md", "w") as f:
        f.write(guide)
    
    print("✅ Usage guide created")

def main():
    """Main setup function"""
    print("🚀 Complete RAG Setup")
    print("=" * 30)
    
    # Step 1: Create directories
    create_directories()
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return
    
    # Step 3: Create sample documents
    create_sample_documents()
    
    # Step 4: Create RAG scripts
    create_rag_scripts()
    
    # Step 5: Create usage guide
    create_usage_guide()
    
    print("\n🎉 RAG Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. 🧪 Test: python /Users/andrejsp/ai/scripts/test_rag.py")
    print("2. 📚 Add documents: python scripts/ingest_documents.py sample_docs/*.txt")
    print("3. 🔍 Query: python scripts/rag_query.py --query 'Your question'")
    print("4. 📖 Read guide: cat /Users/andrejsp/ai/RAG_SETUP_COMPLETE.md")

if __name__ == "__main__":
    main()