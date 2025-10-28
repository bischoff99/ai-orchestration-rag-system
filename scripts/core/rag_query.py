#!/usr/bin/env python3
"""
RAG Query Interface
Interactive query interface for RAG system
"""

import os
import sys
import json
import argparse
from typing import Dict, Any

# Add the examples directory to path
sys.path.append('/Users/andrejsp/ai/examples')

from rag_setup import RAGVectorDB, RAGPipeline

def load_config(config_path: str = "/Users/andrejsp/ai/configs/rag_config.json") -> Dict[str, Any]:
    """Load RAG configuration"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return {}

def interactive_query(rag_pipeline: RAGPipeline):
    """Interactive query interface"""
    print("\n🤖 RAG Query Interface")
    print("=" * 30)
    print("Type 'quit' or 'exit' to stop")
    print("Type 'help' for commands")
    
    while True:
        try:
            query = input("\n❓ Your question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if query.lower() == 'help':
                print("\n📋 Available commands:")
                print("  - Ask any question about your documents")
                print("  - 'quit' or 'exit' to stop")
                print("  - 'help' to show this message")
                continue
            
            if not query:
                continue
            
            # Query RAG system
            response = rag_pipeline.query(query)
            
            print(f"\n🤖 Answer:")
            print(f"{response['answer']}")
            
            print(f"\n📚 Sources:")
            for i, source in enumerate(response['sources'], 1):
                print(f"  {i}. {source.get('file_name', 'Unknown')} (chunk {source.get('chunk_index', 'N/A')})")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def single_query(rag_pipeline: RAGPipeline, question: str):
    """Single query mode"""
    print(f"❓ Question: {question}")
    
    response = rag_pipeline.query(question)
    
    print(f"\n🤖 Answer:")
    print(f"{response['answer']}")
    
    print(f"\n📚 Sources:")
    for i, source in enumerate(response['sources'], 1):
        print(f"  {i}. {source.get('file_name', 'Unknown')} (chunk {source.get('chunk_index', 'N/A')})")

def list_collections(backend: str):
    """List available collections"""
    if backend == "chroma":
        try:
            vector_db = RAGVectorDB(backend=backend)
            collections = vector_db.client.list_collections()
            print(f"📚 Available collections in {backend}:")
            for collection in collections:
                print(f"  - {collection.name}")
        except Exception as e:
            print(f"❌ Error listing collections: {e}")
    else:
        print(f"❌ Collection listing not supported for {backend}")

def search_only(backend: str, collection: str, query: str, k: int = 5):
    """Search without RAG (just vector search)"""
    try:
        vector_db = RAGVectorDB(backend=backend, collection_name=collection)
        results = vector_db.search(query, k=k)
        
        print(f"🔍 Search results for: '{query}'")
        print("=" * 40)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Score: {result['distance']:.3f}")
            print(f"   Text: {result['text'][:200]}...")
            print(f"   Metadata: {result['metadata']}")
    
    except Exception as e:
        print(f"❌ Search error: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Query RAG vector database")
    parser.add_argument("--backend", choices=["chroma", "faiss"], default="chroma", help="Vector database backend")
    parser.add_argument("--collection", default="documents", help="Collection name")
    parser.add_argument("--model", default="llama-assistant", help="Ollama model to use")
    parser.add_argument("--query", help="Single query (non-interactive mode)")
    parser.add_argument("--search-only", action="store_true", help="Only do vector search, no RAG")
    parser.add_argument("--k", type=int, default=5, help="Number of results to return")
    parser.add_argument("--list-collections", action="store_true", help="List available collections")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    if args.list_collections:
        list_collections(args.backend)
        return
    
    try:
        # Initialize RAG pipeline
        vector_db = RAGVectorDB(backend=args.backend, collection_name=args.collection)
        rag_pipeline = RAGPipeline(vector_db, args.model)
        
        if args.search_only:
            if not args.query:
                print("❌ --query is required for search-only mode")
                return
            search_only(args.backend, args.collection, args.query, args.k)
        elif args.query:
            single_query(rag_pipeline, args.query)
        else:
            interactive_query(rag_pipeline)
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()