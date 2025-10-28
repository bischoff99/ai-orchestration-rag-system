#!/usr/bin/env python3
import sys
sys.path.append('/Users/andrejsp/ai/examples')
from unified_rag import UnifiedRAG

def test_rag():
    print("🧪 Testing RAG System")
    print("=" * 25)
    
    # Initialize RAG
    rag = UnifiedRAG(backend="chroma")
    
    # Test documents
    documents = [
        "Python is a programming language known for its simplicity and readability.",
        "Machine learning enables computers to learn from data without explicit programming.",
        "Docker containers package applications with their dependencies for easy deployment."
    ]
    
    metadatas = [
        {"title": "Python", "category": "programming"},
        {"title": "Machine Learning", "category": "ai"},
        {"title": "Docker", "category": "devops"}
    ]
    
    # Add documents
    rag.add_documents(documents, metadatas)
    
    # Test queries
    queries = [
        "What is Python?",
        "How does machine learning work?",
        "What is Docker used for?"
    ]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        response = rag.query_ollama(query)
        print(f"🤖 Answer: {response['answer']}")
        print(f"📚 Sources: {len(response['sources'])} documents")

if __name__ == "__main__":
    test_rag()
