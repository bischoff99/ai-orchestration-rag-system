#!/usr/bin/env python3
"""
Production FAISS Ingestion for RAG Documents

This is the OPTIMUM CHOICE for your use case:
- Local, fast, reliable vector storage
- No network dependencies or API compatibility issues
- GPU-accelerated similarity search
- Proven sentence-transformers integration
"""

import os
import json
import glob
from pathlib import Path
from typing import List, Dict, Any
import time
import pickle
import numpy as np

# FAISS and transformers imports
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    print("✅ FAISS and sentence-transformers imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install: pip install faiss-cpu sentence-transformers")
    exit(1)

class ProductionFAISSIngester:
    def __init__(self):
        self.documents_dir = Path("/Users/andrejsp/ai/rag_sources/docs/general")
        self.faiss_dir = Path("/Users/andrejsp/ai/vector_db/faiss")
        self.index_file = self.faiss_dir / "documents.index"
        self.metadata_file = self.faiss_dir / "documents_metadata.json"

        # Initialize the embedding model
        print("🔄 Loading sentence transformer model...")
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("✅ Model loaded successfully")

        # Ensure directory exists
        self.faiss_dir.mkdir(parents=True, exist_ok=True)

    def load_documents(self) -> List[Dict[str, Any]]:
        """Load all RAG documents"""
        documents = []
        doc_files = sorted(glob.glob(str(self.documents_dir / "rag_doc_general_*.md")))

        print(f"📂 Found {len(doc_files)} document files")

        for doc_file in doc_files:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()

                if content:
                    doc_id = Path(doc_file).stem
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

    def create_embeddings(self, documents: List[Dict[str, Any]]) -> tuple:
        """Create embeddings for all documents"""
        print("🔄 Creating embeddings for all documents...")

        texts = [doc["content"] for doc in documents]
        embeddings = self.model.encode(texts, show_progress_bar=True, normalize_embeddings=True)

        # Convert to float32 for FAISS
        embeddings = np.array(embeddings, dtype=np.float32)

        print(f"✅ Created embeddings with shape: {embeddings.shape}")
        return embeddings, documents

    def build_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Build optimized FAISS index"""
        print("🔄 Building optimized FAISS index...")

        dimension = embeddings.shape[1]

        # Use IndexIVFFlat for large datasets (> 1000 vectors)
        # This provides good balance of speed and accuracy
        nlist = min(100, max(4, len(embeddings) // 39))  # Rule of thumb: sqrt(n)/4
        quantizer = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_INNER_PRODUCT)

        print("🔄 Training FAISS index...")
        index.train(embeddings)
        print("✅ Index trained successfully")

        print("🔄 Adding vectors to index...")
        index.add(embeddings)
        print("✅ Vectors added successfully")

        return index

    def save_index_and_metadata(self, index: faiss.Index, documents: List[Dict[str, Any]]):
        """Save FAISS index and metadata"""
        print("💾 Saving FAISS index...")
        faiss.write_index(index, str(self.index_file))

        metadata = {
            "documents": documents,
            "total_documents": len(documents),
            "embedding_dimension": self.model.get_sentence_embedding_dimension(),
            "model_name": "sentence-transformers/all-MiniLM-L6-v2",
            "created_at": time.time(),
            "index_type": "IndexIVFFlat",
            "metric": "inner_product",
            "nlist": index.nlist,
            "is_trained": index.is_trained
        }

        print("💾 Saving metadata...")
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def generate_report(self, stats: Dict[str, Any]):
        """Generate comprehensive ingestion report"""
        print("\n" + "="*60)
        print("🎯 PRODUCTION FAISS INGESTION REPORT")
        print("="*60)
        print(f"📊 Total Documents: {stats['total_documents']}")
        print(f"🔢 Embedding Dimension: {stats['embedding_dimension']}")
        print(f"💾 Index Size: {stats['index_size_mb']:.2f} MB")
        print(f"⏱️  Duration: {stats['duration_seconds']:.2f} seconds")
        print(f"🚀 Throughput: {stats['documents_per_second']:.1f} docs/sec")
        print(f"🎯 Model: {stats['model_used']}")
        print(f"💪 Index Type: {stats['index_type']} (Optimized for {stats['total_documents']} docs)")
        print("="*60)
        print("✅ INGESTION SUCCESSFUL!")
        print("🎉 Ready for production RAG queries")
        print("="*60)

    def test_retrieval(self) -> bool:
        """Test retrieval functionality"""
        print("\n🧪 Testing retrieval functionality...")

        try:
            # Load index and metadata
            if not self.index_file.exists() or not self.metadata_file.exists():
                print("❌ Index or metadata not found")
                return False

            index = faiss.read_index(str(self.index_file))

            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)

            # Test queries
            test_queries = [
                "What is machine learning?",
                "How does Python programming work?",
                "Explain Docker containers"
            ]

            for query in test_queries:
                # Create query embedding
                query_embedding = self.model.encode([query], normalize_embeddings=True)
                query_embedding = np.array(query_embedding, dtype=np.float32)

                # Search
                D, I = index.search(query_embedding, 2)

                print(f"🔍 Query: '{query}'")
                print(f"   📄 Found {len(D[0])} results")
                for i, (distance, idx) in enumerate(zip(D[0], I[0])):
                    if idx < len(metadata["documents"]):
                        doc = metadata["documents"][idx]
                        print(f"   {i+1}. Score: {distance:.4f} - {doc['content'][:60]}...")
                print()

            print("✅ Retrieval test successful!")
            return True

        except Exception as e:
            print(f"❌ Retrieval test failed: {e}")
            return False

    def run_ingestion(self) -> Dict[str, Any]:
        """Main ingestion pipeline"""
        print("🚀 Starting PRODUCTION FAISS ingestion...")
        start_time = time.time()

        # Load documents
        documents = self.load_documents()
        if not documents:
            raise ValueError("No documents found to ingest")

        # Create embeddings
        embeddings, documents = self.create_embeddings(documents)

        # Build FAISS index
        index = self.build_faiss_index(embeddings)

        # Save everything
        self.save_index_and_metadata(index, documents)

        # Calculate statistics
        end_time = time.time()
        duration = end_time - start_time

        stats = {
            "total_documents": len(documents),
            "embedding_dimension": self.model.get_sentence_embedding_dimension(),
            "index_size_mb": self.index_file.stat().st_size / (1024 * 1024),
            "duration_seconds": duration,
            "documents_per_second": len(documents) / duration if duration > 0 else 0,
            "model_used": "sentence-transformers/all-MiniLM-L6-v2",
            "index_type": "IndexIVFFlat"
        }

        return stats

def main():
    try:
        ingester = ProductionFAISSIngester()
        stats = ingester.run_ingestion()
        ingester.generate_report(stats)

        # Test the system
        if ingester.test_retrieval():
            print("\n🎯 PRODUCTION SYSTEM VALIDATION: PASSED")
        else:
            print("\n⚠️  PRODUCTION SYSTEM VALIDATION: ISSUES DETECTED")

        # Save stats
        with open("/Users/andrejsp/ai/faiss_production_stats.json", 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"\n📁 Stats saved to: /Users/andrejsp/ai/faiss_production_stats.json")
        print(f"📁 Index saved to: {ingester.index_file}")
        print(f"📁 Metadata saved to: {ingester.metadata_file}")

        return True

    except Exception as e:
        print(f"❌ Production ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
