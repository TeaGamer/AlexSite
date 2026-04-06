"""Fine-tuning utilities for local LLM"""
import json
from pathlib import Path
from typing import List, Dict, Optional
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TextDataset,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments
)
from app.config import settings


class FineTuner:
    """Fine-tuning utility for Llama or other causal LM models"""
    
    def __init__(
        self,
        model_name: str = None,
        cache_dir: str = None
    ):
        """Initialize fine-tuner"""
        self.model_name = model_name or settings.llm_model_name
        self.cache_dir = cache_dir or settings.models_cache_dir
        self.device = settings.device
        
        print(f"Loading model for fine-tuning: {self.model_name}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            cache_dir=self.cache_dir,
            trust_remote_code=True
        )
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            cache_dir=self.cache_dir,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
    
    def prepare_training_data(
        self,
        data: List[Dict],
        output_file: str,
        question_key: str = "question",
        answer_key: str = "answer"
    ) -> str:
        """
        Prepare training data in the format suitable for fine-tuning
        
        Args:
            data: List of dicts with question-answer pairs
            output_file: Output file path
            question_key: Key for questions in data
            answer_key: Key for answers in data
        
        Returns:
            Path to output file
        """
        training_texts = []
        
        for item in data:
            if question_key in item and answer_key in item:
                question = item[question_key]
                answer = item[answer_key]
                
                # Format: "Q: ... A: ..."
                text = f"Q: {question}\nA: {answer}\n"
                training_texts.append(text)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            for text in training_texts:
                f.write(text)
        
        print(f"Prepared {len(training_texts)} training examples")
        return output_file
    
    def fine_tune(
        self,
        training_file: str,
        output_dir: str = "./fine_tuned_model",
        num_epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-5,
        max_steps: int = -1
    ):
        """
        Fine-tune the model
        
        Args:
            training_file: Path to training file
            output_dir: Directory to save fine-tuned model
            num_epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate
            max_steps: Maximum training steps (-1 for no limit)
        """
        # Load dataset
        dataset = TextDataset(
            tokenizer=self.tokenizer,
            file_path=training_file,
            block_size=512
        )
        
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            overwrite_output_dir=True,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            save_steps=500,
            save_total_limit=2,
            logging_steps=100,
            learning_rate=learning_rate,
            weight_decay=0.01,
            warmup_steps=100,
            fp16=self.device == "cuda",
            max_steps=max_steps
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=dataset,
        )
        
        print("Starting fine-tuning...")
        trainer.train()
        
        # Save model
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        print(f"Fine-tuning completed! Model saved to {output_dir}")
        return output_dir
    
    @staticmethod
    def load_fine_tuned_model(model_dir: str, device: str = None):
        """Load fine-tuned model"""
        if device is None:
            device = settings.device
        
        tokenizer = AutoTokenizer.from_pretrained(model_dir)
        model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto" if device == "cuda" else None,
        )
        
        if device != "cuda":
            model.to(device)
        
        return tokenizer, model


def create_sample_training_data(output_file: str = "sample_training_data.json"):
    """
    Create sample training data structure
    
    Args:
        output_file: Path to save sample data
    """
    sample_data = [
        {
            "question": "What courses are required for the first year?",
            "answer": "First year students typically take foundational courses in mathematics, programming, and general education courses."
        },
        {
            "question": "How many credits are needed to graduate?",
            "answer": "Most undergraduate programs require 120-130 credits for graduation, with specific requirements varying by major."
        },
        {
            "question": "Is internship mandatory?",
            "answer": "Internship requirements vary by program. Some programs require an internship, while others offer it as an elective option."
        },
        {
            "question": "What is the capstone project?",
            "answer": "The capstone project is a major final year requirement where students apply their learning to solve a real-world problem."
        },
        {
            "question": "How many courses per semester?",
            "answer": "Students typically take 4-5 courses per semester, amounting to 12-15 credit hours."
        }
    ]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    print(f"Sample training data created: {output_file}")
