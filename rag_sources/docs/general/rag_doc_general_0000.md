# General Knowledge: Write a Python function to calculate fibonacci numbers

## Context
Technical knowledge and best practices.

## Response
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))  # Output: 55

## Metadata
- **Domain**: general
- **Source**: unknown
- **Quality Score**: 0.50
- **Created**: 2025-10-28T06:31:09.492359