#!/bin/bash

# AI System Startup Script
# Starts all AI services in the correct order

set -e

echo "🚀 Starting AI System"
echo "===================="

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p vector_db/chroma
mkdir -p vector_db/faiss
mkdir -p logs
mkdir -p benchmarks/reports

# Start core services first
echo "🔧 Starting core services..."
docker-compose up -d chromadb ollama

# Wait for core services to be ready
echo "⏳ Waiting for core services to be ready..."
sleep 10

# Start RAG API
echo "🤖 Starting RAG API..."
docker-compose up -d rag-api

# Wait for RAG API
sleep 5

# Start n8n
echo "🔄 Starting n8n workflows..."
docker-compose up -d n8n

# Wait for n8n
sleep 5

# Start monitoring and web interface
echo "📊 Starting monitoring and web interface..."
docker-compose up -d monitoring web-interface

echo ""
echo "✅ AI System started successfully!"
echo ""
echo "🌐 Services available at:"
echo "   - ChromaDB: http://localhost:8000"
echo "   - Ollama: http://localhost:11434"
echo "   - n8n: http://localhost:5678"
echo "   - RAG API: http://localhost:8001"
echo "   - Monitoring: http://localhost:3000"
echo "   - Web Interface: http://localhost:8080"
echo ""
echo "📋 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"