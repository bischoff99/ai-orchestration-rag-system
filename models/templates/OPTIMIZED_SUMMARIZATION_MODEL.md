# Optimized Summarization Model Template
Based on Context7 and Hugging Face best practices for summarization models.

## Recommended Parameters for Summarization Models
```dockerfile
FROM <base-model>
PARAMETER temperature 0.3          # Slightly higher for natural summaries
PARAMETER top_p 0.9               # High for diverse summarization
PARAMETER num_ctx 8192            # Large context for long documents
PARAMETER num_batch 256           # Optimized batch size
PARAMETER repeat_penalty 1.1      # Prevent repetitive summaries
PARAMETER repeat_last_n 64        # Lookback window
PARAMETER top_k 40                # Balanced sampling
PARAMETER min_p 0.05              # Quality threshold
PARAMETER num_predict 1024        # Appropriate summary length
SYSTEM You are a summarization expert. Create concise, accurate summaries that capture key points and essential information. Focus on clarity and coherence.
```

## Key Optimizations
- **Moderate temperature (0.3)**: Natural, readable summaries
- **Large context (8192)**: Process long documents
- **Controlled prediction length (1024)**: Appropriate summary size
- **Enhanced system prompt**: Focus on clarity and coherence
- **Balanced sampling**: Quality over quantity
