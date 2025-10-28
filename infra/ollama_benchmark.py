#!/usr/bin/env python3
"""
Ollama Performance Benchmarking
Runs token throughput tests for quantized models
"""
import requests
import time
import json
import yaml
from datetime import datetime
import os
import subprocess

class OllamaBenchmark:
    def __init__(self, results_dir='/Users/andrejsp/ai/benchmarks/2025-10'):
        self.results_dir = results_dir
        self.models = [
            'llama3.1:8b-instruct-q4_K_M',
            'llama3.1:8b-instruct-q6_K', 
            'llama3.1:8b-instruct-q8_0',
            'llama3.1:8b-instruct-q5_K_M'
        ]
        os.makedirs(results_dir, exist_ok=True)
    
    def benchmark_model(self, model_name, prompt_length=100, max_tokens=200):
        """Benchmark a specific model"""
        print(f"🧪 Benchmarking {model_name}...")
        
        # Test prompt
        test_prompt = "Explain machine learning in detail. " * (prompt_length // 30)
        
        results = {
            'model': model_name,
            'timestamp': datetime.now().isoformat(),
            'prompt_length': len(test_prompt),
            'max_tokens': max_tokens,
            'tests': []
        }
        
        # Run multiple iterations
        for i in range(3):
            print(f"  Run {i+1}/3...")
            
            start_time = time.time()
            
            try:
                response = requests.post(
                    'http://localhost:11434/api/generate',
                    json={
                        'model': model_name,
                        'prompt': test_prompt,
                        'stream': False,
                        'options': {
                            'num_predict': max_tokens,
                            'temperature': 0.7
                        }
                    },
                    timeout=120
                )
                
                end_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get('response', '')
                    
                    # Calculate metrics
                    total_time = end_time - start_time
                    tokens_generated = len(response_text.split())
                    tokens_per_second = tokens_generated / total_time if total_time > 0 else 0
                    
                    test_result = {
                        'iteration': i + 1,
                        'total_time_s': total_time,
                        'tokens_generated': tokens_generated,
                        'tokens_per_second': tokens_per_second,
                        'response_length': len(response_text),
                        'success': True
                    }
                    
                    print(f"    ✅ {tokens_per_second:.2f} tokens/sec")
                    
                else:
                    test_result = {
                        'iteration': i + 1,
                        'error': f"HTTP {response.status_code}",
                        'success': False
                    }
                    print(f"    ❌ HTTP {response.status_code}")
                    
            except Exception as e:
                test_result = {
                    'iteration': i + 1,
                    'error': str(e),
                    'success': False
                }
                print(f"    ❌ {e}")
            
            results['tests'].append(test_result)
            time.sleep(2)  # Cool down between tests
        
        # Calculate averages
        successful_tests = [t for t in results['tests'] if t['success']]
        if successful_tests:
            results['summary'] = {
                'avg_tokens_per_second': sum(t['tokens_per_second'] for t in successful_tests) / len(successful_tests),
                'avg_total_time': sum(t['total_time_s'] for t in successful_tests) / len(successful_tests),
                'success_rate': len(successful_tests) / len(results['tests']) * 100
            }
        else:
            results['summary'] = {
                'avg_tokens_per_second': 0,
                'avg_total_time': 0,
                'success_rate': 0
            }
        
        return results
    
    def run_all_benchmarks(self):
        """Run benchmarks for all models"""
        print("🚀 Starting Ollama benchmark suite...")
        
        all_results = {
            'timestamp': datetime.now().isoformat(),
            'models': {}
        }
        
        for model in self.models:
            try:
                results = self.benchmark_model(model)
                all_results['models'][model] = results
                
                # Save individual model results
                model_file = f"{self.results_dir}/ollama_{model.replace(':', '_')}.yaml"
                with open(model_file, 'w') as f:
                    yaml.dump(results, f, default_flow_style=False)
                
            except Exception as e:
                print(f"❌ Failed to benchmark {model}: {e}")
                all_results['models'][model] = {'error': str(e)}
        
        # Save combined results
        combined_file = f"{self.results_dir}/ollama_benchmark_combined.yaml"
        with open(combined_file, 'w') as f:
            yaml.dump(all_results, f, default_flow_style=False)
        
        print(f"📊 Results saved to {self.results_dir}")
        return all_results
    
    def generate_report(self, results):
        """Generate human-readable benchmark report"""
        print("\n📈 OLLAMA BENCHMARK REPORT")
        print("=" * 50)
        
        for model, data in results['models'].items():
            if 'error' in data:
                print(f"\n❌ {model}: {data['error']}")
                continue
                
            summary = data.get('summary', {})
            print(f"\n🤖 {model}")
            print(f"   Tokens/sec: {summary.get('avg_tokens_per_second', 0):.2f}")
            print(f"   Avg time: {summary.get('avg_total_time', 0):.2f}s")
            print(f"   Success rate: {summary.get('success_rate', 0):.1f}%")

if __name__ == "__main__":
    benchmark = OllamaBenchmark()
    results = benchmark.run_all_benchmarks()
    benchmark.generate_report(results)