#!/usr/bin/env python3
"""
Document Ingestion Script for RAG
Processes various document types and adds them to vector database
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Add the examples directory to path
sys.path.append('/Users/andrejsp/ai/examples')

from rag_setup import RAGVectorDB

def load_text_file(file_path: str) -> str:
    """Load text from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return ""

def load_markdown_file(file_path: str) -> str:
    """Load markdown file"""
    return load_text_file(file_path)

def load_pdf_file(file_path: str) -> str:
    """Load PDF file (requires PyPDF2)"""
    try:
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except ImportError:
        print("❌ PyPDF2 not installed. Install with: pip install PyPDF2")
        return ""
    except Exception as e:
        print(f"❌ Error reading PDF {file_path}: {e}")
        return ""

def load_docx_file(file_path: str) -> str:
    """Load DOCX file (requires python-docx)"""
    try:
        from docx import Document
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except ImportError:
        print("❌ python-docx not installed. Install with: pip install python-docx")
        return ""
    except Exception as e:
        print(f"❌ Error reading DOCX {file_path}: {e}")
        return ""

def load_document(file_path: str) -> str:
    """Load document based on file extension"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return ""
    
    extension = file_path.suffix.lower()
    
    # Handle files without extensions (like Modelfile)
    if not extension or file_path.name in ['Modelfile', 'Dockerfile', 'Makefile']:
        return load_text_file(str(file_path))
    elif extension == '.txt':
        return load_text_file(str(file_path))
    elif extension == '.md':
        return load_markdown_file(str(file_path))
    elif extension == '.pdf':
        return load_pdf_file(str(file_path))
    elif extension == '.docx':
        return load_docx_file(str(file_path))
    else:
        print(f"❌ Unsupported file type: {extension}")
        return ""

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """Split text into chunks"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings
            for i in range(end, max(start + chunk_size - 100, start), -1):
                if text[i] in '.!?':
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - chunk_overlap
        if start >= len(text):
            break
    
    return chunks

def create_metadata(file_path: str, chunk_index: int = 0) -> Dict[str, Any]:
    """Create metadata for document chunk"""
    file_path = Path(file_path)
    
    return {
        "file_name": file_path.name,
        "file_path": str(file_path),
        "file_type": file_path.suffix,
        "chunk_index": chunk_index,
        "file_size": file_path.stat().st_size if file_path.exists() else 0
    }

def ingest_documents(
    file_paths: List[str], 
    backend: str = "chroma",
    collection_name: str = "documents",
    chunk_size: int = 1000,
    chunk_overlap: int = 200
):
    """Ingest documents into vector database"""
    
    print(f"📚 Ingesting {len(file_paths)} documents into {backend}")
    print("=" * 50)
    
    # Initialize vector database
    vector_db = RAGVectorDB(backend=backend, collection_name=collection_name)
    
    all_documents = []
    all_metadatas = []
    
    for file_path in file_paths:
        print(f"\n📄 Processing: {file_path}")
        
        # Load document
        text = load_document(file_path)
        if not text:
            continue
        
        # Chunk text
        chunks = chunk_text(text, chunk_size, chunk_overlap)
        print(f"   📝 Created {len(chunks)} chunks")
        
        # Create metadata for each chunk
        for i, chunk in enumerate(chunks):
            metadata = create_metadata(file_path, i)
            all_documents.append(chunk)
            all_metadatas.append(metadata)
    
    # Add all documents to vector database
    if all_documents:
        vector_db.add_documents(all_documents, all_metadatas)
        print(f"\n✅ Successfully ingested {len(all_documents)} chunks from {len(file_paths)} files")
    else:
        print("\n❌ No documents were successfully loaded")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Ingest documents into RAG vector database")
    parser.add_argument("files", nargs="+", help="Files to ingest")
    parser.add_argument("--backend", choices=["chroma", "faiss"], default="chroma", help="Vector database backend")
    parser.add_argument("--collection", default="documents", help="Collection name")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Chunk size for text splitting")
    parser.add_argument("--chunk-overlap", type=int, default=200, help="Overlap between chunks")
    
    args = parser.parse_args()
    
    # Check if files exist
    valid_files = []
    for file_path in args.files:
        if os.path.exists(file_path):
            valid_files.append(file_path)
        else:
            print(f"❌ File not found: {file_path}")
    
    if not valid_files:
        print("❌ No valid files to process")
        return
    
    # Ingest documents
    ingest_documents(
        valid_files,
        backend=args.backend,
        collection_name=args.collection,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )

if __name__ == "__main__":
    main()