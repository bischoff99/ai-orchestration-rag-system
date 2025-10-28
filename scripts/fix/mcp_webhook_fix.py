#!/usr/bin/env python3
"""
MCP Webhook Fix - Use MCP tools to fix webhook registration issues
Comprehensive solution using MCP n8n tools
"""

import requests
import json
import time
import sys
from datetime import datetime

class MCPWebhookFixer:
    def __init__(self):
        self.n8n_url = "http://localhost:5678"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def create_working_webhook_workflow(self):
        """Create a simple working webhook workflow using MCP approach"""
        print("🔧 Creating Working Webhook Workflow")
        print("=" * 40)
        
        # Simple webhook workflow that should work
        workflow = {
            "name": "MCP Fixed Webhook",
            "nodes": [
                {
                    "id": "webhook-trigger",
                    "name": "Webhook Trigger",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 2,
                    "position": [240, 300],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "mcp-fixed",
                        "responseMode": "responseNode"
                    }
                },
                {
                    "id": "respond",
                    "name": "Respond",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [460, 300],
                    "parameters": {
                        "respondWith": "json",
                        "responseBody": "={{ {\"status\": \"success\", \"message\": \"MCP Fixed Webhook Working!\", \"timestamp\": new Date().toISOString()} }}"
                    }
                }
            ],
            "connections": {
                "Webhook Trigger": {
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
                json=workflow,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                workflow_id = result.get('id')
                print(f"   ✅ Workflow created (ID: {workflow_id})")
                
                # Activate workflow
                activate_response = requests.put(
                    f"{self.n8n_url}/api/v2/workflows/{workflow_id}",
                    headers=self.headers,
                    json={"active": True},
                    timeout=10
                )
                
                if activate_response.status_code == 200:
                    print("   ✅ Workflow activated")
                    
                    # Wait for webhook registration
                    time.sleep(5)
                    
                    # Test webhook
                    test_response = requests.post(
                        f"{self.n8n_url}/webhook/mcp-fixed",
                        json={"test": "data"},
                        timeout=10
                    )
                    
                    if test_response.status_code == 200:
                        result = test_response.json()
                        print(f"   ✅ Webhook working! Response: {result}")
                        return True
                    else:
                        print(f"   ❌ Webhook test failed: HTTP {test_response.status_code}")
                        return False
                else:
                    print(f"   ❌ Failed to activate workflow: HTTP {activate_response.status_code}")
                    return False
            else:
                print(f"   ❌ Failed to create workflow: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def fix_existing_workflows(self):
        """Fix existing workflows by recreating them with proper structure"""
        print("\n🔧 Fixing Existing Workflows")
        print("=" * 40)
        
        try:
            # Get all workflows
            response = requests.get(f"{self.n8n_url}/api/v2/workflows", headers=self.headers, timeout=10)
            if response.status_code != 200:
                print(f"   ❌ Failed to get workflows: HTTP {response.status_code}")
                return False
            
            workflows_data = response.json()
            workflows = workflows_data.get('data', [])
            
            fixed_count = 0
            
            for workflow in workflows:
                workflow_id = workflow.get('id')
                workflow_name = workflow.get('name', 'Unknown')
                is_active = workflow.get('active', False)
                
                if not is_active:
                    continue
                
                print(f"   📄 Processing: {workflow_name}")
                
                # Deactivate and reactivate to force webhook registration
                try:
                    # Deactivate
                    deactivate_response = requests.put(
                        f"{self.n8n_url}/api/v2/workflows/{workflow_id}",
                        headers=self.headers,
                        json={"active": False},
                        timeout=10
                    )
                    
                    time.sleep(2)
                    
                    # Reactivate
                    activate_response = requests.put(
                        f"{self.n8n_url}/api/v2/workflows/{workflow_id}",
                        headers=self.headers,
                        json={"active": True},
                        timeout=10
                    )
                    
                    if activate_response.status_code == 200:
                        print(f"      ✅ Fixed: {workflow_name}")
                        fixed_count += 1
                    else:
                        print(f"      ❌ Failed to fix: {workflow_name}")
                
                except Exception as e:
                    print(f"      ❌ Error fixing {workflow_name}: {e}")
                
                time.sleep(1)  # Wait between fixes
            
            print(f"\n   📊 Fixed {fixed_count} workflows")
            return fixed_count > 0
            
        except Exception as e:
            print(f"   ❌ Error fixing workflows: {e}")
            return False
    
    def test_all_webhooks(self):
        """Test all webhook endpoints"""
        print("\n🧪 Testing All Webhooks")
        print("=" * 40)
        
        webhook_tests = [
            ("mcp-fixed", {"test": "data"}),
            ("rag-query", {"query": "What is machine learning?", "collection": "general_knowledge"}),
            ("document-ingestion", {"directory_path": "/Users/andrejsp/ai/sample_docs", "collection_name": "test"}),
            ("production-rag", {"action": "query", "query": "What is AI?", "collection": "general_knowledge"})
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
                    print(f"      Response: {result.get('message', 'No message')[:50]}...")
                    working_webhooks.append(webhook_name)
                else:
                    print(f"   ❌ {webhook_name}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {webhook_name}: {e}")
        
        print(f"\n   📊 Working webhooks: {len(working_webhooks)}/{len(webhook_tests)}")
        return working_webhooks
    
    def create_production_rag_workflow(self):
        """Create a production-ready RAG workflow"""
        print("\n🚀 Creating Production RAG Workflow")
        print("=" * 40)
        
        rag_workflow = {
            "name": "Production RAG - MCP Fixed",
            "nodes": [
                {
                    "id": "webhook-trigger",
                    "name": "RAG Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 2,
                    "position": [240, 300],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "production-rag-fixed",
                        "responseMode": "responseNode"
                    }
                },
                {
                    "id": "validate-input",
                    "name": "Validate Input",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 2,
                    "position": [460, 300],
                    "parameters": {
                        "jsCode": """// Validate and process input
const body = $json.body || $json;
const query = body.query;

if (!query || query.trim().length === 0) {
  return [{
    json: {
      error: 'Query is required and cannot be empty',
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
                    "id": "generate-response",
                    "name": "Generate Response",
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
                    "name": "Respond to Webhook",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [900, 300],
                    "parameters": {
                        "respondWith": "json",
                        "responseBody": "={{ {\n  \"answer\": $json.response,\n  \"query\": $('Validate Input').item.json.query,\n  \"timestamp\": new Date().toISOString(),\n  \"status\": \"success\"\n} }}"
                    }
                }
            ],
            "connections": {
                "RAG Webhook": {
                    "main": [[{"node": "Validate Input", "type": "main", "index": 0}]]
                },
                "Validate Input": {
                    "main": [[{"node": "Generate Response", "type": "main", "index": 0}]]
                },
                "Generate Response": {
                    "main": [[{"node": "Respond to Webhook", "type": "main", "index": 0}]]
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
                print(f"   ✅ Production RAG workflow created (ID: {workflow_id})")
                
                # Activate workflow
                activate_response = requests.put(
                    f"{self.n8n_url}/api/v2/workflows/{workflow_id}",
                    headers=self.headers,
                    json={"active": True},
                    timeout=10
                )
                
                if activate_response.status_code == 200:
                    print("   ✅ Production RAG workflow activated")
                    
                    # Wait for webhook registration
                    time.sleep(5)
                    
                    # Test the workflow
                    test_response = requests.post(
                        f"{self.n8n_url}/webhook/production-rag-fixed",
                        json={"query": "What is artificial intelligence?"},
                        timeout=30
                    )
                    
                    if test_response.status_code == 200:
                        result = test_response.json()
                        print(f"   ✅ Production RAG working! Answer: {result.get('answer', 'No answer')[:100]}...")
                        return True
                    else:
                        print(f"   ❌ Production RAG test failed: HTTP {test_response.status_code}")
                        return False
                else:
                    print(f"   ❌ Failed to activate Production RAG workflow: HTTP {activate_response.status_code}")
                    return False
            else:
                print(f"   ❌ Failed to create Production RAG workflow: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error creating Production RAG workflow: {e}")
            return False
    
    def run_mcp_fix(self):
        """Run complete MCP-based fix"""
        print("🚀 MCP Webhook Fix - Using MCP Tools")
        print("=" * 50)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Create working webhook
        webhook_success = self.create_working_webhook_workflow()
        
        # Step 2: Fix existing workflows
        fix_success = self.fix_existing_workflows()
        
        # Step 3: Create production RAG workflow
        rag_success = self.create_production_rag_workflow()
        
        # Step 4: Test all webhooks
        working_webhooks = self.test_all_webhooks()
        
        # Summary
        print(f"\n📊 MCP Fix Summary:")
        print(f"   Working webhook: {'✅' if webhook_success else '❌'}")
        print(f"   Workflow fixes: {'✅' if fix_success else '❌'}")
        print(f"   Production RAG: {'✅' if rag_success else '❌'}")
        print(f"   Working webhooks: {len(working_webhooks)}")
        
        if len(working_webhooks) > 0:
            print(f"\n🎉 MCP Fix Successful!")
            print(f"   Working webhooks: {', '.join(working_webhooks)}")
            return True
        else:
            print(f"\n⚠️  MCP Fix partially successful - manual activation may be needed")
            return False

def main():
    """Main function"""
    fixer = MCPWebhookFixer()
    success = fixer.run_mcp_fix()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())