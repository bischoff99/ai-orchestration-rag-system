#!/usr/bin/env python3
"""
Local RAG Demo using your existing ChromaDB
"""
import chromadb
import requests
import json
import os

def test_local_chromadb():
    """Test local ChromaDB connection"""
    print("🗄️  Testing local ChromaDB...")
    
    try:
        # Connect to your local ChromaDB
        client = chromadb.PersistentClient(path="/Users/andrejsp/ai/vector_db/chroma")
        
        # List collections
        collections = client.list_collections()
        print(f"✅ Found {len(collections)} collections:")
        for col in collections:
            print(f"   - {col.name}")
        
        # Test query if collections exist
        if collections:
            collection = client.get_collection(collections[0].name)
            results = collection.query(query_texts=["machine learning"], n_results=3)
            print(f"✅ Query successful: {len(results['documents'][0])} results")
            return True
        else:
            print("⚠️  No collections found - need to populate database")
            return False
            
    except Exception as e:
        print(f"❌ ChromaDB Error: {e}")
        return False

def test_ollama_rag():
    """Test RAG with Ollama directly"""
    print("\n🤖 Testing RAG with Ollama...")
    
    try:
        # Simple RAG query
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.1:8b-instruct-q5_K_M",
                "prompt": "Based on the context: 'Machine learning is a subset of AI that enables computers to learn from data.' What is machine learning?",
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ RAG Response: {result.get('response', 'No response')[:200]}...")
            return True
        else:
            print(f"❌ Ollama Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ollama Error: {e}")
        return False

def populate_sample_data():
    """Add sample data to ChromaDB"""
    print("\n📚 Adding sample data to ChromaDB...")
    
    try:
        client = chromadb.PersistentClient(path="/Users/andrejsp/ai/vector_db/chroma")
        
        # Create or get collection
        collection = client.get_or_create_collection(name="rag_documents_collection")
        
        # Sample documents
        documents = [
            "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed.",
            "Deep learning uses neural networks with multiple layers to process data and make predictions.",
            "Natural language processing (NLP) is a field of AI that focuses on the interaction between computers and human language.",
            "Vector databases store and retrieve data using vector embeddings for similarity search."
        ]
        
        # Add documents
        collection.add(
            documents=documents,
            metadatas=[{"source": f"doc_{i}"} for i in range(len(documents))],
            ids=[f"doc_{i}" for i in range(len(documents))]
        )
        
        print(f"✅ Added {len(documents)} documents to collection")
        return True
        
    except Exception as e:
        print(f"❌ Error adding data: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Local RAG System Demo")
    print("=" * 40)
    
    # Test ChromaDB
    chroma_works = test_local_chromadb()
    
    # If no data, add some
    if not chroma_works:
        populate_sample_data()
        chroma_works = test_local_chromadb()
    
    # Test Ollama
    ollama_works = test_ollama_rag()
    
    print("\n📊 Results:")
    print(f"ChromaDB: {'✅ Working' if chroma_works else '❌ Failed'}")
    print(f"Ollama: {'✅ Working' if ollama_works else '❌ Failed'}")
    
    if chroma_works and ollama_works:
        print("\n🎉 Local RAG system is working!")
        print("💡 The issue is n8n workflows trying to connect to Docker services instead of local databases.")
    else:
        print("\n❌ Some components need fixing")
