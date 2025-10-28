#!/usr/bin/env python3
"""
Create a simple working webhook to test the system
"""

import requests
import json

def create_working_webhook():
    """Create a simple working webhook"""

    n8n_url = "http://localhost:5678"
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"

    headers = {
        'X-N8N-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    # Simple working webhook workflow
    workflow = {
        "name": "Working Test Webhook",
        "nodes": [
            {
                "id": "webhook-trigger",
                "name": "Test Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "working-test",
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
                    "jsCode": """// Process incoming data
const body = $json.body || $json;
const message = body.message || body.query || 'Hello from n8n!';

return [{
  json: {
    message: message,
    timestamp: new Date().toISOString(),
    status: 'success',
    processed: true
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
            "Test Webhook": {
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
        print("🚀 Creating working webhook...")
        response = requests.post(
            f"{n8n_url}/api/v2/workflows",
            headers=headers,
            json=workflow,
            timeout=30
        )

        if response.status_code in [200, 201]:
            result = response.json()
            workflow_id = result.get('id')
            print(f"   ✅ Webhook workflow created (ID: {workflow_id})")

            # Activate workflow
            activate_response = requests.put(
                f"{n8n_url}/api/v2/workflows/{workflow_id}",
                headers=headers,
                json={"active": True},
                timeout=10
            )

            if activate_response.status_code == 200:
                print("   ✅ Webhook workflow activated")

                # Wait for webhook registration
                import time
                time.sleep(3)

                # Test the webhook
                test_response = requests.post(
                    f"{n8n_url}/webhook/working-test",
                    json={"message": "Testing webhook functionality"},
                    timeout=10
                )

                if test_response.status_code == 200:
                    result = test_response.json()
                    print(f"   ✅ Webhook test successful!")
                    print(f"      Response: {result}")
                    return True
                else:
                    print(f"   ❌ Webhook test failed: HTTP {test_response.status_code}")
                    print(f"      Response: {test_response.text}")
                    return False
            else:
                print(f"   ❌ Failed to activate webhook: HTTP {activate_response.status_code}")
                return False
        else:
            print(f"   ❌ Failed to create webhook: HTTP {response.status_code}")
            print(f"      Response: {response.text}")
            return False

    except Exception as e:
        print(f"   ❌ Error creating webhook: {e}")
        return False

if __name__ == "__main__":
    success = create_working_webhook()
    exit(0 if success else 1)
