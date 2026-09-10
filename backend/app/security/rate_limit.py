from __future__ import annotations

import redis
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.redis import get_redis


class RateLimitExceeded(HTTPException):
    def __init__(self, retry_after: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
            headers={
                "Retry-After": str(retry_after),
            },
        )


def enforce_rate_limit(
    key: str,
    limit: int,
    window_seconds: int,
) -> None:
    if limit <= 0:
        raise ValueError("Rate limit must be greater than zero.")

    if window_seconds <= 0:
        raise ValueError(
            "Rate-limit window must be greater than zero."
        )

    redis_client = get_redis()

    redis_key = f"karya:ratelimit:{key}"

    try:
        count = redis_client.incr(redis_key)

        if count == 1:
            redis_client.expire(
                redis_key,
                window_seconds,
            )

        if count > limit:
            raise RateLimitExceeded(
                retry_after=window_seconds
            )

    except RateLimitExceeded:
        raise

    except redis.RedisError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Authentication security service "
                "is temporarily unavailable."
            ),
        ) from exc


def enforce_auth_rate_limit(
    key: str,
    limit: int,
) -> None:
    enforce_rate_limit(
        key=f"auth:{key}",
        limit=limit,
        window_seconds=(
            settings.AUTH_RATE_LIMIT_WINDOW_SECONDS
        ),
    )