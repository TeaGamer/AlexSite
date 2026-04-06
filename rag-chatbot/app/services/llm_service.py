"""Local LLM service using Hugging Face Transformers"""
from typing import List, Optional
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    pipeline
)
from app.config import settings
import os


class LLMService:
    """Service for local LLM interactions using Hugging Face models"""
    
    def __init__(
        self, 
        model_name: str = None,
        device: str = None,
        cache_dir: str = None
    ):
        """Initialize local LLM"""
        self.model_name = model_name or settings.llm_model_name
        self.device = device or settings.device
        self.cache_dir = cache_dir or settings.models_cache_dir
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        print(f"Loading model: {self.model_name}...")
        print(f"Using device: {self.device}")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                trust_remote_code=True
            )
            
            # If tokenizer doesn't have pad token, set it
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            if self.device != "cuda":
                self.model.to(self.device)
            
            self.model.eval()
            print("Model loaded successfully!")
            
        except Exception as e:
            raise Exception(f"Error loading model: {str(e)}")
    
    def generate_text(
        self, 
        prompt: str,
        max_new_tokens: int = None,
        temperature: float = None,
        top_p: float = None
    ) -> str:
        """
        Generate text from a prompt
        
        Args:
            prompt: Input prompt
            max_new_tokens: Maximum new tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
        
        Returns:
            Generated text
        """
        if max_new_tokens is None:
            max_new_tokens = settings.max_new_tokens
        if temperature is None:
            temperature = settings.temperature
        if top_p is None:
            top_p = settings.top_p
        
        try:
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )
            
            generated_text = self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            )
            
            # Remove the prompt from the output
            return generated_text[len(prompt):].strip()
        
        except Exception as e:
            raise Exception(f"Error generating text: {str(e)}")
    
    def generate_response(
        self,
        question: str,
        context: str,
        system_prompt: str = None
    ) -> str:
        """
        Generate response using the LLM with context (RAG)
        
        Args:
            question: User's question
            context: Retrieved context from RAG
            system_prompt: Optional custom system prompt
        
        Returns:
            Generated response
        """
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()
        
        # Build the full prompt
        full_prompt = f"""{system_prompt}

Context:
{context}

Question: {question}

Answer:"""
        
        try:
            response = self.generate_text(full_prompt)
            return response.strip()
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
    
    def generate_response_with_history(
        self,
        messages: List[dict],
        system_prompt: str = None
    ) -> str:
        """
        Generate response with conversation history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional custom system prompt
        
        Returns:
            Generated response
        """
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()
        
        # Build conversation prompt
        conversation = f"{system_prompt}\n\n"
        
        for msg in messages:
            role = msg.get("role", "user").upper()
            content = msg.get("content", "")
            conversation += f"{role}: {content}\n"
        
        conversation += "ASSISTANT:"
        
        try:
            response = self.generate_text(conversation)
            return response.strip()
        except Exception as e:
            raise Exception(f"Error generating response with history: {str(e)}")
    
    @staticmethod
    def _get_default_system_prompt() -> str:
        """Get default system prompt for the chatbot"""
        return """You are a helpful AI assistant specializing in answering questions about university study programs and curricula.

Your responsibilities:
1. Answer questions about courses, requirements, and program structure
2. Provide detailed and accurate information based on the provided context
3. If information is not available in the context, clearly state that
4. Be helpful, professional, and student-friendly
5. Clarify confusing points and provide examples when needed

Always cite the source material when providing information."""


class EmbeddingService:
    """Service for generating embeddings using Sentence Transformers"""
    
    def __init__(
        self,
        model_name: str = None,
        device: str = None,
        cache_dir: str = None
    ):
        """Initialize embedding service"""
        self.model_name = model_name or settings.embedding_model_name
        self.device = device or settings.device
        self.cache_dir = cache_dir or settings.models_cache_dir
        
        os.makedirs(self.cache_dir, exist_ok=True)
        
        print(f"Loading embedding model: {self.model_name}...")
        
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(
                self.model_name,
                cache_folder=self.cache_dir,
                device=self.device
            )
            print("Embedding model loaded successfully!")
        except Exception as e:
            raise Exception(f"Error loading embedding model: {str(e)}")
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text"""
        try:
            embedding = self.model.encode(
                text,
                convert_to_tensor=False,
                show_progress_bar=False
            )
            return embedding.tolist()
        except Exception as e:
            raise Exception(f"Error getting embedding: {str(e)}")
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts in batch"""
        try:
            embeddings = self.model.encode(
                texts,
                convert_to_tensor=False,
                show_progress_bar=True,
                batch_size=32
            )
            return embeddings.tolist()
        except Exception as e:
            raise Exception(f"Error getting batch embeddings: {str(e)}")


# Global instances
_llm_service = None
_embedding_service = None


def get_llm_service() -> LLMService:
    """Get or create LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
