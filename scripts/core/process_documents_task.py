#!/usr/bin/env python3
"""
Document Processing Task - Ingest and analyze project files
"""

import requests
import json
import time
from pathlib import Path

# RAG System Configuration
RAG_WEBHOOK_URL = "http://localhost:5678/webhook/rag-chat"
DOCUMENT_INGESTION_URL = "http://localhost:5678/webhook/preprocess-document"

# Sample documents to process
SAMPLE_DOCS = {
    "docker_guide.txt": {
        "content": """Docker Containerization Guide

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
- docker logs <container_id>""",
        "category": "DevOps"
    },
    "machine_learning_basics.txt": {
        "content": """Machine Learning Basics

Machine Learning (ML) is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed.

Types of Machine Learning:

1. Supervised Learning:
   - Uses labeled training data
   - Examples: Classification, Regression
   - Algorithms: Linear Regression, Decision Trees, Random Forest, SVM

2. Unsupervised Learning:
   - Works with unlabeled data
   - Examples: Clustering, Dimensionality Reduction
   - Algorithms: K-Means, PCA, DBSCAN

3. Reinforcement Learning:
   - Learns through interaction with environment
   - Examples: Game playing, Robotics
   - Algorithms: Q-Learning, Policy Gradient

Common ML Workflow:
1. Data Collection and Preprocessing
2. Feature Engineering
3. Model Selection
4. Training and Validation
5. Model Evaluation
6. Deployment and Monitoring

Popular Python Libraries:
- Scikit-learn: General purpose ML
- TensorFlow: Deep learning framework
- PyTorch: Deep learning with dynamic graphs
- Pandas: Data manipulation
- NumPy: Numerical computing
- Matplotlib/Seaborn: Data visualization

Evaluation Metrics:
- Classification: Accuracy, Precision, Recall, F1-Score
- Regression: MSE, RMSE, MAE, R²
- Clustering: Silhouette Score, Inertia

Best Practices:
- Always split data into train/validation/test sets
- Use cross-validation for model selection
- Handle missing values and outliers
- Scale features when necessary
- Regularize to prevent overfitting""",
        "category": "Machine Learning"
    },
    "python_guide.txt": {
        "content": """Python Programming Guide

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
squares = [x**2 for x in range(10)]""",
        "category": "Programming"
    }
}

# Configuration files to analyze
CONFIG_FILES = {
    "rag_config.json": {
        "content": """{
  "vector_databases": {
    "chroma": {
      "path": "/Users/andrejsp/ai/vector_db/chroma",
      "collection_name": "documents",
      "distance_metric": "cosine"
    },
    "faiss": {
      "path": "/Users/andrejsp/ai/vector_db/faiss",
      "index_type": "IndexFlatIP",
      "normalize": true
    }
  },
  "embedding_model": {
    "name": "all-MiniLM-L6-v2",
    "dimension": 384,
    "max_sequence_length": 256
  },
  "ollama": {
    "url": "http://localhost:11434/api/generate",
    "default_model": "llama-assistant",
    "timeout": 30,
    "temperature": 0.1,
    "top_p": 0.9
  },
  "rag_settings": {
    "max_context_length": 2000,
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "max_results": 5,
    "similarity_threshold": 0.7
  },
  "document_types": {
    "supported_formats": [".txt", ".md", ".pdf", ".docx"],
    "text_splitter": "RecursiveCharacterTextSplitter",
    "preprocessing": {
      "remove_extra_whitespace": true,
      "normalize_unicode": true,
      "remove_special_chars": false
    }
  }
}""",
        "category": "Configuration"
    }
}

def test_rag_system():
    """Test if RAG system is working"""
    print("🔍 Testing RAG system...")
    try:
        response = requests.post(RAG_WEBHOOK_URL, json={
            "query": "System test - are you working?",
            "collection": "rag_documents_collection"
        }, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ RAG system is working!")
            return True
        else:
            print(f"   ❌ RAG system error: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False

def ingest_document(filename, content, category):
    """Ingest a document into the RAG system"""
    print(f"📄 Ingesting: {filename} ({category})")
    
    # For now, we'll simulate ingestion by asking the RAG system about the content
    # In a real implementation, you'd have a dedicated ingestion endpoint
    try:
        response = requests.post(RAG_WEBHOOK_URL, json={
            "query": f"Please remember this {category} content: {content[:500]}...",
            "collection": "rag_documents_collection"
        }, timeout=15)
        
        if response.status_code == 200:
            print(f"   ✅ {filename} processed successfully")
            return True
        else:
            print(f"   ❌ Failed to process {filename}: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error processing {filename}: {e}")
        return False

def test_queries():
    """Test various queries on the processed content"""
    test_queries = [
        "What are the key concepts of Docker?",
        "Explain the different types of machine learning",
        "What are Python best practices?",
        "What is the RAG configuration for vector databases?",
        "How do I create a Dockerfile?",
        "What evaluation metrics are used in machine learning?",
        "What are the main features of Python?",
        "What is the chunk size in the RAG configuration?"
    ]
    
    print("\n🎯 Testing RAG queries...")
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Query {i}: {query} ---")
        try:
            response = requests.post(RAG_WEBHOOK_URL, json={
                "query": query,
                "collection": "rag_documents_collection"
            }, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Response: {result.get('response', 'No response')[:200]}...")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Query failed: {e}")
        
        time.sleep(1)  # Rate limiting

def main():
    """Main execution function"""
    print("🚀 Starting Document Processing Task")
    print("=" * 50)
    
    # Test RAG system
    if not test_rag_system():
        print("❌ RAG system not available. Please check n8n and Ollama services.")
        return
    
    # Process sample documents
    print("\n📚 Processing Sample Documents...")
    for filename, doc_info in SAMPLE_DOCS.items():
        ingest_document(filename, doc_info["content"], doc_info["category"])
        time.sleep(2)  # Rate limiting
    
    # Process configuration files
    print("\n⚙️ Processing Configuration Files...")
    for filename, config_info in CONFIG_FILES.items():
        ingest_document(filename, config_info["content"], config_info["category"])
        time.sleep(2)  # Rate limiting
    
    # Test queries
    test_queries()
    
    print("\n✅ Document Processing Task Complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()