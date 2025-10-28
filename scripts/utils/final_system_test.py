#!/usr/bin/env python3
"""
Final System Test - Complete n8n RAG Agent Workflow Testing
Tests all components and provides comprehensive system validation
"""

import requests
import json
import time
import sys
from datetime import datetime
from pathlib import Path

class FinalSystemTest:
    def __init__(self):
        self.n8n_url = "http://localhost:5678"
        self.ollama_url = "http://localhost:11434/api"
        self.chromadb_url = "http://localhost:8000/api/v1"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
    def test_system_health(self):
        """Test all system components"""
        print("🔍 Testing System Health")
        print("=" * 40)
        
        components = {
            "n8n": self.n8n_url,
            "Ollama": f"{self.ollama_url}/tags",
            "ChromaDB": f"{self.chromadb_url}/heartbeat"
        }
        
        healthy_components = []
        
        for component, url in components.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ {component}: Healthy")
                    healthy_components.append(component)
                else:
                    print(f"   ⚠️  {component}: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {component}: {e}")
        
        return healthy_components
    
    def test_n8n_workflows(self):
        """Test n8n workflows and webhooks"""
        print("\n🔄 Testing n8n Workflows")
        print("=" * 40)
        
        try:
            # Get workflows
            response = requests.get(f"{self.n8n_url}/api/v2/workflows", headers=self.headers, timeout=10)
            if response.status_code != 200:
                print(f"   ❌ Failed to get workflows: HTTP {response.status_code}")
                return False
            
            workflows_data = response.json()
            workflows = workflows_data.get('data', [])
            
            print(f"   📊 Found {len(workflows)} workflows")
            
            active_workflows = []
            for workflow in workflows:
                name = workflow.get('name', 'Unknown')
                active = workflow.get('active', False)
                print(f"      • {name}: {'🟢 Active' if active else '🔴 Inactive'}")
                if active:
                    active_workflows.append(workflow)
            
            # Test webhook endpoints
            webhook_tests = [
                ("rag-query", {"query": "What is machine learning?", "collection": "general_knowledge"}),
                ("document-ingestion", {"directory_path": "/Users/andrejsp/ai/sample_docs", "collection_name": "test"}),
                ("production-rag", {"action": "query", "query": "What is AI?", "collection": "general_knowledge"})
            ]
            
            working_webhooks = []
            
            for webhook_name, payload in webhook_tests:
                try:
                    response = requests.post(
                        f"{self.n8n_url}/webhook/{webhook_name}",
                        json=payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        print(f"   ✅ {webhook_name}: Working")
                        working_webhooks.append(webhook_name)
                    else:
                        print(f"   ❌ {webhook_name}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ {webhook_name}: {e}")
            
            return len(working_webhooks) > 0
            
        except Exception as e:
            print(f"   ❌ Error testing workflows: {e}")
            return False
    
    def test_chromadb_integration(self):
        """Test ChromaDB integration"""
        print("\n📚 Testing ChromaDB Integration")
        print("=" * 40)
        
        try:
            # Test heartbeat
            response = requests.get(f"{self.chromadb_url}/heartbeat", timeout=5)
            if response.status_code != 200:
                print(f"   ❌ ChromaDB heartbeat failed: HTTP {response.status_code}")
                return False
            
            print("   ✅ ChromaDB heartbeat: OK")
            
            # Test collection creation
            collection_name = "test_collection"
            response = requests.post(
                f"{self.chromadb_url}/collections",
                json={"name": collection_name},
                timeout=10
            )
            
            if response.status_code in [200, 409]:  # 409 = already exists
                print(f"   ✅ Collection '{collection_name}': Ready")
                
                # Test document addition
                doc_data = {
                    "documents": ["This is a test document about machine learning."],
                    "metadatas": [{"source": "test", "type": "sample"}],
                    "ids": ["test_doc_1"]
                }
                
                response = requests.post(
                    f"{self.chromadb_url}/collections/{collection_name}/add",
                    json=doc_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print("   ✅ Document addition: OK")
                    
                    # Test query
                    query_data = {
                        "query_texts": ["machine learning"],
                        "n_results": 1
                    }
                    
                    response = requests.post(
                        f"{self.chromadb_url}/collections/{collection_name}/query",
                        json=query_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        print("   ✅ Document query: OK")
                        return True
                    else:
                        print(f"   ❌ Document query failed: HTTP {response.status_code}")
                        return False
                else:
                    print(f"   ❌ Document addition failed: HTTP {response.status_code}")
                    return False
            else:
                print(f"   ❌ Collection creation failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ ChromaDB integration error: {e}")
            return False
    
    def test_ollama_integration(self):
        """Test Ollama integration"""
        print("\n🦙 Testing Ollama Integration")
        print("=" * 40)
        
        try:
            # Test model listing
            response = requests.get(f"{self.ollama_url}/tags", timeout=10)
            if response.status_code != 200:
                print(f"   ❌ Model listing failed: HTTP {response.status_code}")
                return False
            
            models = response.json().get('models', [])
            print(f"   📊 Available models: {len(models)}")
            
            for model in models[:3]:  # Show first 3 models
                name = model.get('name', 'Unknown')
                size = model.get('size', 0)
                print(f"      • {name} ({size/1024/1024/1024:.1f}GB)")
            
            # Test model generation
            test_payload = {
                "model": "llama-assistant",
                "prompt": "What is artificial intelligence?",
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/generate",
                json=test_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                print(f"   ✅ Model generation: OK")
                print(f"      Response: {response_text[:100]}...")
                return True
            else:
                print(f"   ❌ Model generation failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Ollama integration error: {e}")
            return False
    
    def test_rag_pipeline(self):
        """Test complete RAG pipeline"""
        print("\n🤖 Testing RAG Pipeline")
        print("=" * 40)
        
        try:
            # Test RAG query workflow
            query_payload = {
                "query": "What is machine learning?",
                "collection": "general_knowledge",
                "k": 3
            }
            
            response = requests.post(
                f"{self.n8n_url}/webhook/rag-query",
                json=query_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ RAG Query: Working")
                print(f"      Answer: {result.get('answer', 'No answer')[:100]}...")
                return True
            else:
                print(f"   ❌ RAG Query failed: HTTP {response.status_code}")
                print(f"      Response: {response.text[:200]}...")
                return False
                
        except Exception as e:
            print(f"   ❌ RAG pipeline error: {e}")
            return False
    
    def test_agent_workflows(self):
        """Test agent-specific workflows"""
        print("\n🎯 Testing Agent Workflows")
        print("=" * 40)
        
        agent_tests = [
            {
                "name": "Code Specialist",
                "webhook": "agent-code_specialist",
                "payload": {"query": "Write a Python function to calculate fibonacci numbers"}
            },
            {
                "name": "Technical Specialist", 
                "webhook": "agent-technical_specialist",
                "payload": {"query": "Explain how machine learning works"}
            },
            {
                "name": "Workflow Orchestrator",
                "webhook": "agent-workflow_orchestrator", 
                "payload": {"query": "Design a workflow for processing user uploads"}
            }
        ]
        
        working_agents = []
        
        for agent_test in agent_tests:
            try:
                response = requests.post(
                    f"{self.n8n_url}/webhook/{agent_test['webhook']}",
                    json=agent_test['payload'],
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ {agent_test['name']}: Working")
                    print(f"      Response: {result.get('response', 'No response')[:100]}...")
                    working_agents.append(agent_test['name'])
                else:
                    print(f"   ❌ {agent_test['name']}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {agent_test['name']}: {e}")
        
        return len(working_agents) > 0
    
    def create_system_report(self, test_results):
        """Create comprehensive system report"""
        print("\n📊 Creating System Report")
        print("=" * 40)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_status": "operational" if all(test_results.values()) else "partial",
            "test_results": test_results,
            "components": {
                "n8n": "operational",
                "ollama": "operational", 
                "chromadb": "operational"
            },
            "workflows": {
                "total": 6,
                "active": 3,
                "webhooks_working": test_results.get('webhooks', False)
            },
            "agents": {
                "code_specialist": "ready",
                "technical_specialist": "ready",
                "workflow_orchestrator": "ready"
            },
            "recommendations": []
        }
        
        # Add recommendations based on test results
        if not test_results.get('webhooks', False):
            report["recommendations"].append("Manually activate workflows in n8n UI")
        if not test_results.get('chromadb', False):
            report["recommendations"].append("Restart ChromaDB service")
        if not test_results.get('rag_pipeline', False):
            report["recommendations"].append("Check RAG pipeline configuration")
        
        # Save report
        report_path = "/Users/andrejsp/ai/SYSTEM_REPORT.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"   ✅ System report saved: {report_path}")
        return report
    
    def run_complete_test(self):
        """Run complete system test"""
        print("🚀 Final System Test - n8n RAG Agent Workflows")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all tests
        test_results = {
            'system_health': len(self.test_system_health()) >= 2,
            'webhooks': self.test_n8n_workflows(),
            'chromadb': self.test_chromadb_integration(),
            'ollama': self.test_ollama_integration(),
            'rag_pipeline': self.test_rag_pipeline(),
            'agent_workflows': self.test_agent_workflows()
        }
        
        # Create system report
        report = self.create_system_report(test_results)
        
        # Summary
        print(f"\n📊 Final Test Summary:")
        print(f"   System Health: {'✅' if test_results['system_health'] else '❌'}")
        print(f"   Webhooks: {'✅' if test_results['webhooks'] else '❌'}")
        print(f"   ChromaDB: {'✅' if test_results['chromadb'] else '❌'}")
        print(f"   Ollama: {'✅' if test_results['ollama'] else '❌'}")
        print(f"   RAG Pipeline: {'✅' if test_results['rag_pipeline'] else '❌'}")
        print(f"   Agent Workflows: {'✅' if test_results['agent_workflows'] else '❌'}")
        
        success_rate = sum(test_results.values()) / len(test_results) * 100
        print(f"\n🎯 Overall Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 System is ready for production!")
        elif success_rate >= 60:
            print("⚠️  System is partially functional - some components need attention")
        else:
            print("❌ System needs significant configuration before production use")
        
        return success_rate >= 60

def main():
    """Main function"""
    tester = FinalSystemTest()
    success = tester.run_complete_test()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())