#!/usr/bin/env python3
"""
RAG Document Converter
Converts training examples to properly formatted RAG documents following best practices
"""
import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RAGDocument:
    """RAG document with proper formatting and metadata"""
    id: str
    content: str
    metadata: Dict[str, Any]
    domain: str
    source: str
    quality_score: float
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return asdict(self)

class RAGDocumentConverter:
    """Converts training examples to RAG documents following best practices"""

    def __init__(self, base_dir: str = "/Users/andrejsp/ai"):
        self.base_dir = Path(base_dir)
        self.rag_sources_dir = self.base_dir / "rag_sources"
        self.docs_dir = self.rag_sources_dir / "docs"
        self.final_dir = self.base_dir / "datasets" / "final"

        # Create directories
        for dir_path in [self.docs_dir, self.rag_sources_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # RAG formatting templates based on best practices
        self.templates = {
            "instruction_response": """
# {domain_title}: {instruction}

## Context
{context}

## Response
{output}

## Metadata
- **Domain**: {domain}
- **Source**: {source}
- **Quality Score**: {quality_score:.2f}
- **Created**: {created_at}
""".strip(),

            "technical_guide": """
# {title}

## Overview
{instruction}

## Technical Details
{output}

## Key Points
{key_points}

## Domain: {domain}
""".strip(),

            "code_example": """
# Code Example: {instruction}

## Implementation
```python
{code_block}
```

## Explanation
{output}

## Domain: {domain}
## Quality: {quality_score:.2f}
""".strip()
        }

    def load_training_examples(self) -> List[Dict[str, Any]]:
        """Load training examples from final JSONL file"""
        examples = []
        jsonl_file = self.final_dir / "combined_training.jsonl"

        if not jsonl_file.exists():
            logger.warning(f"Training file not found: {jsonl_file}")
            return examples

        with open(jsonl_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        example = json.loads(line)
                        examples.append(example)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parsing line {line_num}: {e}")

        logger.info(f"Loaded {len(examples)} training examples from {jsonl_file}")
        return examples

    def format_document_content(self, example: Dict[str, Any]) -> str:
        """Format document content following RAG best practices"""

        instruction = example.get("instruction", "")
        output = example.get("output", "")
        domain = example.get("domain", "general")
        source = example.get("source", "unknown")
        quality_score = example.get("quality_score", 0.5)

        # Choose appropriate template based on content type
        template_key = self._determine_template_type(example)

        # Extract code blocks if present
        code_blocks = self._extract_code_blocks(output)

        # Generate key points for technical content
        key_points = self._generate_key_points(output, domain)

        # Format using template
        if template_key == "code_example" and code_blocks:
            content = self.templates[template_key].format(
                instruction=instruction,
                code_block=code_blocks[0],  # Use first code block
                output=self._clean_output_for_code(output),
                domain=domain,
                quality_score=quality_score
            )
        else:
            content = self.templates["instruction_response"].format(
                domain_title=self._get_domain_title(domain),
                instruction=instruction,
                context=self._generate_context(domain),
                output=output,
                domain=domain,
                source=source,
                quality_score=quality_score,
                created_at=datetime.now().isoformat()
            )

        return content.strip()

    def _determine_template_type(self, example: Dict[str, Any]) -> str:
        """Determine which template to use based on content analysis"""
        instruction = example.get("instruction", "").lower()
        output = example.get("output", "").lower()
        domain = example.get("domain", "")

        # Check for code-related content
        code_indicators = ["def ", "function", "class ", "import ", "```"]
        has_code = any(indicator in output for indicator in code_indicators)

        if has_code and domain in ["python", "code_generation"]:
            return "code_example"

        # Check for technical guide content
        if domain in ["docker", "machine_learning"] and len(output.split()) > 50:
            return "technical_guide"

        return "instruction_response"

    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from text"""
        code_blocks = []
        # Find all ``` code blocks
        import re
        pattern = r'```(?:\w+)?\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        code_blocks.extend(matches)

        # Also look for indented code blocks
        lines = text.split('\n')
        current_block = []
        in_block = False

        for line in lines:
            if line.startswith('    ') or line.startswith('\t'):
                current_block.append(line.strip())
                in_block = True
            elif in_block and current_block:
                code_blocks.append('\n'.join(current_block))
                current_block = []
                in_block = False

        if current_block:
            code_blocks.append('\n'.join(current_block))

        return code_blocks

    def _clean_output_for_code(self, output: str) -> str:
        """Clean output text when code blocks are present"""
        # Remove code blocks and keep explanations
        lines = output.split('\n')
        cleaned_lines = []

        in_code_block = False
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            elif not in_code_block and not line.startswith('    ') and not line.startswith('\t'):
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines).strip()

    def _generate_key_points(self, output: str, domain: str) -> str:
        """Generate key points from content"""
        sentences = re.split(r'[.!?]+', output)
        key_sentences = []

        # Simple heuristic: sentences with technical keywords
        tech_keywords = {
            "python": ["python", "function", "class", "import", "variable"],
            "docker": ["container", "image", "dockerfile", "volume", "network"],
            "machine_learning": ["model", "training", "algorithm", "data", "prediction"]
        }

        keywords = tech_keywords.get(domain, ["important", "key", "note"])

        for sentence in sentences[:5]:  # Limit to first 5 sentences
            sentence = sentence.strip()
            if len(sentence.split()) > 5 and any(kw in sentence.lower() for kw in keywords):
                key_sentences.append(f"- {sentence}")

        return '\n'.join(key_sentences) if key_sentences else "- Key technical concepts covered"

    def _get_domain_title(self, domain: str) -> str:
        """Get human-readable domain title"""
        titles = {
            "python": "Python Programming",
            "docker": "Docker Containerization",
            "machine_learning": "Machine Learning",
            "api_design": "API Design",
            "code_generation": "Code Generation",
            "general": "General Knowledge"
        }
        return titles.get(domain, domain.title())

    def _generate_context(self, domain: str) -> str:
        """Generate contextual information for the domain"""
        contexts = {
            "python": "Python is a high-level programming language known for its simplicity and readability.",
            "docker": "Docker is a platform for developing, shipping, and running applications in containers.",
            "machine_learning": "Machine learning involves algorithms that can learn patterns from data.",
            "api_design": "API design involves creating interfaces for software applications to communicate.",
            "code_generation": "Code generation automates the creation of source code from specifications."
        }
        return contexts.get(domain, "Technical knowledge and best practices.")

    def create_rag_documents(self, examples: List[Dict[str, Any]]) -> List[RAGDocument]:
        """Convert training examples to RAG documents"""
        documents = []

        for i, example in enumerate(examples):
            try:
                # Format content
                content = self.format_document_content(example)

                # Create document ID
                doc_id = f"rag_doc_{example.get('domain', 'general')}_{i:04d}"

                # Create metadata
                metadata = {
                    "instruction": example.get("instruction", ""),
                    "domain": example.get("domain", "general"),
                    "source": example.get("source", "synthetic"),
                    "quality_score": example.get("quality_score", 0.5),
                    "word_count": len(content.split()),
                    "has_code": "```" in content,
                    "created_at": datetime.now().isoformat()
                }

                # Create RAG document
                doc = RAGDocument(
                    id=doc_id,
                    content=content,
                    metadata=metadata,
                    domain=example.get("domain", "general"),
                    source=example.get("source", "synthetic"),
                    quality_score=example.get("quality_score", 0.5),
                    created_at=datetime.now().isoformat()
                )

                documents.append(doc)

            except Exception as e:
                logger.error(f"Error creating document for example {i}: {e}")

        logger.info(f"Created {len(documents)} RAG documents")
        return documents

    def save_documents_to_files(self, documents: List[RAGDocument]):
        """Save documents to individual files and combined JSON"""
        logger.info("💾 Saving RAG documents...")

        # Group by domain
        domain_docs = {}
        for doc in documents:
            domain = doc.domain
            if domain not in domain_docs:
                domain_docs[domain] = []
            domain_docs[domain].append(doc)

        # Save by domain
        for domain, docs in domain_docs.items():
            domain_dir = self.docs_dir / domain
            domain_dir.mkdir(exist_ok=True)

            # Save individual documents
            for doc in docs:
                filename = f"{doc.id}.md"
                filepath = domain_dir / filename

                with open(filepath, 'w') as f:
                    f.write(doc.content)

            # Save domain metadata
            metadata_file = domain_dir / "metadata.json"
            metadata = {
                "domain": domain,
                "total_documents": len(docs),
                "created_at": datetime.now().isoformat(),
                "documents": [doc.to_dict() for doc in docs]
            }

            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"✅ Saved {len(docs)} documents for domain '{domain}'")

        # Save combined index
        index_file = self.docs_dir / "document_index.json"
        index_data = {
            "total_documents": len(documents),
            "domains": list(domain_docs.keys()),
            "domain_counts": {domain: len(docs) for domain, docs in domain_docs.items()},
            "created_at": datetime.now().isoformat(),
            "documents": [doc.to_dict() for doc in documents]
        }

        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)

        logger.info(f"✅ Saved document index: {index_file}")

    def generate_statistics(self, documents: List[RAGDocument]) -> Dict[str, Any]:
        """Generate comprehensive statistics about the RAG documents"""
        stats = {
            "total_documents": len(documents),
            "domains": {},
            "sources": {},
            "quality_distribution": {
                "excellent": 0,  # 0.9+
                "good": 0,       # 0.7-0.9
                "acceptable": 0, # 0.6-0.7
                "poor": 0        # <0.6
            },
            "content_stats": {
                "avg_word_count": 0,
                "total_word_count": 0,
                "has_code_blocks": 0,
                "avg_quality_score": 0
            },
            "generated_at": datetime.now().isoformat()
        }

        total_words = 0
        total_quality = 0
        code_blocks_count = 0

        for doc in documents:
            # Domain stats
            domain = doc.domain
            stats["domains"][domain] = stats["domains"].get(domain, 0) + 1

            # Source stats
            source = doc.source
            stats["sources"][source] = stats["sources"].get(source, 0) + 1

            # Quality distribution
            quality = doc.quality_score
            if quality >= 0.9:
                stats["quality_distribution"]["excellent"] += 1
            elif quality >= 0.7:
                stats["quality_distribution"]["good"] += 1
            elif quality >= 0.6:
                stats["quality_distribution"]["acceptable"] += 1
            else:
                stats["quality_distribution"]["poor"] += 1

            # Content stats
            word_count = len(doc.content.split())
            total_words += word_count
            total_quality += quality

            if "```" in doc.content:
                code_blocks_count += 1

        # Calculate averages
        if documents:
            stats["content_stats"]["avg_word_count"] = total_words / len(documents)
            stats["content_stats"]["total_word_count"] = total_words
            stats["content_stats"]["has_code_blocks"] = code_blocks_count
            stats["content_stats"]["avg_quality_score"] = total_quality / len(documents)

        return stats

    def run_conversion(self) -> Dict[str, Any]:
        """Run the complete document conversion process"""
        logger.info("🚀 Starting RAG Document Conversion")
        logger.info("=" * 60)

        # Load training examples
        examples = self.load_training_examples()
        if not examples:
            logger.error("No training examples found. Run ingestion pipeline first.")
            return {}

        # Convert to RAG documents
        documents = self.create_rag_documents(examples)

        # Save documents
        self.save_documents_to_files(documents)

        # Generate statistics
        stats = self.generate_statistics(documents)

        # Save statistics
        stats_file = self.docs_dir / "conversion_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)

        logger.info("=" * 60)
        logger.info("📊 RAG Document Conversion Statistics:")
        logger.info(f"   Total Documents: {stats['total_documents']}")
        logger.info(f"   Domains: {', '.join(f'{k}: {v}' for k, v in stats['domains'].items())}")
        logger.info(f"   Quality Distribution: {stats['quality_distribution']}")
        logger.info(f"   Content Stats: Avg words: {stats['content_stats']['avg_word_count']:.1f}, Code blocks: {stats['content_stats']['has_code_blocks']}")
        logger.info(f"   Statistics saved to: {stats_file}")

        return {
            "stats": stats,
            "documents_count": len(documents),
            "output_dirs": {
                "docs": str(self.docs_dir),
                "stats": str(stats_file)
            }
        }

def main():
    """Main function to run the RAG document conversion"""
    converter = RAGDocumentConverter()
    results = converter.run_conversion()

    if results:
        print("\n🎉 RAG Document Conversion Complete!")
        print(f"Generated {results['documents_count']} formatted documents")
        print(f"Documents saved to: {results['output_dirs']['docs']}")
        print(f"Statistics: {results['output_dirs']['stats']}")
    else:
        print("\n❌ RAG Document Conversion Failed!")

    return results

if __name__ == "__main__":
    main()