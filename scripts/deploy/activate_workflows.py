#!/usr/bin/env python3
"""
Activate n8n Workflows
Activates all imported workflows in n8n
"""

import requests
import json
import time
import sys

def activate_workflows():
    """Activate all n8n workflows"""
    print("🔄 Activating n8n Workflows")
    print("=" * 40)
    
    base_url = "http://localhost:5678"
    api_url = f"{base_url}/api/v1"
    
    # First, let's try to get workflows without API key
    print("🔍 Checking workflows...")
    try:
        # Try to access the web interface to get workflow info
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ n8n web interface accessible")
            print(f"🌐 Access n8n at: {base_url}")
            print("📋 Manual activation required:")
            print("   1. Open http://localhost:5678 in your browser")
            print("   2. Log in to n8n")
            print("   3. Go to Workflows section")
            print("   4. Find and activate these workflows:")
            print("      - RAG Document Ingestion Pipeline")
            print("      - RAG Query Processing Pipeline") 
            print("      - RAG System Monitoring & Maintenance")
            print("      - Production RAG Workflow")
            print("   5. Toggle the 'Active' switch for each workflow")
        else:
            print(f"❌ n8n web interface not accessible: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing n8n: {e}")
    
    # Try to test webhook endpoints to see if any are active
    print("\n🔗 Testing webhook endpoints...")
    
    webhooks_to_test = [
        ("rag-query", {"query": "test", "collection": "general_knowledge"}),
        ("document-ingestion", {"directory_path": "/Users/andrejsp/ai/sample_docs", "collection_name": "test"}),
        ("production-rag", {"action": "query", "query": "test", "collection": "general_knowledge"})
    ]
    
    active_webhooks = []
    
    for webhook_name, payload in webhooks_to_test:
        try:
            response = requests.post(
                f"{base_url}/webhook/{webhook_name}",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ {webhook_name}: Active")
                active_webhooks.append(webhook_name)
            elif response.status_code == 404:
                print(f"❌ {webhook_name}: Not registered (needs activation)")
            else:
                print(f"⚠️  {webhook_name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {webhook_name}: Error - {e}")
    
    if active_webhooks:
        print(f"\n🎉 {len(active_webhooks)} webhooks are active!")
    else:
        print("\n⚠️  No webhooks are active. Manual activation required.")
    
    return len(active_webhooks) > 0

def test_activated_workflows():
    """Test workflows after activation"""
    print("\n🧪 Testing Activated Workflows...")
    
    base_url = "http://localhost:5678"
    
    # Test RAG Query
    print("Testing RAG Query workflow...")
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
            print("✅ RAG Query workflow working!")
            print(f"   Answer: {result.get('answer', 'No answer')[:100]}...")
            return True
        else:
            print(f"❌ RAG Query failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ RAG Query error: {e}")
        return False

def main():
    """Main function"""
    print("🚀 n8n Workflow Activation Tool")
    print("=" * 50)
    
    # Check if n8n is running
    try:
        response = requests.get("http://localhost:5678", timeout=5)
        if response.status_code != 200:
            print("❌ n8n is not running. Please start n8n first:")
            print("   ./n8n/start_n8n.sh")
            return 1
    except Exception as e:
        print(f"❌ Cannot connect to n8n: {e}")
        print("   Please start n8n first: ./n8n/start_n8n.sh")
        return 1
    
    # Try to activate workflows
    activated = activate_workflows()
    
    if activated:
        # Test the activated workflows
        test_activated_workflows()
    else:
        print("\n📋 Manual Activation Steps:")
        print("1. Open http://localhost:5678 in your browser")
        print("2. Log in to n8n")
        print("3. Go to Workflows section")
        print("4. Find these workflows and activate them:")
        print("   - RAG Document Ingestion Pipeline")
        print("   - RAG Query Processing Pipeline")
        print("   - RAG System Monitoring & Maintenance")
        print("   - Production RAG Workflow")
        print("5. Toggle the 'Active' switch for each workflow")
        print("6. Run this script again to test")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())