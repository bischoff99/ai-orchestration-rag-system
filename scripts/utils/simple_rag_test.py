#!/usr/bin/env python3
"""
Simple RAG test that works without external vector databases
"""
import requests
import json

def test_simple_ollama():
    """Test Ollama directly without n8n"""
    print("🤖 Testing Ollama directly...")
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.1:8b-instruct-q5_K_M",
                "prompt": "What is machine learning? Answer in 2 sentences.",
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Ollama Response: {result.get('response', 'No response')}")
            return True
        else:
            print(f"❌ Ollama Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ollama Connection Error: {e}")
        return False

def test_simple_webhook():
    """Test a simple webhook that just echoes back"""
    print("\n🔗 Testing simple webhook...")
    
    try:
        response = requests.post(
            "http://localhost:5678/webhook/rag-chat",
            json={"query": "Hello, this is a test"},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Webhook Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Simple RAG System Test")
    print("=" * 40)
    
    # Test Ollama directly
    ollama_works = test_simple_ollama()
    
    # Test webhook
    webhook_works = test_simple_webhook()
    
    print("\n📊 Results:")
    print(f"Ollama: {'✅ Working' if ollama_works else '❌ Failed'}")
    print(f"Webhook: {'✅ Working' if webhook_works else '❌ Failed'}")
    
    if ollama_works and webhook_works:
        print("\n🎉 System is working! The issue is in the n8n workflow configuration.")
    elif ollama_works:
        print("\n⚠️  Ollama works but webhook fails - n8n workflow issue")
    else:
        print("\n❌ Ollama not responding - check Ollama service")
