#!/usr/bin/env python3
"""
Unified RAG System
Complete RAG implementation with proper collection management
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
import chromadb
import faiss
from sentence_transformers import SentenceTransformer
import requests

class UnifiedRAG:
    """Unified RAG system with proper collection management"""

    def __init__(self, backend: str = "chroma", collection_name: str = "unified_docs"):
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

        # Get or create collection (don't delete existing)
        try:
            self.collection = self.client.get_collection(self.collection_name)
            print(f"✅ ChromaDB connected to existing collection: {self.collection_name}")
        except:
            # Create new collection only if it doesn't exist
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"✅ ChromaDB created new collection: {self.collection_name}")

    def _init_faiss(self):
        """Initialize FAISS"""
        self.index_path = f"/Users/andrejsp/ai/vector_db/faiss/{self.collection_name}.index"
        self.metadata_path = f"/Users/andrejsp/ai/vector_db/faiss/{self.collection_name}_metadata.json"

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        # Reset FAISS index
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.metadata_path):
            os.remove(self.metadata_path)

        self.index = None
        self.metadata = []
        print(f"✅ FAISS initialized with collection: {self.collection_name}")

    def add_documents(self, documents, metadatas: Optional[List[Dict]] = None):
        """Add documents to vector database"""
        print(f"📄 Adding {len(documents)} documents to {self.backend}")

        # Handle Document objects from LangChain
        if documents and hasattr(documents[0], 'page_content'):
            # Extract text content from Document objects
            texts = [doc.page_content for doc in documents]
            if metadatas is None:
                metadatas = [doc.metadata for doc in documents]
        else:
            # Assume documents are already strings
            texts = documents
            if metadatas is None:
                metadatas = [{"doc_id": i} for i in range(len(documents))]

        # Generate embeddings
        embeddings = self.embedding_model.encode(texts)

        if self.backend == "chroma":
            self._add_to_chroma(texts, embeddings, metadatas)
        elif self.backend == "faiss":
            self._add_to_faiss(texts, embeddings, metadatas)

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

    def query_ollama(self, question: str, k: int = 3) -> Dict[str, Any]:
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
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama-assistant",
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

def main():
    """Test the unified RAG system"""
    print("🚀 Unified RAG System Test")
    print("=" * 35)

    # Create directories
    os.makedirs("/Users/andrejsp/ai/vector_db", exist_ok=True)
    os.makedirs("/Users/andrejsp/ai/vector_db/chroma", exist_ok=True)
    os.makedirs("/Users/andrejsp/ai/vector_db/faiss", exist_ok=True)

    # Test ChromaDB
    print("\n🔧 Testing ChromaDB")
    print("=" * 25)

    try:
        # Initialize RAG
        rag = UnifiedRAG(backend="chroma")

        # Sample documents
        documents = [
            "Python is a high-level programming language known for its simplicity and readability. Best practices include following PEP 8 style guide, using meaningful variable names, writing docstrings, and using virtual environments.",

            "Machine learning is a subset of artificial intelligence. Common types include supervised learning (classification, regression), unsupervised learning (clustering), and reinforcement learning. Popular Python libraries include scikit-learn, TensorFlow, and PyTorch.",

            "Docker is a containerization platform that packages applications and dependencies into containers. Key concepts include Dockerfile, Docker images, and Docker containers. It ensures consistency across different environments."
        ]

        metadatas = [
            {"title": "Python Best Practices", "category": "programming"},
            {"title": "Machine Learning Guide", "category": "ai"},
            {"title": "Docker Basics", "category": "devops"}
        ]

        # Add documents
        rag.add_documents(documents, metadatas)

        # Test search
        results = rag.search("What are Python best practices?", k=3)
        print(f"✅ Search results:")
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result['text'][:80]}... (score: {result['distance']:.3f})")

        # Test RAG query
        response = rag.query_ollama("What are the best practices for Python programming?")
        print(f"\n🤖 RAG Response:")
        print(f"{response['answer']}")

        print(f"\n📚 Sources:")
        for i, source in enumerate(response['sources'], 1):
            print(f"  {i}. {source.get('title', 'Unknown')}")

    except Exception as e:
        print(f"❌ ChromaDB error: {e}")

    print(f"\n🎉 Unified RAG Test Complete!")

if __name__ == "__main__":
    main()
