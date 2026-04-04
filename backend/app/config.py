"""
Configuration settings loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from .env file."""
    
    # API Security
    api_key: str = "default-dev-key-change-me"
    
    # Environment
    environment: str = "development"
    
    # File Processing Limits
    max_file_size_mb: int = 10
    
    # App Info
    app_name: str = "DocuMind AI"
    app_version: str = "1.0.0"
    app_description: str = "AI-Powered Document Analysis & Extraction API"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Returns cached settings instance."""
    return Settings()
