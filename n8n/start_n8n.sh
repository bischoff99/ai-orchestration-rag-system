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
