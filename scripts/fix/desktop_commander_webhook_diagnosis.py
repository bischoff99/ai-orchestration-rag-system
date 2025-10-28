#!/usr/bin/env python3
"""
Desktop Commander Webhook Diagnosis and Fix
Comprehensive diagnosis and fix for n8n webhook issues
"""

import requests
import json
import time
import subprocess
import os
from typing import Dict, Any, List

class N8nWebhookDiagnosis:
    def __init__(self):
        self.base_url = "http://localhost:5678"
        self.api_url = f"{self.base_url}/api/v1"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
        self.session = requests.Session()
        self.session.headers.update({
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json"
        })
    
    def check_n8n_status(self) -> bool:
        """Check if n8n is running and accessible"""
        try:
            response = self.session.get(f"{self.base_url}/healthz", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_workflows(self) -> List[Dict]:
        """Get all workflows"""
        try:
            response = self.session.get(f"{self.api_url}/workflows")
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                print(f"❌ Failed to get workflows: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting workflows: {e}")
            return []
    
    def get_workflow_details(self, workflow_id: str) -> Dict:
        """Get detailed workflow information"""
        try:
            response = self.session.get(f"{self.api_url}/workflows/{workflow_id}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get workflow {workflow_id}: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Error getting workflow {workflow_id}: {e}")
            return {}
    
    def test_webhook_endpoint(self, webhook_path: str) -> Dict:
        """Test a webhook endpoint"""
        webhook_url = f"{self.base_url}/webhook/{webhook_path}"
        try:
            response = requests.post(
                webhook_url,
                json={"test": "data"},
                timeout=5
            )
            return {
                "status_code": response.status_code,
                "response": response.text[:200],
                "working": response.status_code != 404
            }
        except Exception as e:
            return {
                "status_code": 0,
                "response": str(e),
                "working": False
            }
    
    def restart_n8n(self) -> bool:
        """Restart n8n service"""
        try:
            print("🔄 Restarting n8n...")
            
            # Kill existing n8n processes
            subprocess.run(["pkill", "-f", "n8n"], capture_output=True)
            time.sleep(2)
            
            # Start n8n
            env = os.environ.copy()
            env.update({
                "N8N_USER_FOLDER": "/Users/andrejsp/ai/n8n/data",
                "N8N_HOST": "localhost",
                "N8N_PORT": "5678",
                "N8N_WEBHOOK_URL": "http://localhost:5678",
                "N8N_WEBHOOK_TUNNEL_URL": "http://localhost:5678"
            })
            
            # Start n8n in background
            process = subprocess.Popen(
                ["n8n", "start"],
                cwd="/Users/andrejsp/ai/n8n",
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for n8n to start
            for i in range(30):
                time.sleep(2)
                if self.check_n8n_status():
                    print("✅ n8n restarted successfully")
                    return True
                print(f"⏳ Waiting for n8n to start... ({i+1}/30)")
            
            print("❌ n8n failed to start within 60 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Error restarting n8n: {e}")
            return False
    
    def diagnose_webhooks(self):
        """Comprehensive webhook diagnosis"""
        print("🔍 N8N Webhook Diagnosis")
        print("=" * 50)
        
        # Check n8n status
        if not self.check_n8n_status():
            print("❌ n8n is not running or not accessible")
            return False
        
        print("✅ n8n is running")
        
        # Get workflows
        workflows = self.get_workflows()
        if not workflows:
            print("❌ No workflows found")
            return False
        
        print(f"✅ Found {len(workflows)} workflows")
        
        # Check each workflow
        webhook_workflows = []
        for workflow in workflows:
            workflow_id = workflow.get('id')
            workflow_name = workflow.get('name')
            active = workflow.get('active', False)
            
            print(f"\n📋 Workflow: {workflow_name} (ID: {workflow_id})")
            print(f"   Active: {'✅' if active else '❌'}")
            
            if active:
                # Get detailed workflow info
                details = self.get_workflow_details(workflow_id)
                nodes = details.get('nodes', [])
                
                # Find webhook nodes
                webhook_nodes = [node for node in nodes if node.get('type') == 'n8n-nodes-base.webhook']
                
                if webhook_nodes:
                    for webhook_node in webhook_nodes:
                        webhook_path = webhook_node.get('parameters', {}).get('path', '')
                        if webhook_path:
                            webhook_workflows.append({
                                'workflow_id': workflow_id,
                                'workflow_name': workflow_name,
                                'webhook_path': webhook_path,
                                'webhook_node': webhook_node
                            })
                            print(f"   Webhook: /webhook/{webhook_path}")
                            
                            # Test webhook
                            test_result = self.test_webhook_endpoint(webhook_path)
                            status = "✅ WORKING" if test_result['working'] else "❌ NOT WORKING"
                            print(f"   Status: {status}")
                            if not test_result['working']:
                                print(f"   Error: {test_result['response']}")
                else:
                    print("   No webhook nodes found")
        
        return webhook_workflows
    
    def fix_webhook_registration(self):
        """Attempt to fix webhook registration"""
        print("\n🔧 Attempting to fix webhook registration...")
        
        # Method 1: Restart n8n
        if self.restart_n8n():
            print("✅ n8n restarted, testing webhooks...")
            time.sleep(5)
            
            # Test webhooks again
            webhook_workflows = self.diagnose_webhooks()
            
            if webhook_workflows:
                working_count = 0
                for webhook_info in webhook_workflows:
                    test_result = self.test_webhook_endpoint(webhook_info['webhook_path'])
                    if test_result['working']:
                        working_count += 1
                
                print(f"\n📊 Results: {working_count}/{len(webhook_workflows)} webhooks working")
                
                if working_count == len(webhook_workflows):
                    print("🎉 All webhooks are now working!")
                    return True
                else:
                    print("⚠️  Some webhooks are still not working")
                    return False
            else:
                print("❌ No webhook workflows found")
                return False
        else:
            print("❌ Failed to restart n8n")
            return False

def main():
    """Main diagnosis and fix process"""
    diagnosis = N8nWebhookDiagnosis()
    
    print("🚀 Starting comprehensive n8n webhook diagnosis and fix")
    print("=" * 60)
    
    # Run diagnosis
    webhook_workflows = diagnosis.diagnose_webhooks()
    
    if not webhook_workflows:
        print("\n❌ No webhook workflows found. Cannot proceed with fix.")
        return
    
    # Attempt fix
    success = diagnosis.fix_webhook_registration()
    
    if success:
        print("\n🎉 Webhook fix completed successfully!")
        print("\nNext steps:")
        print("1. Test your workflows in the n8n UI")
        print("2. Verify webhook endpoints are accessible")
        print("3. Run your RAG system tests")
    else:
        print("\n❌ Webhook fix failed. Manual intervention required.")
        print("\nManual steps:")
        print("1. Open n8n UI: http://localhost:5678")
        print("2. Go to each workflow")
        print("3. Toggle the 'Active' switch off and on")
        print("4. This will force webhook re-registration")

if __name__ == "__main__":
    main()