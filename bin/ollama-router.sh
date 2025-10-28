#!/usr/bin/env zsh
set -euo pipefail
task="${1:-fast}"
prompt="${2:-}"
stream="${3:-true}"

case "$task" in
  fast)       model="gemma2:2b" ;;
  chat)       model="llama-assistant" ;;
  code)       model="qwen-coder32" ;;
  summarize)  model="mistral-summarizer" ;;
  analyze)    model="llama70b-analyst" ;;
  embed)      printf '{"model":"embedder","input":"%s"}' "$prompt" | curl -s http://localhost:11434/api/embed -d @- ; exit ;;
  *)          model="gemma2:2b" ;;
esac

if [ "$stream" = "true" ]; then
  curl -N http://localhost:11434/api/generate -d "{
    \"model\":\"$model\",
    \"prompt\":\"$prompt\",
    \"stream\":true,
    \"options\":{\"num_ctx\":4096,\"keep_alive\":\"30m\"}
  }"
else
  ollama run "$model" "$prompt"
fi
