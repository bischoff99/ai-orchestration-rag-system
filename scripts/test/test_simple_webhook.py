#!/usr/bin/env python3
"""
Test Simple Webhook Creation
Creates a minimal webhook workflow to test n8n webhook functionality
"""

import requests
import json

def create_simple_webhook_workflow():
    """Create a simple test webhook workflow"""
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
    
    headers = {
        'X-N8N-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    # Simple webhook workflow
    workflow = {
        "name": "Simple Test Webhook",
        "nodes": [
            {
                "id": "webhook-trigger",
                "name": "Webhook Trigger",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "test-webhook",
                    "responseMode": "responseNode"
                }
            },
            {
                "id": "respond",
                "name": "Respond to Webhook",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [460, 300],
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ {\"status\": \"success\", \"message\": \"Webhook working!\", \"data\": $json} }}"
                }
            }
        ],
        "connections": {
            "Webhook Trigger": {
                "main": [[{"node": "Respond to Webhook", "type": "main", "index": 0}]]
            }
        },
        "settings": {
            "executionOrder": "v1"
        }
    }
    
    try:
        print("📄 Creating simple test webhook...")
        response = requests.post(
            'http://localhost:5678/api/v2/workflows',
            headers=headers,
            json=workflow,
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            workflow_id = result.get('id')
            print(f"✅ Created test webhook (ID: {workflow_id})")
            
            # Activate the workflow
            print("🔄 Activating test webhook...")
            activate_response = requests.patch(
                f'http://localhost:5678/api/v2/workflows/{workflow_id}',
                headers=headers,
                json={"active": True},
                timeout=10
            )
            
            if activate_response.status_code == 200:
                print("✅ Test webhook activated")
                
                # Test the webhook
                print("🧪 Testing webhook...")
                test_response = requests.post(
                    'http://localhost:5678/webhook/test-webhook',
                    json={"test": "data"},
                    timeout=10
                )
                
                if test_response.status_code == 200:
                    result = test_response.json()
                    print(f"✅ Webhook test successful!")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                    return True
                else:
                    print(f"❌ Webhook test failed: HTTP {test_response.status_code}")
                    print(f"   Response: {test_response.text}")
                    return False
            else:
                print(f"❌ Failed to activate webhook: HTTP {activate_response.status_code}")
                return False
        else:
            print(f"❌ Failed to create webhook: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing n8n Webhook Functionality")
    print("=" * 40)
    
    success = create_simple_webhook_workflow()
    
    if success:
        print("\n🎉 n8n webhook system is working!")
        print("The issue is with the existing workflow configurations.")
    else:
        print("\n❌ n8n webhook system has issues.")
        print("Check n8n logs for more details.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())