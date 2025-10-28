#!/usr/bin/env python3
"""
FAISS Ingestion Script for RAG Documents

Fallback script using FAISS instead of ChromaDB for document ingestion.
"""

import os
import json
import glob
import pickle
from pathlib import Path
from typing import List, Dict, Any
import time
import numpy as np

# Import FAISS and sentence transformers
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    print("✅ FAISS and transformers imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Installing required packages...")
    import subprocess
    subprocess.run(["pip", "install", "faiss-cpu", "sentence-transformers"], check=True)
    import faiss
    from sentence_transformers import SentenceTransformer

class FAISSIngester:
    def __init__(self, faiss_path: str = "/Users/andrejsp/ai/vector_db/faiss"):
        self.faiss_path = Path(faiss_path)
        self.documents_dir = Path("/Users/andrejsp/ai/rag_sources/docs/general")
        self.index_file = self.faiss_path / "documents.index"
        self.metadata_file = self.faiss_path / "documents_metadata.json"

        # Initialize the embedding model
        print("🔄 Loading sentence transformer model...")
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("✅ Model loaded successfully")

        # Ensure directory exists
        self.faiss_path.mkdir(parents=True, exist_ok=True)

    def _load_documents(self) -> List[Dict[str, Any]]:
        """Load all RAG documents from the general directory"""
        documents = []
        doc_files = sorted(glob.glob(str(self.documents_dir / "rag_doc_general_*.md")))

        print(f"📂 Found {len(doc_files)} document files")

        for doc_file in doc_files:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()

                if content:
                    # Create document ID from filename
                    doc_id = Path(doc_file).stem

                    # Create metadata
                    metadata = {
                        "source": "synthetic_training_data",
                        "domain": "general",
                        "filename": doc_id,
                        "word_count": len(content.split()),
                        "has_code": "```" in content
                    }

                    documents.append({
                        "id": doc_id,
                        "content": content,
                        "metadata": metadata
                    })

            except Exception as e:
                print(f"⚠️  Error loading {doc_file}: {e}")

        print(f"✅ Loaded {len(documents)} documents successfully")
        return documents

    def _create_embeddings(self, documents: List[Dict[str, Any]]) -> tuple:
        """Create embeddings for all documents"""
        print("🔄 Creating embeddings...")

        texts = [doc["content"] for doc in documents]
        embeddings = self.model.encode(texts, show_progress_bar=True)

        # Convert to float32 for FAISS
        embeddings = np.array(embeddings, dtype=np.float32)

        print(f"✅ Created embeddings with shape: {embeddings.shape}")
        return embeddings, documents

    def _build_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Build FAISS index"""
        print("🔄 Building FAISS index...")

        dimension = embeddings.shape[1]

        # Use IndexIVFFlat for better performance with large datasets
        nlist = min(100, max(4, len(embeddings) // 39))  # Rule of thumb: sqrt(n)/4
        quantizer = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
        index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_INNER_PRODUCT)

        # Train the index
        print("🔄 Training FAISS index...")
        index.train(embeddings)
        print("✅ Index trained successfully")

        # Add vectors
        print("🔄 Adding vectors to index...")
        index.add(embeddings)
        print("✅ Vectors added successfully")

        return index

    def ingest_documents(self) -> Dict[str, Any]:
        """Main ingestion process"""
        print("🚀 Starting FAISS ingestion process...")
        start_time = time.time()

        # Load documents
        documents = self._load_documents()

        if not documents:
            raise ValueError("No documents found to ingest")

        # Create embeddings
        embeddings, documents = self._create_embeddings(documents)

        # Build FAISS index
        index = self._build_faiss_index(embeddings)

        # Save index
        print("💾 Saving FAISS index...")
        faiss.write_index(index, str(self.index_file))

        # Save metadata
        metadata = {
            "documents": documents,
            "total_documents": len(documents),
            "embedding_dimension": embeddings.shape[1],
            "model_name": "sentence-transformers/all-MiniLM-L6-v2",
            "created_at": time.time(),
            "index_type": "IndexIVFFlat",
            "metric": "inner_product"
        }

        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Calculate statistics
        end_time = time.time()
        duration = end_time - start_time

        stats = {
            "total_documents": len(documents),
            "embedding_dimension": embeddings.shape[1],
            "index_size_mb": self.index_file.stat().st_size / (1024 * 1024),
            "duration_seconds": duration,
            "documents_per_second": len(documents) / duration if duration > 0 else 0,
            "model_used": "sentence-transformers/all-MiniLM-L6-v2"
        }

        return stats

    def test_retrieval(self, query: str = "What is machine learning?", k: int = 3):
        """Test retrieval functionality"""
        print(f"🧪 Testing retrieval with query: '{query}'")

        # Load index and metadata
        if not self.index_file.exists() or not self.metadata_file.exists():
            print("❌ Index or metadata not found")
            return

        index = faiss.read_index(str(self.index_file))

        with open(self.metadata_file, 'r') as f:
            metadata = json.load(f)

        # Create query embedding
        query_embedding = self.model.encode([query], normalize_embeddings=True)
        query_embedding = np.array(query_embedding, dtype=np.float32)

        # Search
        D, I = index.search(query_embedding, k)

        print(f"📊 Top {k} results:")
        for i, (distance, idx) in enumerate(zip(D[0], I[0])):
            if idx < len(metadata["documents"]):
                doc = metadata["documents"][idx]
                print(f"{i+1}. Score: {distance:.4f}")
                print(f"   ID: {doc['id']}")
                print(f"   Content: {doc['content'][:100]}...")
                print()

    def generate_report(self, stats: Dict[str, Any]):
        """Generate ingestion report"""
        print("\n" + "="*50)
        print("📊 FAISS INGESTION REPORT")
        print("="*50)
        print(f"Total Documents: {stats['total_documents']}")
        print(f"Embedding Dimension: {stats['embedding_dimension']}")
        print(f"Index Size: {stats['index_size_mb']:.2f} MB")
        print(f"Duration: {stats['duration_seconds']:.2f} seconds")
        print(f"Throughput: {stats['documents_per_second']:.1f} docs/sec")
        print(f"Model: {stats['model_used']}")
        print("="*50)
        print("🎉 INGESTION SUCCESSFUL!")
        print("="*50)

def main():
    try:
        ingester = FAISSIngester()
        stats = ingester.ingest_documents()
        ingester.generate_report(stats)

        # Test retrieval
        ingester.test_retrieval()

        # Save stats to file
        with open("/Users/andrejsp/ai/faiss_ingestion_stats.json", 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"\n📁 Stats saved to: /Users/andrejsp/ai/faiss_ingestion_stats.json")
        print(f"📁 Index saved to: {ingester.index_file}")
        print(f"📁 Metadata saved to: {ingester.metadata_file}")

    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
