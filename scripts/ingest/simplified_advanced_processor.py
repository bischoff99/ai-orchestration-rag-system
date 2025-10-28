#!/usr/bin/env python3
"""
Simplified Advanced Document Processor
Works with existing setup and incorporates Context7 best practices
"""

import os
import sys
import time
import hashlib
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import mimetypes

# Add the examples directory to path
sys.path.append('/Users/andrejsp/ai/examples')

from rag_setup import RAGVectorDB

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
    
    def chunk_text(self, text: str, doc_type: str, metadata: Dict) -> List[Dict[str, Any]]:
        """Chunk text based on type and content"""
        if doc_type == 'code':
            return self._chunk_code(text, metadata)
        elif doc_type == 'markdown':
            return self._chunk_markdown(text, metadata)
        else:
            return self._chunk_generic(text, metadata)
    
    def _chunk_code(self, text: str, metadata: Dict) -> List[Dict[str, Any]]:
        """Chunk code files by functions, classes, and logical blocks"""
        chunks = []
        lines = text.split('\n')
        current_chunk = []
        current_size = 0
        
        for line in lines:
            # Check for logical boundaries
            if (line.strip().startswith(('def ', 'class ', 'import ', 'from ')) and 
                current_chunk and current_size > 100):
                # Save current chunk
                chunk_text = '\n'.join(current_chunk)
                chunks.append({
                    'content': chunk_text,
                    'metadata': {**metadata, 'chunk_type': 'code_block'}
                })
                current_chunk = [line]
                current_size = len(line)
            else:
                current_chunk.append(line)
                current_size += len(line) + 1
                
                if current_size > self.chunk_size:
                    chunk_text = '\n'.join(current_chunk)
                    chunks.append({
                        'content': chunk_text,
                        'metadata': {**metadata, 'chunk_type': 'code_block'}
                    })
                    current_chunk = []
                    current_size = 0
        
        # Add remaining content
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            chunks.append({
                'content': chunk_text,
                'metadata': {**metadata, 'chunk_type': 'code_block'}
            })
        
        return chunks
    
    def _chunk_markdown(self, text: str, metadata: Dict) -> List[Dict[str, Any]]:
        """Chunk markdown by headers and sections"""
        chunks = []
        sections = re.split(r'\n(#{1,6}\s)', text)
        
        current_section = ""
        for i, section in enumerate(sections):
            if section.strip().startswith('#'):
                if current_section:
                    chunks.append({
                        'content': current_section.strip(),
                        'metadata': {**metadata, 'chunk_type': 'markdown_section'}
                    })
                current_section = section
            else:
                current_section += section
                
                if len(current_section) > self.chunk_size:
                    chunks.append({
                        'content': current_section.strip(),
                        'metadata': {**metadata, 'chunk_type': 'markdown_section'}
                    })
                    current_section = ""
        
        if current_section.strip():
            chunks.append({
                'content': current_section.strip(),
                'metadata': {**metadata, 'chunk_type': 'markdown_section'}
            })
        
        return chunks
    
    def _chunk_generic(self, text: str, metadata: Dict) -> List[Dict[str, Any]]:
        """Generic chunking for unknown document types"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunks.append({
                'content': chunk_text,
                'metadata': {**metadata, 'chunk_type': 'generic'}
            })
        
        return chunks

class DocumentQualityScorer:
    """Score document quality for filtering and prioritization"""
    
    def __init__(self):
        self.quality_indicators = {
            'min_length': 50,
            'max_length': 50000,
            'min_sentences': 2,
            'max_repetition': 0.3
        }
    
    def score_document(self, content: str) -> Tuple[float, Dict[str, Any]]:
        """Score document quality and return score with details"""
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

class SimplifiedAdvancedProcessor:
    """Simplified advanced document processing pipeline"""
    
    def __init__(self, chroma_path: str = "/Users/andrejsp/ai/chroma_db"):
        self.chroma_path = chroma_path
        self.type_detector = DocumentTypeDetector()
        self.chunker = SemanticChunker()
        self.quality_scorer = DocumentQualityScorer()
        self.stats = ProcessingStats()
    
    def process_document(self, file_path: str, collection_name: str = "advanced_docs") -> ProcessingStats:
        """Process a single document with advanced pipeline"""
        start_time = time.time()
        
        try:
            # Detect document type
            doc_type = self.type_detector.detect_type(file_path)
            
            # Read document content
            content = self._read_document(file_path)
            if not content:
                self.stats.failed_documents += 1
                self.stats.errors.append(f"Failed to read {file_path}")
                return self.stats
            
            # Quality scoring
            quality_score, quality_details = self.quality_scorer.score_document(content)
            
            # Skip low-quality documents
            if quality_score < 0.3:
                self.stats.failed_documents += 1
                self.stats.errors.append(f"Low quality score for {file_path}: {quality_score:.3f}")
                return self.stats
            
            # Create metadata
            metadata = {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'doc_type': doc_type,
                'file_size': os.path.getsize(file_path),
                'quality_score': quality_score,
                'quality_details': quality_details,
                'processing_time': time.time()
            }
            
            # Chunk document
            chunks = self.chunker.chunk_text(content, doc_type, metadata)
            
            # Add to RAG system
            if chunks:
                self._add_to_rag_system(chunks, collection_name)
                self.stats.processed_documents += 1
                self.stats.total_chunks += len(chunks)
            
            self.stats.total_documents += 1
            
        except Exception as e:
            self.stats.failed_documents += 1
            self.stats.errors.append(f"Error processing {file_path}: {str(e)}")
        
        self.stats.processing_time = time.time() - start_time
        return self.stats
    
    def _read_document(self, file_path: str) -> str:
        """Read document content based on file type"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception:
                return ""
        except Exception:
            return ""
    
    def _add_to_rag_system(self, chunks: List[Dict[str, Any]], collection_name: str):
        """Add chunks to RAG system"""
        try:
            rag = RAGVectorDB(backend="chroma", collection_name=collection_name)
            
            # Convert chunks to documents
            documents = []
            for chunk in chunks:
                from langchain.schema import Document
                doc = Document(
                    page_content=chunk['content'],
                    metadata=chunk['metadata']
                )
                documents.append(doc)
            
            # Add to vector database
            rag.add_documents(documents)
            
        except Exception as e:
            self.stats.errors.append(f"RAG system error: {str(e)}")
    
    def process_directory(self, directory_path: str, collection_name: str = "advanced_docs") -> ProcessingStats:
        """Process all documents in a directory"""
        print(f"🔍 Processing directory: {directory_path}")
        
        # Find all files
        file_paths = []
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
                    file_paths.append(file_path)
        
        print(f"📄 Found {len(file_paths)} files to process")
        
        # Process each file
        for i, file_path in enumerate(file_paths, 1):
            print(f"📄 Processing {i}/{len(file_paths)}: {os.path.basename(file_path)}")
            self.process_document(file_path, collection_name)
        
        return self.stats

def main():
    """Test the simplified advanced processor"""
    processor = SimplifiedAdvancedProcessor()
    
    # Test with sample documents
    test_files = [
        "/Users/andrejsp/ai/sample_docs/python_guide.txt",
        "/Users/andrejsp/ai/sample_docs/machine_learning_basics.txt"
    ]
    
    print("🚀 Simplified Advanced Document Processing Test")
    print("=" * 50)
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"📄 Processing: {file_path}")
            stats = processor.process_document(file_path, "simplified_advanced")
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