#!/usr/bin/env python3
"""
Advanced Document Processing Pipeline
Incorporates Context7 best practices for maximized document ingestion
"""

import os
import sys
import time
import hashlib
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import mimetypes
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# Document processing libraries
from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, Docx2txtLoader, 
    UnstructuredHTMLLoader, UnstructuredMarkdownLoader,
    UnstructuredPowerPointLoader, UnstructuredExcelLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import chromadb
from chromadb.utils import embedding_functions

# Add the examples directory to path
sys.path.append('/Users/andrejsp/ai/examples')

@dataclass
class ProcessingStats:
    """Track processing statistics"""
    total_documents: int = 0
    processed_documents: int = 0
    failed_documents: int = 0
    total_chunks: int = 0
    processing_time: float = 0.0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class DocumentTypeDetector:
    """Detect and classify document types for specialized processing"""
    
    def __init__(self):
        self.type_patterns = {
            'code': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.php'],
            'markdown': ['.md', '.markdown'],
            'document': ['.pdf', '.docx', '.doc', '.txt'],
            'presentation': ['.pptx', '.ppt'],
            'spreadsheet': ['.xlsx', '.xls', '.csv'],
            'web': ['.html', '.htm'],
            'config': ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg'],
            'data': ['.xml', '.rss', '.atom']
        }
    
    def detect_type(self, file_path: str) -> str:
        """Detect document type based on file extension and content"""
        ext = Path(file_path).suffix.lower()
        
        # Check by extension first
        for doc_type, extensions in self.type_patterns.items():
            if ext in extensions:
                return doc_type
        
        # Fallback to MIME type detection
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            if 'pdf' in mime_type:
                return 'document'
            elif 'text' in mime_type:
                return 'document'
            elif 'html' in mime_type:
                return 'web'
        
        return 'unknown'

class SemanticChunker:
    """Advanced semantic chunking based on Context7 techniques"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.sentence_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
    
    def chunk_document(self, document: Document, doc_type: str) -> List[Document]:
        """Chunk document based on type and content"""
        content = document.page_content
        
        # Type-specific chunking strategies
        if doc_type == 'code':
            return self._chunk_code(content, document.metadata)
        elif doc_type == 'markdown':
            return self._chunk_markdown(content, document.metadata)
        elif doc_type == 'document':
            return self._chunk_document_text(content, document.metadata)
        else:
            return self._chunk_generic(content, document.metadata)
    
    def _chunk_code(self, content: str, metadata: Dict) -> List[Document]:
        """Chunk code files by functions, classes, and logical blocks"""
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_size = 0
        
        for line in lines:
            # Check for logical boundaries
            if (line.strip().startswith(('def ', 'class ', 'import ', 'from ')) and 
                current_chunk and current_size > 100):
                # Save current chunk
                chunk_text = '\n'.join(current_chunk)
                chunks.append(Document(
                    page_content=chunk_text,
                    metadata={**metadata, 'chunk_type': 'code_block'}
                ))
                current_chunk = [line]
                current_size = len(line)
            else:
                current_chunk.append(line)
                current_size += len(line) + 1
                
                if current_size > self.chunk_size:
                    chunk_text = '\n'.join(current_chunk)
                    chunks.append(Document(
                        page_content=chunk_text,
                        metadata={**metadata, 'chunk_type': 'code_block'}
                    ))
                    current_chunk = []
                    current_size = 0
        
        # Add remaining content
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            chunks.append(Document(
                page_content=chunk_text,
                metadata={**metadata, 'chunk_type': 'code_block'}
            ))
        
        return chunks
    
    def _chunk_markdown(self, content: str, metadata: Dict) -> List[Document]:
        """Chunk markdown by headers and sections"""
        chunks = []
        sections = re.split(r'\n(#{1,6}\s)', content)
        
        current_section = ""
        for i, section in enumerate(sections):
            if section.strip().startswith('#'):
                if current_section:
                    chunks.append(Document(
                        page_content=current_section.strip(),
                        metadata={**metadata, 'chunk_type': 'markdown_section'}
                    ))
                current_section = section
            else:
                current_section += section
                
                if len(current_section) > self.chunk_size:
                    chunks.append(Document(
                        page_content=current_section.strip(),
                        metadata={**metadata, 'chunk_type': 'markdown_section'}
                    ))
                    current_section = ""
        
        if current_section.strip():
            chunks.append(Document(
                page_content=current_section.strip(),
                metadata={**metadata, 'chunk_type': 'markdown_section'}
            ))
        
        return chunks
    
    def _chunk_document_text(self, content: str, metadata: Dict) -> List[Document]:
        """Chunk regular documents using sentence splitting"""
        return self.sentence_splitter.split_documents([Document(
            page_content=content,
            metadata=metadata
        )])
    
    def _chunk_generic(self, content: str, metadata: Dict) -> List[Document]:
        """Generic chunking for unknown document types"""
        return self.sentence_splitter.split_documents([Document(
            page_content=content,
            metadata=metadata
        )])

class DocumentQualityScorer:
    """Score document quality for filtering and prioritization"""
    
    def __init__(self):
        self.quality_indicators = {
            'min_length': 50,
            'max_length': 50000,
            'min_sentences': 2,
            'max_repetition': 0.3
        }
    
    def score_document(self, document: Document) -> Tuple[float, Dict[str, Any]]:
        """Score document quality and return score with details"""
        content = document.page_content
        score = 1.0
        details = {}
        
        # Length check
        if len(content) < self.quality_indicators['min_length']:
            score *= 0.3
            details['too_short'] = True
        elif len(content) > self.quality_indicators['max_length']:
            score *= 0.8
            details['too_long'] = True
        
        # Sentence count
        sentences = len(re.findall(r'[.!?]+', content))
        if sentences < self.quality_indicators['min_sentences']:
            score *= 0.5
            details['too_few_sentences'] = True
        
        # Repetition check
        words = content.lower().split()
        if len(words) > 0:
            unique_words = len(set(words))
            repetition_ratio = 1 - (unique_words / len(words))
            if repetition_ratio > self.quality_indicators['max_repetition']:
                score *= 0.4
                details['high_repetition'] = repetition_ratio
        
        # Content quality indicators
        if any(keyword in content.lower() for keyword in ['error', 'exception', 'failed', 'null', 'undefined']):
            score *= 0.9
            details['contains_errors'] = True
        
        # Positive indicators
        if any(keyword in content.lower() for keyword in ['example', 'tutorial', 'guide', 'documentation']):
            score *= 1.1
            details['educational_content'] = True
        
        return min(score, 1.0), details

class AdvancedDocumentProcessor:
    """Main document processing pipeline with advanced features"""
    
    def __init__(self, chroma_path: str = "/Users/andrejsp/ai/chroma_db"):
        self.chroma_path = chroma_path
        self.type_detector = DocumentTypeDetector()
        self.chunker = SemanticChunker()
        self.quality_scorer = DocumentQualityScorer()
        self.stats = ProcessingStats()
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=chroma_path)
        
        # Document loaders by type
        self.loaders = {
            'document': [PyPDFLoader, Docx2txtLoader, TextLoader],
            'web': [UnstructuredHTMLLoader],
            'markdown': [UnstructuredMarkdownLoader],
            'presentation': [UnstructuredPowerPointLoader],
            'spreadsheet': [UnstructuredExcelLoader],
            'code': [TextLoader],
            'config': [TextLoader],
            'data': [TextLoader]
        }
    
    def process_document(self, file_path: str, collection_name: str = "unified_docs") -> ProcessingStats:
        """Process a single document with advanced pipeline"""
        start_time = time.time()
        
        try:
            # Detect document type
            doc_type = self.type_detector.detect_type(file_path)
            
            # Load document
            documents = self._load_document(file_path, doc_type)
            if not documents:
                self.stats.failed_documents += 1
                self.stats.errors.append(f"Failed to load {file_path}")
                return self.stats
            
            # Process each document
            all_chunks = []
            for doc in documents:
                # Add metadata
                doc.metadata.update({
                    'file_path': file_path,
                    'file_name': os.path.basename(file_path),
                    'doc_type': doc_type,
                    'file_size': os.path.getsize(file_path),
                    'processing_time': time.time()
                })
                
                # Quality scoring
                quality_score, quality_details = self.quality_scorer.score_document(doc)
                doc.metadata['quality_score'] = quality_score
                doc.metadata['quality_details'] = quality_details
                
                # Skip low-quality documents
                if quality_score < 0.3:
                    self.stats.failed_documents += 1
                    continue
                
                # Chunk document
                chunks = self.chunker.chunk_document(doc, doc_type)
                all_chunks.extend(chunks)
            
            # Add to ChromaDB
            if all_chunks:
                self._add_to_chromadb(all_chunks, collection_name)
                self.stats.processed_documents += 1
                self.stats.total_chunks += len(all_chunks)
            
            self.stats.total_documents += 1
            
        except Exception as e:
            self.stats.failed_documents += 1
            self.stats.errors.append(f"Error processing {file_path}: {str(e)}")
        
        self.stats.processing_time = time.time() - start_time
        return self.stats
    
    def _load_document(self, file_path: str, doc_type: str) -> List[Document]:
        """Load document using appropriate loader"""
        if doc_type not in self.loaders:
            doc_type = 'document'  # Fallback
        
        for loader_class in self.loaders[doc_type]:
            try:
                loader = loader_class(file_path)
                return loader.load()
            except Exception:
                continue
        
        return []
    
    def _add_to_chromadb(self, chunks: List[Document], collection_name: str):
        """Add chunks to ChromaDB with metadata"""
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
            )
            
            # Prepare data for ChromaDB
            documents = [chunk.page_content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            ids = [f"{hashlib.md5(chunk.page_content.encode()).hexdigest()}_{i}" 
                   for i, chunk in enumerate(chunks)]
            
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
        except Exception as e:
            self.stats.errors.append(f"ChromaDB error: {str(e)}")
    
    async def process_batch_async(self, file_paths: List[str], collection_name: str = "unified_docs") -> ProcessingStats:
        """Process multiple documents asynchronously"""
        start_time = time.time()
        
        # Create tasks for parallel processing
        tasks = []
        for file_path in file_paths:
            task = asyncio.create_task(self._process_document_async(file_path, collection_name))
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        for result in results:
            if isinstance(result, ProcessingStats):
                self.stats.total_documents += result.total_documents
                self.stats.processed_documents += result.processed_documents
                self.stats.failed_documents += result.failed_documents
                self.stats.total_chunks += result.total_chunks
                self.stats.errors.extend(result.errors)
        
        self.stats.processing_time = time.time() - start_time
        return self.stats
    
    async def _process_document_async(self, file_path: str, collection_name: str) -> ProcessingStats:
        """Async wrapper for document processing"""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(
                executor, self.process_document, file_path, collection_name
            )

def main():
    """Test the advanced document processor"""
    processor = AdvancedDocumentProcessor()
    
    # Test with sample documents
    test_files = [
        "/Users/andrejsp/ai/sample_docs/python_guide.txt",
        "/Users/andrejsp/ai/sample_docs/machine_learning_basics.txt"
    ]
    
    print("🚀 Advanced Document Processing Test")
    print("=" * 40)
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"📄 Processing: {file_path}")
            stats = processor.process_document(file_path, "advanced_docs")
            print(f"   ✅ Processed: {stats.processed_documents} documents")
            print(f"   📊 Chunks: {stats.total_chunks}")
            print(f"   ⏱️  Time: {stats.processing_time:.2f}s")
            if stats.errors:
                print(f"   ❌ Errors: {len(stats.errors)}")
        else:
            print(f"❌ File not found: {file_path}")
    
    print(f"\n🎉 Processing Complete!")
    print(f"📊 Total Stats:")
    print(f"   - Documents: {processor.stats.total_documents}")
    print(f"   - Processed: {processor.stats.processed_documents}")
    print(f"   - Failed: {processor.stats.failed_documents}")
    print(f"   - Chunks: {processor.stats.total_chunks}")

if __name__ == "__main__":
    main()