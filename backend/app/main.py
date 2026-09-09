from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.core.redis import get_redis
from app.password_reset.router import router as password_reset_router
from app.mfa.router import router as mfa_router
from app.oauth.router import router as oauth_router
from app.sessions.router import router as sessions_router
from app.users.router import router as users_router
from app.verification.router import router as verification_router
from app.domain.router import router as domain_router
from app.models import domain  # noqa: F401


app = FastAPI(
    title="KARYA AI API",
    description="KARYA AI Authentication and Backend API",
    version="1.0.0",
)
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.middleware.security_headers import SecurityHeadersMiddleware
# =========================
# Security Middleware
# =========================

app.add_middleware(SecurityHeadersMiddleware)

allowed_origins = [
    origin.strip()
    for origin in settings.CORS_ALLOW_ORIGINS.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# =========================
# Authentication Routes
# =========================
app.include_router(auth_router)
app.include_router(password_reset_router)
app.include_router(mfa_router)
app.include_router(oauth_router)
app.include_router(verification_router)
app.include_router(sessions_router)
app.include_router(users_router)
app.include_router(domain_router)

from app.core.database import Base, engine
Base.metadata.create_all(bind=engine)


# =========================
# Redis Health Check
# =========================
@app.get(
    "/health/redis",
    tags=["Health"],
)
def redis_health():
    redis = get_redis()

    redis.set("karya_test", "KARYA_AI")

    value = redis.get("karya_test")

    return {
        "redis": "connected",
        "value": value,
    }


# =========================
# General Health Check
# =========================
@app.get(
    "/health",
    tags=["Health"],
)
def health_check():
    return {
        "status": "ok",
        "service": "KARYA AI API",
    }