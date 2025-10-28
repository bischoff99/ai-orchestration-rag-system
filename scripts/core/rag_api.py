#!/usr/bin/env python3
"""
RAG API Service
FastAPI service for RAG operations
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_query import query_rag_system
from ingest_documents import ingest_directory

app = FastAPI(
    title="AI RAG API",
    description="RAG (Retrieval-Augmented Generation) API Service",
    version="1.0.0"
)

# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    collection: str = "default_docs"
    k: int = 5
    model: str = "llama-assistant"

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    query: str
    timestamp: str
    model: str
    collection: str

class IngestRequest(BaseModel):
    directory_path: str
    collection_name: str = "default_docs"

class IngestResponse(BaseModel):
    status: str
    message: str
    collection: str
    stats: Dict[str, Any]
    timestamp: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "rag-api"}

@app.post("/api/search", response_model=QueryResponse)
async def search_documents(request: QueryRequest):
    """Search documents and generate response"""
    try:
        result = query_rag_system(
            query=request.query,
            collection=request.collection,
            k=request.k
        )
        
        return QueryResponse(
            answer=result.get("answer", "No answer generated"),
            sources=result.get("sources", []),
            query=request.query,
            timestamp=result.get("timestamp", ""),
            model=request.model,
            collection=request.collection
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest):
    """Ingest documents from directory"""
    try:
        result = ingest_directory(
            directory_path=request.directory_path,
            collection_name=request.collection_name
        )
        
        return IngestResponse(
            status="success",
            message="Documents ingested successfully",
            collection=request.collection_name,
            stats=result.get("stats", {}),
            timestamp=result.get("timestamp", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/collections")
async def list_collections():
    """List available collections"""
    try:
        # This would integrate with your vector database
        return {"collections": ["default_docs", "test_collection"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    try:
        return {
            "total_collections": 2,
            "total_documents": 1000,
            "status": "operational"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)