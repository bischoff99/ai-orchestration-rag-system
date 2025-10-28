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
