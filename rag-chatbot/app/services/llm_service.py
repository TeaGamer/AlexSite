"""LLM service using external API (OpenAI, Anthropic, Cohere, etc.)"""
from typing import List, Optional
import os
from app.config import settings


class LLMService:
    """Service for LLM interactions using external API"""
    
    def __init__(
        self, 
        provider: str = None,
        model_name: str = None,
        api_key: str = None
    ):
        """Initialize LLM API client"""
        self.provider = provider or settings.llm_provider
        self.model_name = model_name or settings.llm_model_name
        self.api_key = api_key or settings.llm_api_key
        
        if not self.api_key:
            raise ValueError(f"No API key provided for {self.provider}. Set LLM_API_KEY environment variable.")
        
        print(f"Initializing {self.provider.upper()} LLM service...")
        print(f"Using model: {self.model_name}")
        
        if self.provider.lower() == "openai":
            self._init_openai()
        elif self.provider.lower() == "anthropic":
            self._init_anthropic()
        elif self.provider.lower() == "cohere":
            self._init_cohere()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            import openai
            openai.api_key = self.api_key
            self.client = openai
            print("OpenAI client initialized successfully!")
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")
        except Exception as e:
            raise Exception(f"Error initializing OpenAI: {str(e)}")
    
    def _init_anthropic(self):
        """Initialize Anthropic (Claude) client"""
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            print("Anthropic client initialized successfully!")
        except ImportError:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")
        except Exception as e:
            raise Exception(f"Error initializing Anthropic: {str(e)}")
    
    def _init_cohere(self):
        """Initialize Cohere client"""
        try:
            import cohere
            self.client = cohere.Client(api_key=self.api_key)
            print("Cohere client initialized successfully!")
        except ImportError:
            raise ImportError("cohere package not installed. Install with: pip install cohere")
        except Exception as e:
            raise Exception(f"Error initializing Cohere: {str(e)}")
    
    def generate_text(
        self, 
        prompt: str,
        max_tokens: int = None,
        temperature: float = None,
        top_p: float = None
    ) -> str:
        """
        Generate text from a prompt
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
        
        Returns:
            Generated text
        """
        if max_tokens is None:
            max_tokens = settings.max_tokens
        if temperature is None:
            temperature = settings.temperature
        if top_p is None:
            top_p = settings.top_p
        
        try:
            if self.provider.lower() == "openai":
                return self._generate_openai(prompt, max_tokens, temperature, top_p)
            elif self.provider.lower() == "anthropic":
                return self._generate_anthropic(prompt, max_tokens, temperature, top_p)
            elif self.provider.lower() == "cohere":
                return self._generate_cohere(prompt, max_tokens, temperature, top_p)
        except Exception as e:
            raise Exception(f"Error generating text: {str(e)}")
    
    def _generate_openai(self, prompt: str, max_tokens: int, temperature: float, top_p: float) -> str:
        """Generate text using OpenAI API"""
        response = self.client.ChatCompletion.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )
        return response.choices[0].message.content.strip()
    
    def _generate_anthropic(self, prompt: str, max_tokens: int, temperature: float, top_p: float) -> str:
        """Generate text using Anthropic API"""
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    
    def _generate_cohere(self, prompt: str, max_tokens: int, temperature: float, top_p: float) -> str:
        """Generate text using Cohere API"""
        response = self.client.generate(
            model=self.model_name,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            p=top_p
        )
        return response.generations[0].text.strip()
    
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
        Generate response with conversation history (for OpenAI/Anthropic)
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional custom system prompt
        
        Returns:
            Generated response
        """
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()
        
        try:
            if self.provider.lower() == "openai":
                return self._generate_with_history_openai(messages, system_prompt)
            elif self.provider.lower() == "anthropic":
                return self._generate_with_history_anthropic(messages, system_prompt)
            else:
                # Fallback for Cohere
                conversation = f"{system_prompt}\n\n"
                for msg in messages:
                    role = msg.get("role", "user").upper()
                    content = msg.get("content", "")
                    conversation += f"{role}: {content}\n"
                return self.generate_text(conversation)
        except Exception as e:
            raise Exception(f"Error generating response with history: {str(e)}")
    
    def _generate_with_history_openai(self, messages: List[dict], system_prompt: str) -> str:
        """Generate with history using OpenAI API"""
        formatted_messages = [{"role": "system", "content": system_prompt}]
        formatted_messages.extend(messages)
        
        response = self.client.ChatCompletion.create(
            model=self.model_name,
            messages=formatted_messages,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
            top_p=settings.top_p
        )
        return response.choices[0].message.content.strip()
    
    def _generate_with_history_anthropic(self, messages: List[dict], system_prompt: str) -> str:
        """Generate with history using Anthropic API"""
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
            system=system_prompt,
            messages=messages
        )
        return response.content[0].text.strip()
    
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
