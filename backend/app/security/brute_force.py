from app.core.redis import get_redis


MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 900


def get_login_attempt_key(email: str) -> str:
    return f"login_attempts:{email.lower()}"


def is_login_blocked(email: str) -> bool:
    redis = get_redis()

    key = get_login_attempt_key(email)

    attempts = redis.get(key)

    if attempts is None:
        return False

    return int(attempts) >= MAX_FAILED_ATTEMPTS


def record_failed_login(email: str) -> int:
    redis = get_redis()

    key = get_login_attempt_key(email)

    attempts = redis.incr(key)

    if attempts == 1:
        redis.expire(key, LOCKOUT_SECONDS)

    return attempts


def clear_failed_logins(email: str) -> None:
    redis = get_redis()

    key = get_login_attempt_key(email)

    redis.delete(key)