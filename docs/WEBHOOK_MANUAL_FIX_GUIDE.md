# 🔧 Manual Webhook Fix Guide

## Problem Identified
All 4 n8n workflows are marked as "Active" in the API, but their webhook endpoints are not registered. This is a known n8n issue where the API state and webhook registration get out of sync.

## Current Status
- ✅ n8n is running on http://localhost:5678
- ✅ 4 workflows are active in the API
- ❌ 0 webhooks are accessible (all return 404)

## Manual Fix Required

### Step 1: Open n8n UI
Open your browser and go to: http://localhost:5678

### Step 2: Fix Each Workflow
For each of these 4 workflows, you need to manually toggle the "Active" switch:

#### Workflow 1: RAG Document Ingestion Pipeline
1. Find the workflow named "RAG Document Ingestion Pipeline"
2. Click on it to open
3. Toggle the "Active" switch OFF
4. Wait 2-3 seconds
5. Toggle the "Active" switch ON
6. Verify the webhook shows as registered

#### Workflow 2: RAG Query Processing Pipeline
1. Find the workflow named "RAG Query Processing Pipeline"
2. Click on it to open
3. Toggle the "Active" switch OFF
4. Wait 2-3 seconds
5. Toggle the "Active" switch ON
6. Verify the webhook shows as registered

#### Workflow 3: Enhanced RAG Query Processing Pipeline
1. Find the workflow named "Enhanced RAG Query Processing Pipeline"
2. Click on it to open
3. Toggle the "Active" switch OFF
4. Wait 2-3 seconds
5. Toggle the "Active" switch ON
6. Verify the webhook shows as registered

#### Workflow 4: Production RAG Workflow
1. Find the workflow named "Production RAG Workflow"
2. Click on it to open
3. Toggle the "Active" switch OFF
4. Wait 2-3 seconds
5. Toggle the "Active" switch ON
6. Verify the webhook shows as registered

### Step 3: Verify Webhooks Are Working
After fixing all workflows, test the webhooks:

```bash
# Test Document Ingestion
curl -X POST http://localhost:5678/webhook/document-ingestion \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/test", "collection_name": "test"}'

# Test RAG Query
curl -X POST http://localhost:5678/webhook/rag-query \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "collection": "test"}'

# Test Enhanced RAG Query
curl -X POST http://localhost:5678/webhook/rag-query-enhanced \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "collection": "test"}'

# Test Production RAG
curl -X POST http://localhost:5678/webhook/production-rag \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "collection": "test"}'
```

## Why This Happens
This is a known n8n behavior where:
1. Workflows can be activated via API
2. But webhook registration requires the UI toggle action
3. The API state and webhook registry get out of sync
4. Manual toggle forces webhook re-registration

## After Fix
Once all webhooks are working:
1. Your RAG system will be fully functional
2. You can test the complete workflow
3. The system will be ready for production use

## Alternative: Complete Re-import
If manual toggle doesn't work, you can:
1. Export all workflows
2. Delete them from n8n
3. Re-import them
4. Activate them in the UI

This ensures clean webhook registration.