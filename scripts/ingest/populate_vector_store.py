#!/usr/bin/env python3
"""
Script to populate the vector store with sample documents
"""

import requests
import json
import time

def populate_vector_store():
    """Populate the vector store with sample documents"""
    
    # Sample documents to add
    documents = [
        {
            "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It focuses on algorithms that can access data and use it to learn for themselves.",
            "filename": "ml_intro.txt",
            "metadata": {"topic": "machine_learning", "type": "introduction"}
        },
        {
            "content": "Deep learning is a subset of machine learning that uses neural networks with multiple layers to model and understand complex patterns in data. It has revolutionized fields like computer vision, natural language processing, and speech recognition.",
            "filename": "deep_learning.txt", 
            "metadata": {"topic": "deep_learning", "type": "introduction"}
        },
        {
            "content": "Natural Language Processing (NLP) is a field of artificial intelligence that focuses on the interaction between computers and humans through natural language. It combines computational linguistics with machine learning to process and analyze large amounts of natural language data.",
            "filename": "nlp_intro.txt",
            "metadata": {"topic": "nlp", "type": "introduction"}
        },
        {
            "content": "Vector databases are specialized databases designed to store and query high-dimensional vectors efficiently. They are essential for RAG (Retrieval-Augmented Generation) systems as they enable fast similarity search for finding relevant documents.",
            "filename": "vector_databases.txt",
            "metadata": {"topic": "vector_databases", "type": "technical"}
        }
    ]
    
    print("🚀 Populating vector store with sample documents...")
    
    # First, let's try to add documents using a direct approach
    # We'll use the webhook to trigger document processing
    webhook_url = "http://localhost:5678/webhook/rag-chat"
    
    for i, doc in enumerate(documents, 1):
        print(f"📄 Adding document {i}/{len(documents)}: {doc['filename']}")
        
        # Try to add document via webhook
        payload = {
            "query": f"Add document: {doc['filename']}",
            "content": doc["content"],
            "filename": doc["filename"],
            "metadata": doc["metadata"],
            "action": "insert"
        }
        
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Document added successfully")
            else:
                print(f"   ❌ Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error adding document: {e}")
        
        time.sleep(1)  # Small delay between requests
    
    print("\n🎯 Testing RAG query...")
    
    # Test a query
    test_query = {
        "query": "What is machine learning?",
        "collection": "general_knowledge"
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=test_query,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Query Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error testing query: {e}")

if __name__ == "__main__":
    populate_vector_store()