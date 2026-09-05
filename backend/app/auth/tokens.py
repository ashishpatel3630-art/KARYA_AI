
from datetime import datetime, timedelta, timezone
from typing import Any
import uuid

import jwt

from app.core.config import settings


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "jti": uuid.uuid4().hex,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(
    user_id: str,
    token_family: str | None = None,
    parent_jti: str | None = None,
) -> tuple[str, str, str, datetime]:

    now = datetime.now(timezone.utc)

    expires_at = now + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    jti = uuid.uuid4().hex
    family = token_family or uuid.uuid4().hex

    payload = {
        "sub": str(user_id),
        "jti": jti,
        "type": "refresh",
        "token_family": family,
        "parent_jti": parent_jti,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return token, jti, family, expires_at


def get_session_absolute_expiry(created_at: datetime) -> datetime:
    return created_at + timedelta(
        days=settings.SESSION_ABSOLUTE_TIMEOUT_DAYS
    )


def create_mfa_challenge(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "jti": uuid.uuid4().hex,
        "type": "mfa_challenge",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=5)).timestamp()),
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_mfa_challenge(token: str) -> dict[str, Any]:
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["sub", "jti", "type", "iat", "exp"]},
    )
    if payload.get("type") != "mfa_challenge" or not payload.get("sub"):
        raise ValueError("Invalid MFA challenge")
    return payload


def decode_token(token: str) -> dict[str, Any]:
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={
            "require": [
                "sub",
                "jti",
                "type",
                "exp",
                "iat",
            ]
        },
    )

    if not payload.get("sub"):
        raise ValueError("Missing subject")

    if payload.get("type") not in {"access", "refresh"}:
        raise ValueError("Invalid token type")

    return payload
