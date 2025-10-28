#!/bin/bash

# n8n Setup Script for RAG System
# This script installs and configures n8n for document processing workflows

set -e

echo "🚀 Setting up n8n for RAG System"
echo "================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18 or higher is required. Current version: $(node --version)"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Install n8n globally
echo "📦 Installing n8n..."
npm install -g n8n

# Create n8n data directory
N8N_DATA_DIR="/Users/andrejsp/ai/n8n/data"
mkdir -p "$N8N_DATA_DIR"

# Create n8n configuration
cat > "$N8N_DATA_DIR/config.json" << EOF
{
  "database": {
    "type": "sqlite",
    "location": "$N8N_DATA_DIR/database.sqlite"
  },
  "credentials": {
    "overwrite": {
      "data": {
        "encryptionKey": "your-encryption-key-here"
      }
    }
  },
  "endpoints": {
    "rest": "rest",
    "webhook": "webhook",
    "webhookWaiting": "webhook-waiting",
    "webhookTest": "webhook-test"
  },
  "publicApi": {
    "enabled": true,
    "path": "api"
  },
  "workflows": {
    "defaultName": "My workflow"
  },
  "logging": {
    "level": "info",
    "file": "$N8N_DATA_DIR/n8n.log"
  },
  "timezone": "UTC"
}
EOF

# Create systemd service file (for Linux) or launchd plist (for macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - Create LaunchAgent
    LAUNCH_AGENT_DIR="$HOME/Library/LaunchAgents"
    mkdir -p "$LAUNCH_AGENT_DIR"
    
    cat > "$LAUNCH_AGENT_DIR/com.n8n.rag.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.n8n.rag</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/n8n</string>
        <string>start</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>N8N_USER_FOLDER</key>
        <string>$N8N_DATA_DIR</string>
        <key>N8N_HOST</key>
        <string>localhost</string>
        <key>N8N_PORT</key>
        <string>5678</string>
        <key>N8N_PROTOCOL</key>
        <string>http</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$N8N_DATA_DIR/n8n.out.log</string>
    <key>StandardErrorPath</key>
    <string>$N8N_DATA_DIR/n8n.err.log</string>
</dict>
</plist>
EOF

    echo "✅ Created LaunchAgent for macOS"
    echo "   To start n8n: launchctl load ~/Library/LaunchAgents/com.n8n.rag.plist"
    echo "   To stop n8n: launchctl unload ~/Library/LaunchAgents/com.n8n.rag.plist"
else
    # Linux - Create systemd service
    sudo tee /etc/systemd/system/n8n-rag.service > /dev/null << EOF
[Unit]
Description=n8n RAG System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$N8N_DATA_DIR
Environment=N8N_USER_FOLDER=$N8N_DATA_DIR
Environment=N8N_HOST=localhost
Environment=N8N_PORT=5678
Environment=N8N_PROTOCOL=http
ExecStart=/usr/local/bin/n8n start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    echo "✅ Created systemd service"
    echo "   To start n8n: sudo systemctl start n8n-rag"
    echo "   To enable n8n: sudo systemctl enable n8n-rag"
fi

# Create startup script
cat > "/Users/andrejsp/ai/n8n/start_n8n.sh" << 'EOF'
#!/bin/bash

# Start n8n for RAG System
export N8N_USER_FOLDER="/Users/andrejsp/ai/n8n/data"
export N8N_HOST="localhost"
export N8N_PORT="5678"
export N8N_PROTOCOL="http"

echo "🚀 Starting n8n..."
echo "📁 Data directory: $N8N_USER_FOLDER"
echo "🌐 Web interface: http://localhost:5678"
echo "📚 Workflows directory: /Users/andrejsp/ai/n8n/workflows"

n8n start
EOF

chmod +x "/Users/andrejsp/ai/n8n/start_n8n.sh"

# Create workflow import script
cat > "/Users/andrejsp/ai/n8n/import_workflows.sh" << 'EOF'
#!/bin/bash

# Import n8n workflows for RAG system
N8N_API="http://localhost:5678/api/v1"
WORKFLOWS_DIR="/Users/andrejsp/ai/n8n/workflows"

echo "📥 Importing RAG workflows..."

# Wait for n8n to be ready
echo "⏳ Waiting for n8n to be ready..."
until curl -s "$N8N_API/workflows" > /dev/null 2>&1; do
    sleep 2
done

# Import workflows
for workflow_file in "$WORKFLOWS_DIR"/*.json; do
    if [ -f "$workflow_file" ]; then
        workflow_name=$(basename "$workflow_file" .json)
        echo "📄 Importing: $workflow_name"
        
        curl -X POST "$N8N_API/workflows" \
            -H "Content-Type: application/json" \
            -d @"$workflow_file" \
            -s > /dev/null
        
        if [ $? -eq 0 ]; then
            echo "✅ Imported: $workflow_name"
        else
            echo "❌ Failed to import: $workflow_name"
        fi
    fi
done

echo "🎉 Workflow import complete!"
echo "🌐 Access n8n at: http://localhost:5678"
EOF

chmod +x "/Users/andrejsp/ai/n8n/import_workflows.sh"

# Create API integration script
cat > "/Users/andrejsp/ai/n8n/api_integration.py" << 'EOF'
#!/usr/bin/env python3
"""
n8n API Integration for RAG System
Provides Python functions to interact with n8n workflows
"""

import requests
import json
import time
from typing import Dict, Any, Optional

class N8nRAGClient:
    def __init__(self, base_url: str = "http://localhost:5678"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.session = requests.Session()
    
    def trigger_document_ingestion(self, directory_path: str, collection_name: str = "default_docs") -> Dict[str, Any]:
        """Trigger document ingestion workflow"""
        webhook_url = f"{self.base_url}/webhook/document-ingestion"
        
        payload = {
            "directory_path": directory_path,
            "collection_name": collection_name
        }
        
        try:
            response = self.session.post(webhook_url, json=payload, timeout=30)
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

def main():
    """Example usage"""
    client = N8nRAGClient()
    
    # Test connection
    print("🔍 Testing n8n connection...")
    workflows = client.list_workflows()
    if "error" in workflows:
        print(f"❌ Connection failed: {workflows['error']}")
        return
    
    print("✅ Connected to n8n")
    
    # Example: Trigger document ingestion
    print("\n📚 Triggering document ingestion...")
    result = client.trigger_document_ingestion(
        directory_path="/Users/andrejsp/ai/sample_docs",
        collection_name="test_collection"
    )
    print(f"Result: {result}")
    
    # Example: Query RAG system
    print("\n🤖 Querying RAG system...")
    result = client.query_rag(
        query="What is machine learning?",
        collection="test_collection"
    )
    print(f"Answer: {result.get('answer', 'No answer')}")

if __name__ == "__main__":
    main()
EOF

chmod +x "/Users/andrejsp/ai/n8n/api_integration.py"

echo ""
echo "🎉 n8n setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Start n8n: ./start_n8n.sh"
echo "2. Import workflows: ./import_workflows.sh"
echo "3. Access web interface: http://localhost:5678"
echo "4. Test API integration: python3 api_integration.py"
echo ""
echo "📁 Files created:"
echo "   - Configuration: $N8N_DATA_DIR/config.json"
echo "   - Start script: /Users/andrejsp/ai/n8n/start_n8n.sh"
echo "   - Import script: /Users/andrejsp/ai/n8n/import_workflows.sh"
echo "   - API client: /Users/andrejsp/ai/n8n/api_integration.py"
echo "   - Workflows: /Users/andrejsp/ai/n8n/workflows/"
echo ""
echo "🔧 Manual setup (if needed):"
echo "   - Set encryption key in config.json"
echo "   - Configure Slack notifications"
echo "   - Set up webhook URLs"