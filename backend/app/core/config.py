from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./karya.db"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str | None = None

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Security defaults
    PASSWORD_MIN_LENGTH: int = 8
    BRUTE_FORCE_ATTEMPTS: int = 5
    BRUTE_FORCE_WINDOW_SECONDS: int = 900
    EMAIL_VERIFICATION_TTL_MINUTES: int = 60
    PASSWORD_RESET_TTL_MINUTES: int = 60
    MFA_RATE_LIMIT_PER_MINUTE: int = 5

    # Cookie / CORS
    CORS_ALLOW_ORIGINS: str = "http://localhost:5173"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()