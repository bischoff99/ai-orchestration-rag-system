#!/usr/bin/env python3
"""
Activate All Workflows - Final Configuration
Activates all n8n workflows and tests the complete system
"""

import requests
import json
import time
import sys
from datetime import datetime

class WorkflowActivator:
    def __init__(self):
        self.n8n_url = "http://localhost:5678"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def get_workflows(self):
        """Get all workflows"""
        try:
            response = requests.get(f"{self.n8n_url}/api/v2/workflows", headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                print(f"❌ Failed to get workflows: HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting workflows: {e}")
            return []
    
    def activate_workflow(self, workflow_id, workflow_name):
        """Activate a workflow by toggling it off and on"""
        try:
            # First deactivate
            deactivate_response = requests.put(
                f"{self.n8n_url}/api/v2/workflows/{workflow_id}",
                headers=self.headers,
                json={"active": False},
                timeout=10
            )
            
            time.sleep(1)
            
            # Then activate
            activate_response = requests.put(
                f"{self.n8n_url}/api/v2/workflows/{workflow_id}",
                headers=self.headers,
                json={"active": True},
                timeout=10
            )
            
            if activate_response.status_code == 200:
                print(f"   ✅ Activated: {workflow_name}")
                return True
            else:
                print(f"   ❌ Failed to activate {workflow_name}: HTTP {activate_response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error activating {workflow_name}: {e}")
            return False
    
    def test_webhook(self, webhook_name, payload):
        """Test a webhook endpoint"""
        try:
            response = requests.post(
                f"{self.n8n_url}/webhook/{webhook_name}",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"   ✅ {webhook_name}: Working")
                return True
            else:
                print(f"   ❌ {webhook_name}: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ {webhook_name}: {e}")
            return False
    
    def activate_all_workflows(self):
        """Activate all workflows"""
        print("🔄 Activating All Workflows")
        print("=" * 40)
        
        workflows = self.get_workflows()
        if not workflows:
            print("❌ No workflows found")
            return False
        
        activated_count = 0
        
        for workflow in workflows:
            workflow_id = workflow.get('id')
            workflow_name = workflow.get('name', 'Unknown')
            is_active = workflow.get('active', False)
            
            print(f"\n📄 Processing: {workflow_name}")
            print(f"   ID: {workflow_id}")
            print(f"   Currently active: {is_active}")
            
            if self.activate_workflow(workflow_id, workflow_name):
                activated_count += 1
            
            time.sleep(2)  # Wait between activations
        
        print(f"\n📊 Activated {activated_count}/{len(workflows)} workflows")
        return activated_count > 0
    
    def test_all_webhooks(self):
        """Test all webhook endpoints"""
        print("\n🧪 Testing All Webhooks")
        print("=" * 40)
        
        webhook_tests = [
            ("rag-query", {"query": "What is machine learning?", "collection": "general_knowledge"}),
            ("document-ingestion", {"directory_path": "/Users/andrejsp/ai/sample_docs", "collection_name": "test"}),
            ("production-rag", {"action": "query", "query": "What is AI?", "collection": "general_knowledge"}),
            ("test-simple", {"test": "data"}),
            ("rag-query-enhanced", {"query": "What is artificial intelligence?", "collection": "general_knowledge"})
        ]
        
        working_webhooks = []
        
        for webhook_name, payload in webhook_tests:
            if self.test_webhook(webhook_name, payload):
                working_webhooks.append(webhook_name)
        
        print(f"\n📊 Working webhooks: {len(working_webhooks)}/{len(webhook_tests)}")
        return working_webhooks
    
    def create_quick_start_guide(self):
        """Create a quick start guide for the system"""
        print("\n📚 Creating Quick Start Guide")
        print("=" * 40)
        
        guide_content = """# 🚀 n8n RAG Agent Workflows - Quick Start Guide

## System Status
- **n8n**: Running on http://localhost:5678
- **Ollama**: Running on http://localhost:11434
- **ChromaDB**: Running on http://localhost:8000

## Available Webhooks

### RAG Query
```bash
curl -X POST http://localhost:5678/webhook/rag-query \\
  -H "Content-Type: application/json" \\
  -d '{"query": "What is machine learning?", "collection": "general_knowledge"}'
```

### Document Ingestion
```bash
curl -X POST http://localhost:5678/webhook/document-ingestion \\
  -H "Content-Type: application/json" \\
  -d '{"directory_path": "/Users/andrejsp/ai/sample_docs", "collection_name": "test"}'
```

### Production RAG
```bash
curl -X POST http://localhost:5678/webhook/production-rag \\
  -H "Content-Type: application/json" \\
  -d '{"action": "query", "query": "What is AI?", "collection": "general_knowledge"}'
```

## Testing Commands

### Test System Health
```bash
python3 final_system_test.py
```

### Test Individual Components
```bash
# Test n8n workflows
python3 verify_workflows.py

# Test RAG ingestion
python3 phase2_rag_ingestion.py

# Test fine-tuning
python3 phase3_fine_tuning.py
```

## Configuration Files
- `configs/rag_config.json` - RAG system configuration
- `configs/ingestion_workflow.json` - Ingestion pipeline config
- `configs/monitoring_dashboard.json` - Monitoring configuration
- `configs/fallback_mechanisms.json` - Error handling config

## Troubleshooting

### Webhooks Not Working
1. Open http://localhost:5678 in browser
2. Go to Workflows section
3. Toggle "Active" switch for each workflow
4. Save each workflow

### ChromaDB Issues
```bash
# Restart ChromaDB
pkill -f chroma
chroma run --port 8000 &
```

### Ollama Issues
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Pull a model if needed
ollama pull llama-assistant
```

## Support
- Check logs in `/Users/andrejsp/ai/n8n/data/n8n.log`
- Monitor system with `python3 final_system_test.py`
- View system report in `SYSTEM_REPORT.json`
"""
        
        guide_path = "/Users/andrejsp/ai/QUICK_START_GUIDE.md"
        with open(guide_path, 'w') as f:
            f.write(guide_content)
        
        print(f"   ✅ Quick start guide created: {guide_path}")
        return True
    
    def run_activation(self):
        """Run complete workflow activation"""
        print("🚀 Activating All n8n Workflows")
        print("=" * 50)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Activate all workflows
        activation_success = self.activate_all_workflows()
        
        # Step 2: Test all webhooks
        working_webhooks = self.test_all_webhooks()
        
        # Step 3: Create quick start guide
        guide_success = self.create_quick_start_guide()
        
        # Summary
        print(f"\n📊 Activation Summary:")
        print(f"   Workflow activation: {'✅' if activation_success else '❌'}")
        print(f"   Working webhooks: {len(working_webhooks)}")
        print(f"   Quick start guide: {'✅' if guide_success else '❌'}")
        
        if len(working_webhooks) > 0:
            print(f"\n🎉 System is ready!")
            print(f"   Working webhooks: {', '.join(working_webhooks)}")
            print(f"   Access n8n at: http://localhost:5678")
        else:
            print(f"\n⚠️  Manual activation required:")
            print(f"   1. Open http://localhost:5678")
            print(f"   2. Go to Workflows section")
            print(f"   3. Toggle 'Active' switch for each workflow")
        
        return len(working_webhooks) > 0

def main():
    """Main function"""
    activator = WorkflowActivator()
    success = activator.run_activation()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())