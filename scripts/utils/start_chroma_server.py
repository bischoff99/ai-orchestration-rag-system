#!/usr/bin/env python3
"""
Start ChromaDB HTTP Server
Provides web interface for ChromaDB collections
"""

import chromadb
from chromadb.config import Settings
import uvicorn
import os

def start_chroma_server():
    """Start ChromaDB HTTP server with web interface"""
    print("🚀 Starting ChromaDB HTTP Server")
    print("=" * 35)
    
    # Configure ChromaDB settings
    settings = Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="/Users/andrejsp/ai/vector_db/chroma",
        chroma_api_impl="chromadb.api.fastapi.FastAPI",
        chroma_server_host="0.0.0.0",
        chroma_server_http_port=8000,
        chroma_server_ssl_enabled=False,
        chroma_server_cors_allow_origins=["*"]
    )
    
    # Create client
    client = chromadb.Client(settings)
    
    print("✅ ChromaDB HTTP Server Configuration:")
    print(f"   - Host: 0.0.0.0")
    print(f"   - Port: 8000")
    print(f"   - Persist Directory: /Users/andrejsp/ai/vector_db/chroma")
    print(f"   - CORS: Enabled")
    
    print("\n🌐 Web Interface URLs:")
    print("   - ChromaDB Admin: http://localhost:8000")
    print("   - API Docs: http://localhost:8000/docs")
    print("   - Health Check: http://localhost:8000/api/v2/heartbeat")
    
    print("\n📊 Available Collections:")
    collections = client.list_collections()
    for collection in collections:
        print(f"   - {collection.name}: {collection.count()} documents")
    
    print("\n💡 Usage:")
    print("   - Open http://localhost:8000 in your browser")
    print("   - Browse your collections and documents")
    print("   - Use the API for programmatic access")
    print("   - Press Ctrl+C to stop the server")
    
    # Start the server
    try:
        uvicorn.run(
            "chromadb.api.fastapi.FastAPI:app",
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 ChromaDB server stopped")

if __name__ == "__main__":
    start_chroma_server()