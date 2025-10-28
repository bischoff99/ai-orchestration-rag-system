#!/usr/bin/env python3
"""
Create Simple Webhook - Test webhook registration
Creates a minimal webhook workflow to test the system
"""

import requests
import json
import time

def create_simple_webhook():
    """Create a simple webhook workflow"""
    
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
    headers = {
        'X-N8N-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    # Simple webhook workflow
    workflow = {
        "name": "Simple Test Webhook - API Created",
        "nodes": [
            {
                "id": "webhook-trigger",
                "name": "Webhook Trigger",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "api-test",
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
            "Webhook Trigger": {
                "main": [[{"node": "Respond", "type": "main", "index": 0}]]
            }
        },
        "settings": {
            "executionOrder": "v1"
        }
    }
    
    try:
        print("🔧 Creating simple webhook workflow...")
        
        # Create workflow
        response = requests.post(
            "http://localhost:5678/api/v2/workflows",
            headers=headers,
            json=workflow,
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            workflow_id = result.get('id')
            print(f"✅ Workflow created (ID: {workflow_id})")
            
            # Activate workflow
            activate_response = requests.put(
                f"http://localhost:5678/api/v2/workflows/{workflow_id}",
                headers=headers,
                json={"active": True},
                timeout=10
            )
            
            if activate_response.status_code == 200:
                print("✅ Workflow activated")
                
                # Wait a moment for webhook registration
                time.sleep(3)
                
                # Test webhook
                print("🧪 Testing webhook...")
                test_response = requests.post(
                    "http://localhost:5678/webhook/api-test",
                    json={"test": "data"},
                    timeout=10
                )
                
                if test_response.status_code == 200:
                    result = test_response.json()
                    print(f"✅ Webhook working! Response: {result}")
                    return True
                else:
                    print(f"❌ Webhook test failed: HTTP {test_response.status_code}")
                    print(f"Response: {test_response.text[:200]}")
                    return False
            else:
                print(f"❌ Failed to activate workflow: HTTP {activate_response.status_code}")
                return False
        else:
            print(f"❌ Failed to create workflow: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = create_simple_webhook()
    exit(0 if success else 1)