#!/usr/bin/env python3
"""
n8n API Integration for RAG System
Provides Python functions to interact with n8n workflows and RAG system
"""

import requests
import json
import time
import sys
import os
from typing import Dict, Any, Optional

# Add the scripts directory to path for RAG imports
sys.path.append('/Users/andrejsp/ai/scripts')

class N8nRAGClient:
    def __init__(self, base_url: str = "http://localhost:5678", api_key: str = None):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.session = requests.Session()
        self.rag_api_url = "http://localhost:8000"  # Your RAG API endpoint
        
        # Set API key if provided
        if api_key:
            self.session.headers.update({
                "X-N8N-API-KEY": api_key
            })
    
    def trigger_document_ingestion(self, directory_path: str, collection_name: str = "default_docs") -> Dict[str, Any]:
        """Trigger document ingestion workflow via n8n webhook"""
        webhook_url = f"{self.base_url}/webhook/document-ingestion"
        
        payload = {
            "directory_path": directory_path,
            "collection_name": collection_name
        }
        
        try:
            response = self.session.post(webhook_url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "status": "error"}
    
    def query_rag(self, query: str, collection: str = "default_docs", k: int = 5, model: str = "llama-assistant") -> Dict[str, Any]:
        """Query RAG system via n8n workflow"""
        webhook_url = f"{self.base_url}/webhook/rag-query"
        
        payload = {
            "query": query,
            "collection": collection,
            "k": k,
            "model": model
        }
        
        try:
            response = self.session.post(webhook_url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "status": "error"}
    
    def query_rag_direct(self, query: str, collection: str = "default_docs", k: int = 5) -> Dict[str, Any]:
        """Query RAG system directly (bypassing n8n)"""
        try:
            # Import your existing RAG query function
            from rag_query import query_rag_system
            
            result = query_rag_system(
                query=query,
                collection=collection,
                k=k
            )
            return result
        except ImportError:
            return {"error": "RAG query module not found", "status": "error"}
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def ingest_documents_direct(self, directory_path: str, collection_name: str = "default_docs") -> Dict[str, Any]:
        """Ingest documents directly (bypassing n8n)"""
        try:
            # Import your existing ingestion function
            from ingest_documents import ingest_directory
            
            result = ingest_directory(
                directory_path=directory_path,
                collection_name=collection_name
            )
            return result
        except ImportError:
            return {"error": "Document ingestion module not found", "status": "error"}
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        try:
            response = self.session.get(f"{self.api_url}/executions/{workflow_id}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "status": "error"}
    
    def list_workflows(self) -> Dict[str, Any]:
        """List all workflows"""
        try:
            response = self.session.get(f"{self.api_url}/workflows")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "status": "error"}
    
    def test_rag_system(self) -> Dict[str, Any]:
        """Test the RAG system health"""
        test_queries = [
            "What is machine learning?",
            "How does vector search work?",
            "What are the benefits of RAG?"
        ]
        
        results = []
        for query in test_queries:
            result = self.query_rag_direct(query)
            results.append({
                "query": query,
                "status": "success" if "error" not in result else "error",
                "response": result.get("answer", "No response")[:100] + "..." if len(result.get("answer", "")) > 100 else result.get("answer", "No response")
            })
        
        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_queries": results,
            "overall_status": "healthy" if all(r["status"] == "success" for r in results) else "unhealthy"
        }

def main():
    """Example usage and testing"""
    # Use the provided API key
    API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
    
    client = N8nRAGClient(api_key=API_KEY)
    
    print("🚀 n8n RAG System Integration Test")
    print("=" * 50)
    
    # Test n8n connection
    print("\n🔍 Testing n8n connection...")
    workflows = client.list_workflows()
    if "error" in workflows:
        print(f"❌ n8n connection failed: {workflows['error']}")
        print("   Make sure n8n is running: ./start_n8n.sh")
    else:
        print("✅ Connected to n8n")
        print(f"   Found {len(workflows.get('data', []))} workflows")
    
    # Test RAG system directly
    print("\n🤖 Testing RAG system directly...")
    rag_test = client.test_rag_system()
    print(f"   Overall status: {rag_test['overall_status']}")
    for test in rag_test['test_queries']:
        status_icon = "✅" if test['status'] == 'success' else "❌"
        print(f"   {status_icon} {test['query']}: {test['response']}")
    
    # Test document ingestion via n8n
    print("\n📚 Testing document ingestion via n8n...")
    result = client.trigger_document_ingestion(
        directory_path="/Users/andrejsp/ai/sample_docs",
        collection_name="n8n_test_collection"
    )
    if "error" in result:
        print(f"❌ Ingestion failed: {result['error']}")
    else:
        print("✅ Document ingestion triggered successfully")
        print(f"   Result: {result}")
    
    # Test RAG query via n8n
    print("\n🔍 Testing RAG query via n8n...")
    result = client.query_rag(
        query="What is machine learning?",
        collection="n8n_test_collection"
    )
    if "error" in result:
        print(f"❌ Query failed: {result['error']}")
    else:
        print("✅ RAG query successful")
        print(f"   Answer: {result.get('answer', 'No answer')[:200]}...")
    
    print("\n🎉 Integration test complete!")

if __name__ == "__main__":
    main()