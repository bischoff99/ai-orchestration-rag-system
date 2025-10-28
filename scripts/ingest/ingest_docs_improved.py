#!/usr/bin/env python3
"""
Improved Document ingestion script for RAG system
Enhanced with better file filtering and error handling
"""

import os
import argparse
import json
import time
import mimetypes
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

# File filtering configuration
BINARY_EXTENSIONS = {
    '.exe', '.dll', '.so', '.dylib', '.bin', '.app', '.deb', '.rpm', '.msi',
    '.zip', '.tar', '.gz', '.rar', '.7z', '.iso', '.img', '.dmg',
    '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac', '.jpg', '.jpeg', 
    '.png', '.gif', '.bmp', '.tiff', '.ico', '.svg', '.psd', '.ai',
    '.db', '.sqlite', '.sqlite3', '.mdb', '.accdb'
}

SYSTEM_FILES = {
    '.DS_Store', '.Thumbs.db', '.desktop.ini', '.localized',
    '.zshenv', '.zshrc', '.bashrc', '.profile', '.bash_profile',
    'CodeResources', 'PkgInfo', 'Info.plist'
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit

def is_binary_file(file_path):
    """Check if file is binary using multiple methods"""
    try:
        # Check file extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext in BINARY_EXTENSIONS:
            return True
        
        # Check if it's a system file
        filename = os.path.basename(file_path)
        if filename in SYSTEM_FILES:
            return True
        
        # Check if it's an app bundle
        if file_path.endswith('.app') or '/.app/' in file_path:
            return True
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and mime_type.startswith('application/octet-stream'):
            return True
        
        # Check file size
        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            return True
        
        # Try to read first 1024 bytes to detect binary
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:  # Null bytes indicate binary
                return True
        
        return False
    except Exception:
        return True  # If we can't determine, assume binary

def should_skip_file(file_path):
    """Determine if file should be skipped"""
    filename = os.path.basename(file_path)
    
    # Skip hidden files (except .md files)
    if filename.startswith('.') and not filename.endswith('.md'):
        return True, "Hidden file"
    
    # Skip system files
    if filename in SYSTEM_FILES:
        return True, "System file"
    
    # Skip app bundles
    if file_path.endswith('.app') or '/.app/' in file_path:
        return True, "App bundle"
    
    # Skip binary files
    if is_binary_file(file_path):
        return True, "Binary file"
    
    # Skip very large files
    try:
        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            return True, f"File too large ({os.path.getsize(file_path) / (1024*1024):.1f}MB)"
    except OSError:
        return True, "Cannot access file"
    
    return False, None

def load_document(file_path):
    """Load document based on file extension with better error handling"""
    try:
        # Check if file should be skipped
        should_skip, reason = should_skip_file(file_path)
        if should_skip:
            print(f"   ⏭️ Skipping: {reason}")
            return []
        
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if not file_extension and not os.path.basename(file_path).startswith('.'):
            try:
                return TextLoader(file_path).load()
            except Exception as e:
                print(f"   ⚠️ Could not load as text: {e}")
                return []
        elif file_extension in [".txt", ".md"]:
            return TextLoader(file_path).load()
        elif file_extension == ".pdf":
            try:
                return PyPDFLoader(file_path).load()
            except Exception as e:
                print(f"   ⚠️ PDF load error: {e}")
                return []
        elif file_extension == ".docx":
            try:
                return Docx2txtLoader(file_path).load()
            except Exception as e:
                print(f"   ⚠️ DOCX load error: {e}")
                return []
        else:
            print(f"   ❌ Unsupported file type: {file_extension if file_extension else 'No extension'}")
            return []
    except Exception as e:
        print(f"   ❌ Error loading file: {e}")
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
    skipped_files = 0
    
    # Process files in batches
    for i in range(0, len(file_paths), batch_size):
        batch_files = file_paths[i:i + batch_size]
        print(f"\n🔄 Processing batch {i//batch_size + 1}/{(len(file_paths) + batch_size - 1)//batch_size}")
        
        batch_chunks = []
        for file_path in batch_files:
            print(f"📄 Processing: {os.path.basename(file_path)}")
            
            # Check if file should be skipped
            should_skip, reason = should_skip_file(file_path)
            if should_skip:
                print(f"   ⏭️ Skipping: {reason}")
                skipped_files += 1
                continue
            
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
    print(f"   - Files skipped: {skipped_files}")
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
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
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