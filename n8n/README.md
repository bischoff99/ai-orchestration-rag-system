# n8n RAG System Workflows

This directory contains n8n workflows for orchestrating the RAG (Retrieval-Augmented Generation) system.

## 🚀 Quick Start

1. **Install n8n:**
   ```bash
   chmod +x setup_n8n.sh
   ./setup_n8n.sh
   ```

2. **Start n8n:**
   ```bash
   ./start_n8n.sh
   ```

3. **Import workflows:**
   ```bash
   ./import_workflows.sh
   ```

4. **Access web interface:**
   Open http://localhost:5678 in your browser

## 📋 Workflows

### 1. Document Ingestion Pipeline
- **File:** `document_ingestion_workflow.json`
- **Purpose:** Process and ingest documents into ChromaDB
- **Features:**
  - Smart file filtering (skips binary files, system files)
  - Parallel processing by file type (PDF, TXT, DOCX)
  - Error handling and notifications
  - Progress tracking

### 2. RAG Query Processing
- **File:** `rag_query_workflow.json`
- **Purpose:** Handle RAG queries via webhook
- **Features:**
  - Query validation
  - ChromaDB search
  - Ollama generation
  - Response formatting
  - Error handling

### 3. Monitoring & Maintenance
- **File:** `monitoring_workflow.json`
- **Purpose:** Daily health checks and maintenance
- **Features:**
  - Service health monitoring
  - RAG system testing
  - Alert notifications
  - Automated cleanup

## 🔧 Configuration

### Environment Variables
```bash
export N8N_USER_FOLDER="/Users/andrejsp/ai/n8n/data"
export N8N_HOST="localhost"
export N8N_PORT="5678"
export N8N_PROTOCOL="http"
```

### Webhook Endpoints
- **Document Ingestion:** `http://localhost:5678/webhook/document-ingestion`
- **RAG Query:** `http://localhost:5678/webhook/rag-query`

## 📚 API Usage

### Python Client
```python
from api_integration import N8nRAGClient

client = N8nRAGClient()

# Trigger document ingestion
result = client.trigger_document_ingestion(
    directory_path="/path/to/documents",
    collection_name="my_collection"
)

# Query RAG system
result = client.query_rag(
    query="What is machine learning?",
    collection="my_collection"
)
```

### cURL Examples
```bash
# Trigger document ingestion
curl -X POST http://localhost:5678/webhook/document-ingestion \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/path/to/documents", "collection_name": "my_collection"}'

# Query RAG system
curl -X POST http://localhost:5678/webhook/rag-query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "collection": "my_collection"}'
```

## 🔍 Workflow Details

### Document Ingestion Flow
1. **Start Trigger** → Manual or webhook trigger
2. **Scan Directory** → Find all files in specified directory
3. **Filter Files** → Skip binary files, system files, app bundles
4. **Split by Type** → Separate files by type for parallel processing
5. **Process Files** → Extract text from PDF, TXT, DOCX files
6. **Combine Chunks** → Merge all processed chunks
7. **Ingest to ChromaDB** → Store chunks in vector database
8. **Check Success** → Validate ingestion success
9. **Notifications** → Send success/error notifications

### RAG Query Flow
1. **Webhook Trigger** → Receive query via HTTP POST
2. **Process Query** → Validate and format query
3. **Search ChromaDB** → Find relevant documents
4. **Format Context** → Prepare context for LLM
5. **Generate with Ollama** → Generate response using LLM
6. **Format Response** → Structure final response
7. **Return Response** → Send response back to client

### Monitoring Flow
1. **Cron Trigger** → Daily execution at 9 AM
2. **Health Check** → Test all services (ChromaDB, Ollama, n8n)
3. **Test RAG Query** → Verify RAG system functionality
4. **Generate Report** → Create status report
5. **Check Alert Level** → Determine if alerts needed
6. **Send Notifications** → Alert on issues or send daily report
7. **Cleanup Task** → Perform maintenance tasks

## 🛠️ Customization

### Adding New File Types
1. Edit `document_ingestion_workflow.json`
2. Add new file type to "Split by File Type" node
3. Create new processing node for the file type
4. Connect to "Combine Chunks" node

### Adding New Services
1. Edit `monitoring_workflow.json`
2. Add new service check to "Health Check" node
3. Update report generation logic

### Custom Notifications
1. Replace Slack nodes with your preferred notification service
2. Update message templates
3. Configure webhook URLs

## 🐛 Troubleshooting

### Common Issues
1. **n8n won't start:** Check Node.js version (18+ required)
2. **Workflows not importing:** Ensure n8n is running and accessible
3. **Webhook errors:** Check webhook URLs and payload format
4. **ChromaDB connection:** Verify ChromaDB is running on port 8000
5. **Ollama connection:** Verify Ollama is running on port 11434

### Logs
- **n8n logs:** `/Users/andrejsp/ai/n8n/data/n8n.log`
- **System logs:** Check system logs for service issues

### Debug Mode
```bash
export N8N_LOG_LEVEL=debug
./start_n8n.sh
```

## 📈 Benefits of n8n Approach

1. **Visual Workflow Design** - Easy to understand and modify
2. **Built-in Error Handling** - Automatic retries and error notifications
3. **Parallel Processing** - Multiple file types processed simultaneously
4. **Webhook Integration** - Easy integration with external systems
5. **Monitoring & Alerts** - Automated health checks and notifications
6. **Scalability** - Can handle large document collections
7. **Maintainability** - Clear workflow structure and documentation

## 🔗 Integration with Existing RAG System

The n8n workflows integrate with the existing RAG system by:
- Using the same ChromaDB collections
- Calling the same Ollama models
- Maintaining the same API interfaces
- Preserving existing data structures

This provides a visual, maintainable layer on top of the existing Python-based RAG system.