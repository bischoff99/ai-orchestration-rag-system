#!/usr/bin/env python3
"""
Start Web Interfaces for RAG System
Launches ChromaDB and Qdrant web interfaces
"""

import subprocess
import time
import webbrowser
import os
from pathlib import Path

def start_chroma_http_server():
    """Start ChromaDB HTTP server"""
    print("🚀 Starting ChromaDB HTTP Server")
    print("=" * 35)
    
    try:
        # Start ChromaDB server
        cmd = [
            "python", "-c",
            """
import chromadb
from chromadb.config import Settings
import uvicorn

settings = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="/Users/andrejsp/ai/vector_db/chroma",
    chroma_api_impl="chromadb.api.fastapi.FastAPI",
    chroma_server_host="0.0.0.0",
    chroma_server_http_port=8000,
    chroma_server_ssl_enabled=False,
    chroma_server_cors_allow_origins=["*"]
)

client = chromadb.Client(settings)
print("ChromaDB server starting...")
uvicorn.run("chromadb.api.fastapi.FastAPI:app", host="0.0.0.0", port=8000)
"""
        ]
        
        print("🔄 Starting ChromaDB server...")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(5)
        
        print("✅ ChromaDB server started!")
        print("🌐 Web Interface: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        
        return process
        
    except Exception as e:
        print(f"❌ Error starting ChromaDB server: {e}")
        return None

def open_web_interfaces():
    """Open web interfaces in browser"""
    print("\n🌐 Opening Web Interfaces")
    print("=" * 30)
    
    # Open HTML demo
    demo_file = "/Users/andrejsp/ai/web/chroma_demo.html"
    if os.path.exists(demo_file):
        print(f"📄 Opening HTML demo: {demo_file}")
        webbrowser.open(f"file://{demo_file}")
    
    # Open ChromaDB admin (if server is running)
    print("🌐 Opening ChromaDB admin: http://localhost:8000")
    webbrowser.open("http://localhost:8000")

def show_usage_guide():
    """Show usage guide"""
    print("\n📖 Web Interface Usage Guide")
    print("=" * 35)
    
    print("🌐 Available Interfaces:")
    print("   1. HTML Demo: file:///Users/andrejsp/ai/web/chroma_demo.html")
    print("      - Static demo of your collections and queries")
    print("      - No server required")
    print("      - Shows sample data and query results")
    
    print("\n   2. ChromaDB Admin: http://localhost:8000")
    print("      - Full ChromaDB web interface")
    print("      - Browse collections and documents")
    print("      - Interactive query interface")
    print("      - API documentation")
    
    print("\n   3. API Endpoints:")
    print("      - Collections: http://localhost:8000/api/v2/collections")
    print("      - Query: http://localhost:8000/api/v2/collections/{collection}/query")
    print("      - Health: http://localhost:8000/api/v2/heartbeat")
    
    print("\n🔧 Collections Available:")
    print("   - documents: Your original documents")
    print("   - optimal_hf_datasets: Hugging Face datasets (1,000 docs)")
    print("   - ollama_docs: Ollama-specific documents")
    print("   - unified_docs: Unified document collection")
    
    print("\n💡 Next Steps:")
    print("   1. Browse collections in the web interface")
    print("   2. Test queries using the API")
    print("   3. Integrate with your applications")
    print("   4. Add more documents as needed")

def main():
    """Main function"""
    print("🚀 Starting RAG Web Interfaces")
    print("=" * 40)
    
    # Start ChromaDB server
    chroma_process = start_chroma_http_server()
    
    if chroma_process:
        # Open web interfaces
        open_web_interfaces()
        
        # Show usage guide
        show_usage_guide()
        
        print(f"\n🎉 Web interfaces are running!")
        print(f"Press Ctrl+C to stop the ChromaDB server")
        
        try:
            # Keep server running
            chroma_process.wait()
        except KeyboardInterrupt:
            print(f"\n👋 Stopping ChromaDB server...")
            chroma_process.terminate()
            print(f"✅ Server stopped")
    else:
        print("❌ Could not start ChromaDB server")
        print("💡 You can still use the HTML demo: file:///Users/andrejsp/ai/web/chroma_demo.html")

if __name__ == "__main__":
    main()