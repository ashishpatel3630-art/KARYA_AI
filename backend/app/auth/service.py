from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.password import verify_password
from app.auth.tokens import create_access_token, create_refresh_token
from app.models.user import User


def authenticate_user(
    db: Session,
    email: str,
    password: str,
):
    result = db.execute(
        select(User).where(User.email == email)
    )

    user = result.scalar_one_or_none()

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def login_user(
    db: Session,
    email: str,
    password: str,
):
    user = authenticate_user(
        db=db,
        email=email,
        password=password,
    )

    if user is None:
        return None

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }