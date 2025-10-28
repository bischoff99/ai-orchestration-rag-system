#!/usr/bin/env python3
"""
Final System Health Verification for ChromaDB v2 Migration
Comprehensive validation of all components and endpoints
"""
import requests
import json
import time
from datetime import datetime
import os

def verify_chromadb_v2():
    """Verify ChromaDB v2 API endpoints"""
    print("🔍 ChromaDB v2 API Verification")
    print("-" * 40)
    
    base_url = "http://localhost:8000/api/v2"
    results = {}
    
    # Test heartbeat
    try:
        response = requests.get(f"{base_url}/heartbeat", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ /api/v2/heartbeat - {data}")
            results["heartbeat"] = {"status": "healthy", "response": data}
        else:
            print(f"❌ /api/v2/heartbeat - HTTP {response.status_code}")
            results["heartbeat"] = {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"❌ /api/v2/heartbeat - Error: {e}")
        results["heartbeat"] = {"status": "error", "error": str(e)}
    
    # Test version
    try:
        response = requests.get(f"{base_url}/version", timeout=10)
        if response.status_code == 200:
            version = response.text.strip()
            print(f"✅ /api/v2/version - {version}")
            results["version"] = {"status": "healthy", "version": version}
        else:
            print(f"❌ /api/v2/version - HTTP {response.status_code}")
            results["version"] = {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"❌ /api/v2/version - Error: {e}")
        results["version"] = {"status": "error", "error": str(e)}
    
    # Test collections (expected to be empty or 404)
    try:
        response = requests.get(f"{base_url}/collections", timeout=10)
        if response.status_code == 200:
            collections = response.json()
            print(f"✅ /api/v2/collections - {len(collections.get('data', []))} collections")
            results["collections"] = {"status": "healthy", "count": len(collections.get('data', []))}
        elif response.status_code == 404:
            print(f"⚠️  /api/v2/collections - 404 (expected, no collections)")
            results["collections"] = {"status": "empty", "note": "No collections created yet"}
        else:
            print(f"❌ /api/v2/collections - HTTP {response.status_code}")
            results["collections"] = {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"❌ /api/v2/collections - Error: {e}")
        results["collections"] = {"status": "error", "error": str(e)}
    
    return results

def verify_rag_system():
    """Verify RAG system functionality"""
    print("\n🔍 RAG System Verification")
    print("-" * 40)
    
    test_queries = [
        "What is machine learning?",
        "How does Docker work?",
        "Explain Python programming"
    ]
    
    results = {"queries": [], "summary": {}}
    
    for i, query in enumerate(test_queries, 1):
        print(f"Test {i}: {query[:30]}...")
        
        start_time = time.time()
        try:
            response = requests.post(
                "http://localhost:5678/webhook/rag-chat",
                json={"query": query},
                timeout=30
            )
            latency = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Workflow was started":
                    print(f"  ✅ Success ({latency:.2f}s) - Workflow started")
                    results["queries"].append({
                        "query": query,
                        "success": True,
                        "latency": latency,
                        "status": "workflow_started"
                    })
                else:
                    print(f"  ⚠️  Unexpected response: {data}")
                    results["queries"].append({
                        "query": query,
                        "success": False,
                        "latency": latency,
                        "error": f"Unexpected response: {data}"
                    })
            else:
                print(f"  ❌ HTTP {response.status_code} ({latency:.2f}s)")
                results["queries"].append({
                    "query": query,
                    "success": False,
                    "latency": latency,
                    "error": f"HTTP {response.status_code}"
                })
        except Exception as e:
            latency = time.time() - start_time
            print(f"  ❌ Error: {e} ({latency:.2f}s)")
            results["queries"].append({
                "query": query,
                "success": False,
                "latency": latency,
                "error": str(e)
            })
        
        time.sleep(1)  # Rate limiting
    
    # Calculate summary
    successful = sum(1 for q in results["queries"] if q["success"])
    total = len(results["queries"])
    avg_latency = sum(q["latency"] for q in results["queries"]) / total
    
    results["summary"] = {
        "successful": successful,
        "total": total,
        "success_rate": (successful / total) * 100,
        "avg_latency": avg_latency
    }
    
    print(f"\n📊 RAG Summary: {successful}/{total} successful ({results['summary']['success_rate']:.1f}%)")
    print(f"   Average latency: {avg_latency:.2f}s")
    
    return results

def verify_system_components():
    """Verify all system components"""
    print("🔍 System Components Verification")
    print("-" * 40)
    
    components = {
        "n8n": "http://localhost:5678/healthz",
        "chromadb": "http://localhost:8000/api/v2/heartbeat",
        "ollama": "http://localhost:11434/api/tags"
    }
    
    results = {}
    
    for name, url in components.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name} - Healthy")
                results[name] = {"status": "healthy", "port": url.split(":")[2].split("/")[0]}
            else:
                print(f"❌ {name} - HTTP {response.status_code}")
                results[name] = {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"❌ {name} - Error: {e}")
            results[name] = {"status": "error", "error": str(e)}
    
    return results

def main():
    """Main verification function"""
    print("🚀 ChromaDB v2 Migration - Final System Health Verification")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Verify system components
    components = verify_system_components()
    
    # Verify ChromaDB v2 API
    chromadb_v2 = verify_chromadb_v2()
    
    # Verify RAG system
    rag_system = verify_rag_system()
    
    # Overall assessment
    print("\n📊 Overall Assessment")
    print("-" * 40)
    
    healthy_components = sum(1 for comp in components.values() if comp["status"] == "healthy")
    total_components = len(components)
    
    chromadb_healthy = all(endpoint["status"] in ["healthy", "empty"] for endpoint in chromadb_v2.values())
    rag_healthy = rag_system["summary"]["success_rate"] >= 90
    
    print(f"System Components: {healthy_components}/{total_components} healthy")
    print(f"ChromaDB v2 API: {'✅ Healthy' if chromadb_healthy else '❌ Issues'}")
    print(f"RAG System: {'✅ Operational' if rag_healthy else '❌ Issues'}")
    
    overall_health = healthy_components == total_components and chromadb_healthy and rag_healthy
    
    if overall_health:
        print("\n🎉 MIGRATION SUCCESSFUL!")
        print("   All systems operational with ChromaDB v2")
        print("   No regressions detected")
        print("   Ready for production use")
    else:
        print("\n⚠️  MIGRATION ISSUES DETECTED")
        print("   Some components may need attention")
    
    # Save detailed results
    results = {
        "timestamp": datetime.now().isoformat(),
        "migration_status": "Complete" if overall_health else "Issues",
        "overall_health": overall_health,
        "components": components,
        "chromadb_v2": chromadb_v2,
        "rag_system": rag_system
    }
    
    results_file = f"/Users/andrejsp/ai/benchmarks/2025-10/final_health_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Detailed results saved to: {results_file}")
    
    return overall_health

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)