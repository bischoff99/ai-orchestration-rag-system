#!/usr/bin/env python3
"""
Start Qdrant Server with Web Dashboard
Provides web interface for Qdrant vector database
"""

import subprocess
import os
import time
import requests

def start_qdrant_server():
    """Start Qdrant server with web dashboard"""
    print("🚀 Starting Qdrant Server with Web Dashboard")
    print("=" * 45)
    
    # Qdrant configuration
    qdrant_host = "0.0.0.0"
    qdrant_port = 6333
    qdrant_data_path = "/Users/andrejsp/ai/vector_db/qdrant"
    
    # Create data directory
    os.makedirs(qdrant_data_path, exist_ok=True)
    
    print("✅ Qdrant Server Configuration:")
    print(f"   - Host: {qdrant_host}")
    print(f"   - Port: {qdrant_port}")
    print(f"   - Data Path: {qdrant_data_path}")
    
    print("\n🌐 Web Interface URLs:")
    print(f"   - Qdrant Dashboard: http://localhost:{qdrant_port}/dashboard")
    print(f"   - API Docs: http://localhost:{qdrant_port}/docs")
    print(f"   - Health Check: http://localhost:{qdrant_port}/health")
    print(f"   - Collections: http://localhost:{qdrant_port}/collections")
    
    print("\n💡 Usage:")
    print("   - Open http://localhost:6333/dashboard in your browser")
    print("   - Browse your collections and vectors")
    print("   - Use the API for programmatic access")
    print("   - Press Ctrl+C to stop the server")
    
    # Start Qdrant server
    try:
        cmd = [
            "qdrant",
            "--host", qdrant_host,
            "--port", str(qdrant_port),
            "--storage", qdrant_data_path
        ]
        
        print(f"\n🔄 Starting Qdrant server...")
        print(f"Command: {' '.join(cmd)}")
        
        # Run Qdrant server
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get(f"http://localhost:{qdrant_port}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Qdrant server started successfully!")
            else:
                print("⚠️  Qdrant server may not be fully ready yet")
        except:
            print("⚠️  Could not verify Qdrant server status")
        
        # Wait for user to stop
        print("\n🔄 Qdrant server is running... Press Ctrl+C to stop")
        process.wait()
        
    except KeyboardInterrupt:
        print("\n👋 Stopping Qdrant server...")
        if 'process' in locals():
            process.terminate()
        print("✅ Qdrant server stopped")
    except FileNotFoundError:
        print("❌ Qdrant not found. Please install Qdrant:")
        print("   - Docker: docker run -p 6333:6333 qdrant/qdrant")
        print("   - Binary: Download from https://github.com/qdrant/qdrant/releases")
        print("   - Python: pip install qdrant-client")

if __name__ == "__main__":
    start_qdrant_server()