#!/bin/bash

# AI System Shutdown Script
# Stops all AI services gracefully

echo "🛑 Stopping AI System"
echo "===================="

# Stop all services
echo "🔄 Stopping services..."
docker-compose down

# Optional: Remove volumes (uncomment if needed)
# echo "🗑️  Removing volumes..."
# docker-compose down -v

echo ""
echo "✅ AI System stopped successfully!"
echo ""
echo "💡 To start again: ./docker/start-ai-system.sh"