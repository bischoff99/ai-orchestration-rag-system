#!/usr/bin/env python3
"""
Download Quality Datasets for Training and RAG
Downloads curated, high-quality datasets from HuggingFace with quality filtering
"""
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datasets import load_dataset
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QualityDatasetDownloader:
    """Downloads and filters high-quality datasets for training and RAG"""
    
    def __init__(self, output_dir: str = "/Users/andrejsp/ai/datasets/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Quality-focused dataset configuration
        self.datasets_config = {
            "alpaca": {
                "name": "tatsu-lab/alpaca",
                "type": "instruction",
                "sample_size": 200,  # Quality over quantity
                "priority": 1,
                "description": "High-quality instruction-following data",
                "quality_filters": {
                    "min_instruction_length": 20,
                    "min_output_length": 50,
                    "max_total_length": 2048
                }
            },
            "fineweb_edu": {
                "name": "HuggingFaceFW/fineweb-edu",
                "type": "educational",
                "sample_size": 300,  # Educational content
                "priority": 2,
                "description": "Educational content for technical knowledge",
                "quality_filters": {
                    "min_length": 100,
                    "max_length": 2000,
                    "keywords": ["python", "machine learning", "docker", "api", "database", "programming"]
                }
            },
            "gsm8k": {
                "name": "openai/gsm8k",
                "type": "reasoning",
                "sample_size": 100,  # Math reasoning
                "priority": 3,
                "description": "Math reasoning problems for analytical thinking",
                "quality_filters": {
                    "min_question_length": 30,
                    "min_answer_length": 20
                }
            },
            "chatgpt_prompts": {
                "name": "fka/awesome-chatgpt-prompts",
                "type": "prompts",
                "sample_size": 50,  # High-quality prompts
                "priority": 4,
                "description": "Curated prompt templates",
                "quality_filters": {
                    "min_prompt_length": 30,
                    "max_prompt_length": 500
                }
            },
            "github_code_2025": {
                "name": "nick007x/github-code-2025",
                "type": "code",
                "sample_size": 150,  # Code examples
                "priority": 5,
                "description": "Modern GitHub code snippets for coding knowledge",
                "quality_filters": {
                    "min_code_length": 50,
                    "max_code_length": 1000,
                    "languages": ["python", "javascript", "typescript", "go", "rust"]
                }
            },
            "code_alpaca": {
                "name": "sahil2801/CodeAlpaca-20k",
                "type": "code_instruction",
                "sample_size": 100,  # Code instructions
                "priority": 6,
                "description": "Code-focused instruction-response pairs",
                "quality_filters": {
                    "min_instruction_length": 25,
                    "min_code_length": 20,
                    "languages": ["python", "javascript", "java", "cpp", "sql"]
                }
            },
            "wikipedia_python": {
                "name": "aadityaubhat/GPT-wiki-python-dataset",
                "type": "technical_wiki",
                "sample_size": 80,  # Python technical content
                "priority": 7,
                "description": "Python programming concepts and examples",
                "quality_filters": {
                    "min_length": 200,
                    "max_length": 1500,
                    "keywords": ["python", "programming", "code", "function", "class", "algorithm"]
                }
            },
            "ml_questions": {
                "name": "sdtblck/ml-questions-and-answers",
                "type": "ml_qa",
                "sample_size": 60,  # ML Q&A pairs
                "priority": 8,
                "description": "Machine learning questions and expert answers",
                "quality_filters": {
                    "min_question_length": 20,
                    "min_answer_length": 100,
                    "keywords": ["machine learning", "neural network", "deep learning", "training", "model"]
                }
            },
            "docker_docs": {
                "name": "nicholasKluge/docker-docs-qa",
                "type": "docker_qa",
                "sample_size": 40,  # Docker Q&A
                "priority": 9,
                "description": "Docker documentation Q&A pairs",
                "quality_filters": {
                    "min_question_length": 15,
                    "min_answer_length": 50,
                    "keywords": ["docker", "container", "image", "compose", "volume", "network"]
                }
            },
            "api_design": {
                "name": "fka/awesome-chatgpt-prompts",
                "type": "api_design",
                "sample_size": 30,  # API design prompts
                "priority": 10,
                "description": "API design and development prompts",
                "quality_filters": {
                    "min_prompt_length": 40,
                    "max_prompt_length": 600,
                    "keywords": ["api", "rest", "graphql", "design", "endpoint", "authentication"]
                }
            }
        }
        
        self.downloaded_data = {}
    
    def apply_quality_filters(self, example: Dict[str, Any], dataset_name: str) -> bool:
        """Apply quality filters to determine if example should be kept"""
        filters = self.datasets_config[dataset_name]["quality_filters"]
        
        try:
            # Check instruction length
            if "min_instruction_length" in filters:
                instruction = example.get("instruction", "")
                if len(instruction.split()) < filters["min_instruction_length"]:
                    return False
            
            # Check output length
            if "min_output_length" in filters:
                output = example.get("output", "")
                if len(output.split()) < filters["min_output_length"]:
                    return False
            
            # Check total length
            if "max_total_length" in filters:
                total_text = f"{example.get('instruction', '')} {example.get('output', '')}"
                if len(total_text.split()) > filters["max_total_length"]:
                    return False
            
            # Check content length
            if "min_length" in filters:
                content = example.get("text", example.get("output", ""))
                if len(content.split()) < filters["min_length"]:
                    return False
            
            if "max_length" in filters:
                content = example.get("text", example.get("output", ""))
                if len(content.split()) > filters["max_length"]:
                    return False
            
            # Check keywords for educational content
            if "keywords" in filters:
                content = example.get("text", example.get("output", "")).lower()
                if not any(keyword in content for keyword in filters["keywords"]):
                    return False
            
            # Check prompt length
            if "min_prompt_length" in filters:
                prompt = example.get("prompt", example.get("instruction", ""))
                if len(prompt.split()) < filters["min_prompt_length"]:
                    return False

            if "max_prompt_length" in filters:
                prompt = example.get("prompt", example.get("instruction", ""))
                if len(prompt.split()) > filters["max_prompt_length"]:
                    return False

            # Check code length for code-related datasets
            if "min_code_length" in filters:
                code = example.get("code", example.get("output", ""))
                if len(code.split()) < filters["min_code_length"]:
                    return False

            if "max_code_length" in filters:
                code = example.get("code", example.get("output", ""))
                if len(code.split()) > filters["max_code_length"]:
                    return False

            # Check programming languages for code datasets
            if "languages" in filters:
                language = example.get("language", "").lower()
                if language and language not in filters["languages"]:
                    return False

            return True
            
        except Exception as e:
            logger.warning(f"Error applying filters to example: {e}")
            return False
    
    def download_alpaca_dataset(self) -> Tuple[List[Dict], int]:
        """Download and filter Alpaca instruction-following dataset"""
        logger.info("📥 Downloading Alpaca dataset...")
        
        try:
            dataset = load_dataset(
                self.datasets_config["alpaca"]["name"],
                split=f"train[:{self.datasets_config['alpaca']['sample_size']}]"
            )
            
            filtered_examples = []
            total_examples = len(dataset)
            
            for example in dataset:
                if self.apply_quality_filters(example, "alpaca"):
                    # Normalize to our schema
                    normalized = {
                        "instruction": example.get("instruction", ""),
                        "input": example.get("input", ""),
                        "output": example.get("output", ""),
                        "source": "alpaca",
                        "domain": "general",
                        "quality_score": self.calculate_quality_score(example)
                    }
                    filtered_examples.append(normalized)
            
            logger.info(f"✅ Alpaca: {len(filtered_examples)}/{total_examples} examples passed quality filters")
            return filtered_examples, total_examples
            
        except Exception as e:
            logger.error(f"❌ Error downloading Alpaca: {e}")
            return [], 0
    
    def download_fineweb_edu_dataset(self) -> Tuple[List[Dict], int]:
        """Download and filter FineWeb-Edu educational dataset"""
        logger.info("📥 Downloading FineWeb-Edu dataset...")
        
        try:
            dataset = load_dataset(
                self.datasets_config["fineweb_edu"]["name"],
                split=f"train[:{self.datasets_config['fineweb_edu']['sample_size']}]"
            )
            
            filtered_examples = []
            total_examples = len(dataset)
            
            for example in dataset:
                if self.apply_quality_filters(example, "fineweb_edu"):
                    # Convert to instruction format
                    content = example.get("text", "")
                    # Split into instruction and output (simplified)
                    lines = content.split('\n')
                    instruction = lines[0] if lines else "Explain this concept"
                    output = content
                    
                    normalized = {
                        "instruction": instruction,
                        "input": "",
                        "output": output,
                        "source": "fineweb_edu",
                        "domain": "technical",
                        "quality_score": self.calculate_quality_score(example)
                    }
                    filtered_examples.append(normalized)
            
            logger.info(f"✅ FineWeb-Edu: {len(filtered_examples)}/{total_examples} examples passed quality filters")
            return filtered_examples, total_examples
            
        except Exception as e:
            logger.error(f"❌ Error downloading FineWeb-Edu: {e}")
            return [], 0
    
    def download_gsm8k_dataset(self) -> Tuple[List[Dict], int]:
        """Download and filter GSM8K math reasoning dataset"""
        logger.info("📥 Downloading GSM8K dataset...")
        
        try:
            dataset = load_dataset(
                self.datasets_config["gsm8k"]["name"],
                split=f"train[:{self.datasets_config['gsm8k']['sample_size']}]"
            )
            
            filtered_examples = []
            total_examples = len(dataset)
            
            for example in dataset:
                if self.apply_quality_filters(example, "gsm8k"):
                    normalized = {
                        "instruction": f"Solve this math problem step by step: {example.get('question', '')}",
                        "input": "",
                        "output": example.get("answer", ""),
                        "source": "gsm8k",
                        "domain": "reasoning",
                        "quality_score": self.calculate_quality_score(example)
                    }
                    filtered_examples.append(normalized)
            
            logger.info(f"✅ GSM8K: {len(filtered_examples)}/{total_examples} examples passed quality filters")
            return filtered_examples, total_examples
            
        except Exception as e:
            logger.error(f"❌ Error downloading GSM8K: {e}")
            return [], 0
    
    def download_chatgpt_prompts_dataset(self) -> Tuple[List[Dict], int]:
        """Download and filter ChatGPT prompts dataset"""
        logger.info("📥 Downloading ChatGPT prompts dataset...")
        
        try:
            dataset = load_dataset(
                self.datasets_config["chatgpt_prompts"]["name"],
                split="train"
            )
            
            filtered_examples = []
            total_examples = len(dataset)
            
            for example in dataset:
                if self.apply_quality_filters(example, "chatgpt_prompts"):
                    # Extract prompt and act
                    prompt = example.get("prompt", "")
                    act = example.get("act", "")
                    
                    normalized = {
                        "instruction": f"Use this prompt template: {prompt}",
                        "input": "",
                        "output": f"Template: {prompt}\nAct: {act}",
                        "source": "chatgpt_prompts",
                        "domain": "prompts",
                        "quality_score": self.calculate_quality_score(example)
                    }
                    filtered_examples.append(normalized)
            
            # Limit to sample size
            filtered_examples = filtered_examples[:self.datasets_config["chatgpt_prompts"]["sample_size"]]
            
            logger.info(f"✅ ChatGPT Prompts: {len(filtered_examples)}/{total_examples} examples passed quality filters")
            return filtered_examples, total_examples
            
        except Exception as e:
            logger.error(f"❌ Error downloading ChatGPT prompts: {e}")
            return [], 0

    def download_github_code_dataset(self) -> Tuple[List[Dict], int]:
        """Download and filter GitHub code 2025 dataset"""
        logger.info("📥 Downloading GitHub Code 2025 dataset...")

        try:
            dataset = load_dataset(
                self.datasets_config["github_code_2025"]["name"],
                split=f"train[:{self.datasets_config['github_code_2025']['sample_size']}]"
            )

            filtered_examples = []
            total_examples = len(dataset)

            for example in dataset:
                if self.apply_quality_filters(example, "github_code_2025"):
                    normalized = {
                        "instruction": f"Analyze and explain this code: {example.get('code', '')}",
                        "input": "",
                        "output": f"This is a code example in {example.get('language', 'unknown')}. Key features: {example.get('description', 'Code snippet')}",
                        "source": "github_code_2025",
                        "domain": "coding",
                        "quality_score": self.calculate_quality_score(example)
                    }
                    filtered_examples.append(normalized)

            logger.info(f"✅ GitHub Code 2025: {len(filtered_examples)}/{total_examples} examples passed quality filters")
            return filtered_examples, total_examples

        except Exception as e:
            logger.error(f"❌ Error downloading GitHub Code 2025: {e}")
            return [], 0

    def download_code_alpaca_dataset(self) -> Tuple[List[Dict], int]:
        """Download and filter CodeAlpaca dataset"""
        logger.info("📥 Downloading CodeAlpaca dataset...")

        try:
            dataset = load_dataset(
                self.datasets_config["code_alpaca"]["name"],
                split=f"train[:{self.datasets_config['code_alpaca']['sample_size']}]"
            )

            filtered_examples = []
            total_examples = len(dataset)

            for example in dataset:
                if self.apply_quality_filters(example, "code_alpaca"):
                    normalized = {
                        "instruction": example.get("instruction", ""),
                        "input": example.get("input", ""),
                        "output": example.get("output", ""),
                        "source": "code_alpaca",
                        "domain": "code_instruction",
                        "quality_score": self.calculate_quality_score(example)
                    }
                    filtered_examples.append(normalized)

            logger.info(f"✅ CodeAlpaca: {len(filtered_examples)}/{total_examples} examples passed quality filters")
            return filtered_examples, total_examples

        except Exception as e:
            logger.error(f"❌ Error downloading CodeAlpaca: {e}")
            return [], 0

    def download_wikipedia_python_dataset(self) -> Tuple[List[Dict], int]:
        """Download and filter Python Wikipedia dataset"""
        logger.info("📥 Downloading Python Wikipedia dataset...")

        try:
            dataset = load_dataset(
                self.datasets_config["wikipedia_python"]["name"],
                split=f"train[:{self.datasets_config['wikipedia_python']['sample_size']}]"
            )

            filtered_examples = []
            total_examples = len(dataset)

            for example in dataset:
                if self.apply_quality_filters(example, "wikipedia_python"):
                    content = example.get("text", "")
                    # Split content into instruction and output
                    lines = content.split('\n')
                    instruction = lines[0] if lines else "Explain this Python concept"
                    output = content

                    normalized = {
                        "instruction": instruction,
                        "input": "",
                        "output": output,
                        "source": "wikipedia_python",
                        "domain": "python_technical",
                        "quality_score": self.calculate_quality_score(example)
                    }
                    filtered_examples.append(normalized)

            logger.info(f"✅ Python Wikipedia: {len(filtered_examples)}/{total_examples} examples passed quality filters")
            return filtered_examples, total_examples

        except Exception as e:
            logger.error(f"❌ Error downloading Python Wikipedia: {e}")
            return [], 0

    def download_ml_questions_dataset(self) -> Tuple[List[Dict], int]:
        """Download and filter ML Questions & Answers dataset"""
        logger.info("📥 Downloading ML Questions dataset...")

        try:
            dataset = load_dataset(
                self.datasets_config["ml_questions"]["name"],
                split=f"train[:{self.datasets_config['ml_questions']['sample_size']}]"
            )

            filtered_examples = []
            total_examples = len(dataset)

            for example in dataset:
                if self.apply_quality_filters(example, "ml_questions"):
                    normalized = {
                        "instruction": example.get("instruction", example.get("question", "")),
                        "input": "",
                        "output": example.get("output", example.get("answer", "")),
                        "source": "ml_questions",
                        "domain": "machine_learning",
                        "quality_score": self.calculate_quality_score(example)
                    }
                    filtered_examples.append(normalized)

            logger.info(f"✅ ML Questions: {len(filtered_examples)}/{total_examples} examples passed quality filters")
            return filtered_examples, total_examples

        except Exception as e:
            logger.error(f"❌ Error downloading ML Questions: {e}")
            return [], 0

    def download_docker_docs_dataset(self) -> Tuple[List[Dict], int]:
        """Download and filter Docker Docs Q&A dataset"""
        logger.info("📥 Downloading Docker Docs Q&A dataset...")

        try:
            dataset = load_dataset(
                self.datasets_config["docker_docs"]["name"],
                split=f"train[:{self.datasets_config['docker_docs']['sample_size']}]"
            )

            filtered_examples = []
            total_examples = len(dataset)

            for example in dataset:
                if self.apply_quality_filters(example, "docker_docs"):
                    normalized = {
                        "instruction": example.get("instruction", example.get("question", "")),
                        "input": "",
                        "output": example.get("output", example.get("answer", "")),
                        "source": "docker_docs",
                        "domain": "docker",
                        "quality_score": self.calculate_quality_score(example)
                    }
                    filtered_examples.append(normalized)

            logger.info(f"✅ Docker Docs: {len(filtered_examples)}/{total_examples} examples passed quality filters")
            return filtered_examples, total_examples

        except Exception as e:
            logger.error(f"❌ Error downloading Docker Docs: {e}")
            return [], 0

    def download_api_design_dataset(self) -> Tuple[List[Dict], int]:
        """Download and filter API design prompts from ChatGPT prompts dataset"""
        logger.info("📥 Downloading API Design prompts...")

        try:
            dataset = load_dataset(
                self.datasets_config["api_design"]["name"],
                split="train"
            )

            filtered_examples = []
            total_examples = len(dataset)

            for example in dataset:
                if self.apply_quality_filters(example, "api_design"):
                    prompt = example.get("prompt", "")
                    act = example.get("act", "")

                    normalized = {
                        "instruction": f"Use this API design prompt: {prompt}",
                        "input": "",
                        "output": f"Template: {prompt}\nAct: {act}",
                        "source": "api_design",
                        "domain": "api_design",
                        "quality_score": self.calculate_quality_score(example)
                    }
                    filtered_examples.append(normalized)

            # Limit to sample size
            filtered_examples = filtered_examples[:self.datasets_config["api_design"]["sample_size"]]

            logger.info(f"✅ API Design: {len(filtered_examples)}/{total_examples} examples passed quality filters")
            return filtered_examples, total_examples

        except Exception as e:
            logger.error(f"❌ Error downloading API Design: {e}")
            return [], 0

    def calculate_quality_score(self, example: Dict[str, Any]) -> float:
        """Calculate a quality score for an example (0.0 to 1.0)"""
        score = 0.0
        
        # Length factor (optimal length gets higher score)
        instruction = example.get("instruction", "")
        output = example.get("output", "")
        total_length = len(instruction.split()) + len(output.split())
        
        if 50 <= total_length <= 1000:
            score += 0.3
        elif 20 <= total_length < 50 or 1000 < total_length <= 2000:
            score += 0.2
        else:
            score += 0.1
        
        # Content quality indicators
        if "step" in output.lower() or "explain" in instruction.lower():
            score += 0.2  # Structured content
        
        if any(word in output.lower() for word in ["code", "function", "example", "implementation"]):
            score += 0.2  # Technical content
        
        if len(instruction.split()) > 10 and len(output.split()) > 20:
            score += 0.2  # Substantial content
        
        # Completeness
        if instruction and output:
            score += 0.1  # Complete example
        
        return min(score, 1.0)
    
    def save_dataset(self, examples: List[Dict], dataset_name: str):
        """Save dataset to file"""
        output_file = self.output_dir / f"{dataset_name}_filtered.json"
        
        with open(output_file, 'w') as f:
            json.dump(examples, f, indent=2)
        
        logger.info(f"💾 Saved {len(examples)} examples to {output_file}")
    
    def download_all_datasets(self) -> Dict[str, Any]:
        """Download all configured datasets"""
        logger.info("🚀 Starting quality dataset download...")
        logger.info("=" * 60)
        
        results = {
            "total_downloaded": 0,
            "total_filtered": 0,
            "datasets": {}
        }
        
        # Download each dataset
        datasets = [
            ("alpaca", self.download_alpaca_dataset),
            ("fineweb_edu", self.download_fineweb_edu_dataset),
            ("gsm8k", self.download_gsm8k_dataset),
            ("chatgpt_prompts", self.download_chatgpt_prompts_dataset),
            ("github_code_2025", self.download_github_code_dataset),
            ("code_alpaca", self.download_code_alpaca_dataset),
            ("wikipedia_python", self.download_wikipedia_python_dataset),
            ("ml_questions", self.download_ml_questions_dataset),
            ("docker_docs", self.download_docker_docs_dataset),
            ("api_design", self.download_api_design_dataset)
        ]
        
        for dataset_name, download_func in datasets:
            try:
                examples, total = download_func()
                results["datasets"][dataset_name] = {
                    "downloaded": total,
                    "filtered": len(examples),
                    "quality_ratio": len(examples) / total if total > 0 else 0
                }
                results["total_downloaded"] += total
                results["total_filtered"] += len(examples)
                
                # Save dataset
                self.save_dataset(examples, dataset_name)
                
            except Exception as e:
                logger.error(f"❌ Failed to download {dataset_name}: {e}")
                results["datasets"][dataset_name] = {
                    "downloaded": 0,
                    "filtered": 0,
                    "quality_ratio": 0,
                    "error": str(e)
                }
        
        # Save summary
        summary_file = self.output_dir / "download_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info("=" * 60)
        logger.info(f"📊 Download Summary:")
        logger.info(f"   Total downloaded: {results['total_downloaded']}")
        logger.info(f"   Total filtered: {results['total_filtered']}")
        quality_ratio = (results['total_filtered']/results['total_downloaded']*100) if results['total_downloaded'] > 0 else 0
        logger.info(f"   Quality ratio: {quality_ratio:.1f}%")
        logger.info(f"   Summary saved to: {summary_file}")
        
        return results

def main():
    """Main function to download quality datasets"""
    downloader = QualityDatasetDownloader()
    results = downloader.download_all_datasets()
    
    print("\n🎉 Quality dataset download completed!")
    print(f"Downloaded {results['total_filtered']} high-quality examples")
    
    return results

if __name__ == "__main__":
    main()