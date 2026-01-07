"""Configuration management for the marketing platform."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = "postgresql://user:password@localhost:5432/marketing_cdp"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # API Keys - Marketing Platforms
    youtube_api_key: Optional[str] = None
    instagram_access_token: Optional[str] = None
    facebook_access_token: Optional[str] = None
    facebook_app_id: Optional[str] = None
    facebook_app_secret: Optional[str] = None
    
    # Email/SMS APIs
    sendgrid_api_key: Optional[str] = None
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    
    # LLM Configuration (Free Tier)
    llm_provider: str = "ollama"  # ollama, groq, huggingface
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    groq_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    
    # JWT Secret for Authentication
    jwt_secret_key: str = "change-this-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Encryption Key for Stored Credentials (32 bytes for AES-256)
    encryption_key: Optional[str] = None
    
    # Application Settings
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    streamlit_port: int = 8501
    
    # Celery Configuration
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set Celery URLs if not explicitly provided
        if not self.celery_broker_url:
            self.celery_broker_url = self.redis_url
        if not self.celery_result_backend:
            self.celery_result_backend = self.redis_url


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

