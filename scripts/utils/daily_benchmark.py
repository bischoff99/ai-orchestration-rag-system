#!/usr/bin/env python3
"""
Daily benchmark and status report script
Monitors system performance and generates reports
"""

import os
import json
import time
import subprocess
import psutil
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
BENCHMARK_DIR = "/Users/andrejsp/ai/benchmarks"
LOG_DIR = os.path.join(BENCHMARK_DIR, "logs")
REPORT_DIR = os.path.join(BENCHMARK_DIR, "reports")

def ensure_directories():
    """Create necessary directories"""
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)

def get_system_info():
    """Get system information"""
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_available_gb": psutil.virtual_memory().available / (1024**3),
        "disk_usage_percent": psutil.disk_usage('/').percent,
        "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
    }

def test_ollama_models():
    """Test Ollama models performance"""
    print("🔄 Testing Ollama models...")
    
    models_to_test = [
        "llama-assistant",
        "gemma2:2b", 
        "mistral-summarizer"
    ]
    
    results = {}
    
    for model in models_to_test:
        print(f"   Testing {model}...")
        start_time = time.time()
        
        try:
            # Test model with simple prompt
            cmd = f"ollama run {model} 'Hello, how are you?'"
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                # Extract token count from response (simplified)
                response_length = len(result.stdout.split())
                tokens_per_second = response_length / duration if duration > 0 else 0
                
                results[model] = {
                    "status": "success",
                    "duration": duration,
                    "response_length": response_length,
                    "tokens_per_second": tokens_per_second,
                    "error": None
                }
                print(f"   ✅ {model}: {tokens_per_second:.1f} tok/s")
            else:
                results[model] = {
                    "status": "error",
                    "duration": duration,
                    "response_length": 0,
                    "tokens_per_second": 0,
                    "error": result.stderr
                }
                print(f"   ❌ {model}: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            results[model] = {
                "status": "timeout",
                "duration": 30,
                "response_length": 0,
                "tokens_per_second": 0,
                "error": "Timeout after 30 seconds"
            }
            print(f"   ⏰ {model}: Timeout")
        except Exception as e:
            results[model] = {
                "status": "error",
                "duration": 0,
                "response_length": 0,
                "tokens_per_second": 0,
                "error": str(e)
            }
            print(f"   ❌ {model}: {e}")
    
    return results

def test_rag_system():
    """Test RAG system performance"""
    print("🔄 Testing RAG system...")
    
    try:
        # Import RAG testing
        import sys
        sys.path.append("/Users/andrejsp/ai/scripts")
        from evaluate_rag import evaluate_collection, TEST_QUERIES
        
        # Test a few collections quickly
        test_collections = ["general_knowledge", "technical_docs", "ai_ml_knowledge"]
        rag_results = {}
        
        for collection in test_collections:
            if collection in TEST_QUERIES:
                print(f"   Testing {collection}...")
                queries = TEST_QUERIES[collection][:2]  # Test only first 2 queries
                
                start_time = time.time()
                result = evaluate_collection(collection, queries, ["latency", "accuracy"])
                duration = time.time() - start_time
                
                rag_results[collection] = {
                    "duration": duration,
                    "queries_tested": result.get("queries_tested", 0),
                    "successful_queries": result.get("successful_queries", 0),
                    "avg_latency": result.get("avg_latency", 0),
                    "avg_accuracy": result.get("avg_accuracy", 0)
                }
                
                success_rate = (result.get("successful_queries", 0) / result.get("queries_tested", 1)) * 100
                print(f"   ✅ {collection}: {success_rate:.1f}% success, {result.get('avg_latency', 0):.2f}s avg")
        
        return rag_results
        
    except Exception as e:
        print(f"   ❌ RAG test failed: {e}")
        return {"error": str(e)}

def generate_daily_report(system_info, ollama_results, rag_results):
    """Generate daily report"""
    timestamp = datetime.now()
    report_file = os.path.join(REPORT_DIR, f"daily_report_{timestamp.strftime('%Y%m%d')}.json")
    
    # Calculate summary statistics
    successful_models = [m for m, r in ollama_results.items() if r["status"] == "success"]
    avg_tokens_per_second = sum(r["tokens_per_second"] for r in ollama_results.values() if r["status"] == "success")
    avg_tokens_per_second = avg_tokens_per_second / len(successful_models) if successful_models else 0
    
    rag_success_rate = 0
    if rag_results and "error" not in rag_results:
        total_queries = sum(r.get("queries_tested", 0) for r in rag_results.values())
        successful_queries = sum(r.get("successful_queries", 0) for r in rag_results.values())
        rag_success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 0
    
    report = {
        "date": timestamp.strftime("%Y-%m-%d"),
        "timestamp": timestamp.isoformat(),
        "summary": {
            "system_health": "good" if system_info["cpu_percent"] < 80 and system_info["memory_percent"] < 80 else "warning",
            "ollama_models_working": len(successful_models),
            "ollama_models_total": len(ollama_results),
            "avg_tokens_per_second": avg_tokens_per_second,
            "rag_success_rate": rag_success_rate,
            "memory_usage_gb": system_info["memory_available_gb"]
        },
        "system_info": system_info,
        "ollama_results": ollama_results,
        "rag_results": rag_results
    }
    
    # Save report
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

def print_summary(report):
    """Print summary to console"""
    print(f"\n📊 Daily Benchmark Summary - {report['date']}")
    print("=" * 60)
    
    summary = report["summary"]
    print(f"🖥️  System Health: {summary['system_health'].upper()}")
    print(f"🤖 Ollama Models: {summary['ollama_models_working']}/{summary['ollama_models_total']} working")
    print(f"⚡ Avg Speed: {summary['avg_tokens_per_second']:.1f} tokens/sec")
    print(f"🔍 RAG Success: {summary['rag_success_rate']:.1f}%")
    print(f"💾 Memory Available: {summary['memory_usage_gb']:.1f} GB")
    
    # Model details
    print(f"\n🤖 Model Performance:")
    for model, result in report["ollama_results"].items():
        if result["status"] == "success":
            print(f"   ✅ {model}: {result['tokens_per_second']:.1f} tok/s")
        else:
            print(f"   ❌ {model}: {result['status']}")
    
    # RAG details
    if "rag_results" in report and "error" not in report["rag_results"]:
        print(f"\n🔍 RAG Performance:")
        for collection, result in report["rag_results"].items():
            success_rate = (result.get("successful_queries", 0) / result.get("queries_tested", 1)) * 100
            print(f"   📚 {collection}: {success_rate:.1f}% success")

def main():
    print("🚀 Daily AI System Benchmark")
    print("=" * 50)
    
    ensure_directories()
    
    # Step 1: Get system information
    print("🔄 Collecting system information...")
    system_info = get_system_info()
    
    # Step 2: Test Ollama models
    ollama_results = test_ollama_models()
    
    # Step 3: Test RAG system
    rag_results = test_rag_system()
    
    # Step 4: Generate report
    print("🔄 Generating daily report...")
    report = generate_daily_report(system_info, ollama_results, rag_results)
    
    # Step 5: Print summary
    print_summary(report)
    
    # Step 6: Log to daily log file
    log_file = os.path.join(LOG_DIR, "daily_benchmark.log")
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now().isoformat()} - Benchmark completed\n")
        f.write(f"  Models working: {report['summary']['ollama_models_working']}/{report['summary']['ollama_models_total']}\n")
        f.write(f"  Avg speed: {report['summary']['avg_tokens_per_second']:.1f} tok/s\n")
        f.write(f"  RAG success: {report['summary']['rag_success_rate']:.1f}%\n")
        f.write(f"  System health: {report['summary']['system_health']}\n\n")
    
    report_filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
    print(f"\n💾 Report saved to: {os.path.join(REPORT_DIR, report_filename)}")
    print(f"📝 Log updated: {log_file}")

if __name__ == "__main__":
    main()
