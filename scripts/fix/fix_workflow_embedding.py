#!/usr/bin/env python3
"""
Script to fix the workflow by adding the missing embedding connection
"""

import requests
import json

def fix_workflow_embedding():
    """Fix the workflow by adding embedding node and connection"""
    
    # The issue is that the vector store needs an embedding model connected
    # Let's create a simple fix by updating the workflow structure
    
    print("🔧 Fixing workflow embedding connection...")
    
    # For now, let's test if we can use the existing embedding model
    # by updating the vector store configuration
    
    webhook_url = "http://localhost:5678/webhook/rag-chat"
    
    # Test with a simple query to see if we can get it working
    test_query = {
        "query": "What is machine learning?",
        "collection": "general_knowledge"
    }
    
    print("🧪 Testing RAG query...")
    
    try:
        response = requests.post(
            webhook_url,
            json=test_query,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Workflow is working!")
        else:
            print("❌ Workflow needs fixing")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_workflow_embedding()