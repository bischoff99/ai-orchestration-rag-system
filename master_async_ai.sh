#!/bin/zsh
# Master Async AI Operations Script (Fixed)
# Handles all phases with proper error handling and environment setup

set -e  # Exit on any error

echo "🚀 Starting Master Async AI Operations"
echo "======================================"

# Change to AI directory
cd /Users/andrejsp/ai

# Activate virtual environment
source venv/bin/activate

# Create necessary directories
mkdir -p vector_db/chroma vector_db/faiss benchmarks/reports benchmarks/logs fine_tuned_models

echo "📁 Environment setup complete"

# Phase 1: Document Ingestion (4 agents)
echo "📚 Phase 1: Document Ingestion"
echo "==============================="

# Agent 1: Personal Documents
echo "🚀 Starting: Personal Documents Ingestion"
python scripts/ingest/ingest_docs.py --path ~/Documents --collection personal_knowledge --batch 64 &
PID1=$!

# Agent 2: Downloads & Desktop
echo "🚀 Starting: Downloads Ingestion"
python scripts/ingest/ingest_docs.py --path ~/Downloads --collection downloads_knowledge --batch 64 &
PID2=$!

# Agent 3: Code Projects
echo "🚀 Starting: Code Projects Ingestion"
python scripts/ingest/ingest_docs.py --path ~/Code --collection code_knowledge --batch 32 &
PID3=$!

# Agent 4: Research Papers
echo "🚀 Starting: Research Papers Ingestion"
python scripts/ingest/ingest_docs.py --path ~/Research --collection research_knowledge --batch 16 &
PID4=$!

# Wait for Phase 1 to complete
wait $PID1 $PID2 $PID3 $PID4
echo "✅ Phase 1 Complete: Document Ingestion"

# Phase 2: Model Fine-tuning (3 agents)
echo "🎯 Phase 2: Model Fine-tuning"
echo "=============================="

# Agent 1: Code Specialist Model
echo "🚀 Starting: Code Specialist Fine-tuning"
python scripts/phases/fine_tune_qlora.py --base microsoft/DialoGPT-small --dataset ~/datasets/coding.jsonl --epochs 3 --lr 2e-4 --lora_rank 8 --output ./fine_tuned_models/code_specialist &
PID5=$!

# Agent 2: Technical Documentation Model
echo "🚀 Starting: Technical Specialist Fine-tuning"
python scripts/phases/fine_tune_qlora.py --base microsoft/DialoGPT-small --dataset ~/datasets/technical.jsonl --epochs 2 --lr 3e-4 --lora_rank 6 --output ./fine_tuned_models/technical_specialist &
PID6=$!

# Agent 3: AI/ML Specialist Model
echo "🚀 Starting: AI Specialist Fine-tuning"
python scripts/phases/fine_tune_qlora.py --base microsoft/DialoGPT-small --dataset ~/datasets/ai.jsonl --epochs 2 --lr 3e-4 --lora_rank 4 --output ./fine_tuned_models/ai_specialist &
PID7=$!

# Wait for Phase 2 to complete
wait $PID5 $PID6 $PID7
echo "✅ Phase 2 Complete: Model Fine-tuning"

# Phase 3: Evaluation & Monitoring (3 agents)
echo "📊 Phase 3: Evaluation & Monitoring"
echo "===================================="

# Agent 1: Evaluate All Collections
echo "🚀 Starting: RAG Evaluation"
python scripts/core/evaluate_rag.py --collections personal_knowledge,downloads_knowledge,code_knowledge,research_knowledge --metrics latency,accuracy,memory &
PID8=$!

# Agent 2: Performance Benchmark
echo "🚀 Starting: Daily Benchmark"
python scripts/utils/daily_benchmark.py &
PID9=$!

# Agent 3: System Health Check
echo "🚀 Starting: System Health Check"
vm_stat 1 | grep 'Pages active' && top -l 1 | grep "CPU usage" &
PID10=$!

# Wait for Phase 3 to complete
wait $PID8 $PID9 $PID10
echo "✅ Phase 3 Complete: Evaluation & Monitoring"

# Phase 4: Web Services (4 agents)
echo "🌐 Phase 4: Web Services"
echo "========================"

# Agent 1: Main Web Interface
echo "🚀 Starting: Main Web Interface (Port 8000)"
python scripts/utils/start_web_interfaces.py --port 8000 &
PID11=$!

# Agent 2: ChromaDB Admin
echo "🚀 Starting: ChromaDB Admin (Port 8001)"
python scripts/utils/start_chroma_server.py --port 8001 &
PID12=$!

# Agent 3: Qdrant Dashboard
echo "🚀 Starting: Qdrant Dashboard (Port 8002)"
python scripts/utils/start_qdrant_server.py --port 8002 &
PID13=$!

# Agent 4: API Endpoints
echo "🚀 Starting: API Endpoints (Port 8004)"
python scripts/core/simple_rag_api.py --port 8004 &
PID14=$!

echo "🎉 All phases started!"
echo "📊 Services running on ports 8000-8004"
echo "📊 Monitor progress with: ps aux | grep python"
echo "📊 Check logs in: /Users/andrejsp/ai/logs/"

# Keep script running to monitor services
echo "⏳ Monitoring services... (Press Ctrl+C to stop)"
wait
