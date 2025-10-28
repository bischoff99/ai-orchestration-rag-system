#!/usr/bin/env python3
"""
Initialize ChromaDB collections using direct Python client
"""
import chromadb
import os
from datetime import datetime

def init_chromadb_collections():
    """Initialize ChromaDB collections using Python client"""
    print("🚀 ChromaDB Collection Initialization (Direct Client)")
    print("=" * 60)
    
    # Connect to local ChromaDB
    chroma_path = "/Users/andrejsp/ai/vector_db/chroma"
    print(f"📁 Connecting to ChromaDB at: {chroma_path}")
    
    try:
        client = chromadb.PersistentClient(path=chroma_path)
        print("✅ Connected to ChromaDB successfully")
        
        # List existing collections
        print("\n📋 Existing collections:")
        collections = client.list_collections()
        if collections:
            for col in collections:
                print(f"   - {col.name} (id: {col.id})")
        else:
            print("   No collections found")
        
        # Create or get collection
        collection_name = "rag_documents_collection"
        print(f"\n📚 Creating/getting collection: {collection_name}")
        
        try:
            collection = client.get_collection(collection_name)
            print(f"✅ Collection '{collection_name}' already exists")
        except:
            collection = client.create_collection(
                name=collection_name,
                metadata={"description": "RAG documents for AI system", "created": datetime.now().isoformat()}
            )
            print(f"✅ Collection '{collection_name}' created successfully")
        
        # Check if collection has documents
        count = collection.count()
        print(f"📊 Collection has {count} documents")
        
        if count == 0:
            # Add sample documents
            print(f"\n📄 Adding sample documents...")
            sample_docs = [
                "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed.",
                "Docker is a containerization platform that packages applications and their dependencies into lightweight, portable containers.",
                "Python is a high-level programming language known for its simplicity, readability, and extensive library ecosystem.",
                "Vector databases store and retrieve data using vector embeddings for similarity search and machine learning applications.",
                "Natural language processing (NLP) is a field of artificial intelligence that focuses on enabling computers to understand and process human language.",
                "ChromaDB is an open-source vector database designed for storing and querying embeddings for AI applications.",
                "Retrieval Augmented Generation (RAG) combines information retrieval with text generation to provide more accurate and contextual responses.",
                "Embeddings are dense vector representations of text that capture semantic meaning and enable similarity comparisons."
            ]
            
            collection.add(
                documents=sample_docs,
                metadatas=[{"source": f"sample_{i}", "type": "knowledge", "created": datetime.now().isoformat()} for i in range(len(sample_docs))],
                ids=[f"sample_doc_{i}" for i in range(len(sample_docs))]
            )
            
            print(f"✅ Added {len(sample_docs)} sample documents")
            
            # Test query
            print(f"\n🔍 Testing query functionality...")
            results = collection.query(
                query_texts=["What is machine learning?"],
                n_results=3
            )
            
            if results['documents'] and results['documents'][0]:
                print("✅ Query test successful!")
                print(f"   Found {len(results['documents'][0])} relevant documents:")
                for i, doc in enumerate(results['documents'][0]):
                    print(f"   {i+1}. {doc[:100]}...")
            else:
                print("❌ Query test failed - no results returned")
        else:
            print(f"✅ Collection already has {count} documents")
            
            # Test query on existing data
            print(f"\n🔍 Testing query on existing data...")
            results = collection.query(
                query_texts=["What is machine learning?"],
                n_results=3
            )
            
            if results['documents'] and results['documents'][0]:
                print("✅ Query test successful!")
                print(f"   Found {len(results['documents'][0])} relevant documents")
            else:
                print("❌ Query test failed - no results returned")
        
        # Final status
        final_count = collection.count()
        print(f"\n📊 Final Status:")
        print(f"   Collection: {collection_name}")
        print(f"   Documents: {final_count}")
        print(f"   Status: ✅ Ready for RAG queries")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing ChromaDB: {e}")
        return False

if __name__ == "__main__":
    success = init_chromadb_collections()
    if success:
        print("\n🎉 ChromaDB initialization complete!")
    else:
        print("\n❌ ChromaDB initialization failed!")