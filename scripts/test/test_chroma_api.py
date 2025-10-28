#!/usr/bin/env python3
"""
Test ChromaDB HTTP API
Test the ChromaDB web interface and API
"""

import requests
import json
import time

def test_chroma_api():
    """Test ChromaDB HTTP API"""
    print("🧪 Testing ChromaDB HTTP API")
    print("=" * 30)
    
    base_url = "http://localhost:8000"
    
    # Test endpoints
    endpoints = [
        ("/api/v2/heartbeat", "Health Check"),
        ("/api/v2/collections", "Collections List"),
        ("/api/v2/version", "Version Info"),
        ("/docs", "API Documentation")
    ]
    
    for endpoint, description in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n🔍 Testing {description}: {url}")
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {description}: OK")
                
                # Show some data for collections
                if endpoint == "/api/v2/collections":
                    data = response.json()
                    print(f"   Collections found: {len(data)}")
                    for collection in data:
                        print(f"   - {collection.get('name', 'Unknown')}: {collection.get('count', 0)} documents")
            else:
                print(f"❌ {description}: HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {description}: Connection failed (server not running?)")
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
    
    # Test query endpoint
    print(f"\n🔍 Testing Query API: {base_url}/api/v2/collections/optimal_hf_datasets/query")
    try:
        query_data = {
            "query_texts": ["What is machine learning?"],
            "n_results": 3
        }
        
        response = requests.post(
            f"{base_url}/api/v2/collections/optimal_hf_datasets/query",
            json=query_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Query API: OK")
            print(f"   Found {len(data.get('documents', [[]])[0])} results")
            
            # Show first result
            if data.get('documents') and data['documents'][0]:
                first_doc = data['documents'][0][0]
                print(f"   First result: {first_doc[:100]}...")
        else:
            print(f"❌ Query API: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Query API: Error - {e}")

def main():
    """Main function"""
    print("🚀 ChromaDB API Tester")
    print("=" * 25)
    print("Make sure ChromaDB server is running:")
    print("   python /Users/andrejsp/ai/scripts/start_chroma_server.py")
    print()
    
    # Wait a moment for user to start server
    input("Press Enter when ChromaDB server is running...")
    
    test_chroma_api()
    
    print(f"\n🌐 Web Interface:")
    print(f"   - ChromaDB Admin: http://localhost:8000")
    print(f"   - API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main()