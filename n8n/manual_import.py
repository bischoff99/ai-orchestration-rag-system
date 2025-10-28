#!/usr/bin/env python3
"""
Manual workflow import script for n8n
"""

import requests
import json
import os
import time

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
BASE_URL = "http://localhost:5678"
API_URL = f"{BASE_URL}/api/v1"

def import_workflow(workflow_file):
    """Import a single workflow"""
    with open(workflow_file, 'r') as f:
        workflow_data = json.load(f)
    
    headers = {
        "X-N8N-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Remove the id field to let n8n generate a new one
    if 'id' in workflow_data:
        del workflow_data['id']
    
    response = requests.post(f"{API_URL}/workflows", 
                           json=workflow_data, 
                           headers=headers)
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"✅ Imported: {workflow_data['name']} (ID: {result['id']})")
        return result['id']
    else:
        print(f"❌ Failed to import {workflow_data['name']}: {response.status_code} - {response.text}")
        return None

def activate_workflow(workflow_id):
    """Activate a workflow"""
    headers = {"X-N8N-API-KEY": API_KEY}
    
    response = requests.post(f"{API_URL}/workflows/{workflow_id}/activate", 
                           headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Activated workflow {workflow_id}")
        return True
    else:
        print(f"❌ Failed to activate workflow {workflow_id}: {response.status_code} - {response.text}")
        return False

def main():
    workflows_dir = "/Users/andrejsp/ai/n8n/workflows"
    workflow_files = [
        "../test_workflow.json"
    ]
    
    print("📥 Importing RAG workflows...")
    
    workflow_ids = []
    for workflow_file in workflow_files:
        file_path = os.path.join(workflows_dir, workflow_file)
        if os.path.exists(file_path):
            workflow_id = import_workflow(file_path)
            if workflow_id:
                workflow_ids.append(workflow_id)
        else:
            print(f"❌ File not found: {file_path}")
    
    print(f"\n📊 Imported {len(workflow_ids)} workflows")
    
    # Wait a moment for workflows to be processed
    time.sleep(2)
    
    # Activate workflows
    print("\n🔄 Activating workflows...")
    for workflow_id in workflow_ids:
        activate_workflow(workflow_id)
    
    print("\n🎉 Workflow import and activation complete!")
    print(f"🌐 Access n8n at: {BASE_URL}")

if __name__ == "__main__":
    main()