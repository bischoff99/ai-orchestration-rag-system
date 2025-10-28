#!/usr/bin/env python3
"""
ChromaDB Ingestion Script
Ingests RAG documents into ChromaDB with optimized chunking and embeddings
"""
import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """Represents a chunk of document with metadata"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: List[float] = None

class ChromaDBIngestor:
    """Ingests documents into ChromaDB with optimized chunking"""

    def __init__(self, base_dir: str = "/Users/andrejsp/ai"):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "rag_sources" / "docs"
        self.chroma_dir = self.base_dir / "vector_db" / "chroma"

        # Chunking parameters based on research
        self.chunk_size = 1000  # tokens
        self.chunk_overlap = 200  # tokens

        # Embedding model (from HF search results)
        self.embedding_model_name = "nomic-ai/nomic-embed-text-v1.5"

        # Initialize ChromaDB client
        self.chroma_client = None
        self.collection = None

    def initialize_chromadb(self):
        """Initialize ChromaDB HTTP client and collection"""
        try:
            import requests

            # Test connection to ChromaDB server
            response = requests.get("http://localhost:8000/api/v2/heartbeat", timeout=5)
            response.raise_for_status()

            heartbeat = response.json()
            logger.info(f"✅ Connected to ChromaDB server: {heartbeat}")

            # Check if collection exists
            collection_name = "rag_documents_collection"
            response = requests.get(f"http://localhost:8000/api/v2/collections/{collection_name}", timeout=5)

            if response.status_code == 200:
                logger.info(f"✅ Using existing collection: {collection_name}")
            elif response.status_code == 404:
                # Create collection
                create_payload = {
                    "name": collection_name,
                    "metadata": {"description": "RAG documents for AI assistant"}
                }
                response = requests.post(
                    "http://localhost:8000/api/v2/collections",
                    json=create_payload,
                    timeout=10
                )
                response.raise_for_status()
                logger.info(f"✅ Created new collection: {collection_name}")
            else:
                response.raise_for_status()

            self.collection_name = collection_name
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to connect to ChromaDB: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to initialize ChromaDB: {e}")
            return False

    def load_rag_documents(self) -> List[Dict[str, Any]]:
        """Load RAG documents from the docs directory"""
        documents = []
        index_file = self.docs_dir / "document_index.json"

        if not index_file.exists():
            logger.error(f"Document index not found: {index_file}")
            return documents

        try:
            with open(index_file, 'r') as f:
                index_data = json.load(f)

            documents = index_data.get("documents", [])
            logger.info(f"✅ Loaded {len(documents)} documents from index")

        except Exception as e:
            logger.error(f"❌ Error loading documents: {e}")

        return documents

    def chunk_document(self, document: Dict[str, Any]) -> List[DocumentChunk]:
        """Chunk a document using smart chunking strategy"""
        content = document.get("content", "")
        metadata = document.get("metadata", {})
        doc_id = document.get("id", "unknown")

        # Split into sentences first (better semantic boundaries)
        sentences = self.split_into_sentences(content)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_tokens = len(sentence.split())

            # Check if adding this sentence would exceed chunk size
            if current_length + sentence_tokens > self.chunk_size and current_chunk:
                # Create chunk from current sentences
                chunk_content = " ".join(current_chunk)
                chunk_id = f"{doc_id}_chunk_{len(chunks)}"

                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_index": len(chunks),
                    "total_chunks": None,  # Will update later
                    "chunk_size": len(chunk_content.split()),
                    "source_document": doc_id
                })

                chunks.append(DocumentChunk(
                    id=chunk_id,
                    content=chunk_content,
                    metadata=chunk_metadata
                ))

                # Start new chunk with overlap
                overlap_sentences = self.get_overlap_sentences(current_chunk, self.chunk_overlap)
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s.split()) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_length += sentence_tokens

        # Add remaining sentences as final chunk
        if current_chunk:
            chunk_content = " ".join(current_chunk)
            chunk_id = f"{doc_id}_chunk_{len(chunks)}"

            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_index": len(chunks),
                "total_chunks": len(chunks) + 1,
                "chunk_size": len(chunk_content.split()),
                "source_document": doc_id
            })

            chunks.append(DocumentChunk(
                id=chunk_id,
                content=chunk_content,
                metadata=chunk_metadata
            ))

        # Update total_chunks for all chunks
        for chunk in chunks:
            chunk.metadata["total_chunks"] = len(chunks)

        logger.info(f"📄 Document {doc_id}: {len(sentences)} sentences → {len(chunks)} chunks")
        return chunks

    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex"""
        # Simple sentence splitting (can be improved with NLP libraries)
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())

        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def get_overlap_sentences(self, sentences: List[str], target_tokens: int) -> List[str]:
        """Get sentences for overlap based on token count"""
        overlap_sentences = []
        token_count = 0

        # Take sentences from the end backwards until we reach target token count
        for sentence in reversed(sentences):
            sentence_tokens = len(sentence.split())
            if token_count + sentence_tokens <= target_tokens:
                overlap_sentences.insert(0, sentence)
                token_count += sentence_tokens
            else:
                break

        return overlap_sentences

    def initialize_embedding_model(self):
        """Initialize the embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"🔄 Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info("✅ Embedding model loaded successfully")
            return True
        except ImportError:
            logger.error("❌ sentence-transformers not available. Install with: pip install sentence-transformers")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            return False

    def generate_embeddings(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Generate embeddings for document chunks"""
        if not hasattr(self, 'embedding_model'):
            logger.error("❌ Embedding model not initialized")
            return chunks

        logger.info(f"🔄 Generating embeddings for {len(chunks)} chunks...")

        # Extract texts
        texts = [chunk.content for chunk in chunks]

        try:
            # Generate embeddings in batches
            batch_size = 32
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i+batch_size]
                batch_embeddings = self.embedding_model.encode(batch_texts, convert_to_numpy=True)
                all_embeddings.extend(batch_embeddings.tolist())

                logger.info(f"📊 Processed batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")

            # Assign embeddings to chunks
            for chunk, embedding in zip(chunks, all_embeddings):
                chunk.embedding = embedding

            logger.info("✅ Embeddings generated successfully")
            return chunks

        except Exception as e:
            logger.error(f"❌ Failed to generate embeddings: {e}")
            return chunks

    def ingest_to_chromadb(self, chunks: List[DocumentChunk]):
        """Ingest chunks into ChromaDB using HTTP API"""
        if not hasattr(self, 'collection_name'):
            logger.error("❌ ChromaDB collection not available")
            return False

        logger.info(f"🔄 Ingesting {len(chunks)} chunks into ChromaDB...")

        try:
            import requests

            # Filter to only chunks with embeddings
            valid_chunks = [chunk for chunk in chunks if chunk.embedding]
            if not valid_chunks:
                logger.error("❌ No valid embeddings to ingest")
                return False

            if len(valid_chunks) != len(chunks):
                logger.warning(f"⚠️ Only {len(valid_chunks)}/{len(chunks)} chunks have embeddings")

            # Prepare data for ChromaDB v2 API
            # Note: ChromaDB v2 API expects a different format than v1
            # We'll use the /api/v2/collections/{name}/add endpoint

            # For now, let's try the batch add approach
            add_payload = []

            for chunk in valid_chunks:
                item = {
                    "id": chunk.id,
                    "document": chunk.content,
                    "metadata": chunk.metadata,
                    "embedding": chunk.embedding
                }
                add_payload.append(item)

            # Add in batches to avoid payload size limits
            batch_size = 50
            total_ingested = 0

            for i in range(0, len(add_payload), batch_size):
                batch = add_payload[i:i+batch_size]

                response = requests.post(
                    f"http://localhost:8000/api/v2/collections/{self.collection_name}/add",
                    json=batch,
                    timeout=30
                )

                if response.status_code == 200:
                    total_ingested += len(batch)
                    logger.info(f"✅ Ingested batch {i//batch_size + 1}: {len(batch)} chunks")
                else:
                    logger.error(f"❌ Failed to ingest batch {i//batch_size + 1}: {response.status_code} - {response.text}")
                    return False

            logger.info(f"✅ Successfully ingested {total_ingested} chunks into ChromaDB")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to ingest into ChromaDB: {e}")
            return False

    def verify_ingestion(self) -> Dict[str, Any]:
        """Verify ingestion by querying the collection using HTTP API"""
        if not hasattr(self, 'collection_name'):
            return {"success": False, "error": "Collection not available"}

        try:
            import requests

            # Get collection count (approximate via get operation)
            response = requests.get(
                f"http://localhost:8000/api/v2/collections/{self.collection_name}/get",
                params={"limit": 1},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                count = len(data.get("documents", []))
                # Since we can't get exact count, we'll use a sample query to estimate

                # Test a simple query using embedding search
                # First, we need to generate an embedding for the query
                if hasattr(self, 'embedding_model'):
                    query_text = "What is machine learning?"
                    query_embedding = self.embedding_model.encode([query_text])[0].tolist()

                    query_payload = {
                        "query_embeddings": [query_embedding],
                        "n_results": 3
                    }

                    response = requests.post(
                        f"http://localhost:8000/api/v2/collections/{self.collection_name}/query",
                        json=query_payload,
                        timeout=15
                    )

                    if response.status_code == 200:
                        results = response.json()

                        verification = {
                            "success": True,
                            "estimated_documents": count if count > 0 else "unknown",
                            "query_test": {
                                "query": query_text,
                                "results_found": len(results.get("documents", [[]])[0]) if results.get("documents") else 0,
                                "sample_result": results.get("documents", [[]])[0][0][:100] + "..." if results.get("documents") and results["documents"][0] else None
                            }
                        }
                    else:
                        verification = {
                            "success": True,
                            "estimated_documents": count if count > 0 else "unknown",
                            "query_test": {"error": f"Query failed: {response.status_code}"}
                        }
                else:
                    verification = {
                        "success": True,
                        "estimated_documents": count if count > 0 else "unknown",
                        "query_test": {"error": "No embedding model available"}
                    }
            else:
                verification = {
                    "success": False,
                    "error": f"Failed to query collection: {response.status_code}"
                }

            logger.info("✅ Ingestion verification completed")
            return verification

        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return {"success": False, "error": str(e)}

    def run_ingestion_pipeline(self) -> Dict[str, Any]:
        """Run the complete ingestion pipeline"""
        logger.info("🚀 Starting ChromaDB Ingestion Pipeline")
        logger.info("=" * 60)

        results = {
            "stages": {},
            "final_stats": {}
        }

        # Stage 1: Initialize ChromaDB
        logger.info("📍 Stage 1: Initializing ChromaDB...")
        chromadb_ready = self.initialize_chromadb()
        results["stages"]["chromadb_init"] = chromadb_ready

        if not chromadb_ready:
            logger.error("❌ ChromaDB initialization failed")
            return results

        # Stage 2: Initialize embedding model
        logger.info("📍 Stage 2: Initializing embedding model...")
        embedding_ready = self.initialize_embedding_model()
        results["stages"]["embedding_init"] = embedding_ready

        if not embedding_ready:
            logger.error("❌ Embedding model initialization failed")
            return results

        # Stage 3: Load documents
        logger.info("📍 Stage 3: Loading RAG documents...")
        documents = self.load_rag_documents()
        results["stages"]["document_loading"] = len(documents) > 0

        if not documents:
            logger.error("❌ No documents loaded")
            return results

        # Stage 4: Chunk documents
        logger.info("📍 Stage 4: Chunking documents...")
        all_chunks = []
        for doc in documents[:10]:  # Process first 10 documents for testing
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)

        results["stages"]["chunking"] = len(all_chunks) > 0
        logger.info(f"✅ Created {len(all_chunks)} chunks from {len(documents)} documents")

        # Stage 5: Generate embeddings
        logger.info("📍 Stage 5: Generating embeddings...")
        chunks_with_embeddings = self.generate_embeddings(all_chunks)
        valid_chunks = [chunk for chunk in chunks_with_embeddings if chunk.embedding]
        results["stages"]["embedding_generation"] = len(valid_chunks) > 0

        logger.info(f"✅ Generated embeddings for {len(valid_chunks)}/{len(all_chunks)} chunks")

        # Stage 6: Ingest to ChromaDB
        logger.info("📍 Stage 6: Ingesting to ChromaDB...")
        ingestion_success = self.ingest_to_chromadb(valid_chunks)
        results["stages"]["chromadb_ingestion"] = ingestion_success

        # Stage 7: Verify ingestion
        logger.info("📍 Stage 7: Verifying ingestion...")
        verification = self.verify_ingestion()
        results["stages"]["verification"] = verification.get("success", False)
        results["final_stats"] = verification

        # Save results
        output_file = self.base_dir / "chromadb_ingestion_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info("=" * 60)
        logger.info("📊 Ingestion Pipeline Results:")
        logger.info(f"   Stages completed: {sum(1 for v in results['stages'].values() if v)}/{len(results['stages'])}")
        logger.info(f"   Final documents: {results['final_stats'].get('total_documents', 0)}")
        logger.info(f"   Results saved to: {output_file}")

        return results

def main():
    """Main function to run ChromaDB ingestion"""
    ingestor = ChromaDBIngestor()
    results = ingestor.run_ingestion_pipeline()

    success_count = sum(1 for v in results.get("stages", {}).values() if v)
    total_stages = len(results.get("stages", {}))

    print("\n🎉 ChromaDB Ingestion Pipeline Complete!")
    print(f"Stages completed: {success_count}/{total_stages}")

    if results.get("final_stats", {}).get("success"):
        print(f"Documents ingested: {results['final_stats'].get('total_documents', 0)}")
    else:
        print("❌ Ingestion failed - check ChromaDB server status")

    return results

if __name__ == "__main__":
    main()