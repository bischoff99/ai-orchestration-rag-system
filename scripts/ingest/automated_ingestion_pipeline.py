#!/usr/bin/env python3
"""
Automated Dataset Ingestion Pipeline
Processes existing sample docs, generates synthetic data, and creates quality training datasets
"""
import os
import json
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Tuple, Set
from dataclasses import dataclass
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TrainingExample:
    """Standard training example format"""
    instruction: str
    input: str
    output: str
    source: str
    domain: str
    quality_score: float

class AutomatedIngestionPipeline:
    """Complete pipeline for dataset ingestion and processing"""

    def __init__(self, base_dir: str = "/Users/andrejsp/ai"):
        self.base_dir = Path(base_dir)
        self.sample_docs_dir = self.base_dir / "sample_docs"
        self.datasets_dir = self.base_dir / "datasets"
        self.raw_dir = self.datasets_dir / "raw"
        self.processed_dir = self.datasets_dir / "processed"
        self.final_dir = self.datasets_dir / "final"

        # Create directories
        for dir_path in [self.raw_dir, self.processed_dir, self.final_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Existing training data
        self.existing_examples = self.load_existing_examples()

        # Quality thresholds (more reasonable)
        self.quality_thresholds = {
            "min_instruction_length": 8,
            "min_output_length": 15,
            "max_total_length": 2048,
            "min_quality_score": 0.3  # Lower threshold to accept more examples
        }

    def load_existing_examples(self) -> List[TrainingExample]:
        """Load existing training examples from datasets directory"""
        existing_files = [
            self.datasets_dir / "code_training.json",
            self.datasets_dir / "technical_training.json",
            self.datasets_dir / "workflow_training.json"
        ]

        examples = []
        for file_path in existing_files:
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for item in data:
                                example = TrainingExample(
                                    instruction=item.get("instruction", ""),
                                    input=item.get("input", ""),
                                    output=item.get("output", ""),
                                    source=item.get("source", "existing"),
                                    domain=item.get("domain", "general"),
                                    quality_score=item.get("quality_score", 0.8)
                                )
                                examples.append(example)
                        logger.info(f"Loaded {len(data) if isinstance(data, list) else 0} examples from {file_path}")
                except Exception as e:
                    logger.warning(f"Error loading {file_path}: {e}")

        logger.info(f"Total existing examples: {len(examples)}")
        return examples

    def process_sample_docs(self) -> List[TrainingExample]:
        """Process existing sample documents into training examples"""
        logger.info("🎯 Processing sample documents...")

        examples = []
        doc_files = {
            "docker_guide.txt": "docker",
            "machine_learning.txt": "machine_learning",
            "machine_learning_basics.txt": "machine_learning",
            "python_guide.txt": "python"
        }

        for filename, domain in doc_files.items():
            file_path = self.sample_docs_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()

                    # Split into sections and generate examples
                    sections = self.split_into_sections(content, domain)
                    for section in sections:
                        example = self.create_example_from_section(section, domain)
                        if example and self.passes_quality_filter(example):
                            examples.append(example)

                    logger.info(f"✅ Processed {filename}: {len(sections)} sections")

                except Exception as e:
                    logger.error(f"❌ Error processing {filename}: {e}")

        return examples

    def split_into_sections(self, content: str, domain: str) -> List[Dict[str, Any]]:
        """Split document content into meaningful sections"""
        sections = []

        # Split by common section headers
        lines = content.split('\n')
        current_section = {"title": "", "content": "", "domain": domain}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line looks like a section header
            if self.is_section_header(line):
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {
                    "title": line,
                    "content": "",
                    "domain": domain
                }
            else:
                current_section["content"] += line + " "

        # Add the last section
        if current_section["content"]:
            sections.append(current_section)

        return sections

    def is_section_header(self, line: str) -> bool:
        """Check if a line looks like a section header"""
        # Common patterns for headers
        if len(line) > 50:  # Too long to be a header
            return False

        # Check for common header patterns
        header_patterns = [
            r'^[A-Z][^.!?]*:$',  # Title Case:
            r'^\d+\.',  # 1. Numbered
            r'^###',  # ### Markdown
            r'^##',  # ## Markdown
            r'^#',  # # Markdown
            r'^[A-Z\s]{10,}$',  # ALL CAPS
        ]

        for pattern in header_patterns:
            if re.match(pattern, line):
                return True

        return False

    def create_example_from_section(self, section: Dict[str, Any], domain: str) -> TrainingExample:
        """Create a training example from a document section"""
        title = section["title"]
        content = section["content"].strip()

        if len(content.split()) < 20:  # Too short
            return None

        # Generate instruction based on domain and content
        instruction_templates = {
            "docker": [
                f"Explain how to use {title.lower()} in Docker",
                f"What is {title.lower()} and how does it work in Docker?",
                f"Provide a guide for {title.lower()} in containerization"
            ],
            "machine_learning": [
                f"Explain the concept of {title.lower()} in machine learning",
                f"What is {title.lower()} and why is it important in ML?",
                f"Describe how {title.lower()} works in machine learning"
            ],
            "python": [
                f"Explain {title.lower()} in Python programming",
                f"What is {title.lower()} and how is it used in Python?",
                f"Provide an example of {title.lower()} in Python"
            ]
        }

        templates = instruction_templates.get(domain, [
            f"Explain {title.lower()}",
            f"What is {title.lower()}?",
            f"Describe {title.lower()}"
        ])

        instruction = templates[hash(content) % len(templates)]

        # Calculate quality score
        quality_score = self.calculate_quality_score({
            "instruction": instruction,
            "output": content
        })

        return TrainingExample(
            instruction=instruction,
            input="",
            output=content,
            source="sample_docs",
            domain=domain,
            quality_score=quality_score
        )

    def generate_synthetic_examples(self, target_count: int = 1000) -> List[TrainingExample]:
        """Generate synthetic training examples using templates and existing knowledge"""
        logger.info(f"🎯 Generating {target_count} synthetic examples...")

        examples = []
        domains = ["python", "docker", "machine_learning", "api_design", "code_generation"]

        # Template-based generation
        templates = {
            "python": [
                {
                    "instruction": "Write a Python function that {task}",
                    "output": "Here's a Python function that {task}:\n\n```python\ndef {function_name}({params}):\n    {implementation}\n    return {return_value}\n```\n\nThis function {explanation}."
                },
                {
                    "instruction": "Explain how {concept} works in Python",
                    "output": "{concept} in Python is {explanation}. {examples} {use_cases}"
                }
            ],
            "docker": [
                {
                    "instruction": "Create a Dockerfile for {application_type}",
                    "output": "Here's a Dockerfile for {application_type}:\n\n```dockerfile\nFROM {base_image}\nWORKDIR {workdir}\nCOPY {files} .\nRUN {commands}\nEXPOSE {ports}\nCMD {command}\n```\n\nThis Dockerfile {explanation}."
                },
                {
                    "instruction": "How do you {docker_task} with Docker?",
                    "output": "To {docker_task} with Docker: {steps} {commands} {best_practices}"
                }
            ],
            "machine_learning": [
                {
                    "instruction": "Explain {ml_concept} and its applications",
                    "output": "{ml_concept} is {definition}. It works by {mechanism}. Common applications include {applications}. {examples}"
                },
                {
                    "instruction": "How does {algorithm} work in machine learning?",
                    "output": "{algorithm} is a {type} algorithm that {description}. The algorithm {steps}. It's commonly used for {use_cases}."
                }
            ]
        }

        # Fill in templates with specific content
        for domain in domains:
            domain_templates = templates.get(domain, templates["python"])
            domain_examples = target_count // len(domains)

            for i in range(domain_examples):
                template = domain_templates[i % len(domain_templates)]

                # Fill template with specific values (add uniqueness)
                filled = self.fill_template(template, domain, i)

                quality_score = self.calculate_quality_score(filled)

                # Create example regardless of quality score for now, filter later
                example = TrainingExample(
                    instruction=filled["instruction"],
                    input=filled.get("input", ""),
                    output=filled["output"],
                    source="synthetic",
                    domain=domain,
                    quality_score=quality_score
                )
                examples.append(example)

        logger.info(f"✅ Generated {len(examples)} synthetic examples")
        return examples

    def fill_template(self, template: Dict[str, Any], domain: str, index: int = 0) -> Dict[str, Any]:
        """Fill template with domain-specific content"""
        fillers = {
            "python": {
                "task": ["sorts a list", "calculates fibonacci numbers", "validates email addresses", "parses JSON data"],
                "function_name": ["sort_list", "fibonacci", "validate_email", "parse_json"],
                "params": ["data", "n", "email", "json_string"],
                "implementation": ["return sorted(data)", "return fib(n-1) + fib(n-2) if n > 1 else n", "return bool(re.match(pattern, email))", "return json.loads(json_string)"],
                "return_value": ["sorted_data", "result", "is_valid", "parsed_data"],
                "concept": ["list comprehensions", "decorators", "generators", "context managers"],
                "explanation": ["allows you to create lists in a concise way", "modify function behavior without changing the function", "yield values on demand", "manage resources automatically"]
            },
            "docker": {
                "application_type": ["Python Flask app", "Node.js API", "React frontend", "Django application"],
                "base_image": ["python:3.9-slim", "node:18-alpine", "nginx:alpine", "python:3.9"],
                "workdir": ["/app", "/usr/src/app", "/var/www", "/code"],
                "files": ["requirements.txt .", "package*.json .", "dist .", "manage.py ."],
                "commands": ["pip install -r requirements.txt", "npm install", "npm run build", "pip install django gunicorn"],
                "ports": ["5000", "3000", "80", "8000"],
                "command": ["flask run", "npm start", "nginx -g 'daemon off;'", "gunicorn config.wsgi"],
                "docker_task": ["deploy a web application", "create a multi-stage build", "set up a development environment", "optimize image size"],
                "steps": ["1. Create a Dockerfile with FROM, COPY, RUN, and CMD instructions", "2. Use multi-stage builds to reduce final image size", "3. Use .dockerignore to exclude unnecessary files"],
                "commands": ["docker build -t myapp .", "docker run -p 3000:3000 myapp", "docker-compose up -d"],
                "best_practices": ["Use specific image tags, minimize layers, use multi-stage builds"]
            },
            "machine_learning": {
                "ml_concept": ["supervised learning", "unsupervised learning", "reinforcement learning", "neural networks"],
                "definition": ["a type of machine learning where models learn from labeled data", "a type of machine learning that finds patterns in unlabeled data", "a type of learning where agents learn through trial and error", "computing systems inspired by biological neural networks"],
                "mechanism": ["mapping inputs to outputs using training examples", "finding hidden structures in data", "maximizing rewards through exploration", "processing information through interconnected nodes"],
                "applications": ["spam detection, image recognition, medical diagnosis", "customer segmentation, anomaly detection, recommendation systems", "game playing, robotics, autonomous vehicles", "image processing, natural language processing, speech recognition"],
                "algorithm": ["linear regression", "k-means clustering", "Q-learning", "gradient descent"],
                "type": ["regression", "clustering", "reinforcement learning", "optimization"],
                "description": ["predicts continuous values using a linear relationship", "groups data points into k clusters based on similarity", "learns optimal actions through reward maximization", "finds minimum of a function by following gradients"],
                "steps": ["fits a line to minimize the sum of squared errors", "initializes centroids and iteratively assigns points to nearest centroid", "updates Q-values based on rewards received", "computes gradients and updates parameters iteratively"],
                "use_cases": ["house price prediction, sales forecasting", "customer segmentation, image compression", "game AI, robotic control", "training neural networks, optimizing complex functions"]
            }
        }

        domain_fillers = fillers.get(domain, fillers["python"])

        filled = {}
        for key, value in template.items():
            if isinstance(value, str):
                # Replace placeholders with selections based on index for uniqueness
                for placeholder, options in domain_fillers.items():
                    if f"{{{placeholder}}}" in value:
                        choice_index = (hash(value + placeholder + str(index)) % len(options))
                        choice = options[choice_index]
                        value = value.replace(f"{{{placeholder}}}", choice)
                filled[key] = value
            else:
                filled[key] = value

        return filled

    def passes_quality_filter(self, example: TrainingExample) -> bool:
        """Check if example passes quality filters"""
        thresholds = self.quality_thresholds

        # Length checks
        if len(example.instruction.split()) < thresholds["min_instruction_length"]:
            return False

        if len(example.output.split()) < thresholds["min_output_length"]:
            return False

        if len(example.instruction.split()) + len(example.output.split()) > thresholds["max_total_length"]:
            return False

        # Quality score
        if example.quality_score < thresholds["min_quality_score"]:
            return False

        return True

    def calculate_quality_score(self, example: Dict[str, Any]) -> float:
        """Calculate quality score for an example"""
        score = 0.0

        instruction = example.get("instruction", "")
        output = example.get("output", "")

        total_length = len(instruction.split()) + len(output.split())

        # Length factor
        if 50 <= total_length <= 1000:
            score += 0.3
        elif 25 <= total_length < 50 or 1000 < total_length <= 2000:
            score += 0.2
        else:
            score += 0.1

        # Content quality indicators
        if any(word in instruction.lower() for word in ["explain", "what", "how", "describe"]):
            score += 0.2

        if any(word in output.lower() for word in ["example", "code", "function", "implementation", "step"]):
            score += 0.2

        # Technical content
        technical_keywords = ["python", "docker", "machine learning", "algorithm", "function", "class", "api"]
        if any(keyword in (instruction + output).lower() for keyword in technical_keywords):
            score += 0.2

        # Completeness
        if instruction and output:
            score += 0.1

        return min(score, 1.0)

    def deduplicate_examples(self, examples: List[TrainingExample]) -> List[TrainingExample]:
        """Remove duplicate examples based on content hash (more lenient)"""
        logger.info(f"🔄 Deduplicating {len(examples)} examples...")

        seen_hashes = set()
        unique_examples = []

        for example in examples:
            # Create hash from instruction + output, but be more lenient for synthetic examples
            if example.source == "synthetic":
                # For synthetic examples, include domain and some randomness to reduce false duplicates
                content_hash = hashlib.md5(
                    f"{example.instruction}{example.output}{example.domain}{id(example)}".encode()
                ).hexdigest()
            else:
                # For real examples, be more strict about duplicates
                content_hash = hashlib.md5(
                    f"{example.instruction}{example.output}".encode()
                ).hexdigest()

            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_examples.append(example)

        logger.info(f"✅ Removed {len(examples) - len(unique_examples)} duplicates")
        return unique_examples

    def merge_with_existing(self, new_examples: List[TrainingExample]) -> List[TrainingExample]:
        """Merge new examples with existing ones"""
        logger.info("🔄 Merging with existing examples...")

        all_examples = self.existing_examples + new_examples
        deduplicated = self.deduplicate_examples(all_examples)

        logger.info(f"✅ Total examples after merge: {len(deduplicated)}")
        return deduplicated

    def save_processed_datasets(self, examples: List[TrainingExample]):
        """Save processed examples to different domain files"""
        logger.info("💾 Saving processed datasets...")

        # Group by domain
        domain_examples = {}
        for example in examples:
            domain = example.domain
            if domain not in domain_examples:
                domain_examples[domain] = []
            domain_examples[domain].append(example)

        # Save each domain
        for domain, domain_list in domain_examples.items():
            output_file = self.processed_dir / f"{domain}_training.json"

            # Convert to dict format
            dict_examples = [
                {
                    "instruction": ex.instruction,
                    "input": ex.input,
                    "output": ex.output,
                    "source": ex.source,
                    "domain": ex.domain,
                    "quality_score": ex.quality_score
                }
                for ex in domain_list
            ]

            with open(output_file, 'w') as f:
                json.dump(dict_examples, f, indent=2)

            logger.info(f"💾 Saved {len(domain_list)} {domain} examples to {output_file}")

    def create_final_jsonl(self, examples: List[TrainingExample]):
        """Create final JSONL file for training"""
        logger.info("📝 Creating final JSONL training file...")

        output_file = self.final_dir / "combined_training.jsonl"

        with open(output_file, 'w') as f:
            for example in examples:
                # Standard JSONL format for training
                jsonl_entry = {
                    "instruction": example.instruction,
                    "input": example.input,
                    "output": example.output
                }
                f.write(json.dumps(jsonl_entry, ensure_ascii=False) + '\n')

        logger.info(f"✅ Created final JSONL file: {output_file} ({len(examples)} examples)")

    def generate_statistics(self, examples: List[TrainingExample]) -> Dict[str, Any]:
        """Generate comprehensive statistics about the dataset"""
        stats = {
            "total_examples": len(examples),
            "domains": {},
            "sources": {},
            "quality_distribution": {
                "excellent": 0,  # 0.9+
                "good": 0,       # 0.7-0.9
                "acceptable": 0, # 0.6-0.7
                "poor": 0        # <0.6
            },
            "average_lengths": {
                "instruction": 0,
                "output": 0,
                "total": 0
            },
            "generated_at": datetime.now().isoformat()
        }

        total_instruction_len = 0
        total_output_len = 0

        for example in examples:
            # Domain stats
            domain = example.domain
            stats["domains"][domain] = stats["domains"].get(domain, 0) + 1

            # Source stats
            source = example.source
            stats["sources"][source] = stats["sources"].get(source, 0) + 1

            # Quality distribution
            quality = example.quality_score
            if quality >= 0.9:
                stats["quality_distribution"]["excellent"] += 1
            elif quality >= 0.7:
                stats["quality_distribution"]["good"] += 1
            elif quality >= 0.6:
                stats["quality_distribution"]["acceptable"] += 1
            else:
                stats["quality_distribution"]["poor"] += 1

            # Length stats
            total_instruction_len += len(example.instruction.split())
            total_output_len += len(example.output.split())

        # Calculate averages
        if examples:
            stats["average_lengths"]["instruction"] = total_instruction_len / len(examples)
            stats["average_lengths"]["output"] = total_output_len / len(examples)
            stats["average_lengths"]["total"] = stats["average_lengths"]["instruction"] + stats["average_lengths"]["output"]

        return stats

    def run_pipeline(self) -> Dict[str, Any]:
        """Run the complete ingestion pipeline"""
        logger.info("🚀 Starting Automated Dataset Ingestion Pipeline")
        logger.info("=" * 60)

        # Phase 1: Process existing sample docs
        sample_examples = self.process_sample_docs()

        # Phase 2: Generate synthetic examples
        synthetic_examples = self.generate_synthetic_examples(target_count=500)

        # Phase 3: Combine and deduplicate
        combined_examples = sample_examples + synthetic_examples
        deduplicated_examples = self.deduplicate_examples(combined_examples)

        # Phase 4: Merge with existing training data
        final_examples = self.merge_with_existing(deduplicated_examples)

        # Phase 5: Apply final quality filters
        quality_filtered = [
            ex for ex in final_examples
            if self.passes_quality_filter(ex)
        ]

        # Phase 6: Save processed datasets
        self.save_processed_datasets(quality_filtered)

        # Phase 7: Create final JSONL
        self.create_final_jsonl(quality_filtered)

        # Phase 8: Generate statistics
        stats = self.generate_statistics(quality_filtered)

        # Save statistics
        stats_file = self.final_dir / "dataset_statistics.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)

        logger.info("=" * 60)
        logger.info("📊 Final Dataset Statistics:")
        logger.info(f"   Total Examples: {stats['total_examples']}")
        logger.info(f"   Domains: {', '.join(f'{k}: {v}' for k, v in stats['domains'].items())}")
        logger.info(f"   Sources: {', '.join(f'{k}: {v}' for k, v in stats['sources'].items())}")
        logger.info(f"   Quality Distribution: {stats['quality_distribution']}")
        logger.info(f"   Avg Lengths: Instruction: {stats['average_lengths']['instruction']:.1f}, Output: {stats['average_lengths']['output']:.1f}")
        logger.info(f"   Statistics saved to: {stats_file}")

        return {
            "stats": stats,
            "examples_count": len(quality_filtered),
            "output_files": {
                "jsonl": str(self.final_dir / "combined_training.jsonl"),
                "stats": str(stats_file)
            }
        }

def main():
    """Main function to run the ingestion pipeline"""
    pipeline = AutomatedIngestionPipeline()
    results = pipeline.run_pipeline()

    print("\n🎉 Automated Dataset Ingestion Pipeline Complete!")
    print(f"Generated {results['examples_count']} high-quality training examples")
    print(f"JSONL file: {results['output_files']['jsonl']}")
    print(f"Statistics: {results['output_files']['stats']}")

    return results

if __name__ == "__main__":
    main()