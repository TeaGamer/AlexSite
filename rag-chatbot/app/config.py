"""Configuration module for RAG Chatbot"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # LLM Configuration (Using API)
    llm_provider: str = "openai"  # openai, anthropic, or cohere
    llm_api_key: str = ""  # Set via environment variable
    llm_model_name: str = "gpt-3.5-turbo"  # OpenAI model
    
    # Embedding Model (Local)
    embedding_model_name: str = "sentence-transformers/distilbert-base-uncased"
    
    # Model Parameters
    device: str = "cpu"  # for embeddings
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9

    # Vector Database
    vector_db_type: str = "chroma"
    chroma_path: str = "./vector_store"

    # FastAPI
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Environment
    environment: str = "development"

    # Document Processing
    max_upload_size_mb: int = 50
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Dataset
    dataset_path: str = "./datasets"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
