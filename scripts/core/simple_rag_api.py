#!/usr/bin/env python3
"""
Simple RAG API that works without n8n workflow issues
"""
import requests
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

def query_ollama(prompt, model="llama3.1:8b-instruct-q5_K_M"):
    """Query Ollama directly"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get('response', 'No response')
        else:
            return f"Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Connection error: {e}"

@app.route('/rag', methods=['POST'])
def rag_endpoint():
    """RAG endpoint that works like n8n webhook"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        # Simple RAG: Add context and query Ollama
        context = "You are a helpful AI assistant. Answer the following question based on your knowledge:"
        prompt = f"{context}\n\nQuestion: {query}\n\nAnswer:"
        
        response = query_ollama(prompt)
        
        return jsonify({
            "status": "success",
            "query": query,
            "response": response,
            "source": "simple_rag_api"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({"status": "ok", "service": "simple_rag_api"})

if __name__ == "__main__":
    print("🚀 Starting Simple RAG API...")
    print("📡 Endpoints:")
    print("   POST /rag - RAG query endpoint")
    print("   GET /health - Health check")
    print("🔗 Test with: curl -X POST http://localhost:5000/rag -H 'Content-Type: application/json' -d '{\"query\": \"What is AI?\"}'")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
