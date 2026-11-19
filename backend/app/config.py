from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    # General App Config
    APP_NAME: str = "Enterprise Knowledge AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Security & Auth
    API_KEY: str = "ekai_test_secret_key_12345"
    AUTH_ENABLED: bool = True
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "*",
    ]
    RATE_LIMIT_PER_MINUTE: int = 60

    # Groq LLM API
    GROQ_API_KEY: str = ""
    GROQ_GEN_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_FAST_MODEL: str = "llama-3.1-8b-instant"
    GROQ_TIMEOUT_SECONDS: float = 30.0
    GROQ_MAX_RETRIES: int = 3

    # FastEmbed Embeddings
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIMENSION: int = 384
    SPARSE_MODEL: str = "Qdrant/bm25"
    EMBEDDING_CACHE_DIR: str | None = None

    # Qdrant Vector DB
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = "enterprise_knowledge"
    QDRANT_PREFER_GRPC: bool = False

    # Ingestion & Chunking
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 60
    MAX_FILE_SIZE_BYTES: int = 50 * 1024 * 1024  # 50MB

    # Retrieval & Search Tuning
    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_HYBRID_ALPHA: float = 0.5  # 0.5 balanced dense and sparse RRF
    RELEVANCE_SCORE_THRESHOLD: float = 0.35
    MAX_REWRITE_RETRIES: int = 2

    # In-memory Caching
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 3600
    CACHE_MAX_ENTRIES: int = 2000

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        return ["*"]


settings = Settings()
