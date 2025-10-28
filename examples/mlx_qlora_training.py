#!/usr/bin/env python3
"""
MLX QLoRA Training Example for Apple Silicon
Demonstrates efficient fine-tuning using MLX and QLoRA
"""

import mlx.core as mx
import mlx.nn as nn
from mlx_lm import load, generate, lora
from mlx_lm.tuner import lora as lora_tuner
from datasets import load_dataset
import json
import argparse

def load_mlx_model(model_name="mlx-community/Llama-3.2-3B-Instruct-4bit"):
    """Load a quantized model optimized for MLX"""
    print(f"🔄 Loading MLX model: {model_name}")
    
    # Load the model and tokenizer
    model, tokenizer = load(model_name)
    
    print(f"✅ Model loaded successfully")
    print(f"   - Model type: {type(model)}")
    print(f"   - Vocab size: {tokenizer.vocab_size}")
    
    return model, tokenizer

def prepare_mlx_dataset():
    """Prepare a dataset for MLX training"""
    print("📊 Preparing dataset for MLX training...")
    
    # Load a small dataset for demonstration
    dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="train[:1000]")
    
    # Convert to MLX format
    texts = [item["text"] for item in dataset if len(item["text"].strip()) > 0]
    
    print(f"✅ Dataset prepared:")
    print(f"   - Number of texts: {len(texts)}")
    print(f"   - Sample text: {texts[0][:100]}...")
    
    return texts

def setup_lora_for_mlx(model, lora_layers=16, lora_rank=8, lora_alpha=16):
    """Set up LoRA for MLX model"""
    print(f"🎯 Setting up LoRA for MLX:")
    print(f"   - LoRA layers: {lora_layers}")
    print(f"   - LoRA rank: {lora_rank}")
    print(f"   - LoRA alpha: {lora_alpha}")
    
    # Configure LoRA
    lora_config = {
        "lora_layers": lora_layers,
        "lora_rank": lora_rank,
        "lora_alpha": lora_alpha,
        "lora_dropout": 0.05,
        "lora_scale": 10.0
    }
    
    # Apply LoRA to model
    model = lora.apply_lora(model, **lora_config)
    
    print("✅ LoRA applied to model")
    return model, lora_config

def train_mlx_model(model, tokenizer, texts, output_dir="./mlx_training_output"):
    """Train the MLX model with LoRA"""
    print("🚀 Starting MLX training...")
    
    # Prepare training data
    train_data = []
    for text in texts[:100]:  # Use subset for demo
        if len(text.strip()) > 10:  # Filter very short texts
            train_data.append(text)
    
    print(f"📝 Training on {len(train_data)} examples")
    
    # Training configuration
    training_config = {
        "model": model,
        "tokenizer": tokenizer,
        "train": train_data,
        "valid": train_data[:10],  # Small validation set
        "batch_size": 2,
        "iters": 100,  # Number of training iterations
        "val_batches": 5,
        "learning_rate": 1e-4,
        "steps_per_report": 10,
        "steps_per_eval": 50,
        "resume_adapter_file": None,
        "adapter_path": output_dir,
        "save_every": 25,
        "test": False,
        "test_batches": 0,
        "grad_checkpoint": True,
        "seed": 42,
    }
    
    # Run training
    print("🔥 Training started...")
    try:
        lora_tuner.train(**training_config)
        print(f"✅ Training completed! Adapter saved to {output_dir}")
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return None
    
    return output_dir

def test_trained_model(model_path, tokenizer, prompt="Write a Python function to calculate factorial:"):
    """Test the trained model"""
    print(f"\n🧪 Testing trained model with prompt: '{prompt}'")
    
    try:
        # Load the trained adapter
        model, _ = load(model_path)
        
        # Generate response
        response = generate(
            model, 
            tokenizer, 
            prompt=prompt,
            max_tokens=200,
            temp=0.7
        )
        
        print(f"🤖 Model response:")
        print(f"   {response}")
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")

def create_training_script():
    """Create a standalone training script"""
    script_content = '''#!/usr/bin/env python3
"""
Standalone MLX QLoRA Training Script
Usage: python train_mlx_qlora.py --model microsoft/DialoGPT-small --data your_dataset.json
"""

import argparse
import json
from mlx_lm import load, lora
from mlx_lm.tuner import lora as lora_tuner

def main():
    parser = argparse.ArgumentParser(description="Train MLX model with QLoRA")
    parser.add_argument("--model", default="mlx-community/Llama-3.2-3B-Instruct-4bit", 
                       help="Model name or path")
    parser.add_argument("--data", required=True, help="Path to training data JSON file")
    parser.add_argument("--output", default="./mlx_output", help="Output directory")
    parser.add_argument("--epochs", type=int, default=3, help="Number of epochs")
    parser.add_argument("--batch_size", type=int, default=2, help="Batch size")
    parser.add_argument("--learning_rate", type=float, default=1e-4, help="Learning rate")
    
    args = parser.parse_args()
    
    # Load model
    print(f"Loading model: {args.model}")
    model, tokenizer = load(args.model)
    
    # Load data
    with open(args.data, 'r') as f:
        data = json.load(f)
    
    # Apply LoRA
    model = lora.apply_lora(model, lora_layers=16, lora_rank=8, lora_alpha=16)
    
    # Train
    lora_tuner.train(
        model=model,
        tokenizer=tokenizer,
        train=data,
        valid=data[:10],
        batch_size=args.batch_size,
        iters=args.epochs * len(data) // args.batch_size,
        learning_rate=args.learning_rate,
        adapter_path=args.output
    )
    
    print(f"Training completed! Model saved to {args.output}")

if __name__ == "__main__":
    main()
'''
    
    with open("/Users/andrejsp/ai/examples/train_mlx_qlora.py", "w") as f:
        f.write(script_content)
    
    print("📝 Created standalone training script: train_mlx_qlora.py")

def main():
    """Main function demonstrating MLX QLoRA training"""
    print("🚀 MLX QLoRA Training Example")
    print("=" * 40)
    
    # 1. Load MLX model
    model, tokenizer = load_mlx_model()
    
    # 2. Prepare dataset
    texts = prepare_mlx_dataset()
    
    # 3. Set up LoRA
    model, lora_config = setup_lora_for_mlx(model)
    
    # 4. Train model
    output_dir = train_mlx_model(model, tokenizer, texts)
    
    # 5. Test trained model
    if output_dir:
        test_trained_model(output_dir, tokenizer)
    
    # 6. Create standalone script
    create_training_script()
    
    print("\n🎉 MLX QLoRA example completed!")
    print("\nNext steps:")
    print("1. Use your own dataset in JSON format")
    print("2. Adjust LoRA parameters for your model size")
    print("3. Convert trained model to Ollama format")
    print("4. Deploy with your optimized Ollama setup")

if __name__ == "__main__":
    main()
