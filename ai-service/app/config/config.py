"""
Application configuration using Pydantic Settings
"""
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env
    )

    # Application
    APP_NAME: str = "ESG AI Service"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API (support both naming conventions)
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS (Spring Boot + Frontend for local development)
    CORS_ORIGINS: list[str] = ["http://localhost:8080", "http://localhost:5173"]
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:8080"]

    # Spring Boot Backend
    SPRING_BOOT_URL: str = "http://localhost:8080"

    # ChromaDB (alternative to Qdrant)
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION_NAME: str = "esg_documents"

    # LLM API Keys
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Vector Store (Qdrant)
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_PREFIX: str = "esg_"

    # Embedding Model
    EMBEDDING_MODEL: str = "BAAI/bge-m3"

    # Naver API (for news collection)
    NAVER_CLIENT_ID: Optional[str] = None
    NAVER_CLIENT_SECRET: Optional[str] = None

    # RAG Settings
    RAG_TOP_K: int = 5
    RAG_SCORE_THRESHOLD: float = 0.7

    # Issue Pool Settings
    MAX_TOPIC_COUNT: int = 20

    # Carbon Trading Settings
    CARBON_PRICE_CHANGE_THRESHOLD: float = 0.05
    CARBON_CONFIDENCE_THRESHOLD: float = 0.7

    # News Retention (in years)
    NEWS_RETENTION_YEARS: int = 2

    # Retry Settings
    MAX_RETRIES: int = 3
    RETRY_BACKOFF_FACTOR: int = 2

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Data Directories (configurable paths instead of hardcoded)
    DATA_DIR: str = "data"
    BENCHMARK_UPLOADS_DIR: str = "data/benchmark_uploads"
    BENCHMARK_VECTORS_DIR: str = "data/benchmark_vectors"
    BENCHMARK_CACHE_FILE: str = "data/benchmark_cache.json"
    ESG_UPLOADS_DIR: str = "data/esg_uploads"


settings = Settings()
