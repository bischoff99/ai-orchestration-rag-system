#!/usr/bin/env python3
"""
Simple Ollama Performance Benchmark
Tests token generation speed and basic metrics
"""

import subprocess
import time
import json
import os
from datetime import datetime

def test_model_speed(model_name, prompt, max_duration=30):
    """Test how fast a model generates tokens"""
    print(f"🧪 Testing {model_name}...")

    start_time = time.time()

    try:
        # Run the model with timeout
        result = subprocess.run([
            'ollama', 'run', model_name, prompt
        ], capture_output=True, text=True, timeout=max_duration)

        end_time = time.time()
        duration = end_time - start_time

        # Count tokens (rough estimate)
        response_text = result.stdout.strip()
        tokens = len(response_text.split())
        tokens_per_sec = tokens / duration if duration > 0 else 0

        success = result.returncode == 0
        error = result.stderr if not success else None

        print(f"  Duration: {duration:.2f}s")
        print(f"  Tokens: {tokens}")
        print(f"  Speed: {tokens_per_sec:.1f} tokens/sec")
        print(f"  Success: {success}")

        return {
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "duration_sec": duration,
            "tokens_generated": tokens,
            "tokens_per_sec": tokens_per_sec,
            "success": success,
            "error": error
        }

    except subprocess.TimeoutExpired:
        print(f"  Timeout after {max_duration}s")
        return {
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "duration_sec": max_duration,
            "tokens_generated": 0,
            "tokens_per_sec": 0,
            "success": False,
            "error": f"Timeout after {max_duration} seconds"
        }

def run_benchmarks():
    """Run benchmarks on all available models"""

    test_cases = [
        {
            "model": "gemma2:2b",
            "prompt": "Explain quantum computing in simple terms."
        },
        {
            "model": "llama-assistant",
            "prompt": "What are the benefits of model quantization?"
        },
        {
            "model": "llama70b-analyst",
            "prompt": "Analyze the performance trade-offs between different quantization methods."
        },
        {
            "model": "mistral-summarizer",
            "prompt": "Summarize the key advantages of using quantized models in production."
        },
        {
            "model": "qwen-coder32",
            "prompt": "Write a function to calculate fibonacci numbers efficiently."
        },
        {
            "model": "embedder",
            "prompt": "Calculate embedding for machine learning"
        }
    ]

    results = []
    print("🚀 Ollama Performance Benchmark")
    print("=" * 50)

    for test_case in test_cases:
        result = test_model_speed(test_case["model"], test_case["prompt"])
        results.append(result)
        print()

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"/Users/andrejsp/ai/benchmarks/performance/benchmark_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump({
            "benchmark_info": {
                "date": datetime.now().isoformat(),
                "description": "Performance benchmarking of Ollama models"
            },
            "results": results
        }, f, indent=2)

    print(f"💾 Results saved to: {output_file}")
    return results

def print_summary(results):
    """Print a summary of benchmark results"""
    print("\n📊 BENCHMARK SUMMARY")
    print("=" * 60)
    print("Model                Speed (tok/s) Duration (s) Status")
    print("-" * 60)

    for result in results:
        status = "✅ OK" if result["success"] else "❌ FAIL"
        speed = "{:7.1f}".format(result['tokens_per_sec'])
        duration = "{:7.2f}".format(result['duration_sec'])
        print(f"{result['model']:<20} {speed:<12} {duration:<12} {status:<10}")

    # Calculate averages for successful runs
    successful = [r for r in results if r["success"]]
    if successful:
        avg_speed = sum(r["tokens_per_sec"] for r in successful) / len(successful)
        print("-" * 60)
        avg_speed_str = "{:7.1f}".format(avg_speed)
        print(f"{'Average Speed':<20} {avg_speed_str:<12} tok/s")

if __name__ == "__main__":
    results = run_benchmarks()
    print_summary(results)
