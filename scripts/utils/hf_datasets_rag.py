#!/usr/bin/env python3
"""
Hugging Face Datasets Integration with RAG
Download and integrate HF datasets into your RAG system
"""

import os
import sys
from datasets import load_dataset
from typing import List, Dict, Any
import json

# Add the examples directory to path
sys.path.append('/Users/andrejsp/ai/examples')

from ollama_rag import OllamaRAG

class HFDatasetsRAG:
    """Integrate Hugging Face datasets with RAG system"""
    
    def __init__(self, rag_system: OllamaRAG):
        self.rag = rag_system
    
    def load_code_dataset(self, dataset_name: str = "nick007x/github-code-2025", sample_size: int = 1000):
        """Load a code dataset from Hugging Face"""
        print(f"📥 Loading dataset: {dataset_name}")
        
        try:
            # Load dataset with sampling
            dataset = load_dataset(dataset_name, split=f"train[:{sample_size}]")
            
            print(f"✅ Loaded {len(dataset)} examples")
            print(f"📊 Features: {list(dataset.features.keys())}")
            
            # Convert to documents
            documents = []
            metadatas = []
            
            for i, example in enumerate(dataset):
                # Extract text content (adjust based on dataset structure)
                if 'text' in example:
                    text = example['text']
                elif 'content' in example:
                    text = example['content']
                elif 'code' in example:
                    text = example['code']
                else:
                    # Try to find any text field
                    text_fields = [k for k, v in example.items() if isinstance(v, str)]
                    if text_fields:
                        text = example[text_fields[0]]
                    else:
                        continue
                
                # Truncate long texts
                if len(text) > 2000:
                    text = text[:2000] + "..."
                
                documents.append(text)
                metadatas.append({
                    "source": "huggingface",
                    "dataset": dataset_name,
                    "index": i,
                    "length": len(text)
                })
            
            return documents, metadatas
            
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            return [], []
    
    def load_instruction_dataset(self, dataset_name: str = "tatsu-lab/alpaca", sample_size: int = 500):
        """Load an instruction-following dataset"""
        print(f"📥 Loading instruction dataset: {dataset_name}")
        
        try:
            dataset = load_dataset(dataset_name, split=f"train[:{sample_size}]")
            
            documents = []
            metadatas = []
            
            for i, example in enumerate(dataset):
                # Create instruction-response pairs
                if 'instruction' in example and 'output' in example:
                    text = f"Instruction: {example['instruction']}\nOutput: {example['output']}"
                elif 'text' in example:
                    text = example['text']
                else:
                    continue
                
                documents.append(text)
                metadatas.append({
                    "source": "huggingface",
                    "dataset": dataset_name,
                    "type": "instruction",
                    "index": i
                })
            
            return documents, metadatas
            
        except Exception as e:
            print(f"❌ Error loading instruction dataset: {e}")
            return [], []
    
    def load_wikipedia_dataset(self, sample_size: int = 1000):
        """Load Wikipedia dataset"""
        print("📥 Loading Wikipedia dataset")
        
        try:
            dataset = load_dataset("wikimedia/wikipedia", "20231101.en", split=f"train[:{sample_size}]")
            
            documents = []
            metadatas = []
            
            for i, example in enumerate(dataset):
                text = example['text']
                if len(text) > 1500:
                    text = text[:1500] + "..."
                
                documents.append(text)
                metadatas.append({
                    "source": "wikipedia",
                    "title": example.get('title', 'Unknown'),
                    "index": i,
                    "length": len(text)
                })
            
            return documents, metadatas
            
        except Exception as e:
            print(f"❌ Error loading Wikipedia: {e}")
            return [], []
    
    def add_dataset_to_rag(self, dataset_name: str, dataset_type: str = "code", sample_size: int = 1000):
        """Add a Hugging Face dataset to the RAG system"""
        print(f"🔄 Adding {dataset_name} to RAG system")
        
        if dataset_type == "code":
            documents, metadatas = self.load_code_dataset(dataset_name, sample_size)
        elif dataset_type == "instruction":
            documents, metadatas = self.load_instruction_dataset(dataset_name, sample_size)
        elif dataset_type == "wikipedia":
            documents, metadatas = self.load_wikipedia_dataset(sample_size)
        else:
            print(f"❌ Unknown dataset type: {dataset_type}")
            return
        
        if documents:
            self.rag.add_documents(documents, metadatas)
            print(f"✅ Added {len(documents)} documents from {dataset_name}")
        else:
            print(f"❌ No documents loaded from {dataset_name}")

def main():
    """Main function to demonstrate HF datasets integration"""
    print("🚀 Hugging Face Datasets + RAG Integration")
    print("=" * 50)
    
    # Initialize RAG system
    rag = OllamaRAG(collection_name="hf_datasets", embedding_model="embedder")
    hf_rag = HFDatasetsRAG(rag)
    
    # Add different types of datasets
    print("\n📚 Adding Code Dataset")
    hf_rag.add_dataset_to_rag("nick007x/github-code-2025", "code", sample_size=100)
    
    print("\n📚 Adding Instruction Dataset")
    hf_rag.add_dataset_to_rag("tatsu-lab/alpaca", "instruction", sample_size=50)
    
    print("\n📚 Adding Wikipedia Dataset")
    hf_rag.add_dataset_to_rag("wikipedia", "wikipedia", sample_size=100)
    
    # Test queries
    print("\n🧪 Testing RAG with HF Datasets")
    print("=" * 40)
    
    test_queries = [
        "How do I write a Python function?",
        "What is machine learning?",
        "Explain data structures in programming",
        "How to implement a sorting algorithm?"
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        response = rag.query_ollama(query, k=3)
        print(f"🤖 Answer: {response['answer'][:200]}...")
        print(f"📚 Sources: {len(response['sources'])} documents")

if __name__ == "__main__":
    main()