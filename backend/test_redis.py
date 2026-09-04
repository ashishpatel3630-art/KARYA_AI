import asyncio

from app.core.redis import check_redis


async def main():
    result = await check_redis()

    if result:
        print("Redis connection successful ✅")
    else:
        print("Redis connection failed ❌")


asyncio.run(main())