#!/usr/bin/env python3
"""
Final Webhook Test Script
Tests all webhook endpoints after manual fix
"""

import requests
import json
import time

def test_webhook(webhook_name, webhook_path, test_data):
    """Test a single webhook endpoint"""
    url = f"http://localhost:5678/webhook/{webhook_path}"
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {webhook_name}: WORKING")
            print(f"   Response: {response.text[:100]}...")
            return True
        else:
            print(f"❌ {webhook_name}: FAILED (HTTP {response.status_code})")
            print(f"   Error: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ {webhook_name}: ERROR - {str(e)}")
        return False

def main():
    """Test all webhook endpoints"""
    print("🧪 Testing All Webhook Endpoints")
    print("=" * 40)
    
    webhooks = [
        {
            "name": "Document Ingestion",
            "path": "document-ingestion",
            "data": {
                "directory_path": "/Users/andrejsp/ai/sample_docs",
                "collection_name": "test_collection"
            }
        },
        {
            "name": "RAG Query",
            "path": "rag-query",
            "data": {
                "query": "What is machine learning?",
                "collection": "test_collection",
                "k": 5
            }
        },
        {
            "name": "Enhanced RAG Query",
            "path": "rag-query-enhanced",
            "data": {
                "query": "Explain AI concepts",
                "collection": "test_collection",
                "k": 5
            }
        },
        {
            "name": "Production RAG",
            "path": "production-rag",
            "data": {
                "query": "Test production workflow",
                "collection": "test_collection"
            }
        }
    ]
    
    working_count = 0
    total_count = len(webhooks)
    
    for webhook in webhooks:
        print(f"\n🔍 Testing {webhook['name']}...")
        if test_webhook(webhook['name'], webhook['path'], webhook['data']):
            working_count += 1
    
    print(f"\n📊 Results: {working_count}/{total_count} webhooks working")
    
    if working_count == total_count:
        print("🎉 All webhooks are working! Your RAG system is ready.")
    elif working_count > 0:
        print("⚠️  Some webhooks are working, but not all.")
    else:
        print("❌ No webhooks are working. Please follow the manual fix guide.")

if __name__ == "__main__":
    main()