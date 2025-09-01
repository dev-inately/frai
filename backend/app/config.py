"""
Configuration management for the AI Contract Generator backend.
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # AI Provider Configuration
    openai_api_key: str = Field(default="test-key", description="OpenAI API key")
    # anthropic_api_key: str = Field(default="test-key", description="Anthropic API key")
    ai_base_url: str = Field(default="https://openrouter.ai/api/v1", description="Base URL for OpenAI API")
    
    # API Configuration
    cors_origins: List[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=10,
        description="Maximum requests per minute per IP"
    )
    
    # AI Model Configuration
    default_model: str = Field(
        default="openai/gpt-4o-mini",
        description="Default AI model for contract generation"
    )
    
    # Contract Generation
    max_tokens_per_section: int = Field(
        default=100000,
        description="Maximum tokens per contract section"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
