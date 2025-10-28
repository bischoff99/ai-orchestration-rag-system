# 🔄 n8n Workflow Activation Guide

## Quick Activation Steps

### 1. Access n8n Web Interface
Open your browser and go to: **http://localhost:5678**

### 2. Log In to n8n
- If this is your first time, create an account
- If you already have an account, log in

### 3. Navigate to Workflows
- Click on "Workflows" in the left sidebar
- You should see 6 imported workflows

### 4. Activate Each Workflow
For each workflow, click the toggle switch to activate it:

#### ✅ **RAG Document Ingestion Pipeline**
- **Webhook**: `/webhook/document-ingestion`
- **Purpose**: Process and ingest documents into ChromaDB
- **Status**: Click toggle to activate

#### ✅ **RAG Query Processing Pipeline** 
- **Webhook**: `/webhook/rag-query`
- **Purpose**: Handle RAG queries via webhook
- **Status**: Click toggle to activate

#### ✅ **RAG System Monitoring & Maintenance**
- **Trigger**: Daily cron (9 AM)
- **Purpose**: Health checks and maintenance
- **Status**: Click toggle to activate

#### ✅ **Production RAG Workflow**
- **Webhook**: `/webhook/production-rag`
- **Purpose**: Unified workflow for query and ingest
- **Status**: Click toggle to activate

### 5. Verify Activation
After activating all workflows, run the test script:

```bash
cd /Users/andrejsp/ai
python3 test_activated_workflows.py
```

## Expected Results

When workflows are properly activated, you should see:

```
✅ RAG Query Workflow: SUCCESS
✅ Document Ingestion Workflow: SUCCESS  
✅ Production RAG Workflow: SUCCESS
🎉 All workflows are working correctly!
```

## Troubleshooting

### If workflows don't activate:
1. **Check n8n is running**: `ps aux | grep n8n`
2. **Restart n8n**: `./n8n/start_n8n.sh`
3. **Check web interface**: http://localhost:5678
4. **Verify imports**: Run `./n8n/import_workflows.sh`

### If webhooks return 404:
- Workflows are imported but not activated
- Go to n8n UI and toggle the "Active" switch
- Wait a few seconds for activation to complete

### If webhooks return errors:
- Check that Ollama is running: `curl http://localhost:11434/api/tags`
- Check that RAG system is working: `python3 scripts/rag_query.py --list-collections`

## Webhook Endpoints

Once activated, these endpoints will be available:

- **POST** `/webhook/rag-query` - Query RAG system
- **POST** `/webhook/document-ingestion` - Ingest documents  
- **POST** `/webhook/production-rag` - Unified RAG operations

## Testing Commands

```bash
# Test RAG Query
curl -X POST http://localhost:5678/webhook/rag-query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "collection": "general_knowledge"}'

# Test Document Ingestion
curl -X POST http://localhost:5678/webhook/document-ingestion \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/Users/andrejsp/ai/sample_docs", "collection_name": "test"}'

# Test Production RAG
curl -X POST http://localhost:5678/webhook/production-rag \
  -H "Content-Type: application/json" \
  -d '{"action": "query", "query": "What is AI?", "collection": "general_knowledge"}'
```

## Next Steps

After successful activation:
1. **Test workflows**: Run `python3 test_activated_workflows.py`
2. **Monitor system**: Check n8n execution logs
3. **Deploy production**: Use Docker Compose setup
4. **Set up monitoring**: Configure health checks