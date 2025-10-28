#!/usr/bin/env python3
"""
Deploy n8n Workflows using MCP Tools
Uses the n8n MCP server to deploy workflows programmatically
"""

import json
import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append('/Users/andrejsp/ai')

def load_workflow_file(file_path):
    """Load workflow JSON from file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        return None

def create_workflow_from_file(workflow_data, workflow_name):
    """Create workflow from JSON data"""
    try:
        # Extract nodes and connections from the workflow data
        nodes = workflow_data.get('nodes', [])
        connections = workflow_data.get('connections', {})
        
        # Create the workflow using MCP tools
        print(f"📄 Creating workflow: {workflow_name}")
        
        # This would be called via MCP tools in a real implementation
        # For now, we'll prepare the data structure
        workflow_structure = {
            "name": workflow_name,
            "nodes": nodes,
            "connections": connections,
            "settings": workflow_data.get('settings', {}),
            "active": False  # Start as inactive, user can activate later
        }
        
        return workflow_structure
    except Exception as e:
        print(f"❌ Error creating workflow {workflow_name}: {e}")
        return None

def main():
    """Deploy all workflows using MCP tools"""
    print("🚀 Deploying n8n Workflows with MCP Tools")
    print("=" * 50)
    
    workflows_dir = Path("/Users/andrejsp/ai/n8n/workflows")
    
    if not workflows_dir.exists():
        print(f"❌ Workflows directory not found: {workflows_dir}")
        return 1
    
    # List all workflow files
    workflow_files = list(workflows_dir.glob("*.json"))
    
    if not workflow_files:
        print("❌ No workflow files found")
        return 1
    
    print(f"📁 Found {len(workflow_files)} workflow files")
    
    deployed_workflows = []
    failed_workflows = []
    
    for workflow_file in workflow_files:
        workflow_name = workflow_file.stem.replace('_', ' ').title()
        
        print(f"\n📄 Processing: {workflow_name}")
        
        # Load workflow data
        workflow_data = load_workflow_file(workflow_file)
        if not workflow_data:
            failed_workflows.append(workflow_name)
            continue
        
        # Create workflow structure
        workflow_structure = create_workflow_from_file(workflow_data, workflow_name)
        if not workflow_structure:
            failed_workflows.append(workflow_name)
            continue
        
        deployed_workflows.append(workflow_structure)
        print(f"✅ Prepared: {workflow_name}")
    
    # Summary
    print(f"\n📊 Deployment Summary:")
    print(f"   ✅ Prepared: {len(deployed_workflows)}")
    print(f"   ❌ Failed: {len(failed_workflows)}")
    
    if failed_workflows:
        print(f"\n❌ Failed workflows:")
        for workflow in failed_workflows:
            print(f"   • {workflow}")
    
    if deployed_workflows:
        print(f"\n✅ Successfully prepared workflows:")
        for workflow in deployed_workflows:
            print(f"   • {workflow['name']}")
        
        print(f"\n📋 Next steps:")
        print(f"   1. Use n8n MCP tools to create workflows")
        print(f"   2. Activate workflows in n8n UI")
        print(f"   3. Test with: python3 verify_workflows.py")
    
    return 0

if __name__ == "__main__":
    exit(main())