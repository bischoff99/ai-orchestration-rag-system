#!/bin/bash

# Force Import n8n Workflows
# This script ensures all workflows are properly imported and provides detailed status

set -e

echo "🔄 Force Importing n8n Workflows"
echo "================================="

# Check if n8n is running
echo "🔍 Checking n8n status..."
if ! curl -s http://localhost:5678 > /dev/null 2>&1; then
    echo "❌ n8n is not running. Starting n8n..."
    ./start_n8n.sh &
    echo "⏳ Waiting for n8n to start..."
    sleep 15
fi

# Wait for n8n to be ready
echo "⏳ Waiting for n8n to be ready..."
until curl -s http://localhost:5678 > /dev/null 2>&1; do
    echo "   Waiting for n8n..."
    sleep 2
done

echo "✅ n8n is ready"

# List all workflow files
echo ""
echo "📁 Available workflow files:"
ls -la workflows/*.json | while read line; do
    echo "   $line"
done

# Import each workflow individually with detailed feedback
echo ""
echo "📥 Importing workflows..."

WORKFLOWS_DIR="/Users/andrejsp/ai/n8n/workflows"
IMPORTED_COUNT=0
FAILED_COUNT=0

for workflow_file in "$WORKFLOWS_DIR"/*.json; do
    if [ -f "$workflow_file" ]; then
        workflow_name=$(basename "$workflow_file" .json)
        echo ""
        echo "📄 Importing: $workflow_name"
        
        # Try to import the workflow
        if curl -X POST "http://localhost:5678/api/v1/workflows" \
            -H "Content-Type: application/json" \
            -d @"$workflow_file" \
            -s > /dev/null 2>&1; then
            echo "✅ Successfully imported: $workflow_name"
            ((IMPORTED_COUNT++))
        else
            echo "❌ Failed to import: $workflow_name"
            ((FAILED_COUNT++))
        fi
    fi
done

echo ""
echo "📊 Import Summary:"
echo "   ✅ Successfully imported: $IMPORTED_COUNT"
echo "   ❌ Failed to import: $FAILED_COUNT"

if [ $IMPORTED_COUNT -gt 0 ]; then
    echo ""
    echo "🎉 Workflow import complete!"
    echo "🌐 Access n8n at: http://localhost:5678"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Open http://localhost:5678 in your browser"
    echo "   2. Log in to n8n"
    echo "   3. Go to Workflows section"
    echo "   4. Activate the workflows by toggling the 'Active' switch"
    echo "   5. Test with: python3 test_activated_workflows.py"
else
    echo ""
    echo "⚠️  No workflows were imported successfully"
    echo "   Check n8n logs for errors"
fi