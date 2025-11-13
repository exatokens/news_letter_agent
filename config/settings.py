from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from pathlib import Path
import os
from dotenv import load_dotenv


# Load .env file from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    # API Keys
    GROQ_API_KEY: Optional[str] = Field(
        default=None,
        description="Groq API key for Llama models"
    )
    NEWSDATA_API_KEY: str = Field(description="NewsData API key")

    # Model Configuration
    LLM_MODEL: str = Field(
        default="llama-3.3-70b-versatile",
        description="model to use"
    )
    LLM_TEMPERATURE: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="LLM temperature"
    )
    LLM_MAX_TOKENS: int = Field(
        default=4096,
        gt=0,
        description="Maximum tokens for LLM response"
    )

    # Agent Configuration
    MAX_ARTICLES_PER_FETCH: int = Field(
        default=10,
        gt=0,
        description="Maximum articles to fetch per request"
    )
    TOP_ARTICLES_TO_SELECT: int = Field(
        default=5,
        gt=0,
        description="Number of top articles to select"
    )

    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )

    # class Config:
    #     env_file = ".env"
    #     env_file_encoding = "utf-8"
    #     case_sensitive = True
        
    # def __init__(self, **kwargs):
    #     """Initialize settings and validate"""
    #     super().__init__(**kwargs)
    #     self._validate_settings()
    
    # def _validate_settings(self):
    #     """Validate critical settings"""
    #     if not self.GROQ_API_KEY or self.GROQ_API_KEY == "your_groq_key_here":
    #         raise ValueError(
    #             "GROQ_API_KEY not set! Please set it in .env file:\n"
    #             "GROQ_API_KEY=actual_key_here"
    #         )


# Global settings instance
try:
    settings = Settings()
    print(f"Settings loaded successfully from {env_path}")
    print(f"LLM Model: {settings.LLM_MODEL}")
    print(f"Log Level: {settings.LOG_LEVEL}")
    print(f"Max Articles: {settings.MAX_ARTICLES_PER_FETCH}")
except Exception as e:
    print(f"ERROR: Error loading settings: {e}")
    raise

