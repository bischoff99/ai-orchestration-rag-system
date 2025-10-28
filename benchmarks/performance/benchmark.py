#!/usr/bin/env python3
"""
Ollama Model Performance Benchmark
Tests different quantization levels and records performance metrics
"""

import subprocess
import time
import json
import psutil
import os
from datetime import datetime
import statistics

class OllamaBenchmark:
    def __init__(self):
        self.results = []
        self.baselines = {
            "embedder": "nomic-embed-text:latest",
            "llama-assistant": "llama3.2:latest",
            "llama70b-analyst": "llama3.1:70b",
            "mistral-summarizer": "mistral:latest",
            "qwen-coder32": "qwen2.5-coder:32b"
        }

    def get_system_info(self):
        """Get current system RAM and CPU info"""
        return {
            "timestamp": datetime.now().isoformat(),
            "ram_total": psutil.virtual_memory().total / (1024**3),  # GB
            "ram_available": psutil.virtual_memory().available / (1024**3),  # GB
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1)
        }

    def test_model_performance(self, model_name, prompt, iterations=3):
        """Test model performance and return metrics"""
        print(f"🧪 Testing {model_name}...")

        metrics = []
        system_before = self.get_system_info()

        for i in range(iterations):
            start_time = time.time()
            start_ram = psutil.virtual_memory().used / (1024**3)

            try:
                # Run the model
                result = subprocess.run([
                    'ollama', 'run', model_name, prompt
                ], capture_output=True, text=True, timeout=60)

                end_time = time.time()
                end_ram = psutil.virtual_memory().used / (1024**3)

                # Calculate metrics
                duration = end_time - start_time
                ram_used = end_ram - start_ram

                # Count tokens (rough estimate based on response length)
                response_tokens = len(result.stdout.split()) if result.returncode == 0 else 0
                tokens_per_sec = response_tokens / duration if duration > 0 else 0

                metrics.append({
                    "iteration": i + 1,
                    "duration_sec": duration,
                    "ram_used_gb": ram_used,
                    "tokens_generated": response_tokens,
                    "tokens_per_sec": tokens_per_sec,
                    "success": result.returncode == 0,
                    "error": result.stderr if result.returncode != 0 else None
                })

                print(f"  Iteration {i+1}: {tokens_per_sec:.1f} tokens/sec, {ram_used:.2f}GB RAM")

            except subprocess.TimeoutExpired:
                metrics.append({
                    "iteration": i + 1,
                    "duration_sec": 60,
                    "ram_used_gb": 0,
                    "tokens_generated": 0,
                    "tokens_per_sec": 0,
                    "success": False,
                    "error": "Timeout after 60 seconds"
                })
                print(f"  Iteration {i+1}: Timeout")

        # Calculate averages
        successful_runs = [m for m in metrics if m["success"]]
        if successful_runs:
            avg_tokens_sec = statistics.mean([m["tokens_per_sec"] for m in successful_runs])
            avg_ram_gb = statistics.mean([m["ram_used_gb"] for m in successful_runs])
            avg_duration = statistics.mean([m["duration_sec"] for m in successful_runs])
        else:
            avg_tokens_sec = 0
            avg_ram_gb = 0
            avg_duration = 0

        return {
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "system_info": system_before,
            "test_prompt": prompt,
            "iterations": iterations,
            "metrics": metrics,
            "averages": {
                "tokens_per_sec": avg_tokens_sec,
                "ram_used_gb": avg_ram_gb,
                "duration_sec": avg_duration,
                "success_rate": len(successful_runs) / iterations
            }
        }

    def run_comprehensive_benchmark(self):
        """Run benchmarks on all available models"""
        test_prompts = {
            "embedder": "Calculate the embedding vector for: machine learning",
            "llama-assistant": "Explain the concept of quantization in neural networks in 2 sentences.",
            "llama70b-analyst": "Analyze the trade-offs between model accuracy and inference speed in large language models.",
            "mistral-summarizer": "Summarize the key benefits and challenges of model quantization for deployment.",
            "qwen-coder32": "Write a Python function to calculate Fibonacci numbers with memoization."
        }

        print("🚀 Starting Comprehensive Ollama Benchmark")
        print("=" * 50)

        for model_name, prompt in test_prompts.items():
            if self.model_exists(model_name):
                result = self.test_model_performance(model_name, prompt)
                self.results.append(result)
                print(f"✅ {model_name}: {result['averages']['tokens_per_sec']:.1f} tokens/sec, {result['averages']['ram_used_gb']:.2f}GB RAM\n")
            else:
                print(f"❌ {model_name}: Model not found\n")

        return self.results

    def model_exists(self, model_name):
        """Check if model exists"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            return model_name in result.stdout
        except:
            return False

    def save_results(self, filename=None):
        """Save benchmark results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/Users/andrejsp/ai/benchmarks/performance/benchmark_results_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump({
                "benchmark_info": {
                    "date": datetime.now().isoformat(),
                    "tool": "ollama_benchmark.py",
                    "description": "Performance benchmarking of Ollama models with different quantization levels"
                },
                "results": self.results
            }, f, indent=2)

        print(f"💾 Results saved to: {filename}")
        return filename

def main():
    benchmark = OllamaBenchmark()
    results = benchmark.run_comprehensive_benchmark()
    benchmark.save_results()

    # Print summary
    print("\n📊 BENCHMARK SUMMARY")
    print("=" * 50)
    for result in results:
        avg = result["averages"]
        print(f"{result['model']:<20} | {avg['tokens_per_sec']:6.1f} tok/s | {avg['ram_used_gb']:5.2f}GB | {avg['success_rate']:4.1%}")

if __name__ == "__main__":
    main()
