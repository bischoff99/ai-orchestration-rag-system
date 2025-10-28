#!/usr/bin/env python3
"""
ChromaDB v2 Collections Setup
Creates and populates collections for optimized RAG performance
"""
import requests
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChromaDBv2CollectionManager:
    """Manager for ChromaDB v2 collections"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v2"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def check_health(self) -> bool:
        """Check if ChromaDB v2 is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/heartbeat", timeout=5)
            if response.status_code == 200:
                logger.info("✅ ChromaDB v2 is healthy")
                return True
            else:
                logger.error(f"❌ ChromaDB v2 health check failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ ChromaDB v2 health check error: {e}")
            return False
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """List existing collections"""
        try:
            response = self.session.get(f"{self.base_url}/collections", timeout=10)
            if response.status_code == 200:
                collections = response.json()
                logger.info(f"Found {len(collections)} existing collections")
                return collections
            else:
                logger.warning(f"Failed to list collections: HTTP {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
    
    def create_collection(self, name: str, metadata: Dict[str, Any] = None) -> bool:
        """Create a new collection"""
        try:
            payload = {
                "name": name,
                "metadata": metadata or {}
            }
            
            response = self.session.post(f"{self.base_url}/collections", json=payload, timeout=10)
            if response.status_code == 200 or response.status_code == 201:
                logger.info(f"✅ Created collection: {name}")
                return True
            else:
                logger.error(f"❌ Failed to create collection '{name}': HTTP {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Error creating collection '{name}': {e}")
            return False
    
    def add_documents(self, collection_name: str, documents: List[str], metadatas: List[Dict] = None, ids: List[str] = None) -> bool:
        """Add documents to a collection"""
        try:
            if not ids:
                ids = [f"doc_{i}" for i in range(len(documents))]
            if not metadatas:
                metadatas = [{"source": f"doc_{i}"} for i in range(len(documents))]
            
            payload = {
                "documents": documents,
                "metadatas": metadatas,
                "ids": ids
            }
            
            response = self.session.post(f"{self.base_url}/collections/{collection_name}/add", json=payload, timeout=30)
            if response.status_code == 200:
                logger.info(f"✅ Added {len(documents)} documents to collection '{collection_name}'")
                return True
            else:
                logger.error(f"❌ Failed to add documents to '{collection_name}': HTTP {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Error adding documents to '{collection_name}': {e}")
            return False
    
    def query_collection(self, collection_name: str, query_text: str, n_results: int = 3) -> List[str]:
        """Query a collection"""
        try:
            payload = {
                "query_texts": [query_text],
                "n_results": n_results
            }
            
            response = self.session.post(f"{self.base_url}/collections/{collection_name}/query", json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                documents = data.get("documents", [[]])[0]
                logger.info(f"✅ Retrieved {len(documents)} documents from '{collection_name}'")
                return documents
            else:
                logger.error(f"❌ Failed to query '{collection_name}': HTTP {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"❌ Error querying '{collection_name}': {e}")
            return []
    
    def setup_rag_collections(self) -> bool:
        """Set up collections for RAG system"""
        logger.info("🚀 Setting up RAG collections...")
        
        # Check health first
        if not self.check_health():
            return False
        
        # Define collections to create
        collections = {
            "rag_documents_collection": {
                "description": "Main RAG documents collection",
                "metadata": {"type": "rag_documents", "version": "2.0"}
            },
            "technical_docs_collection": {
                "description": "Technical documentation collection",
                "metadata": {"type": "technical_docs", "version": "2.0"}
            },
            "code_examples_collection": {
                "description": "Code examples and snippets collection",
                "metadata": {"type": "code_examples", "version": "2.0"}
            }
        }
        
        success_count = 0
        
        for collection_name, config in collections.items():
            logger.info(f"Creating collection: {collection_name}")
            if self.create_collection(collection_name, config["metadata"]):
                success_count += 1
        
        logger.info(f"✅ Created {success_count}/{len(collections)} collections")
        return success_count == len(collections)
    
    def populate_sample_data(self) -> bool:
        """Populate collections with sample data"""
        logger.info("📚 Populating collections with sample data...")
        
        # Sample documents for RAG
        sample_documents = {
            "rag_documents_collection": [
                "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed. It focuses on developing algorithms that can identify patterns and make predictions.",
                "Docker is a containerization platform that packages applications and their dependencies into lightweight, portable containers. This ensures consistent environments across development, testing, and production.",
                "Python is a high-level programming language known for its simplicity, readability, and extensive library ecosystem. It's widely used in data science, web development, and automation.",
                "Vector databases are specialized databases designed to store and query high-dimensional vectors efficiently. They're essential for similarity search, recommendation systems, and AI applications.",
                "RAG (Retrieval-Augmented Generation) combines information retrieval with text generation to provide more accurate and contextually relevant responses by retrieving relevant documents before generating answers."
            ],
            "technical_docs_collection": [
                "API design best practices include using RESTful principles, proper HTTP status codes, versioning strategies, comprehensive documentation, and consistent error handling patterns.",
                "Database optimization techniques include proper indexing, query optimization, connection pooling, caching strategies, and regular maintenance routines.",
                "Security best practices for web applications include input validation, authentication, authorization, encryption, secure communication protocols, and regular security audits.",
                "Performance monitoring involves tracking key metrics like response times, throughput, error rates, resource utilization, and user experience indicators.",
                "Microservices architecture involves breaking down applications into small, independent services that communicate over well-defined APIs, enabling better scalability and maintainability."
            ],
            "code_examples_collection": [
                "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)  # Python recursive Fibonacci",
                "const express = require('express'); const app = express(); app.get('/', (req, res) => res.send('Hello World!'));  // Node.js Express server",
                "docker run -p 8080:80 nginx  # Run Nginx container on port 8080",
                "SELECT * FROM users WHERE age > 18 ORDER BY created_at DESC LIMIT 10;  -- SQL query example",
                "import pandas as pd; df = pd.read_csv('data.csv'); print(df.head())  # Python pandas data analysis"
            ]
        }
        
        success_count = 0
        
        for collection_name, documents in sample_documents.items():
            logger.info(f"Populating {collection_name} with {len(documents)} documents...")
            if self.add_documents(collection_name, documents):
                success_count += 1
        
        logger.info(f"✅ Populated {success_count}/{len(sample_documents)} collections")
        return success_count == len(sample_documents)
    
    def test_collections(self) -> bool:
        """Test collections with sample queries"""
        logger.info("🧪 Testing collections with sample queries...")
        
        test_queries = [
            "What is machine learning?",
            "How does Docker work?",
            "Explain Python programming",
            "What are vector databases?",
            "What is RAG?"
        ]
        
        success_count = 0
        
        for query in test_queries:
            logger.info(f"Testing query: {query}")
            results = self.query_collection("rag_documents_collection", query, n_results=2)
            if results:
                logger.info(f"  Found {len(results)} relevant documents")
                success_count += 1
            else:
                logger.warning(f"  No results found for: {query}")
        
        logger.info(f"✅ {success_count}/{len(test_queries)} queries returned results")
        return success_count == len(test_queries)

def main():
    """Main function to set up ChromaDB v2 collections"""
    logger.info("🚀 ChromaDB v2 Collections Setup")
    logger.info("=" * 50)
    
    manager = ChromaDBv2CollectionManager()
    
    # Step 1: Check health
    if not manager.check_health():
        logger.error("❌ ChromaDB v2 is not healthy. Please start the service first.")
        return False
    
    # Step 2: List existing collections
    existing_collections = manager.list_collections()
    logger.info(f"Existing collections: {[c.get('name', 'unknown') for c in existing_collections]}")
    
    # Step 3: Set up collections
    if not manager.setup_rag_collections():
        logger.error("❌ Failed to set up collections")
        return False
    
    # Step 4: Populate with sample data
    if not manager.populate_sample_data():
        logger.error("❌ Failed to populate collections")
        return False
    
    # Step 5: Test collections
    if not manager.test_collections():
        logger.error("❌ Collection testing failed")
        return False
    
    logger.info("🎉 ChromaDB v2 collections setup completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)