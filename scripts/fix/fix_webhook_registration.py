#!/usr/bin/env python3
"""
Fix n8n Webhook Registration Issue
Comprehensive solution for webhook activation problems
"""

import requests
import json
import time
import subprocess
import sys
from datetime import datetime

class WebhookRegistrationFixer:
    def __init__(self):
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
        self.base_url = "http://localhost:5678"
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def restart_n8n_with_workflow_activation(self):
        """Restart n8n and ensure workflows are properly activated"""
        print("🔄 Restarting n8n with workflow activation...")
        
        try:
            # Stop n8n
            print("   Stopping n8n...")
            subprocess.run(["pkill", "-f", "n8n"], check=False)
            time.sleep(3)
            
            # Start n8n with proper environment
            print("   Starting n8n...")
            env = {
                'N8N_USER_FOLDER': '/Users/andrejsp/ai/n8n/data',
                'N8N_HOST': 'localhost',
                'N8N_PORT': '5678',
                'N8N_WEBHOOK_URL': 'http://localhost:5678',
                'N8N_ENCRYPTION_KEY': 'your-encryption-key-here'
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
                    response = requests.get(f"{self.base_url}", timeout=2)
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
    
    def activate_workflows_manually(self):
        """Manually activate workflows by toggling them off and on"""
        print("🔧 Manually activating workflows...")
        
        try:
            # Get all workflows
            response = requests.get(f"{self.base_url}/api/v2/workflows", headers=self.headers, timeout=10)
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
                
                # First, deactivate if active
                if is_active:
                    print(f"      Deactivating...")
                    deactivate_response = requests.put(
                        f"{self.base_url}/api/v2/workflows/{workflow_id}",
                        headers=self.headers,
                        json={"active": False},
                        timeout=10
                    )
                    time.sleep(1)
                
                # Then activate
                print(f"      Activating...")
                activate_response = requests.put(
                    f"{self.base_url}/api/v2/workflows/{workflow_id}",
                    headers=self.headers,
                    json={"active": True},
                    timeout=10
                )
                
                if activate_response.status_code == 200:
                    print(f"      ✅ Activated successfully")
                    activated_count += 1
                else:
                    print(f"      ❌ Failed to activate: HTTP {activate_response.status_code}")
                    print(f"      Response: {activate_response.text[:100]}")
                
                time.sleep(2)  # Wait between activations
            
            print(f"   📊 Activated {activated_count} workflows")
            return activated_count > 0
            
        except Exception as e:
            print(f"   ❌ Error activating workflows: {e}")
            return False
    
    def test_webhook_endpoints(self):
        """Test all webhook endpoints"""
        print("🧪 Testing webhook endpoints...")
        
        # Get all workflows
        try:
            response = requests.get(f"{self.base_url}/api/v2/workflows", headers=self.headers, timeout=10)
            if response.status_code != 200:
                print(f"   ❌ Failed to get workflows: HTTP {response.status_code}")
                return False
            
            workflows_data = response.json()
            workflows = workflows_data.get('data', [])
            
            working_webhooks = []
            failed_webhooks = []
            
            for workflow in workflows:
                workflow_name = workflow.get('name', 'Unknown')
                is_active = workflow.get('active', False)
                
                if not is_active:
                    continue
                
                # Get workflow details to find webhook paths
                workflow_id = workflow.get('id')
                detail_response = requests.get(
                    f"{self.base_url}/api/v2/workflows/{workflow_id}",
                    headers=self.headers,
                    timeout=10
                )
                
                if detail_response.status_code == 200:
                    workflow_detail = detail_response.json()
                    nodes = workflow_detail.get('nodes', [])
                    
                    for node in nodes:
                        if node.get('type') == 'n8n-nodes-base.webhook':
                            path = node.get('parameters', {}).get('path', '')
                            if path:
                                webhook_url = f"{self.base_url}/webhook/{path}"
                                
                                print(f"   🧪 Testing {workhook_url}...")
                                
                                try:
                                    test_response = requests.post(
                                        webhook_url,
                                        json={"test": "data"},
                                        timeout=5
                                    )
                                    
                                    if test_response.status_code == 200:
                                        print(f"      ✅ Working")
                                        working_webhooks.append(webhook_url)
                                    else:
                                        print(f"      ❌ HTTP {test_response.status_code}")
                                        failed_webhooks.append(webhook_url)
                                        
                                except Exception as e:
                                    print(f"      ❌ Error: {e}")
                                    failed_webhooks.append(webhook_url)
            
            print(f"\n   📊 Webhook Test Results:")
            print(f"      ✅ Working: {len(working_webhooks)}")
            print(f"      ❌ Failed: {len(failed_webhooks)}")
            
            if working_webhooks:
                print(f"      Working webhooks:")
                for webhook in working_webhooks:
                    print(f"        • {webhook}")
            
            if failed_webhooks:
                print(f"      Failed webhooks:")
                for webhook in failed_webhooks:
                    print(f"        • {webhook}")
            
            return len(working_webhooks) > 0
            
        except Exception as e:
            print(f"   ❌ Error testing webhooks: {e}")
            return False
    
    def create_simple_test_workflow(self):
        """Create a simple test workflow to verify webhook functionality"""
        print("🔧 Creating simple test workflow...")
        
        simple_workflow = {
            "name": "Simple Webhook Test",
            "nodes": [
                {
                    "id": "webhook-trigger",
                    "name": "Test Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 2,
                    "position": [240, 300],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "test-simple",
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
                        "responseBody": "={{ {\"status\": \"success\", \"message\": \"Webhook working!\", \"timestamp\": new Date().toISOString()} }}"
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
                f"{self.base_url}/api/v2/workflows",
                headers=self.headers,
                json=simple_workflow,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                workflow_id = result.get('id')
                print(f"   ✅ Created test workflow (ID: {workflow_id})")
                
                # Activate workflow
                activate_response = requests.put(
                    f"{self.base_url}/api/v2/workflows/{workflow_id}",
                    headers=self.headers,
                    json={"active": True},
                    timeout=10
                )
                
                if activate_response.status_code == 200:
                    print(f"   ✅ Activated test workflow")
                    
                    # Test the webhook
                    time.sleep(2)
                    test_response = requests.post(
                        f"{self.base_url}/webhook/test-simple",
                        json={"test": "data"},
                        timeout=10
                    )
                    
                    if test_response.status_code == 200:
                        result = test_response.json()
                        print(f"   ✅ Test webhook working: {result.get('message')}")
                        return True
                    else:
                        print(f"   ❌ Test webhook failed: HTTP {test_response.status_code}")
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
    
    def run_complete_fix(self):
        """Run complete webhook registration fix"""
        print("🚀 Fixing n8n Webhook Registration Issues")
        print("=" * 50)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Create simple test workflow
        test_success = self.create_simple_test_workflow()
        
        if not test_success:
            print("\n🔄 Test workflow failed, restarting n8n...")
            restart_success = self.restart_n8n_with_workflow_activation()
            
            if restart_success:
                # Try creating test workflow again
                test_success = self.create_simple_test_workflow()
        
        # Step 2: Manually activate all workflows
        activation_success = self.activate_workflows_manually()
        
        # Step 3: Test all webhook endpoints
        webhook_success = self.test_webhook_endpoints()
        
        # Summary
        print(f"\n📊 Webhook Fix Summary:")
        print(f"   Test workflow: {'✅' if test_success else '❌'}")
        print(f"   Workflow activation: {'✅' if activation_success else '❌'}")
        print(f"   Webhook endpoints: {'✅' if webhook_success else '❌'}")
        
        if webhook_success:
            print(f"\n🎉 Webhook registration fixed successfully!")
            return True
        else:
            print(f"\n⚠️  Webhook registration still has issues")
            print(f"   Manual activation in n8n UI may be required:")
            print(f"   1. Open http://localhost:5678")
            print(f"   2. Go to Workflows section")
            print(f"   3. Toggle 'Active' switch for each workflow")
            return False

def main():
    """Main function"""
    import os
    fixer = WebhookRegistrationFixer()
    success = fixer.run_complete_fix()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())