#!/usr/bin/env python3
"""
Quick Start with Hugging Face Pro + MCP Tools
Simple setup for immediate use
"""

import os
import json
from huggingface_hub import HfApi, login

# Set up your HF Pro API key
HF_TOKEN = os.getenv("HF_TOKEN")  # Set your token as environment variable
if not HF_TOKEN:
    raise ValueError("Please set HF_TOKEN environment variable")
login(token=HF_TOKEN)

def quick_setup():
    """Quick setup for HF Pro features"""
    print("🚀 Hugging Face Pro Quick Setup")
    print("=" * 40)
    
    api = HfApi(token=HF_TOKEN)
    
    # Get user info
    user_info = api.whoami()
    print(f"👤 User: {user_info['name']}")
    print(f"💎 Pro Status: {user_info.get('pro', False)}")
    
    # Create directories
    os.makedirs("/Users/andrejsp/ai/datasets", exist_ok=True)
    os.makedirs("/Users/andrejsp/ai/configs", exist_ok=True)
    os.makedirs("/Users/andrejsp/ai/scripts", exist_ok=True)
    
    print("✅ Directories created")
    
    return api

def create_training_data():
    """Create sample training data"""
    print("\n📊 Creating Training Data")
    print("=" * 30)
    
    # Sample code generation data
    training_data = [
        {
            "instruction": "Write a Python function to calculate fibonacci numbers",
            "input": "n = 10",
            "output": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nprint(fibonacci(10))  # Output: 55"
        },
        {
            "instruction": "Create a JavaScript function to reverse a string",
            "input": "str = 'hello world'",
            "output": "function reverseString(str) {\n    return str.split('').reverse().join('');\n}\n\nconsole.log(reverseString('hello world'));  // Output: dlrow olleh"
        },
        {
            "instruction": "Write a SQL query to find duplicate records",
            "input": "table with id, name, email columns",
            "output": "SELECT name, email, COUNT(*) as count\nFROM users\nGROUP BY name, email\nHAVING COUNT(*) > 1;"
        }
    ]
    
    # Save training data
    with open("/Users/andrejsp/ai/datasets/code_training.json", "w") as f:
        json.dump(training_data, f, indent=2)
    
    print(f"✅ Training data saved: /Users/andrejsp/ai/datasets/code_training.json")
    print(f"   - Examples: {len(training_data)}")
    
    return training_data

def create_training_script():
    """Create a simple training script"""
    print("\n🛠️  Creating Training Script")
    print("=" * 30)
    
    script_content = '''#!/usr/bin/env python3
"""
Simple Hugging Face Training Script
"""

import json
from datasets import Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType

def main():
    # Load training data
    with open("/Users/andrejsp/ai/datasets/code_training.json", "r") as f:
        data = json.load(f)
    
    # Convert to dataset
    dataset = Dataset.from_list(data)
    
    # Load model and tokenizer
    model_name = "microsoft/DialoGPT-small"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    # Set up LoRA
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,
        lora_alpha=32,
        target_modules=["c_attn"],
        lora_dropout=0.1
    )
    
    model = get_peft_model(model, lora_config)
    
    # Prepare data
    def tokenize_function(examples):
        texts = [f"Instruction: {inst}\\nCode: {out}" 
                for inst, out in zip(examples['instruction'], examples['output'])]
        
        tokenized = tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors="pt"
        )
        tokenized["labels"] = tokenized["input_ids"].clone()
        return tokenized
    
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="./hf_training_output",
        per_device_train_batch_size=2,
        num_train_epochs=1,
        logging_steps=10,
        save_steps=100,
        evaluation_strategy="no",
        report_to=None
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer
    )
    
    # Train
    print("🚀 Starting training...")
    trainer.train()
    trainer.save_model()
    
    print("✅ Training completed!")

if __name__ == "__main__":
    main()
'''
    
    with open("/Users/andrejsp/ai/scripts/train_hf_model.py", "w") as f:
        f.write(script_content)
    
    os.chmod("/Users/andrejsp/ai/scripts/train_hf_model.py", 0o755)
    
    print("✅ Training script created: /Users/andrejsp/ai/scripts/train_hf_model.py")

def main():
    """Main setup function"""
    print("🚀 Setting up Hugging Face Pro with MCP Tools")
    print("=" * 50)
    
    # 1. Quick setup
    api = quick_setup()
    
    # 2. Create training data
    training_data = create_training_data()
    
    # 3. Create training script
    create_training_script()
    
    print(f"\n🎉 Setup Complete!")
    print(f"\n📋 What you can do now:")
    print(f"1. 🔍 Search models: Use MCP HF tools to find models")
    print(f"2. 📊 Load datasets: Use datasets library with HF datasets")
    print(f"3. 🏃 Train models: Run python /Users/andrejsp/ai/scripts/train_hf_model.py")
    print(f"4. 📤 Upload models: Use huggingface-cli upload")
    print(f"5. 🚀 Deploy to Ollama: Convert trained models to Ollama format")
    
    print(f"\n💡 MCP Tools Available:")
    print(f"   - hf_whoami: Check authentication")
    print(f"   - model_search: Find models by query")
    print(f"   - dataset_search: Find datasets")
    print(f"   - space_search: Find Hugging Face Spaces")
    print(f"   - hub_repo_details: Get detailed model/dataset info")

if __name__ == "__main__":
    main()
