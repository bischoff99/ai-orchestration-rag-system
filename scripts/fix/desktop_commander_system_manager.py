#!/usr/bin/env python3
"""
Desktop Commander System Manager
Comprehensive system management for n8n RAG Agent Workflows
"""

import requests
import json
import time
import subprocess
import webbrowser
from datetime import datetime

class DesktopCommanderSystemManager:
    def __init__(self):
        self.n8n_url = "http://localhost:5678"
        self.chromadb_url = "http://localhost:8000"
        self.ollama_url = "http://localhost:11434"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def check_system_health(self):
        """Check overall system health"""
        print("🔍 Desktop Commander System Health Check")
        print("=" * 50)
        
        health_status = {
            'n8n': False,
            'chromadb': False,
            'ollama': False,
            'workflows': 0,
            'active_workflows': 0
        }
        
        # Check n8n
        try:
            response = requests.get(self.n8n_url, timeout=5)
            if response.status_code == 200:
                health_status['n8n'] = True
                print("✅ n8n: Healthy")
            else:
                print(f"❌ n8n: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ n8n: {e}")
        
        # Check ChromaDB
        try:
            response = requests.get(f"{self.chromadb_url}/api/v2/heartbeat", timeout=5)
            if response.status_code == 200:
                health_status['chromadb'] = True
                print("✅ ChromaDB: Healthy")
            else:
                print(f"❌ ChromaDB: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ ChromaDB: {e}")
        
        # Check Ollama
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                health_status['ollama'] = True
                models = response.json().get('models', [])
                print(f"✅ Ollama: Healthy ({len(models)} models)")
            else:
                print(f"❌ Ollama: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Ollama: {e}")
        
        # Check workflows
        try:
            response = requests.get(f"{self.n8n_url}/api/v2/workflows", headers=self.headers, timeout=10)
            if response.status_code == 200:
                workflows = response.json().get('data', [])
                active_workflows = [w for w in workflows if w.get('active', False)]
                health_status['workflows'] = len(workflows)
                health_status['active_workflows'] = len(active_workflows)
                print(f"✅ Workflows: {len(active_workflows)}/{len(workflows)} active")
            else:
                print(f"❌ Workflows: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Workflows: {e}")
        
        return health_status
    
    def open_n8n_ui(self):
        """Open n8n UI in browser"""
        print("🌐 Opening n8n UI...")
        try:
            webbrowser.open(self.n8n_url)
            print("✅ n8n UI opened in browser")
            return True
        except Exception as e:
            print(f"❌ Failed to open n8n UI: {e}")
            return False
    
    def test_webhooks(self):
        """Test all webhook endpoints"""
        print("🧪 Testing Webhook Endpoints")
        print("=" * 30)
        
        webhooks = [
            'rag-query',
            'document-ingestion',
            'rag-query-enhanced',
            'production-rag'
        ]
        
        working_webhooks = []
        
        for webhook in webhooks:
            try:
                response = requests.post(
                    f"{self.n8n_url}/webhook/{webhook}",
                    json={'test': 'data', 'query': 'test query'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ {webhook}: WORKING")
                    print(f"   Response: {str(result)[:100]}...")
                    working_webhooks.append(webhook)
                else:
                    print(f"❌ {webhook}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {webhook}: {e}")
        
        print(f"\n📊 Working webhooks: {len(working_webhooks)}/{len(webhooks)}")
        return working_webhooks
    
    def create_webhook_activation_guide(self):
        """Create a webhook activation guide"""
        guide_content = """# 🔧 Webhook Activation Guide

## Current Status
- ✅ All services running (n8n, ChromaDB, Ollama)
- ✅ 4 core workflows active
- ❌ Webhooks need manual activation

## Manual Activation Steps

### Step 1: Open n8n UI
- URL: http://localhost:5678
- Or click the link above

### Step 2: Activate Workflows
Go to the **Workflows** section and for each workflow:

1. **RAG Query Processing Pipeline**
   - Click on the workflow
   - Toggle "Active" switch **OFF**
   - Wait 2 seconds
   - Toggle "Active" switch **ON**
   - Click "Save"

2. **RAG Document Ingestion Pipeline**
   - Same process as above

3. **Enhanced RAG Query Processing Pipeline**
   - Same process as above

4. **Production RAG Workflow**
   - Same process as above

### Step 3: Test Webhooks
After activation, test the webhooks:
```bash
curl -X POST http://localhost:5678/webhook/rag-query \\
  -H "Content-Type: application/json" \\
  -d '{"query": "What is machine learning?"}'
```

## Expected Results
- All 4 webhooks should return JSON responses
- No more 404 "not registered" errors
- System ready for production use

## Troubleshooting
- If webhooks still don't work, restart n8n
- Check workflow logs in n8n UI
- Verify all services are running
"""
        
        with open('/Users/andrejsp/ai/WEBHOOK_ACTIVATION_GUIDE.md', 'w') as f:
            f.write(guide_content)
        
        print("📝 Webhook activation guide created: WEBHOOK_ACTIVATION_GUIDE.md")
        return True
    
    def run_comprehensive_test(self):
        """Run comprehensive system test"""
        print("🚀 Desktop Commander Comprehensive System Test")
        print("=" * 60)
        
        # Check system health
        health = self.check_system_health()
        
        # Open n8n UI
        self.open_n8n_ui()
        
        # Test webhooks
        working_webhooks = self.test_webhooks()
        
        # Create activation guide
        self.create_webhook_activation_guide()
        
        # Summary
        print("\n📊 System Test Summary")
        print("=" * 30)
        print(f"Services: {'✅' if all([health['n8n'], health['chromadb'], health['ollama']]) else '❌'}")
        print(f"Workflows: {health['active_workflows']}/{health['workflows']} active")
        print(f"Webhooks: {len(working_webhooks)}/4 working")
        
        if len(working_webhooks) == 4:
            print("\n🎉 System is fully operational!")
            return True
        else:
            print("\n⚠️  Manual webhook activation required")
            print("📝 See WEBHOOK_ACTIVATION_GUIDE.md for instructions")
            return False

def main():
    """Main function"""
    print("🖥️  Desktop Commander System Manager")
    print("=" * 40)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    manager = DesktopCommanderSystemManager()
    success = manager.run_comprehensive_test()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())