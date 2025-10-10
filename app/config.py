import os
from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings following Single Responsibility Principle"""
    
    # OpenAI Configuration
    openai_api_key: str
    
    # Application Configuration
    app_name: str = "Bank Statement Parser"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "localhost"
    port: int = 8000
    
    # File Processing Configuration
    max_file_size_mb: int = 10
    allowed_file_types: List[str] = ["pdf"]
    
    # LLM Configuration
    model_name: str = "gpt-4-vision-preview"
    max_tokens: int = 4000
    temperature: float = 0.1
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton pattern for settings
_settings = None

def get_settings() -> Settings:
    """Get application settings (Singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings