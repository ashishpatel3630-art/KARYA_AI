from __future__ import annotations

from app.core.config import settings
from app.core.redis import get_redis


def get_login_attempt_key(email: str) -> str:
    normalized_email = email.strip().lower()
    return f"security:login_attempts:{normalized_email}"


def is_login_blocked(email: str) -> bool:
    redis_client = get_redis()
    key = get_login_attempt_key(email)

    attempts = redis_client.get(key)

    if attempts is None:
        return False

    try:
        return int(attempts) >= settings.BRUTE_FORCE_ATTEMPTS
    except (TypeError, ValueError):
        return False


def record_failed_login(email: str) -> int:
    redis_client = get_redis()
    key = get_login_attempt_key(email)

    attempts = redis_client.incr(key)

    if attempts == 1:
        redis_client.expire(
            key,
            settings.BRUTE_FORCE_WINDOW_SECONDS,
        )

    return int(attempts)


def clear_failed_logins(email: str) -> None:
    redis_client = get_redis()
    redis_client.delete(get_login_attempt_key(email))


def reset_failed_logins(email: str) -> None:
    clear_failed_logins(email)


def get_failed_login_attempts(email: str) -> int:
    redis_client = get_redis()

    value = redis_client.get(
        get_login_attempt_key(email)
    )

    if value is None:
        return 0

    try:
        return int(value)
    except (TypeError, ValueError):
        return 0