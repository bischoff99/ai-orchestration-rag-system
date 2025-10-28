#!/usr/bin/env python3
"""
Optimal Hugging Face Datasets for RAG System
Curated selection based on Context7 analysis and sequential thinking
"""

import os
import sys
from datasets import load_dataset
from typing import List, Dict, Any
import json

# Add the examples directory to path
sys.path.append('/Users/andrejsp/ai/examples')

from ollama_rag import OllamaRAG

class OptimalHFDatasets:
    """Optimal dataset selection for RAG system"""
    
    def __init__(self, rag_system: OllamaRAG):
        self.rag = rag_system
        self.datasets_config = {
            "alpaca": {
                "name": "tatsu-lab/alpaca",
                "type": "instruction",
                "sample_size": 5000,
                "priority": 1,
                "description": "High-quality instruction-following data for general assistant models"
            },
            "github_code": {
                "name": "nick007x/github-code-2025", 
                "type": "code",
                "sample_size": 10000,
                "priority": 2,
                "description": "Clean code repositories for coding models",
                "streaming": True
            },
            "chatgpt_prompts": {
                "name": "fka/awesome-chatgpt-prompts",
                "type": "prompts",
                "sample_size": "all",
                "priority": 3,
                "description": "High-quality prompt templates"
            },
            "gsm8k": {
                "name": "openai/gsm8k",
                "type": "reasoning",
                "sample_size": 2000,
                "priority": 4,
                "description": "Math reasoning problems for analytical models"
            },
            "fineweb_edu": {
                "name": "HuggingFaceFW/fineweb-edu",
                "type": "educational",
                "sample_size": 5000,
                "priority": 5,
                "description": "Educational content for general knowledge",
                "streaming": True
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
                # Create instruction-output pairs
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
    
    def load_github_code_dataset(self) -> tuple[List[str], List[Dict]]:
        """Load GitHub code dataset with streaming"""
        print("📥 Loading GitHub Code 2025 dataset (streaming)...")
        
        try:
            dataset = load_dataset(
                self.datasets_config["github_code"]["name"],
                split="train",
                streaming=True
            )
            
            documents = []
            metadatas = []
            sample_size = self.datasets_config["github_code"]["sample_size"]
            
            for i, example in enumerate(dataset):
                if i >= sample_size:
                    break
                
                # Extract code content
                if 'text' in example:
                    text = example['text']
                elif 'content' in example:
                    text = example['content']
                elif 'code' in example:
                    text = example['code']
                else:
                    continue
                
                # Truncate long code
                if len(text) > 2000:
                    text = text[:2000] + "..."
                
                documents.append(text)
                metadatas.append({
                    "source": "huggingface",
                    "dataset": "github-code-2025",
                    "type": "code",
                    "index": i,
                    "priority": 2
                })
            
            print(f"✅ Loaded {len(documents)} GitHub code examples")
            return documents, metadatas
            
        except Exception as e:
            print(f"❌ Error loading GitHub code: {e}")
            return [], []
    
    def load_chatgpt_prompts_dataset(self) -> tuple[List[str], List[Dict]]:
        """Load ChatGPT prompts dataset"""
        print("📥 Loading ChatGPT prompts dataset...")
        
        try:
            dataset = load_dataset(self.datasets_config["chatgpt_prompts"]["name"], split="train")
            
            documents = []
            metadatas = []
            
            for i, example in enumerate(dataset):
                # Extract prompt content
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
                    "priority": 3
                })
            
            print(f"✅ Loaded {len(documents)} ChatGPT prompt examples")
            return documents, metadatas
            
        except Exception as e:
            print(f"❌ Error loading ChatGPT prompts: {e}")
            return [], []
    
    def load_gsm8k_dataset(self) -> tuple[List[str], List[Dict]]:
        """Load GSM8K math reasoning dataset"""
        print("📥 Loading GSM8K dataset (math reasoning)...")
        
        try:
            dataset = load_dataset(
                self.datasets_config["gsm8k"]["name"],
                split=f"train[:{self.datasets_config['gsm8k']['sample_size']}]"
            )
            
            documents = []
            metadatas = []
            
            for i, example in enumerate(dataset):
                # Create question-answer pairs
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
                    "priority": 4
                })
            
            print(f"✅ Loaded {len(documents)} GSM8K examples")
            return documents, metadatas
            
        except Exception as e:
            print(f"❌ Error loading GSM8K: {e}")
            return [], []
    
    def load_fineweb_edu_dataset(self) -> tuple[List[str], List[Dict]]:
        """Load FineWeb-Edu educational dataset with streaming"""
        print("📥 Loading FineWeb-Edu dataset (streaming)...")
        
        try:
            dataset = load_dataset(
                self.datasets_config["fineweb_edu"]["name"],
                split="train",
                streaming=True
            )
            
            documents = []
            metadatas = []
            sample_size = self.datasets_config["fineweb_edu"]["sample_size"]
            
            for i, example in enumerate(dataset):
                if i >= sample_size:
                    break
                
                if 'text' in example:
                    text = example['text']
                    # Truncate long text
                    if len(text) > 1500:
                        text = text[:1500] + "..."
                    
                    documents.append(text)
                    metadatas.append({
                        "source": "huggingface",
                        "dataset": "fineweb-edu",
                        "type": "educational",
                        "index": i,
                        "priority": 5
                    })
            
            print(f"✅ Loaded {len(documents)} FineWeb-Edu examples")
            return documents, metadatas
            
        except Exception as e:
            print(f"❌ Error loading FineWeb-Edu: {e}")
            return [], []
    
    def load_all_optimal_datasets(self):
        """Load all optimal datasets in priority order"""
        print("🚀 Loading Optimal Hugging Face Datasets")
        print("=" * 50)
        
        total_documents = 0
        
        # Load datasets in priority order
        datasets_to_load = [
            ("alpaca", self.load_alpaca_dataset),
            ("github_code", self.load_github_code_dataset),
            ("chatgpt_prompts", self.load_chatgpt_prompts_dataset),
            ("gsm8k", self.load_gsm8k_dataset),
            ("fineweb_edu", self.load_fineweb_edu_dataset)
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
    print("🎯 Optimal Hugging Face Datasets for RAG")
    print("=" * 45)
    
    # Initialize RAG system
    rag = OllamaRAG(collection_name="optimal_hf_datasets", embedding_model="embedder")
    hf_datasets = OptimalHFDatasets(rag)
    
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
        response = rag.query_ollama(query, k=3)
        print(f"🤖 Answer: {response['answer'][:200]}...")
        print(f"📚 Sources: {len(response['sources'])} documents")

if __name__ == "__main__":
    main()