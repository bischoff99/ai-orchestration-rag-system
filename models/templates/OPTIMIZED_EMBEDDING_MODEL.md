# Optimized Embedding Model Template
Based on Context7 and Hugging Face best practices for embedding models.

## Recommended Parameters for Embedding Models
```dockerfile
FROM <embedding-model>
PARAMETER temperature 0.0          # Deterministic embeddings
PARAMETER num_ctx 8192            # Large context for embeddings
PARAMETER num_batch 256           # Optimized batch processing
PARAMETER repeat_penalty 1.0      # No repetition penalty needed
PARAMETER repeat_last_n 0         # No lookback for embeddings
PARAMETER top_k 1                 # Single best token
PARAMETER min_p 0.0               # No minimum probability threshold
```

## Key Optimizations
- **Zero temperature (0.0)**: Deterministic embedding generation
- **Large context (8192)**: Process longer documents
- **Optimized batch size (256)**: Efficient embedding computation
- **Minimal sampling parameters**: Focus on consistency over diversity
- **No repetition controls**: Not relevant for embeddings
