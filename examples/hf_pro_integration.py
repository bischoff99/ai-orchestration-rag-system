#!/usr/bin/env python3
"""
Hugging Face Pro Integration with MCP Tools
Demonstrates advanced features available with HF Pro account
"""

import os
import json
from huggingface_hub import HfApi, login
from datasets import load_dataset
import requests

# Set up your HF Pro API key
HF_TOKEN = os.getenv("HF_TOKEN")  # Set your token as environment variable
if not HF_TOKEN:
    raise ValueError("Please set HF_TOKEN environment variable")
login(token=HF_TOKEN)

def explore_hf_pro_features():
    """Explore what's available with your HF Pro account"""
    print("🔍 Exploring Hugging Face Pro Features")
    print("=" * 50)

    api = HfApi(token=HF_TOKEN)

    # Get user info
    user_info = api.whoami()
    print(f"👤 User: {user_info['name']}")
    print(f"📧 Email: {user_info['email']}")
    print(f"🏢 Organization: {user_info.get('orgs', [{}])[0].get('name', 'Personal')}")
    print(f"💎 Pro Status: {user_info.get('pro', False)}")

    # List your repositories
    print(f"\n📚 Your Repositories:")
    repos = api.list_repos(type="model", limit=5)
    for repo in repos:
        print(f"   - {repo.id} ({repo.private and 'Private' or 'Public'})")

    return api

def download_code_datasets():
    """Download and explore code generation datasets"""
    print(f"\n📊 Downloading Code Generation Datasets")
    print("=" * 40)

    # Download Python code dataset
    print("🐍 Loading Python Codes 25K dataset...")
    python_dataset = load_dataset("flytech/python-codes-25k", split="train[:100]")

    print(f"✅ Dataset loaded:")
    print(f"   - Size: {len(python_dataset)} examples")
    print(f"   - Features: {python_dataset.features}")
    print(f"   - Sample instruction: {python_dataset[0]['instruction']}")
    print(f"   - Sample output: {python_dataset[0]['output'][:100]}...")

    return python_dataset

def create_training_dataset():
    """Create a custom training dataset for your models"""
    print(f"\n🛠️  Creating Custom Training Dataset")
    print("=" * 40)

    # Sample training data for code generation
    training_examples = [
        {
            "instruction": "Write a Python function to calculate the factorial of a number",
            "input": "n = 5",
            "output": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n\nresult = factorial(5)\nprint(result)  # Output: 120"
        },
        {
            "instruction": "Create a JavaScript function to reverse a string",
            "input": "str = 'hello'",
            "output": "function reverseString(str) {\n    return str.split('').reverse().join('');\n}\n\nconsole.log(reverseString('hello'));  // Output: olleh"
        },
        {
            "instruction": "Write a SQL query to find the top 10 customers by total order value",
            "input": "customers and orders tables",
            "output": "SELECT c.customer_id, c.customer_name, SUM(o.order_value) as total_value\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nGROUP BY c.customer_id, c.customer_name\nORDER BY total_value DESC\nLIMIT 10;"
        }
    ]

    # Save as JSON for training
    with open("/Users/andrejsp/ai/datasets/custom_code_training.json", "w") as f:
        json.dump(training_examples, f, indent=2)

    print(f"✅ Custom dataset created:")
    print(f"   - File: /Users/andrejsp/ai/datasets/custom_code_training.json")
    print(f"   - Examples: {len(training_examples)}")

    return training_examples

def setup_advanced_training():
    """Set up advanced training with HF Pro features"""
    print(f"\n🚀 Setting Up Advanced Training")
    print("=" * 40)

    # Create training configuration
    training_config = {
        "model_name": "microsoft/DialoGPT-small",
        "dataset_name": "custom_code_training.json",
        "training_args": {
            "output_dir": "./hf_pro_training_output",
            "num_train_epochs": 3,
            "per_device_train_batch_size": 4,
            "per_device_eval_batch_size": 4,
            "warmup_steps": 100,
            "weight_decay": 0.01,
            "learning_rate": 5e-5,
            "logging_dir": "./logs",
            "logging_steps": 10,
            "save_steps": 500,
            "eval_steps": 500,
            "evaluation_strategy": "steps",
            "save_strategy": "steps",
            "load_best_model_at_end": True,
            "metric_for_best_model": "eval_loss",
            "greater_is_better": False,
            "report_to": "wandb",  # Use Weights & Biases for tracking
            "run_name": "code-generation-finetune"
        },
        "lora_config": {
            "r": 16,
            "lora_alpha": 32,
            "target_modules": ["q_proj", "v_proj"],
            "lora_dropout": 0.1,
            "bias": "none",
            "task_type": "CAUSAL_LM"
        }
    }

    # Save configuration
    with open("/Users/andrejsp/ai/configs/hf_pro_training_config.json", "w") as f:
        json.dump(training_config, f, indent=2)

    print(f"✅ Training configuration saved:")
    print(f"   - Config: /Users/andrejsp/ai/configs/hf_pro_training_config.json")
    print(f"   - Model: {training_config['model_name']}")
    print(f"   - LoRA Rank: {training_config['lora_config']['r']}")
    print(f"   - Epochs: {training_config['training_args']['num_train_epochs']}")

    return training_config

def create_deployment_script():
    """Create a script to deploy trained models to Ollama"""
    print(f"\n🚀 Creating Ollama Deployment Script")
    print("=" * 40)

    deployment_script = '''#!/bin/bash
# Deploy Hugging Face trained model to Ollama

MODEL_NAME="your-trained-model"
HF_REPO="bischoff555/your-trained-model"
OLLAMA_MODEL="custom-code-assistant"

echo "🔄 Converting HF model to Ollama format..."

# Create Modelfile
cat > Modelfile << EOF
FROM $HF_REPO
PARAMETER temperature 0.1
PARAMETER top_p 0.95
PARAMETER num_ctx 4096
PARAMETER num_batch 256
PARAMETER repeat_penalty 1.1
PARAMETER repeat_last_n 64
PARAMETER top_k 40
PARAMETER min_p 0.05
PARAMETER num_predict 2048
SYSTEM You are an expert programming assistant. Provide clear, efficient, and well-documented code solutions with best practices and optimization techniques.
EOF

# Create Ollama model
ollama create $OLLAMA_MODEL -f Modelfile

echo "✅ Model deployed as: $OLLAMA_MODEL"
echo "🧪 Test with: ollama run $OLLAMA_MODEL 'Write a Python function to sort a list'"
'''

    with open("/Users/andrejsp/ai/scripts/deploy_hf_to_ollama.sh", "w") as f:
        f.write(deployment_script)

    os.chmod("/Users/andrejsp/ai/scripts/deploy_hf_to_ollama.sh", 0o755)

    print(f"✅ Deployment script created:")
    print(f"   - Script: /Users/andrejsp/ai/scripts/deploy_hf_to_ollama.sh")
    print(f"   - Usage: ./deploy_hf_to_ollama.sh")

def main():
    """Main function demonstrating HF Pro integration"""
    print("🚀 Hugging Face Pro Integration with MCP Tools")
    print("=" * 60)

    # 1. Explore Pro features
    api = explore_hf_pro_features()

    # 2. Download code datasets
    python_dataset = download_code_datasets()

    # 3. Create custom training dataset
    custom_dataset = create_training_dataset()

    # 4. Set up advanced training
    training_config = setup_advanced_training()

    # 5. Create deployment script
    create_deployment_script()

    print(f"\n🎉 HF Pro Integration Complete!")
    print(f"\n📋 Next Steps:")
    print(f"1. 🏃 Run training: python /Users/andrejsp/ai/examples/hf_datasets_example.py")
    print(f"2. 📤 Upload to HF: huggingface-cli upload bischoff555/your-model ./output")
    print(f"3. 🚀 Deploy to Ollama: ./deploy_hf_to_ollama.sh")
    print(f"4. 🧪 Test with MCP tools: Use the HF search and model tools")

    print(f"\n💡 Pro Features Available:")
    print(f"   - Private model repositories")
    print(f"   - Advanced training metrics")
    print(f"   - Weights & Biases integration")
    print(f"   - Model versioning and management")
    print(f"   - API endpoints for inference")

if __name__ == "__main__":
    main()
