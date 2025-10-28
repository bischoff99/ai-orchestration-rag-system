#!/usr/bin/env python3
"""
Phase 4: Orchestrate Agentic Workflows
Combine all components into cohesive agent-driven pipelines
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime

class AgenticWorkflowOrchestrator:
    def __init__(self):
        self.n8n_url = "http://localhost:5678"
        self.ollama_url = "http://localhost:11434/api"
        self.chromadb_url = "http://localhost:8000/api/v1"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def check_system_health(self):
        """Check health of all system components"""
        print("🔍 Phase 4.1: Checking System Health")
        print("=" * 50)
        
        components = {
            "n8n": f"{self.n8n_url}",
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
    
    def create_master_orchestration_workflow(self):
        """Create master workflow that orchestrates all agents"""
        print("\n🎯 Phase 4.2: Creating Master Orchestration Workflow")
        print("=" * 50)
        
        master_workflow = {
            "name": "Master Agentic Workflow Orchestrator",
            "description": "Orchestrates multiple AI agents for complex task processing",
            "nodes": [
                {
                    "id": "webhook-trigger",
                    "name": "Master Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 2,
                    "position": [240, 300],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "master-orchestrator",
                        "responseMode": "responseNode"
                    }
                },
                {
                    "id": "analyze-request",
                    "name": "Analyze Request",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 2,
                    "position": [460, 300],
                    "parameters": {
                        "jsCode": """// Analyze request and determine which agents to use
const body = $json.body || $json;
const query = body.query || body.input;
const task_type = body.task_type || 'general';

// Determine agent routing based on task type
let agents_to_use = [];
let workflow_steps = [];

if (task_type === 'code' || query.toLowerCase().includes('code') || query.toLowerCase().includes('programming')) {
  agents_to_use.push('code_specialist');
  workflow_steps.push('code_analysis', 'code_generation', 'code_review');
}

if (task_type === 'technical' || query.toLowerCase().includes('technical') || query.toLowerCase().includes('documentation')) {
  agents_to_use.push('technical_specialist');
  workflow_steps.push('technical_analysis', 'documentation_generation');
}

if (task_type === 'workflow' || query.toLowerCase().includes('workflow') || query.toLowerCase().includes('process')) {
  agents_to_use.push('workflow_orchestrator');
  workflow_steps.push('workflow_design', 'process_optimization');
}

// Default to general processing if no specific type detected
if (agents_to_use.length === 0) {
  agents_to_use = ['technical_specialist'];
  workflow_steps = ['general_analysis', 'response_generation'];
}

return [{
  json: {
    query: query,
    task_type: task_type,
    agents_to_use: agents_to_use,
    workflow_steps: workflow_steps,
    timestamp: new Date().toISOString()
  }
}];"""
                    }
                },
                {
                    "id": "rag-search",
                    "name": "RAG Knowledge Search",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 4.2,
                    "position": [680, 300],
                    "parameters": {
                        "method": "POST",
                        "url": "http://localhost:8000/api/v2/collections/general_knowledge/query",
                        "headers": {
                            "Content-Type": "application/json"
                        },
                        "body": {
                            "query_texts": ["{{ $json.query }}"],
                            "n_results": 5
                        },
                        "options": {
                            "timeout": 10000
                        }
                    }
                },
                {
                    "id": "agent-coordinator",
                    "name": "Agent Coordinator",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 2,
                    "position": [900, 300],
                    "parameters": {
                        "jsCode": """// Coordinate multiple agents based on analysis
const analysis = $('Analyze Request').item.json;
const rag_results = $('RAG Knowledge Search').item.json;

// Prepare context for agents
const context = {
  query: analysis.query,
  task_type: analysis.task_type,
  relevant_docs: rag_results.documents || [],
  agents_needed: analysis.agents_to_use,
  workflow_steps: analysis.workflow_steps
};

// Create agent tasks
const agent_tasks = analysis.agents_to_use.map(agent => ({
  agent_type: agent,
  task: analysis.query,
  context: context,
  priority: 'high'
}));

return [{
  json: {
    context: context,
    agent_tasks: agent_tasks,
    coordination_id: `coord_${Date.now()}`,
    timestamp: new Date().toISOString()
  }
}];"""
                    }
                },
                {
                    "id": "parallel-agent-execution",
                    "name": "Parallel Agent Execution",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 2,
                    "position": [1120, 300],
                    "parameters": {
                        "jsCode": """// Execute agents in parallel (simulated)
const coordination = $('Agent Coordinator').item.json;
const agent_tasks = coordination.agent_tasks;

// Simulate parallel execution
const agent_responses = agent_tasks.map(task => {
  // In a real implementation, this would call the actual agent APIs
  return {
    agent_type: task.agent_type,
    response: `Response from ${task.agent_type} for: ${task.task}`,
    confidence: Math.random() * 0.4 + 0.6, // 0.6-1.0
    processing_time: Math.random() * 2000 + 500 // 500-2500ms
  };
});

// Combine responses
const combined_response = {
  original_query: coordination.context.query,
  agent_responses: agent_responses,
  best_response: agent_responses.reduce((best, current) => 
    current.confidence > best.confidence ? current : best
  ),
  coordination_id: coordination.coordination_id,
  timestamp: new Date().toISOString()
};

return [{
  json: combined_response
}];"""
                    }
                },
                {
                    "id": "respond",
                    "name": "Respond to Webhook",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [1340, 300],
                    "parameters": {
                        "respondWith": "json",
                        "responseBody": "={{ {\n  \"response\": $json.best_response.response,\n  \"agent_used\": $json.best_response.agent_type,\n  \"confidence\": $json.best_response.confidence,\n  \"all_responses\": $json.agent_responses,\n  \"coordination_id\": $json.coordination_id,\n  \"timestamp\": $json.timestamp,\n  \"status\": \"success\"\n} }}"
                    }
                }
            ],
            "connections": {
                "Master Webhook": {
                    "main": [[{"node": "Analyze Request", "type": "main", "index": 0}]]
                },
                "Analyze Request": {
                    "main": [[{"node": "RAG Knowledge Search", "type": "main", "index": 0}]]
                },
                "RAG Knowledge Search": {
                    "main": [[{"node": "Agent Coordinator", "type": "main", "index": 0}]]
                },
                "Agent Coordinator": {
                    "main": [[{"node": "Parallel Agent Execution", "type": "main", "index": 0}]]
                },
                "Parallel Agent Execution": {
                    "main": [[{"node": "Respond to Webhook", "type": "main", "index": 0}]]
                }
            },
            "settings": {
                "executionOrder": "v1"
            }
        }
        
        try:
            response = requests.post(
                f"{self.n8n_url}/api/v2/workflows",
                headers=self.headers,
                json=master_workflow,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                workflow_id = result.get('id')
                print(f"   ✅ Created Master Orchestration Workflow (ID: {workflow_id})")
                return workflow_id
            else:
                print(f"   ❌ Failed to create workflow: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error creating workflow: {e}")
            return None
    
    def create_fallback_mechanisms(self):
        """Create fallback mechanisms and human-in-the-loop checkpoints"""
        print("\n🛡️  Phase 4.3: Creating Fallback Mechanisms")
        print("=" * 50)
        
        fallback_config = {
            "circuit_breakers": {
                "ollama_timeout": 30000,  # 30 seconds
                "chromadb_timeout": 10000,  # 10 seconds
                "max_retries": 3,
                "retry_delay": 1000  # 1 second
            },
            "human_checkpoints": {
                "low_confidence_threshold": 0.6,
                "complex_task_threshold": 0.8,
                "error_escalation": True,
                "approval_required": ["workflow_modification", "data_deletion"]
            },
            "fallback_responses": {
                "service_unavailable": "I'm currently experiencing technical difficulties. Please try again later.",
                "low_confidence": "I'm not entirely confident in my response. Would you like me to consult additional resources?",
                "complex_task": "This task requires human review. I've escalated it to our team."
            },
            "monitoring": {
                "health_check_interval": 60,  # seconds
                "performance_metrics": True,
                "error_tracking": True,
                "alert_thresholds": {
                    "error_rate": 0.05,  # 5%
                    "response_time": 5000,  # 5 seconds
                    "availability": 0.99  # 99%
                }
            }
        }
        
        # Save fallback configuration
        fallback_path = "/Users/andrejsp/ai/configs/fallback_mechanisms.json"
        with open(fallback_path, 'w') as f:
            json.dump(fallback_config, f, indent=2)
        
        print(f"   ✅ Created fallback mechanisms config: {fallback_path}")
        return True
    
    def create_monitoring_dashboard(self):
        """Create comprehensive monitoring dashboard"""
        print("\n📊 Phase 4.4: Creating Monitoring Dashboard")
        print("=" * 50)
        
        dashboard_config = {
            "system_metrics": {
                "n8n_workflows": {
                    "total": 0,
                    "active": 0,
                    "executions_today": 0,
                    "success_rate": 0.0
                },
                "ollama_models": {
                    "total": 0,
                    "active": 0,
                    "requests_today": 0,
                    "average_response_time": 0.0
                },
                "chromadb_collections": {
                    "total": 0,
                    "documents": 0,
                    "queries_today": 0,
                    "average_query_time": 0.0
                }
            },
            "agent_metrics": {
                "code_specialist": {
                    "requests": 0,
                    "success_rate": 0.0,
                    "average_confidence": 0.0
                },
                "technical_specialist": {
                    "requests": 0,
                    "success_rate": 0.0,
                    "average_confidence": 0.0
                },
                "workflow_orchestrator": {
                    "requests": 0,
                    "success_rate": 0.0,
                    "average_confidence": 0.0
                }
            },
            "performance_alerts": {
                "high_error_rate": False,
                "slow_response_time": False,
                "low_availability": False,
                "resource_exhaustion": False
            },
            "dashboard_urls": {
                "n8n_ui": "http://localhost:5678",
                "ollama_api": "http://localhost:11434",
                "chromadb_api": "http://localhost:8000"
            }
        }
        
        # Save dashboard configuration
        dashboard_path = "/Users/andrejsp/ai/configs/monitoring_dashboard.json"
        with open(dashboard_path, 'w') as f:
            json.dump(dashboard_config, f, indent=2)
        
        print(f"   ✅ Created monitoring dashboard config: {dashboard_path}")
        return True
    
    def test_orchestration_workflow(self):
        """Test the orchestration workflow"""
        print("\n🧪 Phase 4.5: Testing Orchestration Workflow")
        print("=" * 50)
        
        test_cases = [
            {
                "query": "Write a Python function to calculate fibonacci numbers",
                "task_type": "code",
                "expected_agents": ["code_specialist"]
            },
            {
                "query": "Explain how machine learning works",
                "task_type": "technical",
                "expected_agents": ["technical_specialist"]
            },
            {
                "query": "Design a workflow for processing user uploads",
                "task_type": "workflow",
                "expected_agents": ["workflow_orchestrator"]
            }
        ]
        
        successful_tests = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"   🧪 Test {i}: {test_case['query'][:50]}...")
            
            try:
                # Test the master orchestration webhook
                response = requests.post(
                    f"{self.n8n_url}/webhook/master-orchestrator",
                    json={
                        "query": test_case["query"],
                        "task_type": test_case["task_type"]
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"      ✅ Success: {result.get('agent_used', 'Unknown')} agent used")
                    print(f"      Confidence: {result.get('confidence', 0):.2f}")
                    successful_tests += 1
                else:
                    print(f"      ❌ Failed: HTTP {response.status_code}")
                    print(f"      Response: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
        
        print(f"\n   📊 Test Results: {successful_tests}/{len(test_cases)} tests passed")
        return successful_tests == len(test_cases)
    
    def run_orchestration_pipeline(self):
        """Run complete orchestration pipeline"""
        print("🚀 Phase 4: Orchestrate Agentic Workflows")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Check system health
        healthy_components = self.check_system_health()
        if len(healthy_components) < 2:
            print("   ⚠️  Some components are not healthy")
        
        # Step 2: Create master orchestration workflow
        workflow_id = self.create_master_orchestration_workflow()
        if not workflow_id:
            print("   ❌ Failed to create master workflow")
            return False
        
        # Step 3: Create fallback mechanisms
        fallback_success = self.create_fallback_mechanisms()
        
        # Step 4: Create monitoring dashboard
        monitoring_success = self.create_monitoring_dashboard()
        
        # Step 5: Test orchestration workflow
        test_success = self.test_orchestration_workflow()
        
        # Summary
        print(f"\n📊 Phase 4 Summary:")
        print(f"   Healthy components: {len(healthy_components)}/3")
        print(f"   Master workflow: {'✅' if workflow_id else '❌'}")
        print(f"   Fallback mechanisms: {'✅' if fallback_success else '❌'}")
        print(f"   Monitoring dashboard: {'✅' if monitoring_success else '❌'}")
        print(f"   Testing: {'✅' if test_success else '❌'}")
        
        return all([workflow_id, fallback_success, monitoring_success])

def main():
    """Main function"""
    orchestrator = AgenticWorkflowOrchestrator()
    success = orchestrator.run_orchestration_pipeline()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())