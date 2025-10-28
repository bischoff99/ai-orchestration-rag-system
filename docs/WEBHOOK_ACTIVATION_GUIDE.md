# 🔧 Webhook Activation Guide

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
curl -X POST http://localhost:5678/webhook/rag-query \
  -H "Content-Type: application/json" \
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
