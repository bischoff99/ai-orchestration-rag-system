#!/usr/bin/env python3
"""
Verify n8n Workflows Status
Comprehensive verification of workflow import and activation status
"""

import requests
import json
import time
from datetime import datetime

def check_n8n_status():
    """Check if n8n is running and accessible"""
    print("🔍 Checking n8n Status...")
    
    try:
        response = requests.get("http://localhost:5678", timeout=10)
        if response.status_code == 200:
            print("✅ n8n is running and accessible")
            print(f"🌐 Web interface: http://localhost:5678")
            return True
        else:
            print(f"❌ n8n returned HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ n8n is not accessible: {e}")
        return False

def test_webhook_endpoints():
    """Test all webhook endpoints"""
    print("\n🔗 Testing Webhook Endpoints...")
    
    webhooks = [
        {
            "name": "rag-query",
            "url": "http://localhost:5678/webhook/rag-query",
            "payload": {"query": "test", "collection": "general_knowledge"},
            "description": "RAG Query Processing"
        },
        {
            "name": "document-ingestion", 
            "url": "http://localhost:5678/webhook/document-ingestion",
            "payload": {"directory_path": "/Users/andrejsp/ai/sample_docs", "collection_name": "test"},
            "description": "Document Ingestion"
        },
        {
            "name": "production-rag",
            "url": "http://localhost:5678/webhook/production-rag", 
            "payload": {"action": "query", "query": "test", "collection": "general_knowledge"},
            "description": "Production RAG"
        }
    ]
    
    results = []
    
    for webhook in webhooks:
        print(f"\n🧪 Testing {webhook['description']}...")
        
        try:
            response = requests.post(
                webhook["url"],
                json=webhook["payload"],
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ {webhook['description']}: ACTIVE")
                results.append(True)
            elif response.status_code == 404:
                print(f"❌ {webhook['description']}: NOT REGISTERED (needs activation)")
                results.append(False)
            else:
                print(f"⚠️  {webhook['description']}: HTTP {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {webhook['description']}: ERROR - {e}")
            results.append(False)
    
    return results

def generate_status_report(webhook_results):
    """Generate comprehensive status report"""
    print("\n" + "="*60)
    print("📊 WORKFLOW STATUS REPORT")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    active_count = sum(webhook_results)
    total_count = len(webhook_results)
    
    print(f"Active Webhooks: {active_count}/{total_count}")
    
    if active_count == total_count:
        print("\n🎉 ALL WORKFLOWS ARE ACTIVE!")
        print("✅ Your n8n workflows are ready for use")
        print("\n🚀 Available Endpoints:")
        print("   • POST /webhook/rag-query - Query RAG system")
        print("   • POST /webhook/document-ingestion - Ingest documents")
        print("   • POST /webhook/production-rag - Unified RAG operations")
        
        print("\n🧪 Test Commands:")
        print("   python3 test_activated_workflows.py")
        
    elif active_count > 0:
        print(f"\n⚠️  PARTIALLY ACTIVE ({active_count}/{total_count})")
        print("Some workflows are working, others need activation")
        
    else:
        print("\n❌ NO WORKFLOWS ACTIVE")
        print("All workflows need manual activation in n8n UI")
        
    print("\n📋 Activation Steps:")
    print("1. Open http://localhost:5678 in your browser")
    print("2. Log in to n8n")
    print("3. Go to Workflows section")
    print("4. Toggle 'Active' switch for each workflow:")
    print("   • RAG Document Ingestion Pipeline")
    print("   • RAG Query Processing Pipeline")
    print("   • RAG System Monitoring & Maintenance")
    print("   • Production RAG Workflow")
    print("5. Run this script again to verify")
    
    return active_count == total_count

def main():
    """Main verification function"""
    print("🚀 n8n Workflow Verification Tool")
    print("="*50)
    
    # Check n8n status
    if not check_n8n_status():
        print("\n❌ Cannot proceed - n8n is not running")
        print("Start n8n with: ./n8n/start_n8n.sh")
        return 1
    
    # Test webhook endpoints
    webhook_results = test_webhook_endpoints()
    
    # Generate status report
    all_active = generate_status_report(webhook_results)
    
    if all_active:
        print("\n🎉 Verification complete - All systems ready!")
        return 0
    else:
        print("\n⚠️  Verification complete - Manual activation needed")
        return 1

if __name__ == "__main__":
    exit(main())