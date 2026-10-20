import os
from typing import Any, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration with environment variable overrides.
    Uses Pydantic v2 settings management.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Core Application Settings
    PROJECT_NAME: str = "Autonomous E-Commerce Operations Copilot"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v: Any) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.strip().lower() in ("true", "1", "yes", "on", "debug", "dev", "development")
        return bool(v)

    # Database
    DATABASE_URL: str

    # LLM Provider (Groq)
    GROQ_API_KEY: str
    PRIMARY_MODEL: str = "qwen/qwen3.8-27b"
    FALLBACK_MODEL: str = "openai/gpt-oss-120b"
    TEMPERATURE: float = 0.0
    MAX_RETRIES: int = 2

    # RAG & Embeddings
    CHROMA_PERSIST_DIRECTORY: str = "chroma_db"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

    # MCP Tool Server
    MCP_SERVER_NAME: str = "ecommerce-operations-tools"
    MCP_SERVER_HOST: str = "127.0.0.1"
    MCP_SERVER_PORT: int = 8001

    # Observability (Langfuse)
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"


settings = Settings()

