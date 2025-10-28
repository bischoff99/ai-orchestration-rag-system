#!/usr/bin/env python3
"""
Ollama-Powered RAG System
Uses Ollama embedding model for consistency with your setup
"""

import os
import json
import numpy as np
import requests
from typing import List, Dict, Any, Optional
import chromadb

class OllamaRAG:
    """RAG system using Ollama for both embeddings and generation"""
    
    def __init__(self, collection_name: str = "ollama_docs", embedding_model: str = "embedder"):
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.ollama_url = "http://localhost:11434"
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path="/Users/andrejsp/ai/vector_db/chroma")
        
        # Delete existing collection if it exists
        try:
            self.client.delete_collection(self.collection_name)
        except:
            pass
        
        # Create new collection
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        print(f"✅ Ollama RAG initialized with collection: {self.collection_name}")
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding from Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={
                    "model": self.embedding_model,
                    "prompt": text
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['embedding']
        except Exception as e:
            print(f"❌ Error getting embedding: {e}")
            return []
    
    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None):
        """Add documents to vector database using Ollama embeddings"""
        print(f"📄 Adding {len(documents)} documents using Ollama embeddings")
        
        if metadatas is None:
            metadatas = [{"doc_id": i} for i in range(len(documents))]
        
        # Get embeddings from Ollama
        embeddings = []
        for i, doc in enumerate(documents):
            print(f"🔄 Getting embedding for document {i+1}/{len(documents)}")
            embedding = self.get_embedding(doc)
            if embedding:
                embeddings.append(embedding)
            else:
                print(f"❌ Failed to get embedding for document {i+1}")
                return
        
        # Add to ChromaDB
        ids = [f"doc_{i}" for i in range(len(documents))]
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Added documents successfully")
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        print(f"🔍 Searching: '{query[:50]}...'")
        
        # Get query embedding from Ollama
        query_embedding = self.get_embedding(query)
        if not query_embedding:
            return []
        
        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        search_results = []
        for i in range(len(results['documents'][0])):
            search_results.append({
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })
        
        return search_results
    
    def query_ollama(self, question: str, k: int = 3, model: str = "llama-assistant") -> Dict[str, Any]:
        """Query with RAG using Ollama"""
        print(f"🤖 RAG Query: {question}")
        
        # Search for relevant documents
        search_results = self.search(question, k)
        
        # Prepare context
        context = "\n\n".join([result['text'] for result in search_results])
        
        # Create prompt
        prompt = f"""Based on the following context, answer the question. If the answer is not in the context, say so.

Context:
{context}

Question: {question}

Answer:"""
        
        # Query Ollama
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            answer = response.json()['response']
        except Exception as e:
            answer = f"Error querying Ollama: {e}"
        
        return {
            'answer': answer,
            'sources': [result['metadata'] for result in search_results],
            'context_used': context
        }

def test_ollama_rag():
    """Test the Ollama-powered RAG system"""
    print("🚀 Testing Ollama-Powered RAG")
    print("=" * 40)
    
    # Initialize RAG
    rag = OllamaRAG(embedding_model="embedder")
    
    # Test documents
    documents = [
        "Python is a high-level programming language known for its simplicity and readability. Best practices include following PEP 8 style guide, using meaningful variable names, writing docstrings, and using virtual environments.",
        
        "Machine learning is a subset of artificial intelligence that enables computers to learn from data. Common types include supervised learning, unsupervised learning, and reinforcement learning.",
        
        "Docker is a containerization platform that packages applications and dependencies into containers. It ensures consistency across different environments and simplifies deployment."
    ]
    
    metadatas = [
        {"title": "Python Best Practices", "category": "programming"},
        {"title": "Machine Learning Guide", "category": "ai"},
        {"title": "Docker Basics", "category": "devops"}
    ]
    
    # Add documents
    rag.add_documents(documents, metadatas)
    
    # Test queries
    queries = [
        "What are Python best practices?",
        "How does machine learning work?",
        "What is Docker used for?"
    ]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        response = rag.query_ollama(query)
        print(f"🤖 Answer: {response['answer']}")
        print(f"📚 Sources: {len(response['sources'])} documents")

if __name__ == "__main__":
    test_ollama_rag()