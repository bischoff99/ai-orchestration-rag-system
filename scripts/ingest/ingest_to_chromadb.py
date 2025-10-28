#!/usr/bin/env python3
"""
ChromaDB Ingestion Script for RAG Documents

This script ingests the 249 RAG documents into ChromaDB v2 for retrieval-augmented generation.
"""

import os
import json
import glob
import requests
import hashlib
from pathlib import Path
from typing import List, Dict, Any
import time

class ChromaDBIngester:
    def __init__(self, chroma_url: str = "http://localhost:8000/api/v2"):
        self.chroma_url = chroma_url
        self.collection_name = "rag_documents_collection"
        self.documents_dir = Path("/Users/andrejsp/ai/rag_sources/docs/general")

        # Verify ChromaDB is running
        self._check_chromadb_health()

    def _check_chromadb_health(self):
        """Verify ChromaDB v2 is accessible"""
        try:
            response = requests.get(f"{self.chroma_url}/heartbeat", timeout=10)
            response.raise_for_status()
            print("✅ ChromaDB v2 is healthy")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"❌ ChromaDB not accessible: {e}")

    def _create_collection(self):
        """Create the collection if it doesn't exist"""
        try:
            # Check if collection exists
            response = requests.get(f"{self.chroma_url}/collections", timeout=10)
            response.raise_for_status()
            collections = response.json()

            collection_exists = any(col.get('name') == self.collection_name for col in collections)

            if not collection_exists:
                # Create collection
                payload = {"name": self.collection_name}
                response = requests.post(f"{self.chroma_url}/collections", json=payload, timeout=10)
                response.raise_for_status()
                print(f"✅ Created collection: {self.collection_name}")
            else:
                print(f"ℹ️  Collection already exists: {self.collection_name}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create/access collection: {e}")

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

    def _chunk_documents(self, documents: List[Dict[str, Any]], chunk_size: int = 1000) -> List[List[Dict[str, Any]]]:
        """Split documents into chunks for batch processing"""
        chunks = []
        for i in range(0, len(documents), chunk_size):
            chunks.append(documents[i:i + chunk_size])
        return chunks

    def _ingest_chunk(self, chunk: List[Dict[str, Any]]) -> bool:
        """Ingest a chunk of documents into ChromaDB"""
        try:
            # Prepare the payload for ChromaDB v2
            payload = {
                "ids": [doc["id"] for doc in chunk],
                "documents": [doc["content"] for doc in chunk],
                "metadatas": [doc["metadata"] for doc in chunk]
            }

            # Add to collection
            response = requests.post(
                f"{self.chroma_url}/collections/{self.collection_name}/add",
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            print(f"✅ Ingested chunk of {len(chunk)} documents")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to ingest chunk: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return False

    def ingest_all_documents(self) -> Dict[str, Any]:
        """Main ingestion process"""
        print("🚀 Starting ChromaDB ingestion process...")
        start_time = time.time()

        # Create collection
        self._create_collection()

        # Load documents
        documents = self._load_documents()

        if not documents:
            raise ValueError("No documents found to ingest")

        # Split into chunks for batch processing
        chunks = self._chunk_documents(documents, chunk_size=50)  # Process in batches of 50

        # Track progress
        total_ingested = 0
        failed_chunks = 0

        print(f"📦 Processing {len(chunks)} chunks...")

        for i, chunk in enumerate(chunks):
            print(f"📊 Processing chunk {i+1}/{len(chunks)} ({len(chunk)} documents)")
            if self._ingest_chunk(chunk):
                total_ingested += len(chunk)
            else:
                failed_chunks += 1

        # Calculate statistics
        end_time = time.time()
        duration = end_time - start_time

        stats = {
            "total_documents": len(documents),
            "documents_ingested": total_ingested,
            "failed_chunks": failed_chunks,
            "success_rate": (total_ingested / len(documents)) * 100 if documents else 0,
            "duration_seconds": duration,
            "documents_per_second": total_ingested / duration if duration > 0 else 0
        }

        # Verify final count
        try:
            response = requests.get(f"{self.chroma_url}/collections/{self.collection_name}/count", timeout=10)
            response.raise_for_status()
            final_count = response.json().get("count", 0)
            stats["final_collection_count"] = final_count
        except Exception as e:
            print(f"⚠️  Could not verify final count: {e}")
            stats["final_collection_count"] = "unknown"

        return stats

    def generate_report(self, stats: Dict[str, Any]):
        """Generate ingestion report"""
        print("\n" + "="*50)
        print("📊 CHROMADB INGESTION REPORT")
        print("="*50)
        print(f"Total Documents: {stats['total_documents']}")
        print(f"Successfully Ingested: {stats['documents_ingested']}")
        print(f"Failed Chunks: {stats['failed_chunks']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")
        print(f"Duration: {stats['duration_seconds']:.2f} seconds")
        print(f"Throughput: {stats['documents_per_second']:.1f} docs/sec")
        print(f"Final Collection Count: {stats['final_collection_count']}")
        print("="*50)

        if stats['success_rate'] >= 95:
            print("🎉 INGESTION SUCCESSFUL!")
        else:
            print("⚠️  INGESTION COMPLETED WITH ISSUES")

def main():
    try:
        ingester = ChromaDBIngester()
        stats = ingester.ingest_all_documents()
        ingester.generate_report(stats)

        # Save stats to file
        with open("/Users/andrejsp/ai/chromadb_ingestion_stats.json", 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"\n📁 Stats saved to: /Users/andrejsp/ai/chromadb_ingestion_stats.json")

    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
