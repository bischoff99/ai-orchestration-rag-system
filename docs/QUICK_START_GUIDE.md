# 🚀 n8n RAG Agent Workflows - Quick Start Guide

## System Status
- **n8n**: Running on http://localhost:5678
- **Ollama**: Running on http://localhost:11434
- **ChromaDB**: Running on http://localhost:8000

## Available Webhooks

### RAG Query
```bash
curl -X POST http://localhost:5678/webhook/rag-query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "collection": "general_knowledge"}'
```

### Document Ingestion
```bash
curl -X POST http://localhost:5678/webhook/document-ingestion \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/Users/andrejsp/ai/sample_docs", "collection_name": "test"}'
```

### Production RAG
```bash
curl -X POST http://localhost:5678/webhook/production-rag \
  -H "Content-Type: application/json" \
  -d '{"action": "query", "query": "What is AI?", "collection": "general_knowledge"}'
```

## Testing Commands

### Test System Health
```bash
python3 final_system_test.py
```

### Test Individual Components
```bash
# Test n8n workflows
python3 verify_workflows.py

# Test RAG ingestion
python3 phase2_rag_ingestion.py

# Test fine-tuning
python3 phase3_fine_tuning.py
```

## Configuration Files
- `configs/rag_config.json` - RAG system configuration
- `configs/ingestion_workflow.json` - Ingestion pipeline config
- `configs/monitoring_dashboard.json` - Monitoring configuration
- `configs/fallback_mechanisms.json` - Error handling config

## Troubleshooting

### Webhooks Not Working
1. Open http://localhost:5678 in browser
2. Go to Workflows section
3. Toggle "Active" switch for each workflow
4. Save each workflow

### ChromaDB Issues
```bash
# Restart ChromaDB
pkill -f chroma
chroma run --port 8000 &
```

### Ollama Issues
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Pull a model if needed
ollama pull llama-assistant
```

## Support
- Check logs in `/Users/andrejsp/ai/n8n/data/n8n.log`
- Monitor system with `python3 final_system_test.py`
- View system report in `SYSTEM_REPORT.json`
