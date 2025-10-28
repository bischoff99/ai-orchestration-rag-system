#!/usr/bin/env python3
"""
Complete Training Pipeline with Hugging Face + MCP Tools
Demonstrates end-to-end model training and deployment
"""

import os
import json
import torch
from datasets import load_dataset, Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_training_data():
    """Load and prepare training data from multiple sources"""
    print("📊 Loading Training Data")
    print("=" * 30)
    
    # Load Python codes dataset (small sample)
    print("🐍 Loading Python Codes 25K dataset...")
    python_dataset = load_dataset('flytech/python-codes-25k', split='train[:100]')
    
    # Convert to our format
    training_examples = []
    for example in python_dataset:
        training_examples.append({
            "instruction": example["instruction"],
            "input": example["input"],
            "output": example["output"]
        })
    
    print(f"✅ Loaded {len(training_examples)} examples from Python dataset")
    
    # Add our custom examples
    custom_examples = [
        {
            "instruction": "Write a Python function to calculate the factorial of a number",
            "input": "n = 5",
            "output": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n\nresult = factorial(5)\nprint(result)  # Output: 120"
        },
        {
            "instruction": "Create a JavaScript function to reverse a string",
            "input": "str = 'hello'",
            "output": "function reverseString(str) {\n    return str.split('').reverse().join('');\n}\n\nconsole.log(reverseString('hello'));  // Output: olleh"
        }
    ]
    
    training_examples.extend(custom_examples)
    
    # Save combined dataset
    with open("/Users/andrejsp/ai/datasets/combined_training.json", "w") as f:
        json.dump(training_examples, f, indent=2)
    
    print(f"✅ Total training examples: {len(training_examples)}")
    print(f"💾 Saved to: /Users/andrejsp/ai/datasets/combined_training.json")
    
    return training_examples

def setup_model_and_tokenizer():
    """Set up model and tokenizer for training"""
    print("\n🤖 Setting up Model and Tokenizer")
    print("=" * 35)
    
    # Use a smaller model for faster training
    model_name = "microsoft/DialoGPT-small"
    
    print(f"📥 Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    # Set pad token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    print(f"✅ Model loaded: {model.num_parameters():,} parameters")
    print(f"✅ Tokenizer vocab size: {tokenizer.vocab_size:,}")
    
    return model, tokenizer

def setup_lora(model):
    """Set up LoRA for efficient fine-tuning"""
    print("\n🔧 Setting up LoRA")
    print("=" * 20)
    
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,  # Rank
        lora_alpha=32,  # Scaling factor
        target_modules=["c_attn"],  # Target attention modules
        lora_dropout=0.1,
        bias="none"
    )
    
    model = get_peft_model(model, lora_config)
    
    # Print trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    
    print(f"✅ LoRA configured")
    print(f"📊 Trainable parameters: {trainable_params:,}")
    print(f"📊 Total parameters: {total_params:,}")
    print(f"📊 Trainable %: {100 * trainable_params / total_params:.2f}%")
    
    return model

def prepare_dataset(training_examples, tokenizer):
    """Prepare dataset for training"""
    print("\n📋 Preparing Dataset")
    print("=" * 25)
    
    # Convert to Hugging Face dataset
    dataset = Dataset.from_list(training_examples)
    
    def tokenize_function(examples):
        # Create training text
        texts = []
        for inst, inp, out in zip(examples['instruction'], examples['input'], examples['output']):
            if inp.strip():
                text = f"Instruction: {inst}\nInput: {inp}\nOutput: {out}"
            else:
                text = f"Instruction: {inst}\nOutput: {out}"
            texts.append(text)
        
        # Tokenize
        tokenized = tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=256,  # Shorter for faster training
            return_tensors="pt"
        )
        
        # Set labels for causal LM
        tokenized["labels"] = tokenized["input_ids"].clone()
        
        return tokenized
    
    # Tokenize dataset
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    
    print(f"✅ Dataset tokenized")
    print(f"📊 Examples: {len(tokenized_dataset)}")
    print(f"📊 Max length: 256 tokens")
    
    return tokenized_dataset

def train_model(model, tokenizer, tokenized_dataset):
    """Train the model"""
    print("\n🚀 Starting Training")
    print("=" * 25)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="/Users/andrejsp/ai/models/trained_code_assistant",
        per_device_train_batch_size=2,
        num_train_epochs=1,  # Quick training
        logging_steps=5,
        save_steps=50,
        evaluation_strategy="no",
        report_to=None,
        remove_unused_columns=False,
        dataloader_pin_memory=False,
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
    print("🏃 Training started...")
    trainer.train()
    
    # Save model
    trainer.save_model()
    tokenizer.save_pretrained("/Users/andrejsp/ai/models/trained_code_assistant")
    
    print("✅ Training completed!")
    print(f"💾 Model saved to: /Users/andrejsp/ai/models/trained_code_assistant")
    
    return trainer

def test_model(model, tokenizer):
    """Test the trained model"""
    print("\n🧪 Testing Model")
    print("=" * 20)
    
    # Test prompts
    test_prompts = [
        "Instruction: Write a Python function to calculate the area of a circle",
        "Instruction: Create a JavaScript function to check if a number is prime",
        "Instruction: Write a SQL query to find the average salary by department"
    ]
    
    for prompt in test_prompts:
        print(f"\n📝 Prompt: {prompt}")
        
        # Tokenize input
        inputs = tokenizer(prompt, return_tensors="pt")
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_length=inputs.input_ids.shape[1] + 100,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"🤖 Response: {response[len(prompt):].strip()[:200]}...")

def create_ollama_modelfile():
    """Create Ollama Modelfile for the trained model"""
    print("\n🚀 Creating Ollama Modelfile")
    print("=" * 35)
    
    modelfile_content = '''FROM /Users/andrejsp/ai/models/trained_code_assistant
PARAMETER temperature 0.1
PARAMETER top_p 0.95
PARAMETER num_ctx 2048
PARAMETER num_batch 128
PARAMETER repeat_penalty 1.1
PARAMETER repeat_last_n 64
PARAMETER top_k 40
PARAMETER min_p 0.05
PARAMETER num_predict 512
SYSTEM You are an expert programming assistant. Provide clear, efficient, and well-documented code solutions with best practices and optimization techniques. Focus on security, performance, and maintainability.
'''
    
    with open("/Users/andrejsp/ai/models/trained_code_assistant/Modelfile", "w") as f:
        f.write(modelfile_content)
    
    print("✅ Modelfile created")
    print("📝 To create Ollama model: ollama create code-assistant -f /Users/andrejsp/ai/models/trained_code_assistant/Modelfile")

def main():
    """Main training pipeline"""
    print("🚀 Complete Training Pipeline")
    print("=" * 40)
    
    try:
        # 1. Load training data
        training_examples = load_training_data()
        
        # 2. Set up model and tokenizer
        model, tokenizer = setup_model_and_tokenizer()
        
        # 3. Set up LoRA
        model = setup_lora(model)
        
        # 4. Prepare dataset
        tokenized_dataset = prepare_dataset(training_examples, tokenizer)
        
        # 5. Train model
        trainer = train_model(model, tokenizer, tokenized_dataset)
        
        # 6. Test model
        test_model(model, tokenizer)
        
        # 7. Create Ollama Modelfile
        create_ollama_modelfile()
        
        print(f"\n🎉 Training Pipeline Complete!")
        print(f"\n📋 Next Steps:")
        print(f"1. 🚀 Create Ollama model: ollama create code-assistant -f /Users/andrejsp/ai/models/trained_code_assistant/Modelfile")
        print(f"2. 🧪 Test: ollama run code-assistant 'Write a Python function to sort a list'")
        print(f"3. 📤 Upload to HF: huggingface-cli upload bischoff555/code-assistant /Users/andrejsp/ai/models/trained_code_assistant")
        print(f"4. 🔍 Use MCP tools to find more datasets and models")
        
    except Exception as e:
        logger.error(f"❌ Error in training pipeline: {e}")
        raise

if __name__ == "__main__":
    main()
