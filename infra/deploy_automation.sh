#!/bin/bash
# AI System Automation Deployment Script
# Sets up launchctl services, health monitoring, and telemetry

set -e

echo "🚀 Deploying AI System Automation..."

# Create necessary directories
mkdir -p ~/ai/logs
mkdir -p ~/ai/benchmarks/2025-10
mkdir -p ~/Library/LaunchAgents

# Copy launchctl plists
echo "📋 Installing launchctl services..."
cp ~/ai/infra/launchctl/n8n.plist ~/Library/LaunchAgents/ai.n8n.plist
cp ~/ai/infra/launchctl/chromadb.plist ~/Library/LaunchAgents/ai.chromadb.plist

# Set proper permissions
chmod 644 ~/Library/LaunchAgents/ai.n8n.plist
chmod 644 ~/Library/LaunchAgents/ai.chromadb.plist

# Load services
echo "🔄 Loading services..."
launchctl load ~/Library/LaunchAgents/ai.n8n.plist
launchctl load ~/Library/LaunchAgents/ai.chromadb.plist

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install pyyaml sentence-transformers --break-system-packages

# Make scripts executable
chmod +x ~/ai/infra/health_monitor.py
chmod +x ~/ai/infra/ollama_benchmark.py
chmod +x ~/ai/infra/rag_validation.py

# Create cron job for health monitoring
echo "⏰ Setting up health monitoring cron job..."
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/bin/python3 ~/ai/infra/health_monitor.py") | crontab -

# Test services
echo "🧪 Testing services..."
sleep 5

# Test n8n
if curl -s http://localhost:5678/healthz > /dev/null; then
    echo "✅ n8n is running"
else
    echo "❌ n8n is not responding"
fi

# Test ChromaDB
if curl -s http://localhost:8000/api/v2/heartbeat > /dev/null; then
    echo "✅ ChromaDB is running (v2 API)"
else
    echo "❌ ChromaDB is not responding"
fi

# Test Ollama
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is running"
else
    echo "❌ Ollama is not responding"
fi

echo ""
echo "🎉 Automation deployment complete!"
echo ""
echo "📋 Services installed:"
echo "   - n8n (ai.n8n)"
echo "   - ChromaDB (ai.chromadb)"
echo "   - Health monitoring (every 5 minutes)"
echo ""
echo "🔧 Management commands:"
echo "   Start: launchctl load ~/Library/LaunchAgents/ai.*.plist"
echo "   Stop:  launchctl unload ~/Library/LaunchAgents/ai.*.plist"
echo "   Status: launchctl list | grep ai"
echo ""
echo "📊 Monitoring:"
echo "   Health check: python3 ~/ai/infra/health_monitor.py"
echo "   Benchmark: python3 ~/ai/infra/ollama_benchmark.py"
echo "   RAG validation: python3 ~/ai/infra/rag_validation.py"