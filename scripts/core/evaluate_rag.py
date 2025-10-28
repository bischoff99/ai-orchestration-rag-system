#!/usr/bin/env python3
"""
RAG system evaluation script
Tests performance across collections with various metrics
"""

import os
import argparse
import json
import time
import psutil
import sys
sys.path.append("/Users/andrejsp/ai/examples")
from unified_rag import UnifiedRAG
from langchain_core.documents import Document

# Load configuration
with open("/Users/andrejsp/ai/configs/rag_config.json", "r") as f:
    config = json.load(f)

EMBEDDING_MODEL_NAME = config["embedding_model"]["name"]
OLLAMA_LLM_MODEL = config["ollama"]["default_model"]

# Test queries for different domains
TEST_QUERIES = {
    "general": [
        "What is artificial intelligence?",
        "How does machine learning work?",
        "What are the benefits of cloud computing?",
        "Explain quantum computing basics",
        "What is blockchain technology?"
    ],
    "technical": [
        "How to implement microservices architecture?",
        "What are RESTful API best practices?",
        "How to optimize database performance?",
        "What is container orchestration?",
        "How to implement CI/CD pipelines?"
    ],
    "coding": [
        "How to write clean Python code?",
        "What are design patterns in software?",
        "How to implement error handling?",
        "What is test-driven development?",
        "How to optimize algorithm performance?"
    ],
    "ai_ml": [
        "What is deep learning?",
        "How do neural networks work?",
        "What is MLOps?",
        "Explain machine learning algorithms",
        "What are the types of machine learning?"
    ],
    "devops": [
        "What is Kubernetes?",
        "How to design CI/CD pipelines?",
        "What is Infrastructure as Code?",
        "How to implement blue-green deployment?",
        "What are container orchestration best practices?"
    ],
    "security": [
        "What are OWASP top 10 security risks?",
        "What is zero trust security?",
        "How to implement secure coding practices?",
        "What is authentication vs authorization?",
        "How to prevent SQL injection attacks?"
    ],
    "data_science": [
        "How to analyze data with pandas?",
        "What is data visualization?",
        "How to handle missing data?",
        "What is statistical significance?",
        "How to build a data pipeline?"
    ],
    "reasoning": [
        "Solve: What is 25% of 400?",
        "How to calculate compound interest?",
        "What is the area of a circle with radius 5?",
        "Solve: 2x + 5 = 15",
        "How to calculate standard deviation?"
    ]
}

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def evaluate_collection(collection_name, queries, metrics):
    """Evaluate a single collection"""
    print(f"\n🔍 Testing Collection: {collection_name}")
    print("=" * 50)
    
    try:
        # Initialize RAG database
        rag_db = UnifiedRAG(
            backend="chroma",
            collection_name=collection_name
        )
        
        # Get collection info
        try:
            collection_info = rag_db.collection.count()
            print(f"📊 Documents in collection: {collection_info}")
        except:
            print("📊 Documents in collection: Unknown")
        
        results = {
            "collection": collection_name,
            "queries_tested": len(queries),
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_latency": 0,
            "avg_accuracy": 0,
            "memory_usage_mb": 0,
            "query_results": []
        }
        
        total_latency = 0
        total_accuracy = 0
        memory_before = get_memory_usage()
        
        for i, query in enumerate(queries, 1):
            print(f"❓ Query {i}: {query}")
            
            start_time = time.time()
            try:
                # Perform search
                search_results = rag_db.search(query, k=3)
                latency = time.time() - start_time
                
                if search_results:
                    # Calculate accuracy based on relevance scores
                    # Handle new format: search_results[0]['distance'] instead of search_results[0][1]
                    scores = [result.get('distance', 0) for result in search_results]
                    avg_score = sum(scores) / len(scores)
                    accuracy = min((1 - avg_score) * 100, 100)  # Convert distance to percentage (lower distance = higher accuracy)
                    
                    print(f"   ✅ Found {len(search_results)} results")
                    print(f"   📊 Best match: {search_results[0].get('text', '')[:100]}...")
                    print(f"   📊 Score: {search_results[0].get('distance', 0):.3f}")
                    
                    results["successful_queries"] += 1
                    total_latency += latency
                    total_accuracy += accuracy
                    
                    results["query_results"].append({
                        "query": query,
                        "latency": latency,
                        "accuracy": accuracy,
                        "results_count": len(search_results),
                        "best_score": search_results[0].get('distance', 0)
                    })
                else:
                    print(f"   ❌ No results found")
                    results["failed_queries"] += 1
                    results["query_results"].append({
                        "query": query,
                        "latency": latency,
                        "accuracy": 0,
                        "results_count": 0,
                        "best_score": 0
                    })
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results["failed_queries"] += 1
                results["query_results"].append({
                    "query": query,
                    "latency": 0,
                    "accuracy": 0,
                    "results_count": 0,
                    "best_score": 0,
                    "error": str(e)
                })
        
        memory_after = get_memory_usage()
        results["memory_usage_mb"] = memory_after - memory_before
        
        if results["successful_queries"] > 0:
            results["avg_latency"] = total_latency / results["successful_queries"]
            results["avg_accuracy"] = total_accuracy / results["successful_queries"]
        
        return results
        
    except Exception as e:
        print(f"❌ Error testing collection {collection_name}: {e}")
        return {
            "collection": collection_name,
            "error": str(e),
            "queries_tested": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_latency": 0,
            "avg_accuracy": 0,
            "memory_usage_mb": 0
        }

def main():
    parser = argparse.ArgumentParser(description="Evaluate RAG system performance")
    parser.add_argument("--collections", default="all", 
                       help="Collections to test (comma-separated or 'all')")
    parser.add_argument("--metrics", default="latency,accuracy,memory",
                       help="Metrics to evaluate (comma-separated)")
    parser.add_argument("--output", help="Output file for results (JSON)")
    
    args = parser.parse_args()
    
    # Determine collections to test
    if args.collections == "all":
        collections_to_test = list(TEST_QUERIES.keys())
    else:
        collections_to_test = [c.strip() for c in args.collections.split(",")]
    
    # Determine metrics
    metrics = [m.strip() for m in args.metrics.split(",")]
    
    print("🚀 RAG System Evaluation")
    print("=" * 50)
    print(f"📊 Collections: {', '.join(collections_to_test)}")
    print(f"📈 Metrics: {', '.join(metrics)}")
    
    start_time = time.time()
    all_results = []
    
    for collection in collections_to_test:
        if collection in TEST_QUERIES:
            queries = TEST_QUERIES[collection]
        else:
            # Use general queries for unknown collections
            queries = TEST_QUERIES["general"]
            print(f"⚠️ Using general queries for collection: {collection}")
        
        result = evaluate_collection(collection, queries, metrics)
        all_results.append(result)
    
    duration = time.time() - start_time
    
    # Summary
    print(f"\n🎉 Evaluation Complete!")
    print(f"⏱️  Duration: {duration:.2f} seconds")
    print(f"📊 Overall Statistics:")
    
    total_queries = sum(r.get("queries_tested", 0) for r in all_results)
    successful_queries = sum(r.get("successful_queries", 0) for r in all_results)
    failed_queries = sum(r.get("failed_queries", 0) for r in all_results)
    
    print(f"   - Collections Tested: {len(all_results)}")
    print(f"   - Total Queries: {total_queries}")
    print(f"   - Successful Queries: {successful_queries}")
    print(f"   - Failed Queries: {failed_queries}")
    print(f"   - Success Rate: {(successful_queries/total_queries*100):.1f}%" if total_queries > 0 else "   - Success Rate: 0%")
    
    # Collection summary
    print(f"\n📚 Collection Summary:")
    for result in all_results:
        if "error" not in result:
            success_rate = (result["successful_queries"] / result["queries_tested"] * 100) if result["queries_tested"] > 0 else 0
            print(f"   - {result['collection']}: {result['queries_tested']} queries, {success_rate:.1f}% success")
        else:
            print(f"   - {result['collection']}: ERROR - {result['error']}")
    
    # Save results if output file specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                "evaluation_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_seconds": duration,
                "collections_tested": len(all_results),
                "total_queries": total_queries,
                "successful_queries": successful_queries,
                "failed_queries": failed_queries,
                "success_rate": successful_queries/total_queries*100 if total_queries > 0 else 0,
                "results": all_results
            }, f, indent=2)
        print(f"\n💾 Results saved to: {args.output}")

if __name__ == "__main__":
    main()
