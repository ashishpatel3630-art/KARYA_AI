import redis
import redis.asyncio as redis_async

from app.core.config import settings


redis_client = redis_async.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)

redis_sync_client = redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


async def check_redis() -> bool:
    try:
        return await redis_client.ping()
    except redis_async.RedisError:
        return False