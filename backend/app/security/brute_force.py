from app.core.redis import redis_sync_client


MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 900  # 15 minutes


def is_login_blocked(identifier: str) -> bool:
    key = f"auth:login:blocked:{identifier}"

    return redis_sync_client.exists(key) == 1


def record_failed_login(identifier: str) -> int:
    key = f"auth:login:attempts:{identifier}"

    attempts = redis_sync_client.incr(key)

    if attempts == 1:
        redis_sync_client.expire(
            key,
            LOCKOUT_SECONDS,
        )

    if attempts >= MAX_FAILED_ATTEMPTS:
        blocked_key = f"auth:login:blocked:{identifier}"

        redis_sync_client.setex(
            blocked_key,
            LOCKOUT_SECONDS,
            "1",
        )

    return attempts


def reset_failed_logins(identifier: str) -> None:
    redis_sync_client.delete(
        f"auth:login:attempts:{identifier}",
        f"auth:login:blocked:{identifier}",
    )