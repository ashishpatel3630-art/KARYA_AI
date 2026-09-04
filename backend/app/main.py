from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.core.redis import get_redis


app = FastAPI(
    title="KARYA AI API",
    description="KARYA AI Authentication and Backend API",
    version="1.0.0",
)


# =========================
# Authentication Routes
# =========================
app.include_router(auth_router)


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