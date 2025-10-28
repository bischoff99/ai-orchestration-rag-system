#!/usr/bin/env python3
"""
Create a working RAG workflow with document ingestion and retrieval
"""

import requests
import json

# Create a complete RAG workflow that can both ingest and retrieve documents
workflow_data = {
    "name": "Complete RAG System - Working",
    "nodes": [
        {
            "id": "webhook_trigger",
            "name": "RAG Query Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [100, 300],
            "parameters": {
                "httpMethod": "POST",
                "path": "rag-complete",
                "options": {}
            }
        },
        {
            "id": "embeddings_model",
            "name": "Ollama Embeddings",
            "type": "@n8n/n8n-nodes-langchain.embeddingsOllama",
            "typeVersion": 1,
            "position": [300, 200],
            "parameters": {
                "model": "mxbai-embed-large:latest"
            },
            "credentials": {
                "ollamaApi": {
                    "id": "UZBCdVW7KuzX2MwT",
                    "name": "Ollama account"
                }
            }
        },
        {
            "id": "vector_store",
            "name": "Vector Store",
            "type": "@n8n/n8n-nodes-langchain.vectorStoreInMemory",
            "typeVersion": 1,
            "position": [500, 300],
            "parameters": {
                "mode": "retrieve",
                "memoryKey": "rag_documents_collection"
            }
        },
        {
            "id": "vector_retriever",
            "name": "Vector Store Retriever",
            "type": "@n8n/n8n-nodes-langchain.retrieverVectorStore",
            "typeVersion": 1,
            "position": [700, 200],
            "parameters": {
                "topK": 4
            }
        },
        {
            "id": "chat_model",
            "name": "Ollama Chat Model",
            "type": "@n8n/n8n-nodes-langchain.lmChatOllama",
            "typeVersion": 1,
            "position": [300, 400],
            "parameters": {
                "model": "llama3.1:8b-instruct-q5_K_M"
            },
            "credentials": {
                "ollamaApi": {
                    "id": "UZBCdVW7KuzX2MwT",
                    "name": "Ollama account"
                }
            }
        },
        {
            "id": "qa_chain",
            "name": "Question and Answer Chain",
            "type": "@n8n/n8n-nodes-langchain.chainRetrievalQa",
            "typeVersion": 1,
            "position": [900, 300],
            "parameters": {
                "options": {}
            }
        },
        {
            "id": "response",
            "name": "Response Webhook",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1,
            "position": [1100, 300],
            "parameters": {
                "options": {}
            }
        }
    ],
    "connections": {
        "RAG Query Webhook": {
            "main": [
                [
                    {
                        "node": "Question and Answer Chain",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Ollama Embeddings": {
            "ai_embedding": [
                [
                    {
                        "node": "Vector Store",
                        "type": "ai_embedding",
                        "index": 0
                    }
                ]
            ]
        },
        "Vector Store": {
            "ai_vectorStore": [
                [
                    {
                        "node": "Vector Store Retriever",
                        "type": "ai_vectorStore",
                        "index": 0
                    }
                ]
            ]
        },
        "Vector Store Retriever": {
            "ai_retriever": [
                [
                    {
                        "node": "Question and Answer Chain",
                        "type": "ai_retriever",
                        "index": 0
                    }
                ]
            ]
        },
        "Ollama Chat Model": {
            "ai_languageModel": [
                [
                    {
                        "node": "Question and Answer Chain",
                        "type": "ai_languageModel",
                        "index": 0
                    }
                ]
            ]
        },
        "Question and Answer Chain": {
            "main": [
                [
                    {
                        "node": "Response Webhook",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    },
    "settings": {
        "active": True,
        "saveExecutionProgress": True,
        "saveManualExecutions": True,
        "saveDataErrorExecution": "all",
        "saveDataSuccessExecution": "all",
        "executionOrder": "v1"
    }
}

def create_workflow():
    """Create the RAG workflow"""
    print("🚀 Creating Complete RAG Workflow...")
    
    try:
        response = requests.post("http://localhost:5678/api/v2/workflows", 
                               json=workflow_data,
                               headers={"Content-Type": "application/json"})
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Workflow created successfully!")
            print(f"   ID: {result['id']}")
            print(f"   Name: {result['name']}")
            print(f"   Webhook: http://localhost:5678/webhook/rag-complete")
            return result['id']
        else:
            print(f"❌ Failed to create workflow: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating workflow: {e}")
        return None

def test_workflow(workflow_id):
    """Test the created workflow"""
    if not workflow_id:
        return
        
    print(f"\n🧪 Testing workflow {workflow_id}...")
    
    # Wait a moment for the workflow to be ready
    import time
    time.sleep(2)
    
    # Test query
    test_query = "Hello, can you help me understand what you know?"
    
    try:
        response = requests.post("http://localhost:5678/webhook/rag-complete", 
                               json={"query": test_query},
                               timeout=30)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error testing workflow: {e}")

if __name__ == "__main__":
    workflow_id = create_workflow()
    test_workflow(workflow_id)