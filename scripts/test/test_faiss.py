#!/usr/bin/env python3
"""Simple test script for FAISS ingestion"""

import os
import sys
sys.path.append('/Users/andrejsp/ai')

print("Testing FAISS import...")
try:
    import faiss
    print("✅ FAISS imported successfully")
except ImportError as e:
    print(f"❌ FAISS import failed: {e}")
    sys.exit(1)

print("Testing sentence transformers...")
try:
    from sentence_transformers import SentenceTransformer
    print("✅ Sentence transformers imported successfully")
except ImportError as e:
    print(f"❌ Sentence transformers import failed: {e}")
    sys.exit(1)

print("Testing basic functionality...")
try:
    # Test basic FAISS
    dim = 384  # sentence-transformers dimension
    index = faiss.IndexFlatIP(dim)
    print(f"✅ FAISS index created with dimension {dim}")

    # Test sentence transformer (but don't load full model yet)
    print("✅ All imports working")

except Exception as e:
    print(f"❌ Basic functionality test failed: {e}")
    sys.exit(1)

print("🎉 All tests passed! Ready for ingestion.")
