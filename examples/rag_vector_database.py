#!/usr/bin/env python3
"""
RAG Vector Database Setup
Multiple vector database options with Ollama integration
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
import chromadb
import faiss
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, DirectoryLoader
import requests

class RAGVectorDatabase:
    """Unified RAG Vector Database with multiple backends"""
    
    def __init__(self, backend: str = "chroma", collection_name: str = "documents"):
        self.backend = backend
        self.collection_name = collection_name
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        # Initialize backend
        if backend == "chroma":
            self._init_chroma()
        elif backend == "faiss":
            self._init_faiss()
        elif backend == "qdrant":
            self._init_qdrant()
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
        
        # Load existing index or create new one
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
        else:
            # Create new index (dimension will be set when first document is added)
            self.index = None
            self.metadata = []
        
        print("✅ FAISS initialized")
    
    def _init_qdrant(self):
        """Initialize Qdrant"""
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams
        
        self.client = QdrantClient(path="/Users/andrejsp/ai/vector_db/qdrant")
        
        # Create collection
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
        except Exception:
            pass  # Collection already exists
        
        print("✅ Qdrant initialized")
    
    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None):
        """Add documents to the vector database"""
        print(f"📄 Adding {len(documents)} documents to {self.backend}")
        
        # Split documents into chunks
        chunks = []
        chunk_metadatas = []
        
        for i, doc in enumerate(documents):
            doc_chunks = self.text_splitter.split_text(doc)
            chunks.extend(doc_chunks)
            
            # Create metadata for each chunk
            doc_metadata = metadatas[i] if metadatas else {}
            for j, chunk in enumerate(doc_chunks):
                chunk_metadata = {
                    **doc_metadata,
                    "chunk_id": f"{i}_{j}",
                    "doc_id": i,
                    "chunk_index": j
                }
                chunk_metadatas.append(chunk_metadata)
        
        # Generate embeddings
        print("🔄 Generating embeddings...")
        embeddings = self.embedding_model.encode(chunks)
        
        # Add to vector database
        if self.backend == "chroma":
            self._add_to_chroma(chunks, embeddings, chunk_metadatas)
        elif self.backend == "faiss":
            self._add_to_faiss(chunks, embeddings, chunk_metadatas)
        elif self.backend == "qdrant":
            self._add_to_qdrant(chunks, embeddings, chunk_metadatas)
        
        print(f"✅ Added {len(chunks)} chunks to vector database")
    
    def _add_to_chroma(self, chunks: List[str], embeddings: np.ndarray, metadatas: List[Dict]):
        """Add to ChromaDB"""
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
    
    def _add_to_faiss(self, chunks: List[str], embeddings: np.ndarray, metadatas: List[Dict]):
        """Add to FAISS"""
        if self.index is None:
            # Create new index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        
        # Update metadata
        self.metadata.extend(metadatas)
        
        # Save
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _add_to_qdrant(self, chunks: List[str], embeddings: np.ndarray, metadatas: List[Dict]):
        """Add to Qdrant"""
        from qdrant_client.models import PointStruct
        
        points = []
        for i, (chunk, embedding, metadata) in enumerate(zip(chunks, embeddings, metadatas)):
            point = PointStruct(
                id=i,
                vector=embedding.tolist(),
                payload={
                    "text": chunk,
                    **metadata
                }
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        print(f"🔍 Searching for: '{query[:50]}...'")
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        
        if self.backend == "chroma":
            return self._search_chroma(query_embedding, k)
        elif self.backend == "faiss":
            return self._search_faiss(query_embedding, k)
        elif self.backend == "qdrant":
            return self._search_qdrant(query_embedding, k)
    
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
        # Normalize query embedding
        faiss.normalize_L2(query_embedding)
        
        # Search
        distances, indices = self.index.search(query_embedding, k)
        
        search_results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.metadata):
                search_results.append({
                    'text': self.metadata[idx].get('text', ''),
                    'metadata': {k: v for k, v in self.metadata[idx].items() if k != 'text'},
                    'distance': float(distance)
                })
        
        return search_results
    
    def _search_qdrant(self, query_embedding: np.ndarray, k: int) -> List[Dict[str, Any]]:
        """Search Qdrant"""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding[0].tolist(),
            limit=k
        )
        
        search_results = []
        for result in results:
            search_results.append({
                'text': result.payload['text'],
                'metadata': {k: v for k, v in result.payload.items() if k != 'text'},
                'distance': result.score
            })
        
        return search_results

class RAGPipeline:
    """Complete RAG pipeline with Ollama integration"""
    
    def __init__(self, vector_db: RAGVectorDatabase, ollama_model: str = "llama-assistant"):
        self.vector_db = vector_db
        self.ollama_model = ollama_model
        self.ollama_url = "http://localhost:11434/api/generate"
    
    def query(self, question: str, k: int = 3) -> str:
        """Query the RAG system"""
        print(f"🤖 RAG Query: {question}")
        
        # 1. Retrieve relevant documents
        search_results = self.vector_db.search(question, k=k)
        
        # 2. Prepare context
        context = "\n\n".join([result['text'] for result in search_results])
        
        # 3. Create prompt
        prompt = f"""Based on the following context, answer the question. If the answer is not in the context, say so.

Context:
{context}

Question: {question}

Answer:"""
        
        # 4. Query Ollama
        response = self._query_ollama(prompt)
        
        # 5. Return response with sources
        sources = [result['metadata'] for result in search_results]
        return {
            'answer': response,
            'sources': sources,
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

def create_sample_documents():
    """Create sample documents for testing"""
    print("📚 Creating Sample Documents")
    print("=" * 30)
    
    documents = [
        """
        Python Programming Best Practices
        
        Python is a versatile programming language known for its simplicity and readability. Here are some best practices:
        
        1. Use meaningful variable names: Instead of 'x' or 'temp', use descriptive names like 'user_count' or 'file_path'.
        2. Follow PEP 8 style guide: Use 4 spaces for indentation, limit lines to 79 characters.
        3. Use list comprehensions: They are more Pythonic and often faster than loops.
        4. Handle exceptions properly: Use try-except blocks to handle potential errors.
        5. Use virtual environments: Isolate project dependencies using venv or conda.
        
        Example of good Python code:
        def calculate_fibonacci(n):
            if n <= 1:
                return n
            return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
        """,
        
        """
        Machine Learning with Scikit-learn
        
        Scikit-learn is a powerful machine learning library for Python. Here's how to get started:
        
        1. Data Preprocessing: Use StandardScaler for feature scaling, LabelEncoder for categorical variables.
        2. Model Selection: Try different algorithms like RandomForest, SVM, or Neural Networks.
        3. Cross-validation: Use cross_val_score to evaluate model performance.
        4. Hyperparameter Tuning: Use GridSearchCV or RandomizedSearchCV.
        
        Example workflow:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        model = RandomForestClassifier(n_estimators=100)
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        """,
        
        """
        Docker Containerization Guide
        
        Docker allows you to package applications and their dependencies into containers. Key concepts:
        
        1. Dockerfile: Instructions to build a Docker image
        2. Docker Image: A read-only template for creating containers
        3. Docker Container: A running instance of an image
        4. Docker Compose: Tool for defining multi-container applications
        
        Basic Dockerfile example:
        FROM python:3.9-slim
        WORKDIR /app
        COPY requirements.txt .
        RUN pip install -r requirements.txt
        COPY . .
        EXPOSE 8000
        CMD ["python", "app.py"]
        
        Commands:
        - docker build -t myapp .
        - docker run -p 8000:8000 myapp
        - docker-compose up
        """
    ]
    
    metadatas = [
        {"title": "Python Best Practices", "category": "programming", "language": "python"},
        {"title": "Machine Learning Guide", "category": "ml", "language": "python"},
        {"title": "Docker Guide", "category": "devops", "language": "docker"}
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
    os.makedirs("/Users/andrejsp/ai/vector_db/qdrant", exist_ok=True)
    
    # Test different backends
    backends = ["chroma", "faiss", "qdrant"]
    
    for backend in backends:
        print(f"\n🔧 Testing {backend.upper()} backend")
        print("=" * 30)
        
        try:
            # Initialize vector database
            vector_db = RAGVectorDatabase(backend=backend)
            
            # Create sample documents
            documents, metadatas = create_sample_documents()
            
            # Add documents
            vector_db.add_documents(documents, metadatas)
            
            # Test search
            results = vector_db.search("How do I use Python list comprehensions?", k=2)
            print(f"✅ {backend} search results:")
            for i, result in enumerate(results):
                print(f"   {i+1}. {result['text'][:100]}... (score: {result['distance']:.3f})")
            
            # Test RAG pipeline
            rag = RAGPipeline(vector_db, "llama-assistant")
            response = rag.query("What are the best practices for Python programming?")
            print(f"🤖 RAG Response: {response['answer'][:200]}...")
            
        except Exception as e:
            print(f"❌ Error with {backend}: {e}")
    
    print(f"\n🎉 RAG Setup Complete!")
    print(f"\n📋 Available Backends:")
    print(f"   - ChromaDB: Persistent, easy to use")
    print(f"   - FAISS: Fast, memory-efficient")
    print(f"   - Qdrant: Advanced features, good for production")
    
    print(f"\n💡 Next Steps:")
    print(f"1. 🏃 Run: python /Users/andrejsp/ai/examples/rag_vector_database.py")
    print(f"2. 📚 Add your own documents")
    print(f"3. 🔍 Test queries with different models")
    print(f"4. 🚀 Deploy to production")

if __name__ == "__main__":
    main()
