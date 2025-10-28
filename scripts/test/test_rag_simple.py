#!/usr/bin/env python3
"""
Simple RAG Test - Test the current RAG system
"""

import requests
import json

RAG_WEBHOOK_URL = "http://localhost:5678/webhook/rag-chat"

def test_simple_query():
    """Test a simple query to see what the RAG system returns"""
    print("🔍 Testing simple RAG query...")
    
    query = "Hello, can you help me understand what you know?"
    
    try:
        response = requests.post(RAG_WEBHOOK_URL, json={
            "query": query
        }, timeout=30)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON Response: {json.dumps(data, indent=2)}")
            except:
                print("Response is not JSON")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple_query()