from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

from app.core.config import settings


# --------------------------------------------------
# Password Hashing
# --------------------------------------------------

password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """
    Hash a user's password using Argon2.
    """
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a plain password against its Argon2 hash.
    """
    try:
        return password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False


# --------------------------------------------------
# JWT
# --------------------------------------------------

def create_access_token(
    subject: str,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    Create a short-lived access token.
    """

    now = datetime.now(timezone.utc)

    payload = {
        "sub": subject,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(
    subject: str,
) -> str:
    """
    Create a long-lived refresh token.
    """

    now = datetime.now(timezone.utc)

    payload = {
        "sub": subject,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        ),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT.
    """

    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    
    import hashlib


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_refresh_token(token: str, token_hash: str) -> bool:
    return hashlib.sha256(token.encode("utf-8")).hexdigest() == token_hash