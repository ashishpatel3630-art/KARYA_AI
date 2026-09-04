from fastapi import HTTPException, status

from app.core.redis import get_redis


def enforce_rate_limit(key: str, limit: int, window_seconds: int) -> None:
	redis = get_redis()
	redis_key = f"rate_limit:{key}"
	count = redis.incr(redis_key)
	if count == 1:
		redis.expire(redis_key, window_seconds)
	if count > limit:
		raise HTTPException(
			status_code=status.HTTP_429_TOO_MANY_REQUESTS,
			detail="Rate limit exceeded",
			headers={"Retry-After": str(window_seconds)},
		)
