#!/usr/bin/env python3
"""
Hugging Face Datasets and Training Example
Demonstrates loading, processing, and training with HF datasets on Apple Silicon
"""

import os
import json
from datasets import load_dataset, Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
import torch

def load_and_explore_dataset():
    """Load and explore a Hugging Face dataset"""
    print("🔍 Loading Hugging Face dataset...")
    
    # Load a popular dataset for fine-tuning
    dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")
    
    print(f"📊 Dataset info:")
    print(f"   - Size: {len(dataset)} examples")
    print(f"   - Features: {dataset.features}")
    print(f"   - Sample text: {dataset[0]['text'][:200]}...")
    
    return dataset

def create_custom_dataset():
    """Create a custom dataset for specific use cases"""
    print("\n🛠️  Creating custom dataset...")
    
    # Example: Code generation dataset
    code_examples = [
        {
            "instruction": "Write a Python function to calculate fibonacci numbers",
            "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
            "language": "python"
        },
        {
            "instruction": "Create a JavaScript function to reverse a string",
            "code": "function reverseString(str) {\n    return str.split('').reverse().join('');\n}",
            "language": "javascript"
        },
        {
            "instruction": "Write a SQL query to find the top 10 customers by order value",
            "code": "SELECT customer_id, SUM(order_value) as total_value\nFROM orders\nGROUP BY customer_id\nORDER BY total_value DESC\nLIMIT 10;",
            "language": "sql"
        }
    ]
    
    # Convert to Hugging Face Dataset
    custom_dataset = Dataset.from_list(code_examples)
    
    print(f"📊 Custom dataset created:")
    print(f"   - Size: {len(custom_dataset)} examples")
    print(f"   - Features: {custom_dataset.features}")
    
    return custom_dataset

def prepare_training_data(dataset, tokenizer, max_length=512):
    """Prepare dataset for training"""
    print(f"\n🔧 Preparing training data (max_length={max_length})...")
    
    def tokenize_function(examples):
        # Handle different dataset formats
        if 'text' in examples:
            # For wikitext format
            texts = examples['text']
        elif 'instruction' in examples and 'code' in examples:
            # For instruction-code format
            texts = [f"Instruction: {inst}\nCode: {code}" 
                    for inst, code in zip(examples['instruction'], examples['code'])]
        else:
            # Fallback
            texts = [str(ex) for ex in examples.values()]
        
        # Tokenize
        tokenized = tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=max_length,
            return_tensors="pt"
        )
        
        # For causal LM, labels are the same as input_ids
        tokenized["labels"] = tokenized["input_ids"].clone()
        
        return tokenized
    
    # Tokenize dataset
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names
    )
    
    print(f"✅ Tokenized dataset ready:")
    print(f"   - Input shape: {tokenized_dataset[0]['input_ids'].shape}")
    print(f"   - Attention mask shape: {tokenized_dataset[0]['attention_mask'].shape}")
    
    return tokenized_dataset

def setup_lora_model(model_name="microsoft/DialoGPT-small"):
    """Set up LoRA model for efficient fine-tuning"""
    print(f"\n🎯 Setting up LoRA model: {model_name}")
    
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None
    )
    
    # Configure LoRA
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=16,  # Rank
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj"]  # Target attention layers
    )
    
    # Apply LoRA
    model = get_peft_model(model, lora_config)
    
    print(f"✅ LoRA model ready:")
    print(f"   - Trainable parameters: {model.print_trainable_parameters()}")
    
    return model, tokenizer

def train_model(model, tokenized_dataset, tokenizer, output_dir="./hf_training_output"):
    """Train the model with Hugging Face Trainer"""
    print(f"\n🚀 Starting training...")
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False  # Causal LM, not masked LM
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        num_train_epochs=1,
        logging_steps=10,
        save_steps=100,
        evaluation_strategy="no",
        save_strategy="steps",
        load_best_model_at_end=False,
        report_to=None,  # Disable wandb/tensorboard
        remove_unused_columns=False,
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset.select(range(100)),  # Use subset for demo
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
    
    # Train
    print("🔥 Training started...")
    trainer.train()
    
    # Save model
    trainer.save_model()
    tokenizer.save_pretrained(output_dir)
    
    print(f"✅ Training completed! Model saved to {output_dir}")
    
    return trainer

def main():
    """Main function demonstrating the complete pipeline"""
    print("🚀 Hugging Face Datasets & Training Example")
    print("=" * 50)
    
    # 1. Load and explore datasets
    hf_dataset = load_and_explore_dataset()
    custom_dataset = create_custom_dataset()
    
    # 2. Set up model and tokenizer
    model, tokenizer = setup_lora_model()
    
    # 3. Prepare training data
    tokenized_dataset = prepare_training_data(custom_dataset, tokenizer)
    
    # 4. Train model
    trainer = train_model(model, tokenized_dataset, tokenizer)
    
    print("\n🎉 Complete pipeline executed successfully!")
    print("\nNext steps:")
    print("1. Load your custom dataset")
    print("2. Adjust LoRA parameters for your use case")
    print("3. Fine-tune on your specific domain")
    print("4. Convert to Ollama format for deployment")

if __name__ == "__main__":
    main()
