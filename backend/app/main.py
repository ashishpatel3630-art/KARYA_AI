from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth.router import router as auth_router
from app.core.config import settings
from app.core.redis import get_redis
from app.domain.router import router as domain_router
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.mfa.router import router as mfa_router
from app.models import domain  # noqa: F401
from app.oauth.router import router as oauth_router
from app.password_reset.router import router as password_reset_router
from app.sessions.router import router as sessions_router
from app.users.router import router as users_router
from app.verification.router import router as verification_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    KARYA application lifecycle.

    Database schema changes must be handled through Alembic.
    Application startup should only initialize runtime dependencies.
    """

    app.state.started_at = perf_counter()

    yield

    # Reserved for graceful shutdown:
    # - worker shutdown
    # - Redis connection cleanup
    # - model unloading
    # - telemetry flushing


app = FastAPI(
    title="KARYA AI API",
    description=(
        "Sovereign on-premise Agentic AI Workbench "
        "for confidential industrial operations."
    ),
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============================================================
# SECURITY
# ============================================================

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
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Request-ID",
    ],
)


# ============================================================
# REQUEST TELEMETRY
# ============================================================

@app.middleware("http")
async def request_metrics(request: Request, call_next):
    """
    Lightweight request timing middleware.

    Later this can be replaced/extended with OpenTelemetry.
    """

    started = perf_counter()

    response = await call_next(request)

    duration = perf_counter() - started

    response.headers["X-Response-Time"] = f"{duration:.4f}s"

    return response


# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(password_reset_router)
app.include_router(mfa_router)
app.include_router(oauth_router)
app.include_router(verification_router)
app.include_router(sessions_router)
app.include_router(users_router)
app.include_router(domain_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/", tags=["System"])
async def root():
    return {
        "name": "KARYA AI",
        "service": "Sovereign Agentic AI Workbench",
        "version": "2.0.0",
        "status": "online",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get(
    "/health",
    tags=["Health"],
)
async def health_check():
    return {
        "status": "healthy",
        "service": "karya-api",
        "version": "2.0.0",
    }


@app.get(
    "/health/redis",
    tags=["Health"],
)
async def redis_health():
    """
    Verify Redis connectivity.

    This endpoint intentionally performs a small
    read/write check rather than merely opening a connection.
    """

    try:
        redis = get_redis()

        redis.set(
            "karya:health",
            "ok",
            ex=30,
        )

        value = redis.get("karya:health")

        return {
            "status": "healthy",
            "redis": "connected",
            "value": value,
        }

    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "redis": "disconnected",
                "error": str(exc),
            },
        )


# ============================================================
# GLOBAL ERROR HANDLER
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    """
    Last-resort exception boundary.

    Detailed exception information should be logged internally,
    but should not be exposed to clients in production.
    """

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred.",
            }
        },
    )