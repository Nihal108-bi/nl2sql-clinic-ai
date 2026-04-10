"""
app/core/config.py
Centralised configuration using pydantic-settings.
All settings are read from environment variables / .env file.
"""

import os
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ── LLM Provider ──────────────────────────────────────────────────────
    # Change LLM_PROVIDER to "groq", "openai", or "ollama" if you prefer those options.
    LLM_PROVIDER: str = Field(default="gemini", description="gemini | groq | openai | ollama")

    # Google Gemini
    GOOGLE_API_KEY: str = Field(default="", description="Google AI Studio API key")
    GEMINI_MODEL: str = Field(default="gemini-1.5-flash")

    # Groq
    GROQ_API_KEY: str = Field(default="", description="Groq API key")
    GROQ_MODEL: str = Field(default="llama-3.1-8b-instant")

    # OpenAI
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-4.1-mini")

    # Ollama (local)
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434/v1")
    OLLAMA_MODEL: str = Field(default="llama3")

    # ── Database ──────────────────────────────────────────────────────────
    DB_PATH: str = Field(default="clinic.db")

    # ── App ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = Field(default="INFO")
    CACHE_TTL_SECONDS: int = Field(default=300)   # 5-minute query cache
    RATE_LIMIT: str = Field(default="10/minute")  # per-IP rate limit

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
