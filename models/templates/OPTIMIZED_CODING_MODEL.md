# Optimized Coding Model Template
Based on Context7 and Hugging Face best practices for code generation models.

## Recommended Parameters for Coding Models
```dockerfile
FROM <base-model>
PARAMETER temperature 0.1          # Lower for more deterministic code
PARAMETER top_p 0.95              # High for code diversity
PARAMETER num_ctx 8192            # Larger context for complex code
PARAMETER num_batch 256           # Optimized batch size
PARAMETER repeat_penalty 1.1      # Prevent code repetition
PARAMETER repeat_last_n 64        # Lookback window
PARAMETER top_k 40                # Balanced sampling
PARAMETER min_p 0.05              # Quality threshold
PARAMETER num_predict 2048        # Max code length
SYSTEM You are an expert programming assistant. Provide clear, efficient, and well-documented code solutions with best practices and optimization techniques.
```

## Key Optimizations
- **Lower temperature (0.1)**: More deterministic code generation
- **Higher context (8192)**: Handle complex codebases
- **Larger batch size (256)**: Better GPU utilization
- **Controlled repetition**: Prevents code loops
- **Extended prediction length**: Complete functions/classes
