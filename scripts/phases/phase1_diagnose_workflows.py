#!/usr/bin/env python3
"""
Phase 1: Diagnose & Repair n8n Workflows
Comprehensive workflow audit and repair using MCP tools
"""

import requests
import json
import time
import sys
from datetime import datetime

class N8nWorkflowDiagnostic:
    def __init__(self):
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
        self.base_url = "http://localhost:5678"
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def audit_workflows(self):
        """Audit current workflows to pinpoint errors and performance bottlenecks"""
        print("🔍 Phase 1.1: Auditing n8n Workflows")
        print("=" * 50)
        
        # Get all workflows
        try:
            response = requests.get(f"{self.base_url}/api/v2/workflows", headers=self.headers, timeout=10)
            if response.status_code == 200:
                workflows_data = response.json()
                workflows = workflows_data.get('data', [])
                print(f"✅ Found {len(workflows)} workflows")
                
                issues_found = []
                
                for workflow in workflows:
                    workflow_id = workflow.get('id')
                    workflow_name = workflow.get('name', 'Unknown')
                    is_active = workflow.get('active', False)
                    
                    print(f"\n📄 Analyzing: {workflow_name}")
                    print(f"   ID: {workflow_id}")
                    print(f"   Active: {is_active}")
                    
                    # Get detailed workflow info
                    detail_response = requests.get(
                        f"{self.base_url}/api/v2/workflows/{workflow_id}",
                        headers=self.headers,
                        timeout=10
                    )
                    
                    if detail_response.status_code == 200:
                        workflow_detail = detail_response.json()
                        nodes = workflow_detail.get('nodes', [])
                        connections = workflow_detail.get('connections', {})
                        
                        print(f"   Nodes: {len(nodes)}")
                        print(f"   Connections: {len(connections)}")
                        
                        # Analyze nodes for issues
                        node_issues = self.analyze_nodes(nodes)
                        if node_issues:
                            issues_found.extend([(workflow_name, issue) for issue in node_issues])
                        
                        # Test webhook if it's a webhook workflow
                        webhook_issues = self.test_webhook_endpoints(workflow_detail)
                        if webhook_issues:
                            issues_found.extend([(workflow_name, issue) for issue in webhook_issues])
                    else:
                        print(f"   ❌ Failed to get details: HTTP {detail_response.status_code}")
                        issues_found.append((workflow_name, f"Failed to get workflow details: HTTP {detail_response.status_code}"))
                
                return issues_found
            else:
                print(f"❌ Failed to get workflows: HTTP {response.status_code}")
                return [("API Error", f"Failed to get workflows: HTTP {response.status_code}")]
        except Exception as e:
            print(f"❌ Error auditing workflows: {e}")
            return [("Connection Error", str(e))]
    
    def analyze_nodes(self, nodes):
        """Analyze workflow nodes for common issues"""
        issues = []
        
        for node in nodes:
            node_type = node.get('type', '')
            node_name = node.get('name', 'Unknown')
            parameters = node.get('parameters', {})
            
            # Check for JavaScript simulation nodes
            if node_type == 'n8n-nodes-base.code':
                js_code = parameters.get('jsCode', '')
                if 'simulate' in js_code.lower() or 'mock' in js_code.lower():
                    issues.append(f"Node '{node_name}' uses JavaScript simulation instead of real API calls")
            
            # Check for webhook nodes
            if node_type == 'n8n-nodes-base.webhook':
                path = parameters.get('path', '')
                if not path:
                    issues.append(f"Webhook node '{node_name}' missing path configuration")
            
            # Check for HTTP request nodes
            if node_type == 'n8n-nodes-base.httpRequest':
                url = parameters.get('url', '')
                if not url or 'localhost' not in url:
                    issues.append(f"HTTP Request node '{node_name}' may not be configured for local services")
        
        return issues
    
    def test_webhook_endpoints(self, workflow_detail):
        """Test webhook endpoints for functionality"""
        issues = []
        nodes = workflow_detail.get('nodes', [])
        
        for node in nodes:
            if node.get('type') == 'n8n-nodes-base.webhook':
                path = node.get('parameters', {}).get('path', '')
                if path:
                    webhook_url = f"{self.base_url}/webhook/{path}"
                    
                    try:
                        response = requests.post(
                            webhook_url,
                            json={"test": "data"},
                            timeout=5
                        )
                        
                        if response.status_code == 404:
                            issues.append(f"Webhook '/webhook/{path}' not registered (404 error)")
                        elif response.status_code != 200:
                            issues.append(f"Webhook '/webhook/{path}' returned HTTP {response.status_code}")
                    except Exception as e:
                        issues.append(f"Webhook '/webhook/{path}' connection error: {e}")
        
        return issues
    
    def fix_webhook_activation(self):
        """Fix webhook activation issues"""
        print("\n🔧 Phase 1.2: Fixing Webhook Activation")
        print("=" * 50)
        
        try:
            # Get all workflows
            response = requests.get(f"{self.base_url}/api/v2/workflows", headers=self.headers, timeout=10)
            if response.status_code != 200:
                print(f"❌ Failed to get workflows: HTTP {response.status_code}")
                return False
            
            workflows_data = response.json()
            workflows = workflows_data.get('data', [])
            
            fixed_count = 0
            
            for workflow in workflows:
                workflow_id = workflow.get('id')
                workflow_name = workflow.get('name', 'Unknown')
                is_active = workflow.get('active', False)
                
                print(f"\n📄 Processing: {workflow_name}")
                
                if is_active:
                    print(f"   ✅ Already active")
                    continue
                
                # Try to activate workflow
                try:
                    activate_response = requests.patch(
                        f"{self.base_url}/api/v2/workflows/{workflow_id}",
                        headers=self.headers,
                        json={"active": True},
                        timeout=10
                    )
                    
                    if activate_response.status_code == 200:
                        print(f"   ✅ Activated successfully")
                        fixed_count += 1
                    else:
                        print(f"   ❌ Failed to activate: HTTP {activate_response.status_code}")
                        print(f"   Response: {activate_response.text[:200]}")
                
                except Exception as e:
                    print(f"   ❌ Error activating: {e}")
            
            print(f"\n📊 Activation Summary: {fixed_count} workflows activated")
            return fixed_count > 0
            
        except Exception as e:
            print(f"❌ Error fixing webhook activation: {e}")
            return False
    
    def create_enhanced_workflows(self):
        """Create enhanced workflows with real API integrations"""
        print("\n🚀 Phase 1.3: Creating Enhanced Workflows")
        print("=" * 50)
        
        # Enhanced RAG Query Workflow
        rag_query_workflow = {
            "name": "Enhanced RAG Query Processing Pipeline",
            "nodes": [
                {
                    "id": "webhook-trigger",
                    "name": "RAG Query Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 2,
                    "position": [240, 300],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "rag-query-enhanced",
                        "responseMode": "responseNode"
                    }
                },
                {
                    "id": "validate-input",
                    "name": "Validate Input",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 2,
                    "position": [460, 300],
                    "parameters": {
                        "jsCode": "// Validate and process input\nconst body = $json.body || $json;\nconst query = body.query;\nconst collection = body.collection || 'general_knowledge';\nconst k = body.k || 5;\n\nif (!query || query.trim().length === 0) {\n  return [{\n    json: {\n      error: 'Query is required and cannot be empty',\n      status: 'error',\n      code: 'INVALID_INPUT'\n    }\n  }];\n}\n\nreturn [{\n  json: {\n    query: query.trim(),\n    collection: collection,\n    k: Math.min(k, 10), // Limit to max 10 results\n    timestamp: new Date().toISOString()\n  }\n}];"
                    }
                },
                {
                    "id": "search-chromadb",
                    "name": "Search ChromaDB",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 4.2,
                    "position": [680, 300],
                    "parameters": {
                        "method": "POST",
                        "url": "http://localhost:8000/api/v2/collections/{{ $json.collection }}/query",
                        "headers": {
                            "Content-Type": "application/json"
                        },
                        "body": {
                            "query_texts": ["{{ $json.query }}"],
                            "n_results": "{{ $json.k }}"
                        },
                        "options": {
                            "timeout": 10000,
                            "retry": {
                                "enabled": True,
                                "maxRetries": 3,
                                "retryDelay": 1000
                            }
                        }
                    }
                },
                {
                    "id": "generate-response",
                    "name": "Generate with Ollama",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 4.2,
                    "position": [900, 300],
                    "parameters": {
                        "method": "POST",
                        "url": "http://localhost:11434/api/generate",
                        "headers": {
                            "Content-Type": "application/json"
                        },
                        "body": {
                            "model": "llama-assistant",
                            "prompt": "Based on the following context, answer the question:\n\nContext: {{ $json.documents }}\n\nQuestion: {{ $('Validate Input').item.json.query }}\n\nAnswer:",
                            "stream": False,
                            "options": {
                                "temperature": 0.1,
                                "top_p": 0.9
                            }
                        },
                        "options": {
                            "timeout": 30000,
                            "retry": {
                                "enabled": True,
                                "maxRetries": 2,
                                "retryDelay": 2000
                            }
                        }
                    }
                },
                {
                    "id": "respond",
                    "name": "Respond to Webhook",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [1120, 300],
                    "parameters": {
                        "respondWith": "json",
                        "responseBody": "={{ {\n  \"answer\": $json.response,\n  \"sources\": $('Search ChromaDB').item.json.documents,\n  \"query\": $('Validate Input').item.json.query,\n  \"timestamp\": new Date().toISOString(),\n  \"status\": \"success\"\n} }}"
                    }
                }
            ],
            "connections": {
                "RAG Query Webhook": {
                    "main": [[{"node": "Validate Input", "type": "main", "index": 0}]]
                },
                "Validate Input": {
                    "main": [[{"node": "Search ChromaDB", "type": "main", "index": 0}]]
                },
                "Search ChromaDB": {
                    "main": [[{"node": "Generate with Ollama", "type": "main", "index": 0}]]
                },
                "Generate with Ollama": {
                    "main": [[{"node": "Respond to Webhook", "type": "main", "index": 0}]]
                }
            },
            "settings": {
                "executionOrder": "v1"
            }
        }
        
        try:
            # Create the enhanced workflow
            response = requests.post(
                f"{self.base_url}/api/v2/workflows",
                headers=self.headers,
                json=rag_query_workflow,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                workflow_id = result.get('id')
                print(f"✅ Created Enhanced RAG Query Workflow (ID: {workflow_id})")
                
                # Activate the workflow
                activate_response = requests.patch(
                    f"{self.base_url}/api/v2/workflows/{workflow_id}",
                    headers=self.headers,
                    json={"active": True},
                    timeout=10
                )
                
                if activate_response.status_code == 200:
                    print(f"✅ Activated Enhanced RAG Query Workflow")
                    return True
                else:
                    print(f"⚠️  Created but failed to activate: HTTP {activate_response.status_code}")
                    return True
            else:
                print(f"❌ Failed to create workflow: HTTP {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating enhanced workflow: {e}")
            return False
    
    def test_workflows(self):
        """Test the enhanced workflows"""
        print("\n🧪 Phase 1.4: Testing Enhanced Workflows")
        print("=" * 50)
        
        # Test the enhanced RAG query workflow
        test_url = f"{self.base_url}/webhook/rag-query-enhanced"
        test_payload = {
            "query": "What is machine learning?",
            "collection": "general_knowledge",
            "k": 3
        }
        
        try:
            print("🧪 Testing Enhanced RAG Query Workflow...")
            response = requests.post(
                test_url,
                json=test_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Test successful!")
                print(f"   Answer: {result.get('answer', 'No answer')[:100]}...")
                print(f"   Sources: {len(result.get('sources', []))} documents")
                return True
            else:
                print(f"❌ Test failed: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Test error: {e}")
            return False
    
    def run_diagnostic(self):
        """Run complete diagnostic process"""
        print("🚀 Phase 1: Diagnose & Repair n8n Workflows")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Audit workflows
        issues = self.audit_workflows()
        
        if issues:
            print(f"\n⚠️  Found {len(issues)} issues:")
            for workflow_name, issue in issues:
                print(f"   • {workflow_name}: {issue}")
        else:
            print(f"\n✅ No critical issues found in workflow audit")
        
        # Step 2: Fix webhook activation
        activation_success = self.fix_webhook_activation()
        
        # Step 3: Create enhanced workflows
        workflow_success = self.create_enhanced_workflows()
        
        # Step 4: Test workflows
        test_success = self.test_workflows()
        
        # Summary
        print(f"\n📊 Phase 1 Summary:")
        print(f"   Issues found: {len(issues)}")
        print(f"   Webhook activation: {'✅' if activation_success else '❌'}")
        print(f"   Enhanced workflows: {'✅' if workflow_success else '❌'}")
        print(f"   Testing: {'✅' if test_success else '❌'}")
        
        return {
            'issues_found': len(issues),
            'activation_success': activation_success,
            'workflow_success': workflow_success,
            'test_success': test_success
        }

def main():
    """Main function"""
    diagnostic = N8nWorkflowDiagnostic()
    results = diagnostic.run_diagnostic()
    
    if all([results['activation_success'], results['workflow_success'], results['test_success']]):
        print(f"\n🎉 Phase 1 completed successfully!")
        return 0
    else:
        print(f"\n⚠️  Phase 1 completed with some issues")
        return 1

if __name__ == "__main__":
    exit(main())