import redis
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.redis import get_redis


def enforce_rate_limit(key: str, limit: int, window_seconds: int) -> None:
	redis_key = f"rate_limit:{key}"

	try:
		redis_client = get_redis()
		count = redis_client.incr(redis_key)
		if count == 1:
			redis_client.expire(redis_key, window_seconds)
	except redis.RedisError as exc:
		raise HTTPException(
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
			detail="Authentication service temporarily unavailable",
		) from exc

	if count > limit:
		raise HTTPException(
			status_code=status.HTTP_429_TOO_MANY_REQUESTS,
			detail="Too many requests",
			headers={"Retry-After": str(window_seconds)},
		)


def enforce_auth_rate_limit(key: str, limit: int) -> None:
	enforce_rate_limit(
		key=f"auth:{key}",
		limit=limit,
		window_seconds=settings.AUTH_RATE_LIMIT_WINDOW_SECONDS,
	)
