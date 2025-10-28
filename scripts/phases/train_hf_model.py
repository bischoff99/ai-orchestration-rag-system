#!/usr/bin/env python3
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
        texts = [f"Instruction: {inst}\nCode: {out}" 
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
