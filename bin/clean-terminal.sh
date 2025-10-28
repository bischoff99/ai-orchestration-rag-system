#!/usr/bin/env zsh
# Terminal Cleanup Script
# Run this to clean up terminal startup issues

echo "🧹 Cleaning up terminal environment..."

# Kill any background ollama processes
pkill -f ollama 2>/dev/null || true

# Kill any background curl processes
pkill -f "curl.*ollama" 2>/dev/null || true

# Clear any background jobs
jobs -p | xargs -r kill 2>/dev/null || true

# Clear terminal
clear

echo "✅ Terminal cleanup complete"
echo "💡 Tip: Use 'ollama-manager.sh start' when you need ollama services"
