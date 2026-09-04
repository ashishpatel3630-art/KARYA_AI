import redis

from app.core.config import settings


def _build_redis_client() -> redis.Redis:
    if settings.REDIS_URL:
        return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
    )


redis_client = _build_redis_client()


def get_redis() -> redis.Redis:
    return redis_client


async def check_redis() -> bool:
    try:
        return bool(redis_client.ping())
    except redis.RedisError:
        return False