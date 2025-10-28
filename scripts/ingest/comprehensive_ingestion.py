#!/usr/bin/env python3
"""
Comprehensive Data Ingestion for RAG System
Ingests multiple high-value datasets for comprehensive knowledge base
"""

import os
import sys
import time
from datasets import load_dataset
from typing import List, Dict, Any
import json

# Add the examples directory to path
sys.path.append('/Users/andrejsp/ai/examples')

from rag_setup import RAGVectorDB

class ComprehensiveIngestion:
    """Comprehensive data ingestion for RAG system"""
    
    def __init__(self):
        self.rag_systems = {
            "coding": RAGVectorDB(backend="chroma", collection_name="coding_knowledge"),
            "general": RAGVectorDB(backend="chroma", collection_name="general_knowledge"),
            "technical": RAGVectorDB(backend="chroma", collection_name="technical_docs"),
            "reasoning": RAGVectorDB(backend="chroma", collection_name="reasoning_data")
        }
        
        self.ingestion_stats = {
            "total_documents": 0,
            "collections_created": 0,
            "datasets_processed": 0,
            "errors": 0
        }
    
    def ingest_github_code_dataset(self, sample_size: int = 5000):
        """Ingest GitHub code dataset for coding knowledge"""
        print("📚 Ingesting GitHub Code 2025 dataset...")
        
        try:
            dataset = load_dataset("nick007x/github-code-2025", split="train", streaming=True)
            
            documents = []
            metadatas = []
            
            for i, example in enumerate(dataset):
                if i >= sample_size:
                    break
                
                if 'text' in example:
                    text = example['text']
                    # Truncate long code
                    if len(text) > 3000:
                        text = text[:3000] + "..."
                    
                    documents.append(text)
                    metadatas.append({
                        "source": "huggingface",
                        "dataset": "github-code-2025",
                        "type": "code",
                        "index": i,
                        "collection": "coding"
                    })
            
            if documents:
                self.rag_systems["coding"].add_documents(documents, metadatas)
                self.ingestion_stats["total_documents"] += len(documents)
                self.ingestion_stats["datasets_processed"] += 1
                print(f"✅ Added {len(documents)} GitHub code examples to coding collection")
            
        except Exception as e:
            print(f"❌ Error ingesting GitHub code: {e}")
            self.ingestion_stats["errors"] += 1
    
    def ingest_wikipedia_dataset(self, sample_size: int = 2000):
        """Ingest Wikipedia dataset for general knowledge"""
        print("📚 Ingesting Wikipedia dataset...")
        
        try:
            dataset = load_dataset("wikimedia/wikipedia", "20231101.en", split="train", streaming=True)
            
            documents = []
            metadatas = []
            
            for i, example in enumerate(dataset):
                if i >= sample_size:
                    break
                
                if 'text' in example:
                    text = example['text']
                    # Truncate long articles
                    if len(text) > 2000:
                        text = text[:2000] + "..."
                    
                    documents.append(text)
                    metadatas.append({
                        "source": "wikipedia",
                        "title": example.get('title', 'Unknown'),
                        "type": "general_knowledge",
                        "index": i,
                        "collection": "general"
                    })
            
            if documents:
                self.rag_systems["general"].add_documents(documents, metadatas)
                self.ingestion_stats["total_documents"] += len(documents)
                self.ingestion_stats["datasets_processed"] += 1
                print(f"✅ Added {len(documents)} Wikipedia articles to general collection")
            
        except Exception as e:
            print(f"❌ Error ingesting Wikipedia: {e}")
            self.ingestion_stats["errors"] += 1
    
    def ingest_technical_documentation(self):
        """Ingest technical documentation and guides"""
        print("📚 Ingesting technical documentation...")
        
        # Sample technical documents
        tech_docs = [
            {
                "title": "Docker Best Practices",
                "content": """
                Docker Best Practices Guide
                
                1. Use multi-stage builds to reduce image size
                2. Don't run processes as root
                3. Use .dockerignore to exclude unnecessary files
                4. Leverage build cache
                5. Use specific base image tags
                6. Minimize layers
                7. Use health checks
                8. Don't store secrets in images
                """,
                "type": "devops"
            },
            {
                "title": "Kubernetes Architecture",
                "content": """
                Kubernetes Architecture Overview
                
                Master Components:
                - API Server: Central management point
                - etcd: Distributed key-value store
                - Scheduler: Assigns pods to nodes
                - Controller Manager: Manages cluster state
                
                Node Components:
                - kubelet: Node agent
                - kube-proxy: Network proxy
                - Container Runtime: Docker/containerd
                """,
                "type": "devops"
            },
            {
                "title": "Machine Learning Pipeline",
                "content": """
                ML Pipeline Best Practices
                
                1. Data Collection and Validation
                2. Feature Engineering
                3. Model Selection and Training
                4. Model Evaluation and Validation
                5. Model Deployment and Monitoring
                6. Continuous Integration/Deployment
                7. A/B Testing and Experimentation
                """,
                "type": "ml"
            },
            {
                "title": "API Design Principles",
                "content": """
                RESTful API Design Principles
                
                1. Use HTTP methods correctly (GET, POST, PUT, DELETE)
                2. Use meaningful resource names
                3. Use HTTP status codes appropriately
                4. Version your API
                5. Use consistent response formats
                6. Implement proper error handling
                7. Document your API
                8. Consider rate limiting and authentication
                """,
                "type": "api_design"
            }
        ]
        
        documents = []
        metadatas = []
        
        for i, doc in enumerate(tech_docs):
            documents.append(doc["content"])
            metadatas.append({
                "source": "technical_docs",
                "title": doc["title"],
                "type": doc["type"],
                "index": i,
                "collection": "technical"
            })
        
        if documents:
            self.rag_systems["technical"].add_documents(documents, metadatas)
            self.ingestion_stats["total_documents"] += len(documents)
            self.ingestion_stats["datasets_processed"] += 1
            print(f"✅ Added {len(documents)} technical documents")
    
    def ingest_reasoning_datasets(self):
        """Ingest reasoning and problem-solving datasets"""
        print("📚 Ingesting reasoning datasets...")
        
        try:
            # Load GSM8K math reasoning
            dataset = load_dataset("openai/gsm8k", "main", split="train[:1000]")
            
            documents = []
            metadatas = []
            
            for i, example in enumerate(dataset):
                if 'question' in example and 'answer' in example:
                    text = f"Question: {example['question']}\nAnswer: {example['answer']}"
                    documents.append(text)
                    metadatas.append({
                        "source": "huggingface",
                        "dataset": "gsm8k",
                        "type": "math_reasoning",
                        "index": i,
                        "collection": "reasoning"
                    })
            
            if documents:
                self.rag_systems["reasoning"].add_documents(documents, metadatas)
                self.ingestion_stats["total_documents"] += len(documents)
                self.ingestion_stats["datasets_processed"] += 1
                print(f"✅ Added {len(documents)} math reasoning problems")
            
        except Exception as e:
            print(f"❌ Error ingesting reasoning data: {e}")
            self.ingestion_stats["errors"] += 1
    
    def ingest_programming_languages_docs(self):
        """Ingest programming language documentation"""
        print("📚 Ingesting programming language docs...")
        
        prog_docs = [
            {
                "title": "Python Advanced Features",
                "content": """
                Python Advanced Features
                
                Decorators: Functions that modify other functions
                Generators: Memory-efficient iterators
                Context Managers: Resource management with 'with' statements
                Metaclasses: Classes that create other classes
                Descriptors: Attribute access control
                Async/Await: Asynchronous programming
                Type Hints: Static type checking
                """,
                "language": "python"
            },
            {
                "title": "JavaScript ES6+ Features",
                "content": """
                JavaScript ES6+ Features
                
                Arrow Functions: Concise function syntax
                Destructuring: Extract values from objects/arrays
                Template Literals: String interpolation
                Classes: Object-oriented programming
                Modules: Import/export system
                Promises: Asynchronous operations
                Async/Await: Promise-based async code
                """,
                "language": "javascript"
            },
            {
                "title": "Rust Memory Safety",
                "content": """
                Rust Memory Safety Features
                
                Ownership: Each value has a single owner
                Borrowing: References to values without taking ownership
                Lifetimes: How long references are valid
                Move Semantics: Transfer ownership between variables
                Zero-cost Abstractions: High-level features with no runtime cost
                """,
                "language": "rust"
            }
        ]
        
        documents = []
        metadatas = []
        
        for i, doc in enumerate(prog_docs):
            documents.append(doc["content"])
            metadatas.append({
                "source": "programming_docs",
                "title": doc["title"],
                "language": doc["language"],
                "type": "programming",
                "index": i,
                "collection": "coding"
            })
        
        if documents:
            self.rag_systems["coding"].add_documents(documents, metadatas)
            self.ingestion_stats["total_documents"] += len(documents)
            self.ingestion_stats["datasets_processed"] += 1
            print(f"✅ Added {len(documents)} programming language docs")
    
    def run_comprehensive_ingestion(self):
        """Run comprehensive data ingestion"""
        print("🚀 Starting Comprehensive Data Ingestion")
        print("=" * 50)
        
        start_time = time.time()
        
        # Ingest different types of data
        self.ingest_github_code_dataset(sample_size=3000)  # Reduced for faster ingestion
        self.ingest_wikipedia_dataset(sample_size=1000)
        self.ingest_technical_documentation()
        self.ingest_reasoning_datasets()
        self.ingest_programming_languages_docs()
        
        # Calculate stats
        end_time = time.time()
        duration = end_time - start_time
        
        self.ingestion_stats["collections_created"] = len(self.rag_systems)
        
        print(f"\n🎉 Comprehensive Ingestion Complete!")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📊 Statistics:")
        print(f"   - Total Documents: {self.ingestion_stats['total_documents']}")
        print(f"   - Collections Created: {self.ingestion_stats['collections_created']}")
        print(f"   - Datasets Processed: {self.ingestion_stats['datasets_processed']}")
        print(f"   - Errors: {self.ingestion_stats['errors']}")
        
        print(f"\n📚 Collections Created:")
        for name, rag in self.rag_systems.items():
            try:
                collections = rag.client.list_collections()
                for collection in collections:
                    if collection.name == rag.collection_name:
                        print(f"   - {name}: {collection.count()} documents")
            except:
                print(f"   - {name}: Collection created")
        
        return self.ingestion_stats

def main():
    """Main function"""
    print("🎯 Comprehensive RAG Data Ingestion")
    print("=" * 40)
    
    # Initialize ingestion system
    ingestion = ComprehensiveIngestion()
    
    # Run comprehensive ingestion
    stats = ingestion.run_comprehensive_ingestion()
    
    print(f"\n💡 Next Steps:")
    print(f"1. 🌐 View collections: python /Users/andrejsp/ai/scripts/start_web_interfaces.py")
    print(f"2. 🔍 Test queries: python /Users/andrejsp/ai/scripts/simple_hf_datasets.py")
    print(f"3. 📊 Monitor performance: Check web interface")
    print(f"4. 🚀 Add more datasets as needed")

if __name__ == "__main__":
    main()