#!/usr/bin/env python3
"""
Activate n8n Workflows via API
Activates workflows programmatically using n8n API
"""

import requests
import json
import sys

def get_workflows(api_key):
    """Get list of workflows"""
    headers = {
        'X-N8N-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get('http://localhost:5678/api/v2/workflows', headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get workflows: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting workflows: {e}")
        return None

def activate_workflow(workflow_id, api_key):
    """Activate a workflow by ID"""
    headers = {
        'X-N8N-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {"active": True}
    
    try:
        response = requests.patch(
            f'http://localhost:5678/api/v2/workflows/{workflow_id}',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "Activated successfully"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, str(e)

def main():
    """Main activation function"""
    print("🚀 Activating n8n Workflows via API")
    print("=" * 40)
    
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
    
    # Get workflows
    print("🔍 Getting workflows...")
    workflows_data = get_workflows(api_key)
    
    if not workflows_data:
        print("❌ Failed to get workflows")
        return 1
    
    workflows = workflows_data.get('data', [])
    print(f"📊 Found {len(workflows)} workflows")
    
    # Target workflow names
    target_workflows = [
        "RAG Query Processing Pipeline",
        "RAG Document Ingestion Pipeline", 
        "Production RAG Workflow"
    ]
    
    activated = []
    failed = []
    
    for workflow in workflows:
        workflow_name = workflow.get('name', '')
        workflow_id = workflow.get('id', '')
        is_active = workflow.get('active', False)
        
        if workflow_name in target_workflows:
            print(f"\n📄 Processing: {workflow_name}")
            print(f"   ID: {workflow_id}")
            print(f"   Currently active: {is_active}")
            
            if is_active:
                print(f"✅ Already active: {workflow_name}")
                activated.append(workflow_name)
            else:
                print(f"🔄 Activating: {workflow_name}")
                success, message = activate_workflow(workflow_id, api_key)
                
                if success:
                    print(f"✅ Activated: {workflow_name}")
                    activated.append(workflow_name)
                else:
                    print(f"❌ Failed to activate {workflow_name}: {message}")
                    failed.append(workflow_name)
    
    print(f"\n📊 Activation Summary:")
    print(f"   ✅ Activated: {len(activated)}")
    print(f"   ❌ Failed: {len(failed)}")
    
    if activated:
        print(f"\n🎉 Activated workflows:")
        for workflow in activated:
            print(f"   • {workflow}")
    
    if failed:
        print(f"\n❌ Failed workflows:")
        for workflow in failed:
            print(f"   • {workflow}")
    
    # Test webhooks
    if activated:
        print(f"\n🧪 Testing activated webhooks...")
        test_webhooks()
    
    return 0 if len(failed) == 0 else 1

def test_webhooks():
    """Test the activated webhooks"""
    webhooks = [
        {
            "name": "rag-query",
            "url": "http://localhost:5678/webhook/rag-query",
            "payload": {"query": "What is machine learning?", "collection": "general_knowledge"}
        },
        {
            "name": "document-ingestion",
            "url": "http://localhost:5678/webhook/document-ingestion", 
            "payload": {"directory_path": "/Users/andrejsp/ai/sample_docs", "collection_name": "test"}
        },
        {
            "name": "production-rag",
            "url": "http://localhost:5678/webhook/production-rag",
            "payload": {"action": "query", "query": "What is AI?", "collection": "general_knowledge"}
        }
    ]
    
    for webhook in webhooks:
        print(f"\n🧪 Testing {webhook['name']}...")
        
        try:
            response = requests.post(
                webhook["url"],
                json=webhook["payload"],
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {webhook['name']}: SUCCESS")
                print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
            else:
                print(f"❌ {webhook['name']}: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ {webhook['name']}: ERROR - {e}")

if __name__ == "__main__":
    exit(main())