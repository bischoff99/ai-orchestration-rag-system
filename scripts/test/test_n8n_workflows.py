#!/usr/bin/env python3
"""
Test n8n Workflows
Tests the n8n workflows after import and activation
"""

import requests
import json
import time
import sys

def test_n8n_workflows():
    """Test n8n workflows"""
    print("🔄 Testing n8n Workflows")
    print("=" * 40)
    
    base_url = "http://localhost:5678"
    api_url = f"{base_url}/api/v1"
    
    # Test n8n connection
    print("🔍 Testing n8n connection...")
    try:
        response = requests.get(f"{api_url}/workflows", timeout=10)
        if response.status_code == 200:
            workflows = response.json().get('data', [])
            print(f"✅ n8n connected with {len(workflows)} workflows")
            
            # List workflow names
            for workflow in workflows[:5]:  # Show first 5
                print(f"   - {workflow.get('name', 'Unknown')}")
        else:
            print(f"❌ n8n connection failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ n8n connection failed: {e}")
        return False
    
    # Test webhook endpoints
    print("\n🔗 Testing Webhook Endpoints...")
    
    # Test RAG Query webhook
    print("Testing RAG Query webhook...")
    try:
        response = requests.post(
            f"{base_url}/webhook/rag-query",
            json={
                "query": "What is machine learning?",
                "collection": "general_knowledge",
                "k": 3
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ RAG Query webhook working")
            print(f"   Answer: {result.get('answer', 'No answer')[:100]}...")
        else:
            print(f"❌ RAG Query webhook failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ RAG Query webhook error: {e}")
    
    # Test Document Ingestion webhook
    print("\nTesting Document Ingestion webhook...")
    try:
        response = requests.post(
            f"{base_url}/webhook/document-ingestion",
            json={
                "directory_path": "/Users/andrejsp/ai/sample_docs",
                "collection_name": "test_n8n_collection"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document Ingestion webhook working")
            print(f"   Status: {result.get('status', 'Unknown')}")
        else:
            print(f"❌ Document Ingestion webhook failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Document Ingestion webhook error: {e}")
    
    # Test Production RAG webhook
    print("\nTesting Production RAG webhook...")
    try:
        response = requests.post(
            f"{base_url}/webhook/production-rag",
            json={
                "action": "query",
                "query": "What is artificial intelligence?",
                "collection": "general_knowledge"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Production RAG webhook working")
            print(f"   Answer: {result.get('answer', 'No answer')[:100]}...")
        else:
            print(f"❌ Production RAG webhook failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Production RAG webhook error: {e}")
    
    print("\n🎉 n8n Workflow Testing Complete!")

if __name__ == "__main__":
    test_n8n_workflows()