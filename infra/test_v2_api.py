#!/usr/bin/env python3
"""
Test ChromaDB v2 API endpoints
"""
import requests
import json

def test_chromadb_v2():
    """Test ChromaDB v2 API endpoints"""
    base_url = "http://localhost:8000/api/v2"
    
    print("🧪 Testing ChromaDB v2 API endpoints...")
    
    # Test heartbeat
    try:
        response = requests.get(f"{base_url}/heartbeat", timeout=10)
        if response.status_code == 200:
            print("✅ /api/v2/heartbeat - Working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ /api/v2/heartbeat - Status {response.status_code}")
    except Exception as e:
        print(f"❌ /api/v2/heartbeat - Error: {e}")
    
    # Test version
    try:
        response = requests.get(f"{base_url}/version", timeout=10)
        if response.status_code == 200:
            print("✅ /api/v2/version - Working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ /api/v2/version - Status {response.status_code}")
    except Exception as e:
        print(f"❌ /api/v2/version - Error: {e}")
    
    # Test collections
    try:
        response = requests.get(f"{base_url}/collections", timeout=10)
        if response.status_code == 200:
            print("✅ /api/v2/collections - Working")
            collections = response.json()
            print(f"   Found {len(collections.get('data', []))} collections")
        else:
            print(f"❌ /api/v2/collections - Status {response.status_code}")
    except Exception as e:
        print(f"❌ /api/v2/collections - Error: {e}")

if __name__ == "__main__":
    test_chromadb_v2()