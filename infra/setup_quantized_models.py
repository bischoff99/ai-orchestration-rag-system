#!/usr/bin/env python3
"""
Setup Quantized Models for Ultra-Fast RAG
Downloads and configures quantized Ollama models for maximum performance
"""
import requests
import json
import time
import logging
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Any
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuantizedModelManager:
    """Manager for quantized Ollama models"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.models = {
            "ultra_fast": {
                "name": "llama3.1:8b-instruct-q2_K",
                "description": "Ultra-fast, lowest quality (2-bit quantization)",
                "use_case": "Simple queries, real-time responses",
                "expected_speed": "0.01-0.02s",
                "quality": "Basic"
            },
            "fast": {
                "name": "llama3.1:8b-instruct-q4_K_M",
                "description": "Fast, balanced quality (4-bit quantization)",
                "use_case": "General queries, good balance",
                "expected_speed": "0.02-0.05s",
                "quality": "Good"
            },
            "quality": {
                "name": "llama3.1:8b-instruct-q5_K_M",
                "description": "High quality, moderate speed (5-bit quantization)",
                "use_case": "Complex queries, detailed responses",
                "expected_speed": "0.05-0.1s",
                "quality": "High"
            },
            "ultra_quality": {
                "name": "llama3.1:8b-instruct-q8_0",
                "description": "Ultra-high quality, slower (8-bit quantization)",
                "use_case": "Complex analysis, research",
                "expected_speed": "0.1-0.2s",
                "quality": "Ultra-High"
            }
        }
        self.performance_results = {}
    
    def check_ollama_health(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Ollama is running")
                return True
            else:
                logger.error(f"❌ Ollama health check failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Ollama health check error: {e}")
            return False
    
    def list_installed_models(self) -> List[str]:
        """List currently installed models"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                logger.info(f"Found {len(models)} installed models: {models}")
                return models
            else:
                logger.error(f"Failed to list models: HTTP {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry"""
        try:
            logger.info(f"Pulling model: {model_name}")
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Successfully pulled {model_name}")
                return True
            else:
                logger.error(f"❌ Failed to pull {model_name}: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Timeout pulling {model_name}")
            return False
        except Exception as e:
            logger.error(f"❌ Error pulling {model_name}: {e}")
            return False
    
    def benchmark_model(self, model_name: str, test_prompts: List[str]) -> Dict[str, Any]:
        """Benchmark a model's performance"""
        logger.info(f"Benchmarking model: {model_name}")
        
        results = {
            "model": model_name,
            "total_queries": len(test_prompts),
            "successful_queries": 0,
            "failed_queries": 0,
            "total_latency": 0.0,
            "avg_latency": 0.0,
            "min_latency": float('inf'),
            "max_latency": 0.0,
            "tokens_per_second": 0.0,
            "responses": []
        }
        
        for i, prompt in enumerate(test_prompts):
            try:
                start_time = time.time()
                
                payload = {
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 50
                    }
                }
                
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    latency = time.time() - start_time
                    
                    results["successful_queries"] += 1
                    results["total_latency"] += latency
                    results["min_latency"] = min(results["min_latency"], latency)
                    results["max_latency"] = max(results["max_latency"], latency)
                    
                    # Calculate tokens per second
                    if "eval_count" in data and "eval_duration" in data:
                        tokens_per_second = data["eval_count"] / (data["eval_duration"] / 1e9)
                        results["tokens_per_second"] += tokens_per_second
                    
                    results["responses"].append({
                        "prompt": prompt,
                        "response": data.get("response", "")[:100] + "...",
                        "latency": latency,
                        "tokens_per_second": tokens_per_second if "eval_count" in data else 0
                    })
                    
                    logger.info(f"  Query {i+1}: {latency:.3f}s")
                else:
                    results["failed_queries"] += 1
                    logger.error(f"  Query {i+1}: Failed - HTTP {response.status_code}")
                
            except Exception as e:
                results["failed_queries"] += 1
                logger.error(f"  Query {i+1}: Error - {e}")
        
        # Calculate averages
        if results["successful_queries"] > 0:
            results["avg_latency"] = results["total_latency"] / results["successful_queries"]
            results["tokens_per_second"] = results["tokens_per_second"] / results["successful_queries"]
        
        if results["min_latency"] == float('inf'):
            results["min_latency"] = 0.0
        
        self.performance_results[model_name] = results
        return results
    
    def setup_quantized_models(self) -> bool:
        """Set up all quantized models"""
        logger.info("🚀 Setting up quantized models for ultra-fast RAG...")
        
        if not self.check_ollama_health():
            return False
        
        installed_models = self.list_installed_models()
        success_count = 0
        
        for model_type, model_info in self.models.items():
            model_name = model_info["name"]
            
            if model_name in installed_models:
                logger.info(f"✅ {model_name} already installed")
                success_count += 1
            else:
                logger.info(f"📥 Installing {model_name}...")
                if self.pull_model(model_name):
                    success_count += 1
                else:
                    logger.error(f"❌ Failed to install {model_name}")
        
        logger.info(f"✅ Installed {success_count}/{len(self.models)} quantized models")
        return success_count == len(self.models)
    
    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive benchmark on all models"""
        logger.info("🧪 Running comprehensive model benchmark...")
        
        test_prompts = [
            "What is machine learning?",
            "How does Docker work?",
            "Explain Python programming",
            "What are vector databases?",
            "What is RAG?"
        ]
        
        benchmark_results = {
            "timestamp": time.time(),
            "test_prompts": test_prompts,
            "models": {}
        }
        
        for model_type, model_info in self.models.items():
            model_name = model_info["name"]
            logger.info(f"Benchmarking {model_name}...")
            
            results = self.benchmark_model(model_name, test_prompts)
            benchmark_results["models"][model_name] = results
            
            # Log summary
            logger.info(f"  {model_name} Results:")
            logger.info(f"    Success Rate: {results['successful_queries']}/{results['total_queries']} ({results['successful_queries']/results['total_queries']*100:.1f}%)")
            logger.info(f"    Avg Latency: {results['avg_latency']:.3f}s")
            logger.info(f"    Min Latency: {results['min_latency']:.3f}s")
            logger.info(f"    Max Latency: {results['max_latency']:.3f}s")
            logger.info(f"    Tokens/sec: {results['tokens_per_second']:.1f}")
        
        return benchmark_results
    
    def save_benchmark_results(self, results: Dict[str, Any], filename: str = None) -> str:
        """Save benchmark results to file"""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"quantized_models_benchmark_{timestamp}.json"
        
        output_dir = Path.home() / "ai" / "benchmarks" / "2025-10"
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"📁 Benchmark results saved to: {filepath}")
        return str(filepath)
    
    def generate_performance_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable performance report"""
        report = f"""
# Quantized Models Performance Report

**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Test Prompts**: {len(results['test_prompts'])}  

## Model Performance Summary

| Model | Success Rate | Avg Latency | Min Latency | Max Latency | Tokens/sec | Grade |
|-------|-------------|-------------|-------------|-------------|------------|-------|
"""
        
        for model_name, model_results in results["models"].items():
            success_rate = (model_results["successful_queries"] / model_results["total_queries"]) * 100
            avg_latency = model_results["avg_latency"]
            
            # Calculate grade based on latency
            if avg_latency <= 0.02:
                grade = "A+ (Ultra-Fast)"
            elif avg_latency <= 0.05:
                grade = "A (Fast)"
            elif avg_latency <= 0.1:
                grade = "B (Good)"
            elif avg_latency <= 0.2:
                grade = "C (Acceptable)"
            else:
                grade = "D (Slow)"
            
            report += f"| {model_name} | {success_rate:.1f}% | {avg_latency:.3f}s | {model_results['min_latency']:.3f}s | {model_results['max_latency']:.3f}s | {model_results['tokens_per_second']:.1f} | {grade} |\n"
        
        report += f"""
## Recommendations

### For Ultra-Fast Responses (0.02s target)
- **Primary**: Use `llama3.1:8b-instruct-q2_K` for simple queries
- **Fallback**: Use `llama3.1:8b-instruct-q4_K_M` for balanced performance

### For Quality Responses
- **High Quality**: Use `llama3.1:8b-instruct-q5_K_M` for complex queries
- **Ultra Quality**: Use `llama3.1:8b-instruct-q8_0` for research/analysis

### Performance Optimization
- Pre-load models in memory for instant responses
- Use model selection based on query complexity
- Implement response caching for repeated queries
- Consider streaming for longer responses

## Next Steps
1. Deploy ultra-optimized RAG Orchestrator with model selection
2. Implement intelligent model routing based on query complexity
3. Set up continuous performance monitoring
4. Optimize for specific use cases and query patterns
"""
        
        return report

def main():
    """Main function to set up quantized models"""
    logger.info("🚀 Quantized Models Setup for Ultra-Fast RAG")
    logger.info("=" * 60)
    
    manager = QuantizedModelManager()
    
    # Step 1: Check Ollama health
    if not manager.check_ollama_health():
        logger.error("❌ Ollama is not running. Please start Ollama first.")
        return False
    
    # Step 2: Set up quantized models
    if not manager.setup_quantized_models():
        logger.error("❌ Failed to set up quantized models")
        return False
    
    # Step 3: Run comprehensive benchmark
    logger.info("🧪 Running comprehensive benchmark...")
    benchmark_results = manager.run_comprehensive_benchmark()
    
    # Step 4: Save results
    results_file = manager.save_benchmark_results(benchmark_results)
    
    # Step 5: Generate and display report
    report = manager.generate_performance_report(benchmark_results)
    print(report)
    
    # Save report
    report_file = Path(results_file).parent / f"quantized_models_report_{time.strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info(f"📊 Performance report saved to: {report_file}")
    logger.info("🎉 Quantized models setup completed successfully!")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)