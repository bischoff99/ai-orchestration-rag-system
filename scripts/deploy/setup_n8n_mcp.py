#!/usr/bin/env python3
"""
Setup n8n MCP with API Key
Configures the n8n MCP server with proper authentication
"""

import os
import subprocess
import sys

def setup_n8n_mcp():
    """Setup n8n MCP with API key"""
    print("🔧 Setting up n8n MCP with API Key")
    print("=" * 40)
    
    # API key from the existing configuration
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
    
    # Set environment variable
    os.environ['N8N_API_KEY'] = api_key
    
    print(f"✅ API Key set: {api_key[:20]}...")
    
    # Test connection
    print("🔍 Testing n8n connection...")
    
    try:
        import requests
        
        headers = {
            'X-N8N-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.get('http://localhost:5678/api/v2/workflows', headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ n8n API connection successful")
            workflows = response.json()
            print(f"📊 Found {len(workflows.get('data', []))} existing workflows")
            return True
        else:
            print(f"❌ n8n API connection failed: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to n8n: {e}")
        return False

def create_workflows_via_api():
    """Create workflows using direct API calls"""
    print("\n🚀 Creating Workflows via API")
    print("=" * 40)
    
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
    
    headers = {
        'X-N8N-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    # Load and create workflows
    workflows_dir = "/Users/andrejsp/ai/n8n/workflows"
    
    workflow_files = [
        "production_rag_workflow.json",
        "rag_query_workflow.json", 
        "document_ingestion_workflow.json",
        "monitoring_workflow.json"
    ]
    
    created_workflows = []
    
    for workflow_file in workflow_files:
        file_path = f"{workflows_dir}/{workflow_file}"
        
        try:
            with open(file_path, 'r') as f:
                workflow_data = json.load(f)
            
            print(f"📄 Creating: {workflow_data['name']}")
            
            response = requests.post(
                'http://localhost:5678/api/v2/workflows',
                headers=headers,
                json=workflow_data,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Created: {workflow_data['name']} (ID: {result.get('id', 'unknown')})")
                created_workflows.append(workflow_data['name'])
            else:
                print(f"❌ Failed: {workflow_data['name']} - HTTP {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Error creating {workflow_file}: {e}")
    
    print(f"\n📊 Created {len(created_workflows)} workflows:")
    for workflow in created_workflows:
        print(f"   • {workflow}")
    
    return len(created_workflows)

def main():
    """Main setup function"""
    print("🚀 n8n MCP Setup and Workflow Deployment")
    print("=" * 50)
    
    # Setup MCP
    if not setup_n8n_mcp():
        print("❌ Setup failed")
        return 1
    
    # Create workflows
    created_count = create_workflows_via_api()
    
    if created_count > 0:
        print(f"\n🎉 Successfully created {created_count} workflows!")
        print("\n📋 Next steps:")
        print("   1. Open http://localhost:5678 in your browser")
        print("   2. Activate workflows in n8n UI")
        print("   3. Test with: python3 verify_workflows.py")
    else:
        print("\n⚠️  No workflows were created")
    
    return 0

if __name__ == "__main__":
    import json
    import requests
    exit(main())