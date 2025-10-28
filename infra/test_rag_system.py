#!/usr/bin/env python3
"""
Test RAG System End-to-End
"""
import requests
import time
import json
from datetime import datetime

def test_rag_system():
    """Test the complete RAG system"""
    print("🧪 RAG System End-to-End Test")
    print("=" * 40)
    
    # Test queries
    test_queries = [
        "What is machine learning?",
        "How does Docker work?", 
        "Explain Python programming",
        "What are vector databases?"
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}/{len(test_queries)}: {query}")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                "http://localhost:5678/webhook/rag-chat",
                json={"query": query},
                timeout=60  # Longer timeout for RAG processing
            )
            
            latency = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success ({latency:.2f}s)")
                print(f"   Response: {str(data)[:200]}...")
                
                results.append({
                    "query": query,
                    "success": True,
                    "latency": latency,
                    "response": data
                })
            else:
                print(f"   ❌ HTTP {response.status_code} ({latency:.2f}s)")
                print(f"   Error: {response.text}")
                
                results.append({
                    "query": query,
                    "success": False,
                    "latency": latency,
                    "error": f"HTTP {response.status_code}: {response.text}"
                })
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout after 60s")
            results.append({
                "query": query,
                "success": False,
                "latency": 60,
                "error": "Timeout"
            })
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                "query": query,
                "success": False,
                "latency": time.time() - start_time,
                "error": str(e)
            })
        
        time.sleep(2)  # Rate limiting
    
    # Summary
    print(f"\n📊 Test Summary:")
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    avg_latency = sum(r["latency"] for r in results) / total
    
    print(f"   Success rate: {successful}/{total} ({successful/total*100:.1f}%)")
    print(f"   Average latency: {avg_latency:.2f}s")
    
    if successful > 0:
        print(f"   ✅ RAG system is operational!")
    else:
        print(f"   ❌ RAG system has issues")
    
    # Save results
    results_file = f"/Users/andrejsp/ai/benchmarks/2025-10/rag_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "successful": successful,
                "total": total,
                "success_rate": successful/total*100,
                "avg_latency": avg_latency
            },
            "results": results
        }, f, indent=2)
    
    print(f"   📁 Results saved to: {results_file}")
    
    return successful > 0

if __name__ == "__main__":
    success = test_rag_system()
    exit(0 if success else 1)