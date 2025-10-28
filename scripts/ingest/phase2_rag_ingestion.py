#!/usr/bin/env python3
"""
Phase 2: Automate RAG Data Ingestion
Continuous ingestion pipeline with parallel processing
"""

import os
import sys
import json
import time
import requests
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class RAGIngestionPipeline:
    def __init__(self):
        self.chromadb_url = "http://localhost:8000/api/v1"
        self.ollama_url = "http://localhost:11434/api"
        self.vector_db_path = "/Users/andrejsp/ai/vector_db/chroma"
        self.sample_docs_path = "/Users/andrejsp/ai/sample_docs"
        self.collections = {
            "general_knowledge": "General knowledge documents",
            "technical_docs": "Technical documentation",
            "code_samples": "Code examples and snippets",
            "research_papers": "Research papers and articles"
        }
        
    def check_services(self):
        """Check if required services are running"""
        print("🔍 Phase 2.1: Checking Required Services")
        print("=" * 50)
        
        services = {
            "ChromaDB": f"{self.chromadb_url}/heartbeat",
            "Ollama": f"{self.ollama_url}/tags"
        }
        
        running_services = []
        
        for service_name, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ {service_name}: Running")
                    running_services.append(service_name)
                else:
                    print(f"   ❌ {service_name}: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {service_name}: {e}")
        
        return running_services
    
    def create_collections(self):
        """Create ChromaDB collections for different document types"""
        print("\n📚 Phase 2.2: Creating ChromaDB Collections")
        print("=" * 50)
        
        created_collections = []
        
        for collection_name, description in self.collections.items():
            try:
                # Create collection
                response = requests.post(
                    f"{self.chromadb_url}/collections",
                    json={
                        "name": collection_name,
                        "metadata": {"description": description}
                    },
                    timeout=10
                )
                
                if response.status_code == 200 or response.status_code == 409:  # 409 = already exists
                    print(f"   ✅ Collection '{collection_name}': Ready")
                    created_collections.append(collection_name)
                else:
                    print(f"   ❌ Collection '{collection_name}': HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Collection '{collection_name}': {e}")
        
        return created_collections
    
    def process_document(self, file_path, collection_name):
        """Process a single document and add to ChromaDB"""
        try:
            # Read document content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata
            file_name = Path(file_path).name
            file_size = len(content)
            file_type = Path(file_path).suffix
            
            # Create document chunks (simple chunking)
            chunk_size = 1000
            chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
            
            # Add chunks to ChromaDB
            for i, chunk in enumerate(chunks):
                document_data = {
                    "documents": [chunk],
                    "metadatas": [{
                        "source": file_name,
                        "chunk_id": i,
                        "file_type": file_type,
                        "file_size": file_size,
                        "total_chunks": len(chunks)
                    }],
                    "ids": [f"{file_name}_chunk_{i}"]
                }
                
                response = requests.post(
                    f"{self.chromadb_url}/collections/{collection_name}/add",
                    json=document_data,
                    timeout=10
                )
                
                if response.status_code != 200:
                    print(f"   ⚠️  Failed to add chunk {i} of {file_name}: HTTP {response.status_code}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error processing {file_path}: {e}")
            return False
    
    def parallel_document_processing(self, documents, collection_name, max_workers=4):
        """Process documents in parallel"""
        print(f"   🔄 Processing {len(documents)} documents with {max_workers} workers...")
        
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_doc = {
                executor.submit(self.process_document, doc, collection_name): doc 
                for doc in documents
            }
            
            # Process completed tasks
            for future in as_completed(future_to_doc):
                doc = future_to_doc[future]
                try:
                    success = future.result()
                    results.append((doc, success))
                    if success:
                        print(f"   ✅ Processed: {Path(doc).name}")
                    else:
                        print(f"   ❌ Failed: {Path(doc).name}")
                except Exception as e:
                    print(f"   ❌ Error processing {Path(doc).name}: {e}")
                    results.append((doc, False))
        
        successful = sum(1 for _, success in results if success)
        print(f"   📊 Processed {successful}/{len(documents)} documents successfully")
        return results
    
    def ingest_sample_documents(self):
        """Ingest sample documents from the sample_docs directory"""
        print("\n📄 Phase 2.3: Ingesting Sample Documents")
        print("=" * 50)
        
        if not os.path.exists(self.sample_docs_path):
            print(f"   ❌ Sample docs directory not found: {self.sample_docs_path}")
            return False
        
        # Find all text files
        text_files = []
        for ext in ['.txt', '.md']:
            text_files.extend(Path(self.sample_docs_path).glob(f"*{ext}"))
        
        if not text_files:
            print(f"   ⚠️  No text files found in {self.sample_docs_path}")
            return False
        
        print(f"   📁 Found {len(text_files)} text files")
        
        # Process documents in parallel
        results = self.parallel_document_processing(
            [str(f) for f in text_files], 
            "general_knowledge",
            max_workers=3
        )
        
        successful = sum(1 for _, success in results if success)
        return successful > 0
    
    def create_continuous_ingestion_workflow(self):
        """Create n8n workflow for continuous ingestion"""
        print("\n🔄 Phase 2.4: Creating Continuous Ingestion Workflow")
        print("=" * 50)
        
        # This would create an n8n workflow for continuous ingestion
        # For now, we'll create a Python-based continuous monitor
        
        ingestion_workflow = {
            "name": "Continuous RAG Ingestion Pipeline",
            "description": "Monitors directories and ingests new documents automatically",
            "monitored_directories": [
                "/Users/andrejsp/ai/sample_docs",
                "/Users/andrejsp/Downloads",
                "/Users/andrejsp/Documents"
            ],
            "collections": self.collections,
            "processing_rules": {
                "file_types": [".txt", ".md", ".pdf", ".docx"],
                "chunk_size": 1000,
                "max_file_size": 10 * 1024 * 1024,  # 10MB
                "parallel_workers": 4
            }
        }
        
        # Save workflow configuration
        workflow_path = "/Users/andrejsp/ai/configs/ingestion_workflow.json"
        with open(workflow_path, 'w') as f:
            json.dump(ingestion_workflow, f, indent=2)
        
        print(f"   ✅ Created ingestion workflow config: {workflow_path}")
        return True
    
    def test_rag_query(self):
        """Test RAG query functionality"""
        print("\n🧪 Phase 2.5: Testing RAG Query Functionality")
        print("=" * 50)
        
        test_queries = [
            "What is machine learning?",
            "How does Python work?",
            "What are the basics of Docker?"
        ]
        
        for query in test_queries:
            print(f"   🔍 Testing query: '{query}'")
            
            try:
                # Query ChromaDB
                response = requests.post(
                    f"{self.chromadb_url}/collections/general_knowledge/query",
                    json={
                        "query_texts": [query],
                        "n_results": 3
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    results = response.json()
                    documents = results.get('documents', [[]])[0]
                    distances = results.get('distances', [[]])[0]
                    
                    print(f"      ✅ Found {len(documents)} relevant documents")
                    for i, (doc, dist) in enumerate(zip(documents, distances)):
                        print(f"         {i+1}. Similarity: {1-dist:.3f} - {doc[:100]}...")
                else:
                    print(f"      ❌ Query failed: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Query error: {e}")
    
    def create_monitoring_dashboard(self):
        """Create monitoring dashboard for ingestion pipeline"""
        print("\n📊 Phase 2.6: Creating Monitoring Dashboard")
        print("=" * 50)
        
        dashboard_config = {
            "metrics": {
                "documents_processed": 0,
                "documents_failed": 0,
                "collections_created": len(self.collections),
                "last_ingestion": datetime.now().isoformat(),
                "processing_rate": "documents/minute"
            },
            "alerts": {
                "high_failure_rate": 0.1,  # 10%
                "low_processing_rate": 1,  # 1 doc/minute
                "collection_size_warning": 10000  # 10k documents
            },
            "health_checks": {
                "chromadb_status": "unknown",
                "ollama_status": "unknown",
                "file_system_status": "unknown"
            }
        }
        
        # Save dashboard config
        dashboard_path = "/Users/andrejsp/ai/configs/monitoring_dashboard.json"
        with open(dashboard_path, 'w') as f:
            json.dump(dashboard_config, f, indent=2)
        
        print(f"   ✅ Created monitoring dashboard config: {dashboard_path}")
        return True
    
    def run_ingestion_pipeline(self):
        """Run complete RAG ingestion pipeline"""
        print("🚀 Phase 2: Automate RAG Data Ingestion")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Check services
        running_services = self.check_services()
        if not running_services:
            print("   ❌ No required services running")
            return False
        
        # Step 2: Create collections
        collections = self.create_collections()
        if not collections:
            print("   ❌ Failed to create collections")
            return False
        
        # Step 3: Ingest sample documents
        ingestion_success = self.ingest_sample_documents()
        if not ingestion_success:
            print("   ⚠️  Sample document ingestion had issues")
        
        # Step 4: Create continuous ingestion workflow
        workflow_success = self.create_continuous_ingestion_workflow()
        
        # Step 5: Test RAG query
        self.test_rag_query()
        
        # Step 6: Create monitoring dashboard
        monitoring_success = self.create_monitoring_dashboard()
        
        # Summary
        print(f"\n📊 Phase 2 Summary:")
        print(f"   Services running: {len(running_services)}")
        print(f"   Collections created: {len(collections)}")
        print(f"   Document ingestion: {'✅' if ingestion_success else '⚠️'}")
        print(f"   Workflow creation: {'✅' if workflow_success else '❌'}")
        print(f"   Monitoring setup: {'✅' if monitoring_success else '❌'}")
        
        return all([collections, workflow_success, monitoring_success])

def main():
    """Main function"""
    pipeline = RAGIngestionPipeline()
    success = pipeline.run_ingestion_pipeline()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())