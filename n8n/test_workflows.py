#!/usr/bin/env python3
"""
n8n Workflow Testing Script
Tests all n8n workflows for the RAG system
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class N8nWorkflowTester:
    def __init__(self, base_url: str = "http://localhost:5678"):
        self.base_url = base_url
        self.webhook_base = f"{base_url}/webhook"
        self.api_url = f"{base_url}/api/v1"
        self.session = requests.Session()
    
    def test_webhook_endpoint(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Test a webhook endpoint"""
        url = f"{self.webhook_base}/{endpoint}"
        
        try:
            response = self.session.post(url, json=payload, timeout=30)
            return {
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                "error": None
            }
        except requests.RequestException as e:
            return {
                "status_code": 0,
                "success": False,
                "response": None,
                "error": str(e)
            }
    
    def test_document_ingestion_workflow(self) -> Dict[str, Any]:
        """Test document ingestion workflow"""
        print("📚 Testing Document Ingestion Workflow...")
        
        payload = {
            "directory_path": "/Users/andrejsp/ai/sample_docs",
            "collection_name": "test_ingestion"
        }
        
        result = self.test_webhook_endpoint("document-ingestion", payload)
        
        if result["success"]:
            print("✅ Document ingestion workflow test passed")
        else:
            print(f"❌ Document ingestion workflow test failed: {result['error']}")
        
        return result
    
    def test_rag_query_workflow(self) -> Dict[str, Any]:
        """Test RAG query workflow"""
        print("🤖 Testing RAG Query Workflow...")
        
        payload = {
            "query": "What is machine learning?",
            "collection": "test_ingestion",
            "k": 3,
            "model": "llama-assistant"
        }
        
        result = self.test_webhook_endpoint("rag-query", payload)
        
        if result["success"]:
            print("✅ RAG query workflow test passed")
        else:
            print(f"❌ RAG query workflow test failed: {result['error']}")
        
        return result
    
    def test_n8n_connection(self) -> bool:
        """Test n8n connection"""
        print("🔍 Testing n8n connection...")
        
        try:
            response = self.session.get(f"{self.api_url}/workflows", timeout=10)
            if response.status_code == 200:
                print("✅ n8n connection successful")
                return True
            else:
                print(f"❌ n8n connection failed: HTTP {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"❌ n8n connection failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all workflow tests"""
        print("🚀 Starting n8n Workflow Tests")
        print("=" * 50)
        
        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "n8n_connection": False,
            "document_ingestion": None,
            "rag_query": None,
            "overall_success": False
        }
        
        # Test n8n connection
        results["n8n_connection"] = self.test_n8n_connection()
        
        if not results["n8n_connection"]:
            print("\n❌ Cannot proceed with workflow tests - n8n not accessible")
            return results
        
        print("\n" + "=" * 50)
        
        # Test document ingestion
        results["document_ingestion"] = self.test_document_ingestion_workflow()
        
        # Test RAG query
        results["rag_query"] = self.test_rag_query_workflow()
        
        # Determine overall success
        results["overall_success"] = (
            results["n8n_connection"] and
            results["document_ingestion"]["success"] and
            results["rag_query"]["success"]
        )
        
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        print(f"n8n Connection: {'✅' if results['n8n_connection'] else '❌'}")
        print(f"Document Ingestion: {'✅' if results['document_ingestion']['success'] else '❌'}")
        print(f"RAG Query: {'✅' if results['rag_query']['success'] else '❌'}")
        print(f"Overall Success: {'✅' if results['overall_success'] else '❌'}")
        
        return results

def main():
    """Run the workflow tests"""
    tester = N8nWorkflowTester()
    results = tester.run_all_tests()
    
    # Save results to file
    results_file = "/Users/andrejsp/ai/n8n/test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Test results saved to: {results_file}")
    
    if results["overall_success"]:
        print("\n🎉 All tests passed! n8n workflows are working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()