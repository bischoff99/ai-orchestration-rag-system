#!/usr/bin/env python3
"""
RAG Orchestrator v2 Performance Benchmark Suite
Measures and compares performance between original and optimized versions
"""
import asyncio
import time
import json
import statistics
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from rag_orchestrator_v2_optimized import OptimizedRAGOrchestratorV2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PerformanceBenchmark:
    """Performance benchmark suite for RAG Orchestrator v2"""
    
    def __init__(self, output_dir: str = "~/ai/benchmarks/2025-10"):
        self.output_dir = Path(output_dir).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Test queries for benchmarking
        self.test_queries = [
            "What is machine learning?",
            "How does Docker work?",
            "Explain Python programming",
            "What are vector databases?",
            "What is RAG?",
            "How do I optimize database performance?",
            "What are microservices?",
            "Explain API design best practices",
            "How does caching work?",
            "What is containerization?"
        ]
        
        # Performance targets
        self.targets = {
            "avg_response_time_s": 0.02,
            "max_response_time_s": 0.1,
            "success_rate_percent": 99.0,
            "cache_hit_rate_percent": 50.0
        }
    
    async def run_single_query_benchmark(self, orchestrator: OptimizedRAGOrchestratorV2, query: str, iterations: int = 3) -> Dict[str, Any]:
        """Run benchmark for a single query"""
        logger.info(f"Benchmarking query: {query[:50]}...")
        
        latencies = []
        successes = []
        cache_hits = []
        
        for i in range(iterations):
            start_time = time.time()
            result = await orchestrator.process_rag_query(query)
            latency = time.time() - start_time
            
            latencies.append(latency)
            successes.append(result.success)
            cache_hits.append(result.cache_hit)
            
            logger.info(f"  Iteration {i+1}: {latency:.3f}s, Success: {result.success}, Cache: {result.cache_hit}")
        
        return {
            "query": query,
            "iterations": iterations,
            "latencies": latencies,
            "successes": successes,
            "cache_hits": cache_hits,
            "avg_latency": statistics.mean(latencies),
            "min_latency": min(latencies),
            "max_latency": max(latencies),
            "std_latency": statistics.stdev(latencies) if len(latencies) > 1 else 0,
            "success_rate": (sum(successes) / len(successes)) * 100,
            "cache_hit_rate": (sum(cache_hits) / len(cache_hits)) * 100
        }
    
    async def run_comprehensive_benchmark(self, orchestrator: OptimizedRAGOrchestratorV2) -> Dict[str, Any]:
        """Run comprehensive benchmark across all test queries"""
        logger.info("🚀 Starting comprehensive performance benchmark...")
        
        start_time = time.time()
        results = []
        
        # First pass - cold start (no cache)
        logger.info("📊 Phase 1: Cold start performance (no cache)")
        for query in self.test_queries:
            result = await self.run_single_query_benchmark(orchestrator, query, iterations=2)
            results.append(result)
        
        # Second pass - warm cache
        logger.info("📊 Phase 2: Warm cache performance")
        for query in self.test_queries:
            result = await self.run_single_query_benchmark(orchestrator, query, iterations=2)
            results.append(result)
        
        total_time = time.time() - start_time
        
        # Calculate aggregate metrics
        all_latencies = [r["avg_latency"] for r in results]
        all_successes = [r["success_rate"] for r in results]
        all_cache_hits = [r["cache_hit_rate"] for r in results]
        
        aggregate_metrics = {
            "total_queries": len(results),
            "total_time_s": total_time,
            "queries_per_second": len(results) / total_time,
            "avg_response_time_s": statistics.mean(all_latencies),
            "min_response_time_s": min(all_latencies),
            "max_response_time_s": max(all_latencies),
            "std_response_time_s": statistics.stdev(all_latencies) if len(all_latencies) > 1 else 0,
            "avg_success_rate_percent": statistics.mean(all_successes),
            "avg_cache_hit_rate_percent": statistics.mean(all_cache_hits),
            "p95_response_time_s": self._percentile(all_latencies, 95),
            "p99_response_time_s": self._percentile(all_latencies, 99)
        }
        
        # Performance vs targets
        performance_vs_targets = {
            "response_time_target_met": aggregate_metrics["avg_response_time_s"] <= self.targets["avg_response_time_s"],
            "max_response_time_target_met": aggregate_metrics["max_response_time_s"] <= self.targets["max_response_time_s"],
            "success_rate_target_met": aggregate_metrics["avg_success_rate_percent"] >= self.targets["success_rate_percent"],
            "cache_hit_rate_target_met": aggregate_metrics["avg_cache_hit_rate_percent"] >= self.targets["cache_hit_rate_percent"]
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "orchestrator_version": "2.0.0-optimized",
            "test_queries": self.test_queries,
            "individual_results": results,
            "aggregate_metrics": aggregate_metrics,
            "performance_vs_targets": performance_vs_targets,
            "targets": self.targets
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def save_benchmark_results(self, results: Dict[str, Any], filename: str = None) -> str:
        """Save benchmark results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rag_performance_benchmark_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"📁 Benchmark results saved to: {filepath}")
        return str(filepath)
    
    def generate_performance_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable performance report"""
        metrics = results["aggregate_metrics"]
        targets = results["performance_vs_targets"]
        
        report = f"""
# RAG Orchestrator v2 Performance Report

**Generated**: {results["timestamp"]}  
**Version**: {results["orchestrator_version"]}  
**Total Queries**: {metrics["total_queries"]}  
**Total Time**: {metrics["total_time_s"]:.2f}s  

## Performance Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Average Response Time** | {metrics["avg_response_time_s"]:.3f}s | {self.targets["avg_response_time_s"]:.3f}s | {'✅' if targets["response_time_target_met"] else '❌'} |
| **Max Response Time** | {metrics["max_response_time_s"]:.3f}s | {self.targets["max_response_time_s"]:.3f}s | {'✅' if targets["max_response_time_target_met"] else '❌'} |
| **Success Rate** | {metrics["avg_success_rate_percent"]:.1f}% | {self.targets["success_rate_percent"]:.1f}% | {'✅' if targets["success_rate_target_met"] else '❌'} |
| **Cache Hit Rate** | {metrics["avg_cache_hit_rate_percent"]:.1f}% | {self.targets["cache_hit_rate_percent"]:.1f}% | {'✅' if targets["cache_hit_rate_target_met"] else '❌'} |
| **P95 Response Time** | {metrics["p95_response_time_s"]:.3f}s | - | - |
| **P99 Response Time** | {metrics["p99_response_time_s"]:.3f}s | - | - |
| **Queries/Second** | {metrics["queries_per_second"]:.2f} | - | - |

## Performance Analysis

### Response Time Performance
- **Average**: {metrics["avg_response_time_s"]:.3f}s
- **Improvement Needed**: {((metrics["avg_response_time_s"] / self.targets["avg_response_time_s"]) - 1) * 100:.1f}x faster needed
- **Consistency**: Std Dev {metrics["std_response_time_s"]:.3f}s

### Cache Performance
- **Hit Rate**: {metrics["avg_cache_hit_rate_percent"]:.1f}%
- **Cache Effectiveness**: {'Good' if metrics["avg_cache_hit_rate_percent"] > 30 else 'Needs Improvement'}

### Overall Assessment
- **Targets Met**: {sum(targets.values())}/{len(targets)} ({sum(targets.values())/len(targets)*100:.1f}%)
- **Performance Grade**: {self._calculate_performance_grade(metrics, targets)}

## Recommendations

{self._generate_recommendations(metrics, targets)}
"""
        return report
    
    def _calculate_performance_grade(self, metrics: Dict, targets: Dict) -> str:
        """Calculate overall performance grade"""
        score = 0
        total = 4
        
        if metrics["avg_response_time_s"] <= self.targets["avg_response_time_s"]:
            score += 1
        if metrics["max_response_time_s"] <= self.targets["max_response_time_s"]:
            score += 1
        if metrics["avg_success_rate_percent"] >= self.targets["success_rate_percent"]:
            score += 1
        if metrics["avg_cache_hit_rate_percent"] >= self.targets["cache_hit_rate_percent"]:
            score += 1
        
        percentage = (score / total) * 100
        
        if percentage >= 90:
            return "A+ (Excellent)"
        elif percentage >= 80:
            return "A (Very Good)"
        elif percentage >= 70:
            return "B (Good)"
        elif percentage >= 60:
            return "C (Satisfactory)"
        else:
            return "D (Needs Improvement)"
    
    def _generate_recommendations(self, metrics: Dict, targets: Dict) -> str:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        if not targets["response_time_target_met"]:
            recommendations.append("- **Response Time**: Consider model quantization, connection pooling, or async processing")
        
        if not targets["cache_hit_rate_target_met"]:
            recommendations.append("- **Cache Hit Rate**: Implement smarter caching strategies or increase cache size")
        
        if metrics["std_response_time_s"] > 0.1:
            recommendations.append("- **Consistency**: Response times vary significantly - investigate bottlenecks")
        
        if metrics["avg_success_rate_percent"] < 95:
            recommendations.append("- **Reliability**: Some queries are failing - check error handling and service health")
        
        if not recommendations:
            recommendations.append("- **Excellent Performance**: All targets met! Consider advanced optimizations for even better performance.")
        
        return "\n".join(recommendations)

async def main():
    """Main benchmark execution"""
    logger.info("🚀 RAG Orchestrator v2 Performance Benchmark")
    logger.info("=" * 60)
    
    # Initialize orchestrator
    orchestrator = OptimizedRAGOrchestratorV2()
    
    try:
        # Run comprehensive benchmark
        benchmark = PerformanceBenchmark()
        results = await benchmark.run_comprehensive_benchmark(orchestrator)
        
        # Save results
        results_file = benchmark.save_benchmark_results(results)
        
        # Generate and display report
        report = benchmark.generate_performance_report(results)
        print(report)
        
        # Save report
        report_file = benchmark.output_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"📊 Performance report saved to: {report_file}")
        
        # Show final metrics
        metrics = results["aggregate_metrics"]
        logger.info(f"🎯 Final Performance Summary:")
        logger.info(f"   Average Response Time: {metrics['avg_response_time_s']:.3f}s")
        logger.info(f"   Success Rate: {metrics['avg_success_rate_percent']:.1f}%")
        logger.info(f"   Cache Hit Rate: {metrics['avg_cache_hit_rate_percent']:.1f}%")
        logger.info(f"   Queries/Second: {metrics['queries_per_second']:.2f}")
        
    except Exception as e:
        logger.error(f"❌ Benchmark failed: {e}")
        return False
    
    finally:
        await orchestrator.cleanup()
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)