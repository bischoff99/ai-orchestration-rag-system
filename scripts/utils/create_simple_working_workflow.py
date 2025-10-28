#!/usr/bin/env python3
"""
Create a simple working RAG workflow that doesn't need vector databases
"""
import requests
import json

def create_simple_workflow():
    """Create a simple workflow that just uses Ollama directly"""
    
    workflow = {
        "name": "Simple RAG Chat",
        "nodes": [
            {
                "id": "webhook_trigger",
                "name": "Webhook Trigger", 
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [100, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "simple-rag",
                    "options": {}
                }
            },
            {
                "id": "ollama_chat",
                "name": "Ollama Chat",
                "type": "@n8n/n8n-nodes-langchain.lmChatOllama",
                "typeVersion": 1,
                "position": [400, 300],
                "parameters": {
                    "model": "llama3.1:8b-instruct-q5_K_M",
                    "options": {}
                },
                "credentials": {
                    "ollamaApi": {
                        "id": "UZBCdVW7KuzX2MwT",
                        "name": "Ollama account"
                    }
                }
            },
            {
                "id": "response_webhook",
                "name": "Response",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [700, 300],
                "parameters": {
                    "options": {}
                }
            }
        ],
        "connections": {
            "Webhook Trigger": {
                "main": [
                    [
                        {
                            "node": "Ollama Chat",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Ollama Chat": {
                "main": [
                    [
                        {
                            "node": "Response",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "settings": {
            "executionOrder": "v1",
            "saveDataErrorExecution": "all",
            "saveDataSuccessExecution": "all",
            "saveManualExecutions": True,
            "saveExecutionProgress": True
        }
    }
    
    return workflow

def test_simple_workflow():
    """Test the simple workflow"""
    print("🧪 Testing simple workflow...")
    
    try:
        response = requests.post(
            "http://localhost:5678/webhook/simple-rag",
            json={"query": "What is artificial intelligence?"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Creating Simple RAG Workflow")
    print("=" * 40)
    
    # Test if we can reach n8n
    try:
        response = requests.get("http://localhost:5678/healthz", timeout=5)
        print(f"✅ n8n is running (status: {response.status_code})")
    except Exception as e:
        print(f"❌ n8n not accessible: {e}")
        exit(1)
    
    # Test the simple workflow
    test_simple_workflow()
