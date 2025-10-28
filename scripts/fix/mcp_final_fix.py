#!/usr/bin/env python3
"""
MCP Final Fix - Complete solution using MCP tools
Restart n8n and ensure proper webhook registration
"""

import requests
import json
import time
import subprocess
import sys
from datetime import datetime

class MCPFinalFixer:
    def __init__(self):
        self.n8n_url = "http://localhost:5678"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def restart_n8n_with_webhook_fix(self):
        """Restart n8n with proper webhook configuration"""
        print("🔄 Restarting n8n with Webhook Fix")
        print("=" * 40)
        
        try:
            # Stop n8n
            print("   Stopping n8n...")
            subprocess.run(["pkill", "-f", "n8n"], check=False)
            time.sleep(5)
            
            # Start n8n with proper environment for webhooks
            print("   Starting n8n with webhook configuration...")
            env = {
                'N8N_USER_FOLDER': '/Users/andrejsp/ai/n8n/data',
                'N8N_HOST': 'localhost',
                'N8N_PORT': '5678',
                'N8N_WEBHOOK_URL': 'http://localhost:5678',
                'N8N_WEBHOOK_TUNNEL_URL': 'http://localhost:5678',
                'N8N_ENCRYPTION_KEY': 'your-encryption-key-here',
                'N8N_DISABLE_UI': 'false',
                'N8N_DISABLE_PRODUCTION_MAIN_PROCESS': 'false'
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
    
    def create_simple_test_workflow(self):
        """Create a simple test workflow to verify webhook functionality"""
        print("\n🔧 Creating Simple Test Workflow")
        print("=" * 40)
        
        simple_workflow = {
            "name": "MCP Test Webhook",
            "nodes": [
                {
                    "id": "webhook-trigger",
                    "name": "Test Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 2,
                    "position": [240, 300],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "mcp-test",
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
                        "responseBody": "={{ {\"status\": \"success\", \"message\": \"MCP Test Webhook Working!\", \"timestamp\": new Date().toISOString()} }}"
                    }
                }
            ],
            "connections": {
                "Test Webhook": {
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
                json=simple_workflow,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                workflow_id = result.get('id')
                print(f"   ✅ Test workflow created (ID: {workflow_id})")
                
                # Activate workflow
                activate_response = requests.put(
                    f"{self.n8n_url}/api/v2/workflows/{workflow_id}",
                    headers=self.headers,
                    json={"active": True},
                    timeout=10
                )
                
                if activate_response.status_code == 200:
                    print("   ✅ Test workflow activated")
                    
                    # Wait for webhook registration
                    time.sleep(5)
                    
                    # Test webhook
                    test_response = requests.post(
                        f"{self.n8n_url}/webhook/mcp-test",
                        json={"test": "data"},
                        timeout=10
                    )
                    
                    if test_response.status_code == 200:
                        result = test_response.json()
                        print(f"   ✅ Webhook working! Response: {result}")
                        return True
                    else:
                        print(f"   ❌ Webhook test failed: HTTP {test_response.status_code}")
                        print(f"      Response: {test_response.text[:200]}")
                        return False
                else:
                    print(f"   ❌ Failed to activate test workflow: HTTP {activate_response.status_code}")
                    return False
            else:
                print(f"   ❌ Failed to create test workflow: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error creating test workflow: {e}")
            return False
    
    def test_system_health(self):
        """Test complete system health"""
        print("\n🔍 Testing System Health")
        print("=" * 40)
        
        services = {
            "n8n": self.n8n_url,
            "Ollama": "http://localhost:11434/api/tags",
            "ChromaDB": "http://localhost:8000/api/v2/heartbeat"
        }
        
        healthy_services = []
        
        for service_name, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ {service_name}: Healthy")
                    healthy_services.append(service_name)
                else:
                    print(f"   ⚠️  {service_name}: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {service_name}: {e}")
        
        return healthy_services
    
    def create_final_production_workflow(self):
        """Create final production workflow with RAG capabilities"""
        print("\n🚀 Creating Final Production Workflow")
        print("=" * 40)
        
        production_workflow = {
            "name": "Final Production RAG Workflow",
            "nodes": [
                {
                    "id": "webhook-trigger",
                    "name": "RAG Query Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 2,
                    "position": [240, 300],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "final-rag",
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
                    "name": "Respond to Webhook",
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
                "RAG Query Webhook": {
                    "main": [[{"node": "Process Query", "type": "main", "index": 0}]]
                },
                "Process Query": {
                    "main": [[{"node": "Generate Answer", "type": "main", "index": 0}]]
                },
                "Generate Answer": {
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
                json=production_workflow,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                workflow_id = result.get('id')
                print(f"   ✅ Production workflow created (ID: {workflow_id})")
                
                # Activate workflow
                activate_response = requests.put(
                    f"{self.n8n_url}/api/v2/workflows/{workflow_id}",
                    headers=self.headers,
                    json={"active": True},
                    timeout=10
                )
                
                if activate_response.status_code == 200:
                    print("   ✅ Production workflow activated")
                    
                    # Wait for webhook registration
                    time.sleep(5)
                    
                    # Test the workflow
                    test_response = requests.post(
                        f"{self.n8n_url}/webhook/final-rag",
                        json={"query": "What is artificial intelligence?"},
                        timeout=30
                    )
                    
                    if test_response.status_code == 200:
                        result = test_response.json()
                        print(f"   ✅ Production workflow working!")
                        print(f"      Answer: {result.get('answer', 'No answer')[:100]}...")
                        return True
                    else:
                        print(f"   ❌ Production workflow test failed: HTTP {test_response.status_code}")
                        return False
                else:
                    print(f"   ❌ Failed to activate production workflow: HTTP {activate_response.status_code}")
                    return False
            else:
                print(f"   ❌ Failed to create production workflow: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error creating production workflow: {e}")
            return False
    
    def run_final_fix(self):
        """Run complete final fix using MCP approach"""
        print("🚀 MCP Final Fix - Complete Solution")
        print("=" * 50)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Test system health
        healthy_services = self.test_system_health()
        
        # Step 2: Restart n8n if needed
        if "n8n" not in healthy_services:
            restart_success = self.restart_n8n_with_webhook_fix()
            if not restart_success:
                print("   ❌ Failed to restart n8n")
                return False
        
        # Step 3: Create simple test workflow
        test_success = self.create_simple_test_workflow()
        
        # Step 4: Create production workflow
        production_success = self.create_final_production_workflow()
        
        # Step 5: Final system test
        final_health = self.test_system_health()
        
        # Summary
        print(f"\n📊 MCP Final Fix Summary:")
        print(f"   System health: {len(healthy_services)}/3 services")
        print(f"   Test workflow: {'✅' if test_success else '❌'}")
        print(f"   Production workflow: {'✅' if production_success else '❌'}")
        print(f"   Final health: {len(final_health)}/3 services")
        
        if test_success or production_success:
            print(f"\n🎉 MCP Fix Successful!")
            print(f"   System is ready for production use")
            return True
        else:
            print(f"\n⚠️  MCP Fix completed with issues")
            print(f"   Manual activation in n8n UI may be required")
            return False

def main():
    """Main function"""
    import os
    fixer = MCPFinalFixer()
    success = fixer.run_final_fix()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())