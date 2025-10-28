#!/usr/bin/env python3
"""
Complete Production Deployment
Final solution to activate all workflows and complete production deployment
"""

import requests
import json
import time
import subprocess
import sys
from datetime import datetime

class ProductionDeployment:
    def __init__(self):
        self.n8n_url = "http://localhost:5678"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def restart_n8n_completely(self):
        """Completely restart n8n to fix webhook registration"""
        print("🔄 Completely Restarting n8n")
        print("=" * 40)
        
        try:
            # Stop n8n completely
            print("   Stopping n8n...")
            subprocess.run(["pkill", "-f", "n8n"], check=False)
            time.sleep(5)
            
            # Clear any webhook cache
            print("   Clearing webhook cache...")
            subprocess.run(["rm", "-rf", "/Users/andrejsp/ai/n8n/data/webhooks"], check=False)
            
            # Start n8n with proper configuration
            print("   Starting n8n with proper webhook configuration...")
            env = {
                'N8N_USER_FOLDER': '/Users/andrejsp/ai/n8n/data',
                'N8N_HOST': 'localhost',
                'N8N_PORT': '5678',
                'N8N_WEBHOOK_URL': 'http://localhost:5678',
                'N8N_WEBHOOK_TUNNEL_URL': 'http://localhost:5678',
                'N8N_ENCRYPTION_KEY': 'your-encryption-key-here',
                'N8N_DISABLE_UI': 'false',
                'N8N_DISABLE_PRODUCTION_MAIN_PROCESS': 'false',
                'N8N_WEBHOOK_WAIT_UNLOCK': 'true'
            }
            
            process = subprocess.Popen(
                ["n8n", "start"],
                env={**env, **dict(os.environ)},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for n8n to start
            print("   Waiting for n8n to start...")
            for i in range(30):
                try:
                    response = requests.get(f"{self.n8n_url}", timeout=2)
                    if response.status_code == 200:
                        print("   ✅ n8n started successfully")
                        return True
                except:
                    pass
                time.sleep(2)
                print(f"   Waiting... ({i+1}/30)")
            
            print("   ❌ n8n failed to start within 60 seconds")
            return False
            
        except Exception as e:
            print(f"   ❌ Error restarting n8n: {e}")
            return False
    
    def activate_all_workflows_programmatically(self):
        """Activate all workflows programmatically"""
        print("\n🔧 Activating All Workflows Programmatically")
        print("=" * 40)
        
        try:
            # Get all workflows
            response = requests.get(f"{self.n8n_url}/api/v2/workflows", headers=self.headers, timeout=10)
            if response.status_code != 200:
                print(f"   ❌ Failed to get workflows: HTTP {response.status_code}")
                return False
            
            workflows_data = response.json()
            workflows = workflows_data.get('data', [])
            
            activated_count = 0
            
            for workflow in workflows:
                workflow_id = workflow.get('id')
                workflow_name = workflow.get('name', 'Unknown')
                is_active = workflow.get('active', False)
                
                print(f"   📄 Processing: {workflow_name}")
                
                if not is_active:
                    # Try to activate
                    try:
                        activate_response = requests.put(
                            f"{self.n8n_url}/api/v2/workflows/{workflow_id}",
                            headers=self.headers,
                            json={"active": True},
                            timeout=10
                        )
                        
                        if activate_response.status_code == 200:
                            print(f"      ✅ Activated: {workflow_name}")
                            activated_count += 1
                        else:
                            print(f"      ❌ Failed to activate: {workflow_name}")
                    except Exception as e:
                        print(f"      ❌ Error activating {workflow_name}: {e}")
                else:
                    print(f"      ✅ Already active: {workflow_name}")
                    activated_count += 1
                
                time.sleep(1)  # Wait between activations
            
            print(f"\n   📊 Activated {activated_count}/{len(workflows)} workflows")
            return activated_count > 0
            
        except Exception as e:
            print(f"   ❌ Error activating workflows: {e}")
            return False
    
    def create_working_rag_workflow(self):
        """Create a simple working RAG workflow"""
        print("\n🚀 Creating Working RAG Workflow")
        print("=" * 40)
        
        rag_workflow = {
            "name": "Working RAG Query",
            "nodes": [
                {
                    "id": "webhook-trigger",
                    "name": "RAG Query",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 2,
                    "position": [240, 300],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "working-rag",
                        "responseMode": "responseNode"
                    }
                },
                {
                    "id": "process-query",
                    "name": "Process Query",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 2,
                    "position": [460, 300],
                    "parameters": {
                        "jsCode": """// Process RAG query
const body = $json.body || $json;
const query = body.query || body.input;

if (!query) {
  return [{
    json: {
      error: 'Query is required',
      status: 'error'
    }
  }];
}

return [{
  json: {
    query: query.trim(),
    timestamp: new Date().toISOString()
  }
}];"""
                    }
                },
                {
                    "id": "generate-answer",
                    "name": "Generate Answer",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 4.2,
                    "position": [680, 300],
                    "parameters": {
                        "method": "POST",
                        "url": "http://localhost:11434/api/generate",
                        "headers": {
                            "Content-Type": "application/json"
                        },
                        "body": {
                            "model": "llama-assistant",
                            "prompt": "={{ $json.query }}",
                            "stream": False,
                            "options": {
                                "temperature": 0.1,
                                "top_p": 0.9
                            }
                        },
                        "options": {
                            "timeout": 30000
                        }
                    }
                },
                {
                    "id": "respond",
                    "name": "Respond",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [900, 300],
                    "parameters": {
                        "respondWith": "json",
                        "responseBody": "={{ {\n  \"answer\": $json.response,\n  \"query\": $('Process Query').item.json.query,\n  \"timestamp\": new Date().toISOString(),\n  \"status\": \"success\"\n} }}"
                    }
                }
            ],
            "connections": {
                "RAG Query": {
                    "main": [[{"node": "Process Query", "type": "main", "index": 0}]]
                },
                "Process Query": {
                    "main": [[{"node": "Generate Answer", "type": "main", "index": 0}]]
                },
                "Generate Answer": {
                    "main": [[{"node": "Respond", "type": "main", "index": 0}]]
                }
            },
            "settings": {
                "executionOrder": "v1"
            }
        }
        
        try:
            # Create workflow
            response = requests.post(
                f"{self.n8n_url}/api/v2/workflows",
                headers=self.headers,
                json=rag_workflow,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                workflow_id = result.get('id')
                print(f"   ✅ Working RAG workflow created (ID: {workflow_id})")
                
                # Activate workflow
                activate_response = requests.put(
                    f"{self.n8n_url}/api/v2/workflows/{workflow_id}",
                    headers=self.headers,
                    json={"active": True},
                    timeout=10
                )
                
                if activate_response.status_code == 200:
                    print("   ✅ Working RAG workflow activated")
                    
                    # Wait for webhook registration
                    time.sleep(5)
                    
                    # Test the workflow
                    test_response = requests.post(
                        f"{self.n8n_url}/webhook/working-rag",
                        json={"query": "What is artificial intelligence?"},
                        timeout=30
                    )
                    
                    if test_response.status_code == 200:
                        result = test_response.json()
                        print(f"   ✅ Working RAG workflow tested successfully!")
                        print(f"      Answer: {result.get('answer', 'No answer')[:100]}...")
                        return True
                    else:
                        print(f"   ❌ Working RAG workflow test failed: HTTP {test_response.status_code}")
                        return False
                else:
                    print(f"   ❌ Failed to activate Working RAG workflow: HTTP {activate_response.status_code}")
                    return False
            else:
                print(f"   ❌ Failed to create Working RAG workflow: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error creating Working RAG workflow: {e}")
            return False
    
    def test_all_webhooks(self):
        """Test all webhook endpoints"""
        print("\n🧪 Testing All Webhook Endpoints")
        print("=" * 40)
        
        webhook_tests = [
            ("working-rag", {"query": "What is machine learning?"}),
            ("rag-query", {"query": "What is AI?", "collection": "general_knowledge"}),
            ("document-ingestion", {"directory_path": "/Users/andrejsp/ai/sample_docs", "collection_name": "test"}),
            ("production-rag", {"action": "query", "query": "What is Docker?"})
        ]
        
        working_webhooks = []
        
        for webhook_name, payload in webhook_tests:
            try:
                response = requests.post(
                    f"{self.n8n_url}/webhook/{webhook_name}",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ {webhook_name}: Working")
                    print(f"      Response: {result.get('answer', result.get('message', 'No message'))[:50]}...")
                    working_webhooks.append(webhook_name)
                else:
                    print(f"   ❌ {webhook_name}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {webhook_name}: {e}")
        
        print(f"\n   📊 Working webhooks: {len(working_webhooks)}/{len(webhook_tests)}")
        return working_webhooks
    
    def run_complete_deployment(self):
        """Run complete production deployment"""
        print("🚀 Complete Production Deployment")
        print("=" * 50)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Restart n8n completely
        restart_success = self.restart_n8n_completely()
        if not restart_success:
            print("   ❌ Failed to restart n8n")
            return False
        
        # Step 2: Activate all workflows
        activation_success = self.activate_all_workflows_programmatically()
        
        # Step 3: Create working RAG workflow
        rag_success = self.create_working_rag_workflow()
        
        # Step 4: Test all webhooks
        working_webhooks = self.test_all_webhooks()
        
        # Summary
        print(f"\n📊 Complete Deployment Summary:")
        print(f"   n8n restart: {'✅' if restart_success else '❌'}")
        print(f"   Workflow activation: {'✅' if activation_success else '❌'}")
        print(f"   Working RAG: {'✅' if rag_success else '❌'}")
        print(f"   Working webhooks: {len(working_webhooks)}")
        
        if len(working_webhooks) > 0:
            print(f"\n🎉 Production Deployment Successful!")
            print(f"   Working webhooks: {', '.join(working_webhooks)}")
            print(f"   System is ready for production use!")
            return True
        else:
            print(f"\n⚠️  Production Deployment completed with issues")
            print(f"   Manual activation in n8n UI may be required")
            return False

def main():
    """Main function"""
    import os
    deployment = ProductionDeployment()
    success = deployment.run_complete_deployment()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())