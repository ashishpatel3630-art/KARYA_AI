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
    SESSION_IDLE_TIMEOUT_DAYS: int = 7
    SESSION_ABSOLUTE_TIMEOUT_DAYS: int = 90

    # Security defaults
    PASSWORD_MIN_LENGTH: int = 8
    BRUTE_FORCE_ATTEMPTS: int = 5
    BRUTE_FORCE_WINDOW_SECONDS: int = 900
    AUTH_RATE_LIMIT_WINDOW_SECONDS: int = 60
    AUTH_REGISTER_RATE_LIMIT: int = 5
    AUTH_LOGIN_IP_RATE_LIMIT: int = 30
    AUTH_LOGIN_ACCOUNT_RATE_LIMIT: int = 10
    AUTH_REFRESH_RATE_LIMIT: int = 30
    AUTH_LOGOUT_RATE_LIMIT: int = 30
    EMAIL_VERIFICATION_TTL_MINUTES: int = 60
    PASSWORD_RESET_TTL_MINUTES: int = 60
    PASSWORD_RESET_RATE_LIMIT: int = 5
    VERIFICATION_RESEND_RATE_LIMIT: int = 3
    MFA_RATE_LIMIT_PER_MINUTE: int = 5
    OAUTH_STATE_TTL_SECONDS: int = 600
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None
    MICROSOFT_CLIENT_ID: str | None = None
    MICROSOFT_CLIENT_SECRET: str | None = None

    # Cookie / CORS
    CORS_ALLOW_ORIGINS: str = (
        "http://localhost:3000,http://localhost:5173,"
        "http://127.0.0.1:3000,http://127.0.0.1:5173"
    )
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()