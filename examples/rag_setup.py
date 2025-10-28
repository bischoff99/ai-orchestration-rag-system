#!/usr/bin/env python3
"""
RAG Vector Database Setup with Desktop Commander
Complete setup for ChromaDB, FAISS, and Qdrant
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
import chromadb
import faiss
from sentence_transformers import SentenceTransformer
import requests

class RAGVectorDB:
    """Unified RAG Vector Database"""
    
    def __init__(self, backend: str = "chroma", collection_name: str = "documents"):
        self.backend = backend
        self.collection_name = collection_name
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize backend
        if backend == "chroma":
            self._init_chroma()
        elif backend == "faiss":
            self._init_faiss()
        else:
            raise ValueError(f"Unsupported backend: {backend}")
    
    def _init_chroma(self):
        """Initialize ChromaDB"""
        self.client = chromadb.PersistentClient(path="/Users/andrejsp/ai/vector_db/chroma")
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        print("✅ ChromaDB initialized")
    
    def _init_faiss(self):
        """Initialize FAISS"""
        self.index_path = f"/Users/andrejsp/ai/vector_db/faiss/{self.collection_name}.index"
        self.metadata_path = f"/Users/andrejsp/ai/vector_db/faiss/{self.collection_name}_metadata.json"
        
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.index = None
            self.metadata = []
        
        print("✅ FAISS initialized")
    
    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None):
        """Add documents to vector database"""
        print(f"📄 Adding {len(documents)} documents to {self.backend}")
        
        if metadatas is None:
            metadatas = [{"doc_id": i} for i in range(len(documents))]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents)
        
        if self.backend == "chroma":
            self._add_to_chroma(documents, embeddings, metadatas)
        elif self.backend == "faiss":
            self._add_to_faiss(documents, embeddings, metadatas)
        
        print(f"✅ Added documents successfully")
    
    def _add_to_chroma(self, documents: List[str], embeddings: np.ndarray, metadatas: List[Dict]):
        """Add to ChromaDB"""
        ids = [f"doc_{i}" for i in range(len(documents))]
        
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def _add_to_faiss(self, documents: List[str], embeddings: np.ndarray, metadatas: List[Dict]):
        """Add to FAISS"""
        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        
        # Update metadata
        for i, (doc, meta) in enumerate(zip(documents, metadatas)):
            meta['text'] = doc
            self.metadata.append(meta)
        
        # Save
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        print(f"🔍 Searching: '{query[:50]}...'")
        
        query_embedding = self.embedding_model.encode([query])
        
        if self.backend == "chroma":
            return self._search_chroma(query_embedding, k)
        elif self.backend == "faiss":
            return self._search_faiss(query_embedding, k)
    
    def _search_chroma(self, query_embedding: np.ndarray, k: int) -> List[Dict[str, Any]]:
        """Search ChromaDB"""
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
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
    
    def _search_faiss(self, query_embedding: np.ndarray, k: int) -> List[Dict[str, Any]]:
        """Search FAISS"""
        faiss.normalize_L2(query_embedding)
        distances, indices = self.index.search(query_embedding, k)
        
        search_results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                search_results.append({
                    'text': self.metadata[idx].get('text', ''),
                    'metadata': {k: v for k, v in self.metadata[idx].items() if k != 'text'},
                    'distance': float(distance)
                })
        
        return search_results

class RAGPipeline:
    """RAG Pipeline with Ollama integration"""
    
    def __init__(self, vector_db: RAGVectorDB, ollama_model: str = "llama-assistant"):
        self.vector_db = vector_db
        self.ollama_model = ollama_model
        self.ollama_url = "http://localhost:11434/api/generate"
    
    def query(self, question: str, k: int = 3) -> Dict[str, Any]:
        """Query the RAG system"""
        print(f"🤖 RAG Query: {question}")
        
        # Retrieve relevant documents
        search_results = self.vector_db.search(question, k=k)
        
        # Prepare context
        context = "\n\n".join([result['text'] for result in search_results])
        
        # Create prompt
        prompt = f"""Based on the following context, answer the question. If the answer is not in the context, say so.

Context:
{context}

Question: {question}

Answer:"""
        
        # Query Ollama
        response = self._query_ollama(prompt)
        
        return {
            'answer': response,
            'sources': [result['metadata'] for result in search_results],
            'context_used': context
        }
    
    def _query_ollama(self, prompt: str) -> str:
        """Query Ollama model"""
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            return f"Error querying Ollama: {e}"

def create_sample_data():
    """Create sample documents for testing"""
    documents = [
        "Python is a high-level programming language known for its simplicity and readability. It's widely used in web development, data science, machine learning, and AI applications.",
        
        "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed. It includes supervised learning, unsupervised learning, and reinforcement learning.",
        
        "Docker is a containerization platform that allows you to package applications and their dependencies into lightweight, portable containers. It ensures consistency across different environments.",
        
        "Vector databases are specialized databases designed to store and query high-dimensional vectors efficiently. They're essential for RAG (Retrieval-Augmented Generation) systems and semantic search.",
        
        "Ollama is a tool that makes it easy to run large language models locally on your machine. It supports many open-source models and provides a simple API for integration."
    ]
    
    metadatas = [
        {"title": "Python Programming", "category": "programming", "language": "python"},
        {"title": "Machine Learning", "category": "ai", "language": "python"},
        {"title": "Docker", "category": "devops", "language": "docker"},
        {"title": "Vector Databases", "category": "database", "language": "general"},
        {"title": "Ollama", "category": "llm", "language": "general"}
    ]
    
    return documents, metadatas

def main():
    """Main RAG setup and testing"""
    print("🚀 RAG Vector Database Setup")
    print("=" * 40)
    
    # Create directories
    os.makedirs("/Users/andrejsp/ai/vector_db", exist_ok=True)
    os.makedirs("/Users/andrejsp/ai/vector_db/chroma", exist_ok=True)
    os.makedirs("/Users/andrejsp/ai/vector_db/faiss", exist_ok=True)
    
    # Test ChromaDB
    print("\n🔧 Testing ChromaDB")
    print("=" * 25)
    
    try:
        # Initialize ChromaDB
        vector_db = RAGVectorDB(backend="chroma")
        
        # Create sample data
        documents, metadatas = create_sample_data()
        
        # Add documents
        vector_db.add_documents(documents, metadatas)
        
        # Test search
        results = vector_db.search("What is Python used for?", k=3)
        print(f"✅ ChromaDB search results:")
        for i, result in enumerate(results):
            print(f"   {i+1}. {result['text'][:80]}... (score: {result['distance']:.3f})")
        
        # Test RAG pipeline
        rag = RAGPipeline(vector_db, "llama-assistant")
        response = rag.query("What are the main uses of Python?")
        print(f"\n🤖 RAG Response: {response['answer'][:200]}...")
        
    except Exception as e:
        print(f"❌ ChromaDB error: {e}")
    
    # Test FAISS
    print("\n🔧 Testing FAISS")
    print("=" * 20)
    
    try:
        # Initialize FAISS
        vector_db_faiss = RAGVectorDB(backend="faiss")
        
        # Add documents
        vector_db_faiss.add_documents(documents, metadatas)
        
        # Test search
        results = vector_db_faiss.search("What is machine learning?", k=3)
        print(f"✅ FAISS search results:")
        for i, result in enumerate(results):
            print(f"   {i+1}. {result['text'][:80]}... (score: {result['distance']:.3f})")
        
    except Exception as e:
        print(f"❌ FAISS error: {e}")
    
    print(f"\n🎉 RAG Setup Complete!")
    print(f"\n📋 Available Backends:")
    print(f"   - ChromaDB: Easy to use, persistent storage")
    print(f"   - FAISS: Fast, memory-efficient")
    
    print(f"\n💡 Next Steps:")
    print(f"1. 🏃 Run: python /Users/andrejsp/ai/examples/rag_setup.py")
    print(f"2. 📚 Add your own documents")
    print(f"3. 🔍 Test with different queries")
    print(f"4. 🚀 Integrate with your applications")

if __name__ == "__main__":
    main()