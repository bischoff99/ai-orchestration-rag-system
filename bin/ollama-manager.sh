#!/usr/bin/env zsh
# Ollama Management Script
# Use this to start/stop ollama services when needed

case "${1:-status}" in
  start)
    echo "🚀 Starting Ollama services..."
    ollama serve &
    sleep 2
    echo "✅ Ollama services started"
    ;;
  stop)
    echo "🛑 Stopping Ollama services..."
    pkill -f ollama
    echo "✅ Ollama services stopped"
    ;;
  status)
    echo "📊 Ollama service status:"
    ps aux | grep ollama | grep -v grep || echo "No ollama processes running"
    ;;
  clean)
    echo "🧹 Cleaning up ollama processes..."
    pkill -f ollama
    sleep 1
    echo "✅ Cleanup complete"
    ;;
  *)
    echo "Usage: $0 {start|stop|status|clean}"
    ;;
esac
