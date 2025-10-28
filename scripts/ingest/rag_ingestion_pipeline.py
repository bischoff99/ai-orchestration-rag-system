#!/usr/bin/env python3
"""
RAG Ingestion Pipeline
Converts training examples to RAG documents and ingests them into ChromaDB
"""
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RAGDocument:
    """RAG document structure"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: List[float] = None

class RAGIngestionPipeline:
    """Pipeline for converting training data to RAG documents and ingesting to ChromaDB"""

    def __init__(self, base_dir: str = "/Users/andrejsp/ai"):
        self.base_dir = Path(base_dir)
        self.rag_sources_dir = self.base_dir / "rag_sources"
        self.final_datasets_dir = self.base_dir / "datasets" / "final"

        # Create directories
        for subdir in ["docs", "code_examples", "technical_docs", "training_examples"]:
            (self.rag_sources_dir / subdir).mkdir(parents=True, exist_ok=True)

        # ChromaDB settings
        self.chroma_host = "localhost"
        self.chroma_port = 8000
        self.chroma_api_url = f"http://{self.chroma_host}:{self.chroma_port}/api/v2"

    def load_training_examples(self) -> List[Dict[str, Any]]:
        """Load training examples from final dataset"""
        jsonl_file = self.final_datasets_dir / "combined_training.jsonl"

        examples = []
        if jsonl_file.exists():
            with open(jsonl_file, 'r') as f:
                for line in f:
                    if line.strip():
                        examples.append(json.loads(line))

        logger.info(f"✅ Loaded {len(examples)} training examples from {jsonl_file}")
        return examples

    def convert_to_rag_documents(self, examples: List[Dict[str, Any]]) -> List[RAGDocument]:
        """Convert training examples to RAG documents"""
        logger.info("🔄 Converting training examples to RAG documents...")

        documents = []

        for i, example in enumerate(examples):
            # Create comprehensive document content
            instruction = example.get("instruction", "")
            output = example.get("output", "")

            # Create different document types based on content
            doc_content = self.create_document_content(example, i)
            doc_metadata = self.create_document_metadata(example, i)

            # Generate unique ID
            doc_id = f"training_{i}_{hash(doc_content) % 10000}"

            document = RAGDocument(
                id=doc_id,
                content=doc_content,
                metadata=doc_metadata
            )

            documents.append(document)

        logger.info(f"✅ Created {len(documents)} RAG documents")
        return documents

    def create_document_content(self, example: Dict[str, Any], index: int) -> str:
        """Create comprehensive document content from training example"""
        instruction = example.get("instruction", "")
        output = example.get("output", "")
        input_text = example.get("input", "")

        # Different content formats based on instruction type
        if "function" in instruction.lower() or "code" in instruction.lower():
            # Code example document
            content = f"""# Code Example: {instruction}

## Task
{instruction}

## Input
{input_text if input_text else "No specific input required"}

## Solution
```python
{output}
```

## Explanation
This code example demonstrates {instruction.lower()}. The implementation shows best practices for {instruction.split()[0].lower()} operations.
"""

        elif "explain" in instruction.lower() or "what is" in instruction.lower():
            # Technical explanation document
            content = f"""# Technical Explanation: {instruction}

## Question
{instruction}

## Answer
{output}

## Key Points
- {instruction.split()[0].lower()} concepts
- Implementation details
- Best practices and considerations
"""

        elif "docker" in instruction.lower():
            # Docker-specific document
            content = f"""# Docker Guide: {instruction}

## Topic
{instruction}

## Instructions
{output}

## Docker Best Practices
- Use multi-stage builds for optimization
- Leverage .dockerignore files
- Implement proper security practices
- Use specific image tags
"""

        elif "machine learning" in instruction.lower() or "ml" in instruction.lower():
            # ML-specific document
            content = f"""# Machine Learning Concept: {instruction}

## Concept
{instruction}

## Explanation
{output}

## ML Considerations
- Data preprocessing requirements
- Model evaluation metrics
- Training and validation strategies
- Performance optimization techniques
"""

        else:
            # General technical document
            content = f"""# Technical Guide: {instruction}

## Topic
{instruction}

## Content
{output}

## Implementation Notes
{input_text if input_text else "General implementation guidance"}
"""

        return content

    def create_document_metadata(self, example: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Create metadata for RAG document"""
        instruction = example.get("instruction", "")

        # Determine document type and tags
        doc_type = self.classify_document_type(instruction)
        tags = self.extract_tags(instruction)

        metadata = {
            "source": "training_examples",
            "doc_type": doc_type,
            "tags": tags,
            "instruction_length": len(instruction.split()),
            "content_length": len(example.get("output", "").split()),
            "quality_score": example.get("quality_score", 0.5),
            "domain": self.infer_domain(instruction),
            "created_at": datetime.now().isoformat(),
            "index": index
        }

        return metadata

    def classify_document_type(self, instruction: str) -> str:
        """Classify document type based on instruction"""
        instruction_lower = instruction.lower()

        if any(word in instruction_lower for word in ["function", "code", "write", "create"]):
            return "code_example"
        elif any(word in instruction_lower for word in ["explain", "what is", "describe"]):
            return "technical_explanation"
        elif any(word in instruction_lower for word in ["how", "guide", "tutorial"]):
            return "tutorial"
        elif any(word in instruction_lower for word in ["docker", "container"]):
            return "docker_guide"
        elif any(word in instruction_lower for word in ["api", "endpoint", "rest"]):
            return "api_documentation"
        else:
            return "general_technical"

    def extract_tags(self, instruction: str) -> List[str]:
        """Extract relevant tags from instruction"""
        tags = []
        instruction_lower = instruction.lower()

        # Programming languages
        languages = ["python", "javascript", "java", "cpp", "go", "rust", "sql"]
        for lang in languages:
            if lang in instruction_lower:
                tags.append(f"language:{lang}")

        # Technologies
        technologies = ["docker", "kubernetes", "api", "database", "web", "ml", "ai"]
        for tech in technologies:
            if tech in instruction_lower:
                tags.append(f"technology:{tech}")

        # Concepts
        concepts = ["function", "class", "algorithm", "design", "optimization"]
        for concept in concepts:
            if concept in instruction_lower:
                tags.append(f"concept:{concept}")

        return tags

    def infer_domain(self, instruction: str) -> str:
        """Infer the technical domain from instruction"""
        instruction_lower = instruction.lower()

        if "docker" in instruction_lower or "container" in instruction_lower:
            return "containerization"
        elif "machine learning" in instruction_lower or "neural" in instruction_lower:
            return "machine_learning"
        elif "api" in instruction_lower or "rest" in instruction_lower:
            return "api_design"
        elif "python" in instruction_lower or "function" in instruction_lower:
            return "programming"
        elif "database" in instruction_lower or "sql" in instruction_lower:
            return "data_management"
        else:
            return "general_technical"

    def save_rag_documents(self, documents: List[RAGDocument]):
        """Save RAG documents to files organized by type"""
        logger.info("💾 Saving RAG documents to files...")

        # Group documents by type
        doc_groups = {}
        for doc in documents:
            doc_type = doc.metadata.get("doc_type", "general")
            if doc_type not in doc_groups:
                doc_groups[doc_type] = []
            doc_groups[doc_type].append(doc)

        # Save each group
        for doc_type, docs in doc_groups.items():
            output_dir = self.rag_sources_dir / doc_type
            output_dir.mkdir(exist_ok=True)

            output_file = output_dir / f"{doc_type}_documents.json"

            # Convert to dict format
            dict_docs = []
            for doc in docs:
                dict_docs.append({
                    "id": doc.id,
                    "content": doc.content,
                    "metadata": doc.metadata
                })

            with open(output_file, 'w') as f:
                json.dump(dict_docs, f, indent=2)

            logger.info(f"💾 Saved {len(docs)} {doc_type} documents to {output_file}")

    def check_chromadb_health(self) -> bool:
        """Check if ChromaDB is running and healthy"""
        try:
            import requests
            response = requests.get(f"{self.chroma_api_url}/heartbeat", timeout=5)
            response.raise_for_status()
            logger.info("✅ ChromaDB is healthy and accessible")
            return True
        except Exception as e:
            logger.warning(f"❌ ChromaDB not accessible: {e}")
            return False

    def create_chromadb_collection(self, collection_name: str) -> bool:
        """Create ChromaDB collection if it doesn't exist"""
        try:
            import requests

            # Check if collection exists
            response = requests.get(f"{self.chroma_api_url}/collections", timeout=5)
            if response.status_code == 200:
                collections = response.json()
                collection_names = [c.get("name") for c in collections]
                if collection_name in collection_names:
                    logger.info(f"✅ Collection '{collection_name}' already exists")
                    return True

            # Create collection
            payload = {"name": collection_name}
            response = requests.post(
                f"{self.chroma_api_url}/collections",
                json=payload,
                timeout=10
            )
            response.raise_for_status()

            logger.info(f"✅ Created ChromaDB collection: {collection_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to create ChromaDB collection: {e}")
            return False

    def ingest_documents_to_chromadb(self, documents: List[RAGDocument], collection_name: str = "rag_training_docs"):
        """Ingest documents into ChromaDB collection"""
        if not self.check_chromadb_health():
            logger.error("❌ Cannot ingest documents - ChromaDB not available")
            return False

        if not self.create_chromadb_collection(collection_name):
            logger.error("❌ Cannot create ChromaDB collection")
            return False

        logger.info(f"🚀 Ingesting {len(documents)} documents into ChromaDB collection '{collection_name}'...")

        try:
            import requests

            # Prepare documents for ChromaDB v2 API
            # Note: ChromaDB v2 API expects documents with embeddings
            # For now, we'll store documents and let ChromaDB handle embedding during query time
            # In production, you'd want to pre-compute embeddings

            ingested_count = 0
            batch_size = 10  # Process in batches

            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]

                # Prepare batch data
                batch_data = {
                    "ids": [doc.id for doc in batch],
                    "documents": [doc.content for doc in batch],
                    "metadatas": [doc.metadata for doc in batch]
                }

                # Add to collection
                response = requests.post(
                    f"{self.chroma_api_url}/collections/{collection_name}/add",
                    json=batch_data,
                    timeout=30
                )

                if response.status_code == 200:
                    ingested_count += len(batch)
                    logger.info(f"✅ Ingested batch {i//batch_size + 1}: {len(batch)} documents")
                else:
                    logger.error(f"❌ Failed to ingest batch {i//batch_size + 1}: {response.text}")

            logger.info(f"✅ Successfully ingested {ingested_count}/{len(documents)} documents into ChromaDB")
            return ingested_count > 0

        except Exception as e:
            logger.error(f"❌ Error ingesting documents to ChromaDB: {e}")
            return False

    def verify_ingestion(self, collection_name: str = "rag_training_docs") -> Dict[str, Any]:
        """Verify documents were ingested correctly"""
        logger.info("🔍 Verifying document ingestion...")

        try:
            import requests

            # Get collection info
            response = requests.get(f"{self.chroma_api_url}/collections/{collection_name}", timeout=10)

            if response.status_code == 200:
                collection_info = response.json()
                document_count = collection_info.get("document_count", 0)

                verification_result = {
                    "collection_exists": True,
                    "document_count": document_count,
                    "collection_name": collection_name,
                    "status": "verified" if document_count > 0 else "empty"
                }

                logger.info(f"✅ Verification complete: {document_count} documents in collection")
                return verification_result
            else:
                logger.error(f"❌ Collection verification failed: {response.text}")
                return {"collection_exists": False, "error": response.text}

        except Exception as e:
            logger.error(f"❌ Verification error: {e}")
            return {"collection_exists": False, "error": str(e)}

    def run_ingestion_pipeline(self) -> Dict[str, Any]:
        """Run the complete RAG ingestion pipeline"""
        logger.info("🚀 Starting RAG Ingestion Pipeline")
        logger.info("=" * 60)

        results = {
            "phase": "rag_ingestion",
            "success": False,
            "documents_created": 0,
            "documents_ingested": 0,
            "chromadb_status": "unknown",
            "errors": []
        }

        try:
            # Phase 1: Load training examples
            examples = self.load_training_examples()
            if not examples:
                raise ValueError("No training examples found")

            # Phase 2: Convert to RAG documents
            documents = self.convert_to_rag_documents(examples)
            results["documents_created"] = len(documents)

            # Phase 3: Save documents to files
            self.save_rag_documents(documents)

            # Phase 4: Ingest to ChromaDB
            collection_name = "rag_training_docs"
            ingestion_success = self.ingest_documents_to_chromadb(documents, collection_name)

            if ingestion_success:
                # Phase 5: Verify ingestion
                verification = self.verify_ingestion(collection_name)
                results["chromadb_status"] = "healthy" if verification.get("collection_exists") else "unhealthy"
                results["documents_ingested"] = verification.get("document_count", 0)
                results["success"] = True
            else:
                results["chromadb_status"] = "unhealthy"
                results["errors"].append("ChromaDB ingestion failed")

        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            results["errors"].append(str(e))

        # Save results
        results_file = self.rag_sources_dir / "ingestion_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info("=" * 60)
        logger.info("📊 RAG Ingestion Results:")
        logger.info(f"   Documents Created: {results['documents_created']}")
        logger.info(f"   Documents Ingested: {results['documents_ingested']}")
        logger.info(f"   ChromaDB Status: {results['chromadb_status']}")
        logger.info(f"   Overall Success: {results['success']}")
        logger.info(f"   Results saved to: {results_file}")

        return results

def main():
    """Main function to run RAG ingestion pipeline"""
    pipeline = RAGIngestionPipeline()
    results = pipeline.run_ingestion_pipeline()

    print("\n🎉 RAG Ingestion Pipeline Complete!")
    if results["success"]:
        print(f"✅ Successfully processed {results['documents_created']} documents")
        print(f"✅ Ingested {results['documents_ingested']} documents into ChromaDB")
    else:
        print("❌ Pipeline failed - check logs for details")

    return results

if __name__ == "__main__":
    main()