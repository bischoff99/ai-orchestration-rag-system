#!/usr/bin/env python3
"""
Document ingestion script for RAG system
Supports batch processing and multiple collections
"""

import os
import argparse
import json
import time
from pathlib import Path
import sys
sys.path.append("/Users/andrejsp/ai/examples")
from unified_rag import UnifiedRAG
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Load configuration
with open("/Users/andrejsp/ai/configs/rag_config.json", "r") as f:
    config = json.load(f)

CHUNK_SIZE = config["rag_settings"]["chunk_size"]
CHUNK_OVERLAP = config["rag_settings"]["chunk_overlap"]
EMBEDDING_MODEL_NAME = config["embedding_model"]["name"]

def load_document(file_path):
    """Load document based on file extension"""
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if not file_extension and not os.path.basename(file_path).startswith('.'):
        try:
            return TextLoader(file_path).load()
        except Exception as e:
            print(f"⚠️ Could not load {file_path} as text: {e}")
            return []
    elif file_extension in [".txt", ".md"]:
        return TextLoader(file_path).load()
    elif file_extension == ".pdf":
        return PyPDFLoader(file_path).load()
    elif file_extension == ".docx":
        return Docx2txtLoader(file_path).load()
    else:
        print(f"❌ Unsupported file type: {file_extension if file_extension else 'No extension'}")
        return []

def split_documents(documents):
    """Split documents into chunks"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def ingest_documents(file_paths, collection_name, batch_size=128, use_ollama_embeddings=True):
    """Ingest documents into specified collection"""
    print(f"📚 Ingesting {len(file_paths)} documents into '{collection_name}'")
    print("=" * 60)
    
    start_time = time.time()
    
    # Initialize RAG database
    rag_db = UnifiedRAG(
        backend="chroma",
        collection_name=collection_name
    )
    
    all_chunks = []
    processed_files = 0
    failed_files = 0
    
    # Process files in batches
    for i in range(0, len(file_paths), batch_size):
        batch_files = file_paths[i:i + batch_size]
        print(f"\n🔄 Processing batch {i//batch_size + 1}/{(len(file_paths) + batch_size - 1)//batch_size}")
        
        batch_chunks = []
        for file_path in batch_files:
            print(f"📄 Processing: {os.path.basename(file_path)}")
            documents = load_document(file_path)
            
            if documents:
                chunks = split_documents(documents)
                if chunks:
                    batch_chunks.extend(chunks)
                    processed_files += 1
                    print(f"   ✅ {len(chunks)} chunks created")
                else:
                    print(f"   ⚠️ No chunks created")
                    failed_files += 1
            else:
                print(f"   ❌ Failed to load")
                failed_files += 1
        
        # Add batch to database
        if batch_chunks:
            # Convert Document objects to strings and metadata
            documents = [chunk.page_content for chunk in batch_chunks]
            metadatas = [chunk.metadata for chunk in batch_chunks]
            rag_db.add_documents(documents, metadatas)
            all_chunks.extend(batch_chunks)
            print(f"   📊 Added {len(batch_chunks)} chunks to database")
    
    duration = time.time() - start_time
    
    print(f"\n🎉 Ingestion Complete!")
    print(f"⏱️  Duration: {duration:.2f} seconds")
    print(f"📊 Statistics:")
    print(f"   - Files processed: {processed_files}")
    print(f"   - Files failed: {failed_files}")
    print(f"   - Total chunks: {len(all_chunks)}")
    print(f"   - Collection: {collection_name}")
    print(f"   - Processing speed: {len(all_chunks)/duration:.1f} chunks/sec")

def main():
    parser = argparse.ArgumentParser(description="Ingest documents into RAG system")
    parser.add_argument("--path", required=True, help="Path to documents directory")
    parser.add_argument("--collection", required=True, help="Collection name")
    parser.add_argument("--batch", type=int, default=128, help="Batch size for processing")
    parser.add_argument("--no-ollama", action="store_true", help="Use Sentence Transformers instead of Ollama")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"❌ Path does not exist: {args.path}")
        return
    
    # Find all supported files
    supported_extensions = {'.txt', '.md', '.pdf', '.docx'}
    file_paths = []
    
    for root, dirs, files in os.walk(args.path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.splitext(file)[1].lower() in supported_extensions or not os.path.splitext(file)[1]:
                file_paths.append(file_path)
    
    if not file_paths:
        print(f"❌ No supported files found in {args.path}")
        return
    
    print(f"🔍 Found {len(file_paths)} files to process")
    
    ingest_documents(
        file_paths, 
        args.collection, 
        args.batch, 
        not args.no_ollama
    )

if __name__ == "__main__":
    main()
