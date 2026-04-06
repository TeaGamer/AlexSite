"""Configuration module for RAG Chatbot"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Local LLM Model
    llm_model_name: str = "meta-llama/Llama-2-7b-hf"  # From Hugging Face
    embedding_model_name: str = "sentence-transformers/distilbert-base-uncased"
    
    # Model Parameters
    device: str = "cpu"  # or "cuda" if GPU available
    max_new_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9

    # Vector Database
    vector_db_type: str = "chroma"
    chroma_path: str = "./vector_store"
    models_cache_dir: str = "./models_cache"

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
