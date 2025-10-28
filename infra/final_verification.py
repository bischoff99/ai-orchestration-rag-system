#!/usr/bin/env python3
"""
Final Verification of ChromaDB v2 Migration
"""
import requests
import json
import time
from datetime import datetime

def verify_system():
    """Verify all system components are working"""
    print("🔍 Final System Verification")
    print("=" * 50)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "components": {},
        "overall_status": "unknown"
    }
    
    # Test n8n
    print("1. Testing n8n...")
    try:
        response = requests.get("http://localhost:5678/healthz", timeout=10)
        if response.status_code == 200:
            print("   ✅ n8n healthy")
            results["components"]["n8n"] = {"status": "healthy", "port": 5678}
        else:
            print(f"   ❌ n8n unhealthy: {response.status_code}")
            results["components"]["n8n"] = {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"   ❌ n8n error: {e}")
        results["components"]["n8n"] = {"status": "error", "error": str(e)}
    
    # Test ChromaDB v2
    print("2. Testing ChromaDB v2...")
    try:
        response = requests.get("http://localhost:8000/api/v2/heartbeat", timeout=10)
        if response.status_code == 200:
            print("   ✅ ChromaDB v2 healthy")
            results["components"]["chromadb_v2"] = {"status": "healthy", "port": 8000, "api": "v2"}
        else:
            print(f"   ❌ ChromaDB v2 unhealthy: {response.status_code}")
            results["components"]["chromadb_v2"] = {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"   ❌ ChromaDB v2 error: {e}")
        results["components"]["chromadb_v2"] = {"status": "error", "error": str(e)}
    
    # Test Ollama
    print("3. Testing Ollama...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"   ✅ Ollama healthy ({len(models)} models)")
            results["components"]["ollama"] = {"status": "healthy", "port": 11434, "models": len(models)}
        else:
            print(f"   ❌ Ollama unhealthy: {response.status_code}")
            results["components"]["ollama"] = {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"   ❌ Ollama error: {e}")
        results["components"]["ollama"] = {"status": "error", "error": str(e)}
    
    # Test RAG webhook
    print("4. Testing RAG webhook...")
    try:
        response = requests.post(
            "http://localhost:5678/webhook/rag-chat",
            json={"query": "test query"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("message") == "Workflow was started":
                print("   ✅ RAG webhook working")
                results["components"]["rag_webhook"] = {"status": "healthy", "response": "workflow_started"}
            else:
                print(f"   ⚠️  RAG webhook unexpected response: {data}")
                results["components"]["rag_webhook"] = {"status": "warning", "response": data}
        else:
            print(f"   ❌ RAG webhook unhealthy: {response.status_code}")
            results["components"]["rag_webhook"] = {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"   ❌ RAG webhook error: {e}")
        results["components"]["rag_webhook"] = {"status": "error", "error": str(e)}
    
    # Overall status
    healthy_components = sum(1 for comp in results["components"].values() if comp["status"] == "healthy")
    total_components = len(results["components"])
    
    if healthy_components == total_components:
        results["overall_status"] = "healthy"
        print(f"\n🎉 All {total_components} components are healthy!")
    elif healthy_components > 0:
        results["overall_status"] = "partial"
        print(f"\n⚠️  {healthy_components}/{total_components} components are healthy")
    else:
        results["overall_status"] = "unhealthy"
        print(f"\n❌ No components are healthy")
    
    # Save results
    results_file = f"/Users/andrejsp/ai/benchmarks/2025-10/final_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Verification results saved to: {results_file}")
    
    return results["overall_status"] == "healthy"

if __name__ == "__main__":
    success = verify_system()
    exit(0 if success else 1)