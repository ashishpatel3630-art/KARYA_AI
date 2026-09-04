import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.auth.password import hash_password, verify_password
from app.auth.tokens import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
)
from app.core.config import settings
from app.models.refresh_token import RefreshToken
from app.models.session import Session
from app.models.user import User


def normalize_email(email: str) -> str:
    return email.strip().lower()


def register_user(
    db: DBSession,
    email: str,
    password: str,
) -> User:

    email = normalize_email(email)

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise ValueError("Unable to create account")

    user = User(
        email=email,
        password_hash=hash_password(password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: DBSession,
    email: str,
    password: str,
) -> User | None:

    email = normalize_email(email)

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if not user:
        return None

    if not user.is_active:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user


def create_session(
    db: DBSession,
    user: User,
    ip_address: str | None,
    user_agent: str | None,
):

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    session = Session(
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=now + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        ),
    )

    db.add(session)

    refresh_token = create_refresh_token()

    token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        family_id=str(uuid.uuid4()),
        expires_at=now + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        ),
    )

    db.add(token_record)

    db.commit()

    access_token = create_access_token(user.id)

    return access_token, refresh_token