#!/usr/bin/env python3
"""
Parallel Execution Script for AI Infrastructure
Demonstrates safe parallel execution of various AI operations
"""

import os
import sys
import time
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Add examples to path
sys.path.append("/Users/andrejsp/ai/examples")

def run_command(cmd, description, timeout=300):
    """Run a command with timeout and error handling"""
    print(f"🚀 Starting: {description}")
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd="/Users/andrejsp/ai"
        )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ Completed: {description} ({duration:.1f}s)")
            return {
                "description": description,
                "status": "success",
                "duration": duration,
                "output": result.stdout
            }
        else:
            print(f"❌ Failed: {description} ({duration:.1f}s)")
            print(f"   Error: {result.stderr}")
            return {
                "description": description,
                "status": "failed",
                "duration": duration,
                "error": result.stderr
            }
            
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        print(f"⏰ Timeout: {description} ({duration:.1f}s)")
        return {
            "description": description,
            "status": "timeout",
            "duration": duration,
            "error": f"Timeout after {timeout}s"
        }
    except Exception as e:
        duration = time.time() - start_time
        print(f"💥 Exception: {description} ({duration:.1f}s)")
        return {
            "description": description,
            "status": "exception",
            "duration": duration,
            "error": str(e)
        }

def create_test_data():
    """Create test data for parallel operations"""
    print("📁 Creating test data...")
    
    # Create test directories
    os.makedirs("/Users/andrejsp/data/parallel_test", exist_ok=True)
    os.makedirs("/Users/andrejsp/data/coding_docs", exist_ok=True)
    os.makedirs("/Users/andrejsp/data/technical_docs", exist_ok=True)
    os.makedirs("/Users/andrejsp/data/ai_docs", exist_ok=True)
    
    # Create test documents
    test_docs = {
        "/Users/andrejsp/data/coding_docs/python.txt": "Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms and has a large standard library.",
        "/Users/andrejsp/data/coding_docs/javascript.txt": "JavaScript is a dynamic programming language commonly used for web development. It enables interactive web pages and is an essential part of web applications.",
        "/Users/andrejsp/data/technical_docs/docker.txt": "Docker is a containerization platform that packages applications and dependencies into containers. It ensures consistency across different environments.",
        "/Users/andrejsp/data/technical_docs/kubernetes.txt": "Kubernetes is an open-source container orchestration system for automating software deployment, scaling, and management.",
        "/Users/andrejsp/data/ai_docs/ml.txt": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed.",
        "/Users/andrejsp/data/ai_docs/dl.txt": "Deep learning is a subset of machine learning that uses neural networks with multiple layers to model and understand complex patterns in data."
    }
    
    for file_path, content in test_docs.items():
        with open(file_path, 'w') as f:
            f.write(content)
    
    print(f"✅ Created {len(test_docs)} test documents")

def parallel_ingestion():
    """Run document ingestion in parallel"""
    print("\n🔄 Parallel Document Ingestion")
    print("=" * 50)
    
    commands = [
        {
            "cmd": "source envs/mlx_qlora/bin/activate && python scripts/ingest_docs.py --path /Users/andrejsp/data/coding_docs --collection coding_knowledge --batch 1",
            "description": "Ingest coding documents"
        },
        {
            "cmd": "source envs/mlx_qlora/bin/activate && python scripts/ingest_docs.py --path /Users/andrejsp/data/technical_docs --collection technical_knowledge --batch 1",
            "description": "Ingest technical documents"
        },
        {
            "cmd": "source envs/mlx_qlora/bin/activate && python scripts/ingest_docs.py --path /Users/andrejsp/data/ai_docs --collection ai_knowledge --batch 1",
            "description": "Ingest AI documents"
        }
    ]
    
    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all tasks
        future_to_cmd = {
            executor.submit(run_command, cmd["cmd"], cmd["description"], 60): cmd 
            for cmd in commands
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_cmd):
            result = future.result()
            results.append(result)
    
    return results

def parallel_evaluation():
    """Run RAG evaluation in parallel"""
    print("\n🔍 Parallel RAG Evaluation")
    print("=" * 50)
    
    commands = [
        {
            "cmd": "source envs/mlx_qlora/bin/activate && python scripts/evaluate_rag.py --collections coding_knowledge --metrics latency,accuracy",
            "description": "Evaluate coding knowledge"
        },
        {
            "cmd": "source envs/mlx_qlora/bin/activate && python scripts/evaluate_rag.py --collections technical_knowledge --metrics latency,accuracy",
            "description": "Evaluate technical knowledge"
        },
        {
            "cmd": "source envs/mlx_qlora/bin/activate && python scripts/evaluate_rag.py --collections ai_knowledge --metrics latency,accuracy",
            "description": "Evaluate AI knowledge"
        }
    ]
    
    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_cmd = {
            executor.submit(run_command, cmd["cmd"], cmd["description"], 120): cmd 
            for cmd in commands
        }
        
        for future in as_completed(future_to_cmd):
            result = future.result()
            results.append(result)
    
    return results

def parallel_fine_tuning():
    """Run fine-tuning in parallel (different models)"""
    print("\n🎯 Parallel Fine-tuning")
    print("=" * 50)
    
    # Create different datasets
    datasets = {
        "/Users/andrejsp/datasets/coding.jsonl": [
            {"text": "def hello_world(): print('Hello, World!')"},
            {"text": "class Calculator: def add(self, a, b): return a + b"},
            {"text": "import pandas as pd; df = pd.DataFrame()"}
        ],
        "/Users/andrejsp/datasets/technical.jsonl": [
            {"text": "Docker containers provide isolation and portability"},
            {"text": "Kubernetes manages containerized applications at scale"},
            {"text": "CI/CD pipelines automate software delivery"}
        ]
    }
    
    # Create datasets
    for dataset_path, data in datasets.items():
        with open(dataset_path, 'w') as f:
            for item in data:
                f.write(f"{item}\n")
    
    commands = [
        {
            "cmd": f"source envs/mlx_qlora/bin/activate && python scripts/fine_tune_qlora.py --base microsoft/DialoGPT-small --dataset /Users/andrejsp/datasets/coding.jsonl --epochs 1 --lr 3e-4 --lora_rank 4 --output ./fine_tuned_models/coding_model",
            "description": "Fine-tune coding model"
        },
        {
            "cmd": f"source envs/mlx_qlora/bin/activate && python scripts/fine_tune_qlora.py --base microsoft/DialoGPT-small --dataset /Users/andrejsp/datasets/technical.jsonl --epochs 1 --lr 3e-4 --lora_rank 4 --output ./fine_tuned_models/technical_model",
            "description": "Fine-tune technical model"
        }
    ]
    
    results = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_to_cmd = {
            executor.submit(run_command, cmd["cmd"], cmd["description"], 180): cmd 
            for cmd in commands
        }
        
        for future in as_completed(future_to_cmd):
            result = future.result()
            results.append(result)
    
    return results

def parallel_monitoring():
    """Run monitoring and benchmarking in parallel"""
    print("\n📊 Parallel Monitoring")
    print("=" * 50)
    
    commands = [
        {
            "cmd": "source envs/mlx_qlora/bin/activate && python scripts/daily_benchmark.py",
            "description": "Daily benchmark"
        },
        {
            "cmd": "ollama list",
            "description": "List Ollama models"
        },
        {
            "cmd": "vm_stat 1 | head -5",
            "description": "System memory stats"
        }
    ]
    
    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_cmd = {
            executor.submit(run_command, cmd["cmd"], cmd["description"], 60): cmd 
            for cmd in commands
        }
        
        for future in as_completed(future_to_cmd):
            result = future.result()
            results.append(result)
    
    return results

def print_summary(all_results):
    """Print summary of all parallel operations"""
    print("\n🎉 Parallel Execution Summary")
    print("=" * 60)
    
    total_operations = len(all_results)
    successful = len([r for r in all_results if r["status"] == "success"])
    failed = len([r for r in all_results if r["status"] == "failed"])
    timeouts = len([r for r in all_results if r["status"] == "timeout"])
    exceptions = len([r for r in all_results if r["status"] == "exception"])
    
    total_duration = sum(r["duration"] for r in all_results)
    avg_duration = total_duration / total_operations if total_operations > 0 else 0
    
    print(f"📊 Overall Statistics:")
    print(f"   - Total Operations: {total_operations}")
    print(f"   - Successful: {successful} ({successful/total_operations*100:.1f}%)")
    print(f"   - Failed: {failed} ({failed/total_operations*100:.1f}%)")
    print(f"   - Timeouts: {timeouts}")
    print(f"   - Exceptions: {exceptions}")
    print(f"   - Total Duration: {total_duration:.1f}s")
    print(f"   - Average Duration: {avg_duration:.1f}s")
    
    print(f"\n📋 Operation Details:")
    for result in all_results:
        status_icon = "✅" if result["status"] == "success" else "❌" if result["status"] == "failed" else "⏰" if result["status"] == "timeout" else "💥"
        print(f"   {status_icon} {result['description']}: {result['duration']:.1f}s")

def main():
    """Main parallel execution function"""
    print("🚀 AI Infrastructure Parallel Execution")
    print("=" * 60)
    
    start_time = time.time()
    all_results = []
    
    # Step 1: Create test data
    create_test_data()
    
    # Step 2: Parallel ingestion
    ingestion_results = parallel_ingestion()
    all_results.extend(ingestion_results)
    
    # Step 3: Parallel evaluation
    evaluation_results = parallel_evaluation()
    all_results.extend(evaluation_results)
    
    # Step 4: Parallel fine-tuning
    fine_tuning_results = parallel_fine_tuning()
    all_results.extend(fine_tuning_results)
    
    # Step 5: Parallel monitoring
    monitoring_results = parallel_monitoring()
    all_results.extend(monitoring_results)
    
    total_time = time.time() - start_time
    
    # Print summary
    print_summary(all_results)
    
    print(f"\n⏱️  Total Execution Time: {total_time:.1f}s")
    print(f"🎯 Parallel Efficiency: {sum(r['duration'] for r in all_results)/total_time:.1f}x speedup")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Check individual results above")
    print(f"   2. Review generated models in ./fine_tuned_models/")
    print(f"   3. Test RAG collections with queries")
    print(f"   4. Monitor system performance")

if __name__ == "__main__":
    main()