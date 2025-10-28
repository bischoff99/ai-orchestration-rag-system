#!/usr/bin/env python3
"""
Test Activated n8n Workflows
Tests workflows after they have been activated in n8n UI
"""

import requests
import json
import time

def test_workflow(webhook_name, payload, description):
    """Test a single workflow webhook"""
    print(f"🧪 Testing {description}...")
    
    try:
        response = requests.post(
            f"http://localhost:5678/webhook/{webhook_name}",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {description}: SUCCESS")
            print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
            return True
        else:
            print(f"❌ {description}: FAILED (HTTP {response.status_code})")
            print(f"   Response: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"❌ {description}: ERROR - {e}")
        return False

def main():
    """Test all activated workflows"""
    print("🚀 Testing Activated n8n Workflows")
    print("=" * 50)
    
    # Test workflows
    tests = [
        {
            "webhook": "rag-query",
            "payload": {
                "query": "What is machine learning?",
                "collection": "general_knowledge",
                "k": 3
            },
            "description": "RAG Query Workflow"
        },
        {
            "webhook": "document-ingestion", 
            "payload": {
                "directory_path": "/Users/andrejsp/ai/sample_docs",
                "collection_name": "test_workflow_collection"
            },
            "description": "Document Ingestion Workflow"
        },
        {
            "webhook": "production-rag",
            "payload": {
                "action": "query",
                "query": "What is artificial intelligence?",
                "collection": "general_knowledge"
            },
            "description": "Production RAG Workflow"
        }
    ]
    
    results = []
    
    for test in tests:
        success = test_workflow(
            test["webhook"],
            test["payload"], 
            test["description"]
        )
        results.append(success)
        print()  # Add spacing
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("📊 Test Results Summary")
    print("=" * 30)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All workflows are working correctly!")
    else:
        print(f"\n⚠️  {total - passed} workflows need attention.")
        print("Make sure workflows are activated in n8n UI:")
        print("http://localhost:5678")

if __name__ == "__main__":
    main()