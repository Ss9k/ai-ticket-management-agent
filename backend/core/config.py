"""
SupportPilot Backend Configuration
Reads from environment variables / .env file
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "SupportPilot"
    debug: bool = False

    # Security
    secret_key: str = "changeme-super-secret-key"

    # Database
    database_url: str = "sqlite:///./supportpilot.db"

    # LLM API Keys
    groq_api_key: str = ""
    gemini_api_key: str = ""
    openrouter_api_key: str = ""

    # LLM Configuration
    llm_max_retries: int = 2
    llm_temperature: float = 0.2
    llm_max_tokens: int = 800

    # RAG Configuration
    faiss_index_path: str = "backend/rag/faiss_index.index"
    faiss_metadata_path: str = "backend/rag/faiss_metadata.pkl"
    docs_path: str = "docs/"
    embedding_model: str = "all-MiniLM-L6-v2"
    top_k_results: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
