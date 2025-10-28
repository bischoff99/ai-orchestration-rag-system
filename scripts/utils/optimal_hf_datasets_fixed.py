#!/usr/bin/env python3
"""
Optimal Hugging Face Datasets for RAG System (Fixed Version)
Uses Sentence Transformers as fallback when Ollama embeddings fail
"""

import os
import sys
from datasets import load_dataset
from typing import List, Dict, Any
import json

# Add the examples directory to path
sys.path.append('/Users/andrejsp/ai/examples')

from unified_rag import RAGVectorDB

class OptimalHFDatasetsFixed:
    """Optimal dataset selection with fallback embeddings"""
    
    def __init__(self):
        # Use the original RAG system with Sentence Transformers
        self.rag = RAGVectorDB(backend="chroma", collection_name="optimal_hf_datasets")
        
        self.datasets_config = {
            "alpaca": {
                "name": "tatsu-lab/alpaca",
                "type": "instruction",
                "sample_size": 1000,  # Reduced for testing
                "priority": 1,
                "description": "High-quality instruction-following data"
            },
            "chatgpt_prompts": {
                "name": "fka/awesome-chatgpt-prompts",
                "type": "prompts",
                "sample_size": "all",
                "priority": 2,
                "description": "High-quality prompt templates"
            },
            "gsm8k": {
                "name": "openai/gsm8k",
                "type": "reasoning",
                "sample_size": 500,  # Reduced for testing
                "priority": 3,
                "description": "Math reasoning problems",
                "config": "main"  # Fixed config issue
            }
        }
    
    def load_alpaca_dataset(self) -> tuple[List[str], List[Dict]]:
        """Load Alpaca instruction-following dataset"""
        print("📥 Loading Alpaca dataset (instruction-following)...")
        
        try:
            dataset = load_dataset(
                self.datasets_config["alpaca"]["name"], 
                split=f"train[:{self.datasets_config['alpaca']['sample_size']}]"
            )
            
            documents = []
            metadatas = []
            
            for i, example in enumerate(dataset):
                if 'instruction' in example and 'output' in example:
                    text = f"Instruction: {example['instruction']}\nOutput: {example['output']}"
                elif 'text' in example:
                    text = example['text']
                else:
                    continue
                
                documents.append(text)
                metadatas.append({
                    "source": "huggingface",
                    "dataset": "alpaca",
                    "type": "instruction",
                    "index": i,
                    "priority": 1
                })
            
            print(f"✅ Loaded {len(documents)} Alpaca examples")
            return documents, metadatas
            
        except Exception as e:
            print(f"❌ Error loading Alpaca: {e}")
            return [], []
    
    def load_chatgpt_prompts_dataset(self) -> tuple[List[str], List[Dict]]:
        """Load ChatGPT prompts dataset"""
        print("📥 Loading ChatGPT prompts dataset...")
        
        try:
            dataset = load_dataset(self.datasets_config["chatgpt_prompts"]["name"], split="train")
            
            documents = []
            metadatas = []
            
            for i, example in enumerate(dataset):
                if 'prompt' in example:
                    text = f"Prompt: {example['prompt']}"
                elif 'text' in example:
                    text = example['text']
                else:
                    continue
                
                documents.append(text)
                metadatas.append({
                    "source": "huggingface",
                    "dataset": "chatgpt-prompts",
                    "type": "prompts",
                    "index": i,
                    "priority": 2
                })
            
            print(f"✅ Loaded {len(documents)} ChatGPT prompt examples")
            return documents, metadatas
            
        except Exception as e:
            print(f"❌ Error loading ChatGPT prompts: {e}")
            return [], []
    
    def load_gsm8k_dataset(self) -> tuple[List[str], List[Dict]]:
        """Load GSM8K math reasoning dataset (fixed config)"""
        print("📥 Loading GSM8K dataset (math reasoning)...")
        
        try:
            dataset = load_dataset(
                self.datasets_config["gsm8k"]["name"],
                self.datasets_config["gsm8k"]["config"],  # Use 'main' config
                split=f"train[:{self.datasets_config['gsm8k']['sample_size']}]"
            )
            
            documents = []
            metadatas = []
            
            for i, example in enumerate(dataset):
                if 'question' in example and 'answer' in example:
                    text = f"Question: {example['question']}\nAnswer: {example['answer']}"
                elif 'text' in example:
                    text = example['text']
                else:
                    continue
                
                documents.append(text)
                metadatas.append({
                    "source": "huggingface",
                    "dataset": "gsm8k",
                    "type": "reasoning",
                    "index": i,
                    "priority": 3
                })
            
            print(f"✅ Loaded {len(documents)} GSM8K examples")
            return documents, metadatas
            
        except Exception as e:
            print(f"❌ Error loading GSM8K: {e}")
            return [], []
    
    def load_all_optimal_datasets(self):
        """Load all optimal datasets in priority order"""
        print("🚀 Loading Optimal Hugging Face Datasets (Fixed)")
        print("=" * 55)
        
        total_documents = 0
        
        # Load datasets in priority order
        datasets_to_load = [
            ("alpaca", self.load_alpaca_dataset),
            ("chatgpt_prompts", self.load_chatgpt_prompts_dataset),
            ("gsm8k", self.load_gsm8k_dataset)
        ]
        
        for dataset_name, load_func in datasets_to_load:
            print(f"\n📚 Loading {dataset_name}...")
            documents, metadatas = load_func()
            
            if documents:
                self.rag.add_documents(documents, metadatas)
                total_documents += len(documents)
                print(f"✅ Added {len(documents)} documents from {dataset_name}")
            else:
                print(f"❌ Failed to load {dataset_name}")
        
        print(f"\n🎉 Total documents loaded: {total_documents}")
        return total_documents

def main():
    """Main function to load optimal datasets"""
    print("🎯 Optimal Hugging Face Datasets for RAG (Fixed)")
    print("=" * 50)
    
    # Initialize dataset loader
    hf_datasets = OptimalHFDatasetsFixed()
    
    # Load all optimal datasets
    total_docs = hf_datasets.load_all_optimal_datasets()
    
    # Test queries
    print("\n🧪 Testing RAG with Optimal Datasets")
    print("=" * 40)
    
    test_queries = [
        "How do I write a Python function to sort a list?",
        "What is machine learning and how does it work?",
        "Give me a good prompt for creative writing",
        "Solve this math problem: What is 15% of 200?",
        "Explain the concept of recursion in programming"
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        results = hf_datasets.rag.search(query, k=3)
        
        if results:
            print(f"🔍 Found {len(results)} relevant documents:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['text'][:100]}... (score: {result['distance']:.3f})")
        else:
            print("   No relevant documents found")

if __name__ == "__main__":
    main()