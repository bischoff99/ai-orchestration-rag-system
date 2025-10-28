#!/usr/bin/env python3
"""
Simple Hugging Face Datasets Integration
Loads optimal datasets using Sentence Transformers embeddings
"""

import os
import sys
from datasets import load_dataset
from typing import List, Dict, Any
import json

# Add the examples directory to path
sys.path.append('/Users/andrejsp/ai/examples')

from rag_setup import RAGVectorDB

def load_optimal_datasets():
    """Load the most valuable datasets for RAG"""
    print("🎯 Loading Optimal Hugging Face Datasets")
    print("=" * 45)
    
    # Initialize RAG system
    rag = RAGVectorDB(backend="chroma", collection_name="optimal_hf_datasets")
    
    total_documents = 0
    
    # 1. Load Alpaca (instruction-following)
    print("\n📚 Loading Alpaca dataset...")
    try:
        dataset = load_dataset("tatsu-lab/alpaca", split="train[:1000]")
        documents = []
        metadatas = []
        
        for i, example in enumerate(dataset):
            if 'instruction' in example and 'output' in example:
                text = f"Instruction: {example['instruction']}\nOutput: {example['output']}"
                documents.append(text)
                metadatas.append({
                    "source": "huggingface",
                    "dataset": "alpaca",
                    "type": "instruction",
                    "index": i
                })
        
        rag.add_documents(documents, metadatas)
        total_documents += len(documents)
        print(f"✅ Added {len(documents)} Alpaca examples")
        
    except Exception as e:
        print(f"❌ Error loading Alpaca: {e}")
    
    # 2. Load ChatGPT Prompts
    print("\n📚 Loading ChatGPT prompts...")
    try:
        dataset = load_dataset("fka/awesome-chatgpt-prompts", split="train")
        documents = []
        metadatas = []
        
        for i, example in enumerate(dataset):
            if 'prompt' in example:
                text = f"Prompt: {example['prompt']}"
                documents.append(text)
                metadatas.append({
                    "source": "huggingface",
                    "dataset": "chatgpt-prompts",
                    "type": "prompts",
                    "index": i
                })
        
        rag.add_documents(documents, metadatas)
        total_documents += len(documents)
        print(f"✅ Added {len(documents)} ChatGPT prompt examples")
        
    except Exception as e:
        print(f"❌ Error loading ChatGPT prompts: {e}")
    
    # 3. Load GSM8K (math reasoning)
    print("\n📚 Loading GSM8K dataset...")
    try:
        dataset = load_dataset("openai/gsm8k", "main", split="train[:500]")
        documents = []
        metadatas = []
        
        for i, example in enumerate(dataset):
            if 'question' in example and 'answer' in example:
                text = f"Question: {example['question']}\nAnswer: {example['answer']}"
                documents.append(text)
                metadatas.append({
                    "source": "huggingface",
                    "dataset": "gsm8k",
                    "type": "reasoning",
                    "index": i
                })
        
        rag.add_documents(documents, metadatas)
        total_documents += len(documents)
        print(f"✅ Added {len(documents)} GSM8K examples")
        
    except Exception as e:
        print(f"❌ Error loading GSM8K: {e}")
    
    print(f"\n🎉 Total documents loaded: {total_documents}")
    
    # Test the RAG system
    print("\n🧪 Testing RAG with Optimal Datasets")
    print("=" * 40)
    
    test_queries = [
        "How do I write a Python function?",
        "What is machine learning?",
        "Give me a creative writing prompt",
        "Solve: What is 15% of 200?",
        "Explain recursion in programming"
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        results = rag.search(query, k=3)
        
        if results:
            print(f"🔍 Found {len(results)} relevant documents:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['text'][:80]}... (score: {result['distance']:.3f})")
        else:
            print("   No relevant documents found")

if __name__ == "__main__":
    load_optimal_datasets()