#!/usr/bin/env python3
"""
Deploy Final n8n Workflows with Required Settings
Creates workflows with all required fields for n8n API
"""

import json
import requests
import sys

def create_rag_query_workflow():
    """Create RAG Query workflow with all required fields"""
    return {
        "name": "RAG Query Processing Pipeline",
        "nodes": [
            {
                "id": "webhook-trigger",
                "name": "RAG Query Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "rag-query",
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
                    "jsCode": "// Process RAG query\nconst body = $json.body || $json;\nconst query = body.query;\nconst collection = body.collection || 'general_knowledge';\nconst k = body.k || 5;\n\nif (!query) {\n  return [{\n    json: {\n      error: 'Query is required',\n      status: 'error'\n    }\n  }];\n}\n\nreturn [{\n  json: {\n    query: query,\n    collection: collection,\n    k: k,\n    timestamp: new Date().toISOString()\n  }\n}];"
                }
            },
            {
                "id": "respond",
                "name": "Respond to Webhook",
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
            "RAG Query Webhook": {
                "main": [[{"node": "Process Query", "type": "main", "index": 0}]]
            },
            "Process Query": {
                "main": [[{"node": "Respond to Webhook", "type": "main", "index": 0}]]
            }
        },
        "settings": {
            "executionOrder": "v1"
        }
    }

def create_document_ingestion_workflow():
    """Create Document Ingestion workflow with all required fields"""
    return {
        "name": "RAG Document Ingestion Pipeline",
        "nodes": [
            {
                "id": "webhook-trigger",
                "name": "Document Ingestion Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "document-ingestion",
                    "responseMode": "responseNode"
                }
            },
            {
                "id": "process-ingestion",
                "name": "Process Ingestion",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [460, 300],
                "parameters": {
                    "jsCode": "// Process document ingestion\nconst body = $json.body || $json;\nconst directory_path = body.directory_path;\nconst collection_name = body.collection_name || 'default_docs';\n\nif (!directory_path) {\n  return [{\n    json: {\n      error: 'Directory path is required',\n      status: 'error'\n    }\n  }];\n}\n\nreturn [{\n  json: {\n    directory_path: directory_path,\n    collection_name: collection_name,\n    status: 'processing',\n    timestamp: new Date().toISOString()\n  }\n}];"
                }
            },
            {
                "id": "respond",
                "name": "Respond to Webhook",
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
            "Document Ingestion Webhook": {
                "main": [[{"node": "Process Ingestion", "type": "main", "index": 0}]]
            },
            "Process Ingestion": {
                "main": [[{"node": "Respond to Webhook", "type": "main", "index": 0}]]
            }
        },
        "settings": {
            "executionOrder": "v1"
        }
    }

def create_production_workflow():
    """Create Production RAG workflow with all required fields"""
    return {
        "name": "Production RAG Workflow",
        "nodes": [
            {
                "id": "webhook-trigger",
                "name": "Production RAG Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "production-rag",
                    "responseMode": "responseNode"
                }
            },
            {
                "id": "process-request",
                "name": "Process Request",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [460, 300],
                "parameters": {
                    "jsCode": "// Process RAG request\nconst body = $json.body || $json;\nconst action = body.action || 'query';\nconst query = body.query;\nconst collection = body.collection || 'general_knowledge';\nconst directory_path = body.directory_path;\n\nif (action === 'query' && !query) {\n  return [{\n    json: {\n      error: 'Query is required for query action',\n      status: 'error'\n    }\n  }];\n}\n\nif (action === 'ingest' && !directory_path) {\n  return [{\n    json: {\n      error: 'Directory path is required for ingest action',\n      status: 'error'\n    }\n  }];\n}\n\nreturn [{\n  json: {\n    action: action,\n    query: query,\n    collection: collection,\n    directory_path: directory_path,\n    status: 'processed',\n    timestamp: new Date().toISOString()\n  }\n}];"
                }
            },
            {
                "id": "respond",
                "name": "Respond to Webhook",
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
            "Production RAG Webhook": {
                "main": [[{"node": "Process Request", "type": "main", "index": 0}]]
            },
            "Process Request": {
                "main": [[{"node": "Respond to Webhook", "type": "main", "index": 0}]]
            }
        },
        "settings": {
            "executionOrder": "v1"
        }
    }

def deploy_workflow(workflow_data, api_key):
    """Deploy a single workflow"""
    headers = {
        'X-N8N-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            'http://localhost:5678/api/v2/workflows',
            headers=headers,
            json=workflow_data,
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            return True, result.get('id', 'unknown')
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, str(e)

def main():
    """Main deployment function"""
    print("🚀 Deploying Final n8n Workflows")
    print("=" * 40)
    
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
    
    # Create workflow definitions
    workflows = [
        create_rag_query_workflow(),
        create_document_ingestion_workflow(),
        create_production_workflow()
    ]
    
    deployed = []
    failed = []
    
    for workflow in workflows:
        print(f"\n📄 Deploying: {workflow['name']}")
        
        success, result = deploy_workflow(workflow, api_key)
        
        if success:
            print(f"✅ Created: {workflow['name']} (ID: {result})")
            deployed.append(workflow['name'])
        else:
            print(f"❌ Failed: {workflow['name']} - {result}")
            failed.append(workflow['name'])
    
    print(f"\n📊 Deployment Summary:")
    print(f"   ✅ Successfully deployed: {len(deployed)}")
    print(f"   ❌ Failed: {len(failed)}")
    
    if deployed:
        print(f"\n🎉 Deployed workflows:")
        for workflow in deployed:
            print(f"   • {workflow}")
        
        print(f"\n📋 Next steps:")
        print(f"   1. Open http://localhost:5678 in your browser")
        print(f"   2. Activate workflows in n8n UI")
        print(f"   3. Test with: python3 verify_workflows.py")
    
    if failed:
        print(f"\n❌ Failed workflows:")
        for workflow in failed:
            print(f"   • {workflow}")
    
    return 0 if len(failed) == 0 else 1

if __name__ == "__main__":
    exit(main())