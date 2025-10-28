#!/usr/bin/env python3
"""
Deploy n8n Workflows using MCP Tools
This script demonstrates how to use n8n MCP tools to deploy workflows
"""

import json
import sys
from pathlib import Path

def load_workflow(file_path):
    """Load workflow JSON from file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def create_production_rag_workflow():
    """Create the Production RAG Workflow using MCP tools"""
    print("🚀 Creating Production RAG Workflow...")
    
    # Load the workflow data
    workflow_data = load_workflow("/Users/andrejsp/ai/n8n/workflows/production_rag_workflow.json")
    
    # Extract components
    nodes = workflow_data['nodes']
    connections = workflow_data['connections']
    settings = workflow_data.get('settings', {})
    
    print(f"📄 Workflow: {workflow_data['name']}")
    print(f"📊 Nodes: {len(nodes)}")
    print(f"🔗 Connections: {len(connections)}")
    
    # This is where we would use the MCP tools to create the workflow
    # For now, we'll prepare the data structure
    workflow_structure = {
        "name": "Production RAG Workflow",
        "nodes": nodes,
        "connections": connections,
        "settings": settings
    }
    
    return workflow_structure

def create_rag_query_workflow():
    """Create the RAG Query Workflow"""
    print("🚀 Creating RAG Query Workflow...")
    
    workflow_data = load_workflow("/Users/andrejsp/ai/n8n/workflows/rag_query_workflow.json")
    
    return {
        "name": "RAG Query Processing Pipeline",
        "nodes": workflow_data['nodes'],
        "connections": workflow_data['connections'],
        "settings": workflow_data.get('settings', {})
    }

def create_document_ingestion_workflow():
    """Create the Document Ingestion Workflow"""
    print("🚀 Creating Document Ingestion Workflow...")
    
    workflow_data = load_workflow("/Users/andrejsp/ai/n8n/workflows/document_ingestion_workflow.json")
    
    return {
        "name": "RAG Document Ingestion Pipeline",
        "nodes": workflow_data['nodes'],
        "connections": workflow_data['connections'],
        "settings": workflow_data.get('settings', {})
    }

def create_monitoring_workflow():
    """Create the Monitoring Workflow"""
    print("🚀 Creating Monitoring Workflow...")
    
    workflow_data = load_workflow("/Users/andrejsp/ai/n8n/workflows/monitoring_workflow.json")
    
    return {
        "name": "RAG System Monitoring & Maintenance",
        "nodes": workflow_data['nodes'],
        "connections": workflow_data['connections'],
        "settings": workflow_data.get('settings', {})
    }

def main():
    """Main deployment function"""
    print("🚀 n8n Workflow Deployment with MCP Tools")
    print("=" * 50)
    
    # Create all workflows
    workflows = []
    
    try:
        workflows.append(create_production_rag_workflow())
        workflows.append(create_rag_query_workflow())
        workflows.append(create_document_ingestion_workflow())
        workflows.append(create_monitoring_workflow())
        
        print(f"\n✅ Successfully prepared {len(workflows)} workflows:")
        for workflow in workflows:
            print(f"   • {workflow['name']}")
        
        print(f"\n📋 Next Steps:")
        print(f"   1. Use n8n MCP tools to create these workflows")
        print(f"   2. Activate workflows in n8n UI")
        print(f"   3. Test with: python3 verify_workflows.py")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        return 1

if __name__ == "__main__":
    exit(main())