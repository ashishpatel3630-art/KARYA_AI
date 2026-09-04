from datetime import datetime, timedelta, timezone
import uuid

import jwt

from app.core.config import settings


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)

    expire = now + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(user_id: str) -> tuple[str, str, datetime]:
    now = datetime.now(timezone.utc)

    expire = now + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    jti = str(uuid.uuid4())

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": jti,
        "iat": now,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return token, jti, expire