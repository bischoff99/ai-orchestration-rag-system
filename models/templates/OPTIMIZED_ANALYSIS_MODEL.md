# Optimized Analysis Model Template
Based on Context7 and Hugging Face best practices for analytical and reasoning models.

## Recommended Parameters for Analysis Models
```dockerfile
FROM <base-model>
PARAMETER temperature 0.2          # Balanced creativity/coherence
PARAMETER top_p 0.92              # High for diverse insights
PARAMETER num_ctx 16384           # Large context for complex analysis
PARAMETER num_batch 512           # Large batch for 70B+ models
PARAMETER repeat_penalty 1.1      # Prevent repetitive analysis
PARAMETER repeat_last_n 64        # Lookback window
PARAMETER top_k 40                # Balanced sampling
PARAMETER min_p 0.05              # Quality threshold
PARAMETER num_predict 4096        # Extended analysis length
SYSTEM You are a data analyst and strategic thinker. Provide deep insights, identify patterns, and offer well-reasoned analytical perspectives with supporting evidence and actionable recommendations.
```

## Key Optimizations
- **Moderate temperature (0.2)**: Balanced creativity and coherence
- **Very large context (16384)**: Handle complex datasets and analysis
- **Large batch size (512)**: Optimized for 70B+ parameter models
- **Extended prediction length**: Complete analytical reports
- **Enhanced system prompt**: Focus on evidence-based insights
