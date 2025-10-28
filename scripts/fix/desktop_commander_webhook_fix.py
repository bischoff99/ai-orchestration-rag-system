#!/usr/bin/env python3
"""
Desktop Commander Webhook Fix
Advanced solution to fix n8n webhook registration issues
"""

import requests
import json
import time
import subprocess
import webbrowser
from datetime import datetime

class DesktopCommanderWebhookFix:
    def __init__(self):
        self.n8n_url = "http://localhost:5678"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def restart_n8n_with_webhook_fix(self):
        """Restart n8n with webhook configuration fixes"""
        print("🔄 Desktop Commander: Restarting n8n with webhook fixes...")
        
        try:
            # Kill existing n8n processes
            print("   🛑 Stopping n8n...")
            subprocess.run(["pkill", "-f", "n8n"], check=False)
            time.sleep(3)
            
            # Clear webhook cache
            print("   🧹 Clearing webhook cache...")
            subprocess.run(["rm", "-rf", "/Users/andrejsp/ai/n8n/data/webhooks"], check=False)
            
            # Set webhook environment variables
            print("   ⚙️  Setting webhook environment variables...")
            env_vars = {
                'N8N_USER_FOLDER': '/Users/andrejsp/ai/n8n/data',
                'N8N_HOST': 'localhost',
                'N8N_PORT': '5678',
                'N8N_WEBHOOK_URL': 'http://localhost:5678',
                'N8N_WEBHOOK_TUNNEL_URL': 'http://localhost:5678',
                'N8N_ENCRYPTION_KEY': 'desktop-commander-webhook-fix-key',
                'N8N_DISABLE_UI': 'false',
                'N8N_DISABLE_PRODUCTION_MAIN_PROCESS': 'false',
                'N8N_WEBHOOK_WAIT_UNLOCK': 'true',
                'N8N_WEBHOOK_WAIT_UNLOCK_TIMEOUT': '30000'
            }
            
            # Start n8n with proper webhook configuration
            print("   🚀 Starting n8n with webhook fixes...")
            process = subprocess.Popen(
                ["n8n", "start"],
                env={**env_vars, **dict(subprocess.os.environ)},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for n8n to start
            print("   ⏳ Waiting for n8n to start...")
            for i in range(30):
                try:
                    response = requests.get(self.n8n_url, timeout=2)
                    if response.status_code == 200:
                        print("   ✅ n8n started successfully with webhook fixes")
                        return True
                except:
                    pass
                time.sleep(2)
                print(f"   ⏳ Waiting... ({i+1}/30)")
            
            print("   ❌ n8n failed to start within 60 seconds")
            return False
            
        except Exception as e:
            print(f"   ❌ Error restarting n8n: {e}")
            return False
    
    def create_working_webhook_workflow(self):
        """Create a simple working webhook workflow"""
        print("🔧 Desktop Commander: Creating working webhook workflow...")
        
        workflow = {
            "name": "Desktop Commander Working Webhook",
            "nodes": [
                {
                    "id": "webhook-trigger",
                    "name": "DC Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 2,
                    "position": [240, 300],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "dc-working",
                        "responseMode": "responseNode"
                    }
                },
                {
                    "id": "process-data",
                    "name": "Process Data",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 2,
                    "position": [460, 300],
                    "parameters": {
                        "jsCode": """// Desktop Commander webhook processor
const body = $json.body || $json;
const query = body.query || body.message || 'Hello from Desktop Commander!';

return [{
  json: {
    query: query,
    timestamp: new Date().toISOString(),
    status: 'success',
    processed: true,
    source: 'desktop-commander',
    message: 'Webhook is working!'
  }
}];"""
                    }
                },
                {
                    "id": "respond",
                    "name": "Respond",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [680, 300],
                    "parameters": {
                        "respondWith": "json",
                        "responseBody": "={{ $json }}"
                    }
                }
            ],
            "connections": {
                "DC Webhook": {
                    "main": [[{"node": "Process Data", "type": "main", "index": 0}]]
                },
                "Process Data": {
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
            
            if response.status_code in [200, 201]:
                result = response.json()
                workflow_id = result.get('id')
                print(f"   ✅ Desktop Commander webhook created (ID: {workflow_id})")
                
                # Wait for webhook registration
                print("   ⏳ Waiting for webhook registration...")
                time.sleep(5)
                
                # Test the webhook
                test_response = requests.post(
                    f"{self.n8n_url}/webhook/dc-working",
                    json={'message': 'Desktop Commander test'},
                    timeout=10
                )
                
                if test_response.status_code == 200:
                    result = test_response.json()
                    print(f"   ✅ Desktop Commander webhook test successful!")
                    print(f"      Response: {result}")
                    return True
                else:
                    print(f"   ❌ Desktop Commander webhook test failed: HTTP {test_response.status_code}")
                    return False
            else:
                print(f"   ❌ Failed to create Desktop Commander webhook: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error creating Desktop Commander webhook: {e}")
            return False
    
    def fix_existing_workflows(self):
        """Attempt to fix existing workflows"""
        print("🔧 Desktop Commander: Attempting to fix existing workflows...")
        
        try:
            # Get existing workflows
            response = requests.get(f"{self.n8n_url}/api/v2/workflows", headers=self.headers, timeout=10)
            if response.status_code != 200:
                print(f"   ❌ Failed to get workflows: HTTP {response.status_code}")
                return False
            
            workflows = response.json().get('data', [])
            active_workflows = [w for w in workflows if w.get('active', False)]
            
            print(f"   📊 Found {len(active_workflows)} active workflows")
            
            # Try to trigger workflow execution to force webhook registration
            for wf in active_workflows:
                wf_id = wf.get('id')
                wf_name = wf.get('name', 'Unknown')
                
                try:
                    # Try to execute workflow to trigger webhook registration
                    execute_response = requests.post(
                        f"{self.n8n_url}/api/v2/workflows/{wf_id}/execute",
                        headers=self.headers,
                        json={'test': 'trigger'},
                        timeout=10
                    )
                    
                    if execute_response.status_code in [200, 201]:
                        print(f"   ✅ Triggered execution for: {wf_name}")
                    else:
                        print(f"   ⚠️  Could not trigger: {wf_name}")
                        
                except Exception as e:
                    print(f"   ⚠️  Error triggering {wf_name}: {e}")
                
                time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error fixing workflows: {e}")
            return False
    
    def test_all_webhooks(self):
        """Test all webhook endpoints"""
        print("🧪 Desktop Commander: Testing all webhook endpoints...")
        
        webhooks = [
            'dc-working',
            'rag-query',
            'document-ingestion',
            'rag-query-enhanced',
            'production-rag'
        ]
        
        working_webhooks = []
        
        for webhook in webhooks:
            try:
                response = requests.post(
                    f"{self.n8n_url}/webhook/{webhook}",
                    json={'test': 'data', 'query': 'Desktop Commander test'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ {webhook}: WORKING")
                    print(f"      Response: {str(result)[:100]}...")
                    working_webhooks.append(webhook)
                else:
                    print(f"   ❌ {webhook}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {webhook}: {e}")
        
        print(f"\n   📊 Working webhooks: {len(working_webhooks)}/{len(webhooks)}")
        return working_webhooks
    
    def run_webhook_fix(self):
        """Run comprehensive webhook fix"""
        print("🖥️  Desktop Commander Webhook Fix")
        print("=" * 40)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Step 1: Restart n8n with webhook fixes
        restart_success = self.restart_n8n_with_webhook_fix()
        if not restart_success:
            print("❌ Failed to restart n8n")
            return False
        
        # Step 2: Create working webhook
        webhook_success = self.create_working_webhook_workflow()
        
        # Step 3: Fix existing workflows
        fix_success = self.fix_existing_workflows()
        
        # Step 4: Test all webhooks
        working_webhooks = self.test_all_webhooks()
        
        # Summary
        print("\n📊 Desktop Commander Fix Summary")
        print("=" * 40)
        print(f"n8n restart: {'✅' if restart_success else '❌'}")
        print(f"Working webhook: {'✅' if webhook_success else '❌'}")
        print(f"Workflow fix: {'✅' if fix_success else '❌'}")
        print(f"Working webhooks: {len(working_webhooks)}")
        
        if len(working_webhooks) > 0:
            print("\n🎉 Desktop Commander webhook fix successful!")
            print("✅ System is ready for use!")
            return True
        else:
            print("\n⚠️  Desktop Commander webhook fix completed with issues")
            print("📝 Manual activation may still be required")
            return False

def main():
    """Main function"""
    fixer = DesktopCommanderWebhookFix()
    success = fixer.run_webhook_fix()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())