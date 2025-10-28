#!/usr/bin/env python3
"""
Initialize ChromaDB v2 collections and populate with sample data
"""
import chromadb
from datetime import datetime

def main():
    print("🚀 ChromaDB v2 Collection Initialization")
    print("=" * 50)

    try:
        client = chromadb.Client()
        print("\n1. Checking existing collections...")
        collections = client.list_collections()
        print(f"📋 Found {len(collections)} collections:")
        for col in collections:
            print(f"   - {col.name} (id: {col.id})")

        collection_name = "rag_documents_collection"
        print(f"\n2. Creating collection '{collection_name}'...")
        
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "RAG documents for AI system", "created": datetime.now().isoformat()}
        )
        
        print(f"✅ Collection '{collection_name}' created or retrieved successfully")

        print(f"\n3. Adding sample documents...")
        sample_docs = [
            "Machine learning is a subset of artificial intelligence that enables computers to learn from data.",
            "Docker is a containerization platform that packages applications and their dependencies.",
            "Python is a high-level programming language known for its simplicity and readability.",
            "Vector databases store and retrieve data using vector embeddings for similarity search.",
            "Natural language processing (NLP) is a field of AI that focuses on human language understanding."
        ]
        
        collection.add(
            documents=sample_docs,
            metadatas=[{"source": f"sample_{i}", "type": "knowledge"} for i in range(len(sample_docs))],
            ids=[f"sample_doc_{i}" for i in range(len(sample_docs))]
        )
        
        print(f"✅ Added {len(sample_docs)} documents successfully")

        print(f"\n4. Testing query functionality...")
        query_results = collection.query(
            query_texts=["What is machine learning?"],
            n_results=2
        )
        
        print(f"✅ Query successful, found {len(query_results.get('documents', [[]])[0])} results")
        
        print("✅ ChromaDB v2 collection setup complete!")
        print(f"   Collection: {collection_name}")
        print(f"   Documents: {len(sample_docs)}")
        print(f"   Query test: Successful")

    except Exception as e:
        print(f"❌ Error during ChromaDB initialization: {e}")

if __name__ == "__main__":
    main()
