from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.auth.schemas import LoginRequest, TokenResponse
from app.auth.service import authenticate_user
from app.auth.tokens import create_access_token, create_refresh_token
from app.auth.password import password_hasher
from app.core.database import get_db
from app.models.user import User
from app.sessions.service import create_session
from app.security.brute_force import (
    clear_failed_logins,
    is_login_blocked,
    record_failed_login,
)

from app.auth.exceptions import (
    account_temporarily_locked,
    invalid_credentials,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    email = data.email.lower()

    # 1. Check whether user already exists
    result = db.execute(
        select(User).where(User.email == email)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # 2. Hash password using Argon2
    hashed_password = password_hasher.hash(data.password)

    # 3. Create user
    user = User(
        email=email,
        password_hash=hashed_password,
    )

    # 4. Save to PostgreSQL
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully",
        "user_id": str(user.id),
        "email": user.email,
    }


# ============================================================
# LOGIN
# ============================================================

@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    email = data.email.lower()

    if is_login_blocked(email):
        raise account_temporarily_locked

    user = authenticate_user(
        db=db,
        email=email,
        password=data.password,
    )

    if user is None:
        record_failed_login(email)
        raise invalid_credentials

    clear_failed_logins(email)

    access_token = create_access_token(user.id)

    refresh_token, jti, expires_at = create_refresh_token(
        user.id
    )

    create_session(
        db=db,
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=expires_at,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )