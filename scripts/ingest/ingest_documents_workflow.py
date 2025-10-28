#!/usr/bin/env python3
"""
Create a document ingestion workflow for the RAG system
"""

import requests
import json
import time

# Sample documents to ingest
DOCUMENTS = {
    "docker_guide": {
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
    "machine_learning": {
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
    "python_guide": {
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

def test_rag_system():
    """Test the RAG system with a simple query"""
    print("🔍 Testing RAG system...")
    
    # Test the working RAG workflow
    try:
        response = requests.post("http://localhost:5678/webhook/rag-complete", 
                               json={"query": "Hello, what do you know?"},
                               timeout=30)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ RAG system is responding!")
            return True
        else:
            print("❌ RAG system error")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def simulate_document_ingestion():
    """Simulate document ingestion by asking the RAG system to remember content"""
    print("\n📚 Simulating document ingestion...")
    
    for doc_name, doc_info in DOCUMENTS.items():
        print(f"📄 Processing: {doc_name} ({doc_info['category']})")
        
        # Create a query that includes the document content
        query = f"Please remember this {doc_info['category']} information: {doc_info['content'][:200]}..."
        
        try:
            response = requests.post("http://localhost:5678/webhook/rag-complete", 
                                   json={"query": query},
                                   timeout=30)
            
            if response.status_code == 200:
                print(f"   ✅ {doc_name} processed")
            else:
                print(f"   ❌ {doc_name} failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error processing {doc_name}: {e}")
        
        time.sleep(2)  # Rate limiting

def test_queries():
    """Test various queries on the ingested content"""
    print("\n🎯 Testing queries on ingested content...")
    
    test_queries = [
        "What are the key concepts of Docker?",
        "Explain the different types of machine learning",
        "What are Python best practices?",
        "How do I create a Dockerfile?",
        "What evaluation metrics are used in machine learning?",
        "What are the main features of Python?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Query {i}: {query} ---")
        
        try:
            response = requests.post("http://localhost:5678/webhook/rag-complete", 
                                   json={"query": query},
                                   timeout=30)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
        
        time.sleep(1)  # Rate limiting

def main():
    """Main execution function"""
    print("🚀 Document Ingestion and RAG Testing")
    print("=" * 50)
    
    # Test RAG system
    if not test_rag_system():
        print("❌ RAG system not available")
        return
    
    # Simulate document ingestion
    simulate_document_ingestion()
    
    # Test queries
    test_queries()
    
    print("\n✅ Document processing complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()