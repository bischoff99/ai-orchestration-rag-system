#!/usr/bin/env python3
"""
Simple RAG Setup with ChromaDB
Quick start for vector database and RAG
"""

import os
import json
import chromadb
from sentence_transformers import SentenceTransformer
import requests

class SimpleRAG:
    def __init__(self):
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path="/Users/andrejsp/ai/vector_db/simple_rag")
        self.collection = self.client.get_or_create_collection("documents")
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("✅ Simple RAG initialized")
    
    def add_documents(self, documents: list, metadatas: list = None):
        """Add documents to the vector database"""
        if metadatas is None:
            metadatas = [{"doc_id": i} for i in range(len(documents))]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents)
        
        # Add to ChromaDB
        ids = [f"doc_{i}" for i in range(len(documents))]
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Added {len(documents)} documents")
    
    def search(self, query: str, k: int = 3):
        """Search for similar documents"""
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=k
        )
        
        return results
    
    def query_ollama(self, question: str, k: int = 3):
        """Query with RAG using Ollama"""
        # Search for relevant documents
        search_results = self.search(question, k)
        
        # Prepare context
        context = "\n\n".join(search_results['documents'][0])
        
        # Create prompt
        prompt = f"""Based on the following context, answer the question:

Context:
{context}

Question: {question}

Answer:"""
        
        # Query Ollama
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama-assistant",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            return f"Error: {e}"

def main():
    print("🚀 Simple RAG Setup")
    print("=" * 25)
    
    # Create RAG instance
    rag = SimpleRAG()
    
    # Sample documents
    documents = [
        "Python is a high-level programming language known for its simplicity and readability. It's widely used in web development, data science, and AI.",
        "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed.",
        "Docker is a containerization platform that allows you to package applications and their dependencies into lightweight, portable containers."
    ]
    
    metadatas = [
        {"title": "Python Programming", "category": "programming"},
        {"title": "Machine Learning", "category": "ai"},
        {"title": "Docker", "category": "devops"}
    ]
    
    # Add documents
    rag.add_documents(documents, metadatas)
    
    # Test search
    print("\n🔍 Testing search...")
    results = rag.search("What is Python?", k=2)
    print(f"Found {len(results['documents'][0])} relevant documents")
    
    # Test RAG query
    print("\n🤖 Testing RAG query...")
    answer = rag.query_ollama("What is Python used for?")
    print(f"Answer: {answer}")
    
    print("\n✅ Simple RAG setup complete!")

if __name__ == "__main__":
    main()
