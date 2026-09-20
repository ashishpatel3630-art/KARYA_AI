
"""
KARYA AI application configuration.

Centralized configuration for authentication, security, database,
Redis, local LLM/Ollama, CORS, and application runtime settings.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):


    APP_NAME: str = "KARYA AI API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

   
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/auth_db"

    # ============================================================
    # REDIS
    # ============================================================

    REDIS_URL: str = "redis://localhost:6379/0"

    # ============================================================
    # AUTH / JWT
    # ============================================================

    JWT_SECRET: str = "change-this-development-secret"
    JWT_ISSUER: str = "karya-ai"
    JWT_AUDIENCE: str = "karya-api"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ============================================================
    # PASSWORD SECURITY
    # ============================================================

    PASSWORD_MIN_LENGTH: int = 12

    BRUTE_FORCE_ATTEMPTS: int = 5
    BRUTE_FORCE_WINDOW_SECONDS: int = 900

    AUTH_RATE_LIMIT_WINDOW_SECONDS: int = 60

    AUTH_REGISTER_RATE_LIMIT: int = 5

    AUTH_LOGIN_IP_RATE_LIMIT: int = 30
    AUTH_LOGIN_ACCOUNT_RATE_LIMIT: int = 10

    AUTH_REFRESH_RATE_LIMIT: int = 30
    AUTH_LOGOUT_RATE_LIMIT: int = 30

    PASSWORD_RESET_RATE_LIMIT: int = 5
    VERIFICATION_RESEND_RATE_LIMIT: int = 3

    MFA_RATE_LIMIT_PER_MINUTE: int = 5

    # ============================================================
    # SESSION SECURITY
    # ============================================================

    SESSION_IDLE_TIMEOUT_DAYS: int = 7
    SESSION_ABSOLUTE_TIMEOUT_DAYS: int = 90

    # ============================================================
    # COOKIE SECURITY
    # ============================================================

    COOKIE_SECURE: bool = False
    COOKIE_HTTP_ONLY: bool = True
    COOKIE_SAMESITE: str = "lax"

    REFRESH_COOKIE_NAME: str = "karya_refresh_token"

    # ============================================================
    # CORS
    # ============================================================

    CORS_ORIGINS: str = (
        "http://localhost:3000,"
        "http://127.0.0.1:3000"
    )

    # ============================================================
    # LOCAL LLM / OLLAMA
    # ============================================================

    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "llama3.2"

    # ============================================================
    # EMBEDDINGS
    # ============================================================

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ============================================================
    # VECTOR DATABASE
    # ============================================================

    VECTOR_DB_URL: str = ""

    # ============================================================
    # STORAGE
    # ============================================================

    STORAGE_DIR: str = "./storage"

    # ============================================================
    # RAG
    # ============================================================

    RAG_TOP_K: int = 10
    RAG_RERANK_TOP_K: int = 5
    RAG_MIN_RELEVANCE_SCORE: float = 0.20

    # ============================================================
    # SECURITY
    # ============================================================

    TRUST_PROXY_HEADERS: bool = False

    # ============================================================
    # PYDANTIC SETTINGS
    # ============================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return the cached application settings instance.
    """
    return Settings()


# Global settings instance used throughout KARYA.
settings = get_settings()


__all__ = [
    "Settings",
    "settings",
    "get_settings",
]