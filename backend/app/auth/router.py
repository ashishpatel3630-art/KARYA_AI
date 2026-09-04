from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.security.brute_force import (
    is_login_blocked,
    record_failed_login,
    reset_failed_logins,
)
from app.auth.service import (
    authenticate_user,
    create_session,
    register_user,
)
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):

    try:

        user = register_user(
            db=db,
            email=data.email,
            password=data.password,
        )

    except ValueError:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create account",
        )

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    email = data.email.strip().lower()

    client_ip = (
        request.client.host
        if request.client
        else "unknown"
    )

    # ------------------------------------------------
    # 1. Check email-based brute-force protection
    # ------------------------------------------------

    if is_login_blocked(email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
        )

    # ------------------------------------------------
    # 2. Authenticate user
    # ------------------------------------------------

    user = authenticate_user(
        db=db,
        email=email,
        password=data.password,
    )

    # ------------------------------------------------
    # 3. Failed login
    # ------------------------------------------------

    if not user:

        record_failed_login(email)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # ------------------------------------------------
    # 4. Successful login
    # ------------------------------------------------

    reset_failed_logins(email)

    user.last_login_at = datetime.utcnow()

    access_token, refresh_token = create_session(
        db=db,
        user=user,
        ip_address=client_ip,
        user_agent=request.headers.get("user-agent"),
    )

    # ------------------------------------------------
    # 5. Refresh token → HttpOnly cookie
    # ------------------------------------------------

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/v1/auth",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }