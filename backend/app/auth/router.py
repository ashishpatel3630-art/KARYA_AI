from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.exceptions import (
    account_temporarily_locked,
    invalid_credentials,
)
from app.auth.password import password_hasher
from app.auth.refresh import get_session_from_refresh_token
from app.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    TokenResponse,
)
from app.auth.token_hash import hash_refresh_token
from app.auth.service import authenticate_user
from app.auth.tokens import (
    create_access_token,
    create_refresh_token,
)
from app.core.database import get_db
from app.models.session import Session as SessionModel
from app.models.user import User
from app.security.brute_force import (
    clear_failed_logins,
    is_login_blocked,
    record_failed_login,
)
from app.security.audit import record_security_event
from app.sessions.service import create_session


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

    result = db.execute(
        select(User).where(User.email == email)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    hashed_password = password_hasher.hash(
        data.password
    )

    user = User(
        email=email,
        password_hash=hashed_password,
    )

    db.add(user)
    record_security_event(db, "user_registered", metadata={"email": email})
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

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    email = data.email.lower()

    # 1. Brute-force protection
    if is_login_blocked(email):
        raise account_temporarily_locked

    # 2. Authenticate user
    user = authenticate_user(
        db=db,
        email=email,
        password=data.password,
    )

    if user is None:
        record_failed_login(email)
        record_security_event(db, "login_failed", metadata={"email": email})
        db.commit()
        raise invalid_credentials

    # 3. Clear failed attempts
    clear_failed_logins(email)
    user.last_login_at = datetime.now(timezone.utc)
    record_security_event(db, "login_succeeded", user_id=user.id)

    # 4. Create access token
    access_token = create_access_token(
        user.id
    )

    # 5. Create refresh token
    refresh_token, jti, token_family, expires_at = create_refresh_token(
        user.id
    )

    # 6. Create server-side session
    create_session(
        db=db,
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=expires_at,
        ip_address=(
            request.client.host
            if request.client
            else None
        ),
        user_agent=request.headers.get(
            "user-agent"
        ),
        jti=jti,
        token_family=token_family,
    )

    # 7. Return tokens
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


# ============================================================
# REFRESH TOKEN
# ============================================================

@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh_token(
    data: RefreshRequest,
    db: Session = Depends(get_db),
):
    # 1. Validate refresh token
    session = get_session_from_refresh_token(
        db=db,
        refresh_token=data.refresh_token,
    )

    user_id = session.user_id

    # 2. Revoke old session
    session.revoked = True
    session.revoked_at = datetime.now(timezone.utc)
    record_security_event(db, "refresh_rotated", user_id=user_id)

    # 3. Create new access token
    access_token = create_access_token(
        user_id
    )

    # 4. Create new refresh token
    (
        new_refresh_token,
        jti,
        token_family,
        expires_at,
    ) = create_refresh_token(
        user_id,
        token_family=session.token_family,
        parent_jti=session.jti,
    )

    # 5. Create new session
    new_session = SessionModel(
        user_id=user_id,
        refresh_token_hash=hash_refresh_token(
            new_refresh_token
        ),
        jti=jti,
        token_family=token_family,
        parent_jti=session.jti,
        ip_address=session.ip_address,
        user_agent=session.user_agent,
        expires_at=expires_at,
        revoked=False,
    )

    db.add(new_session)

    # 6. Save changes
    db.commit()

    # 7. Return new token pair
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


# ============================================================
# LOGOUT
# ============================================================

@router.post("/logout")
def logout(
    data: RefreshRequest,
    db: Session = Depends(get_db),
):
    session = get_session_from_refresh_token(
        db=db,
        refresh_token=data.refresh_token,
    )

    session.revoked = True
    session.revoked_at = datetime.now(timezone.utc)
    record_security_event(db, "logout", user_id=session.user_id)
    db.commit()

    return {
        "message": "Logged out successfully",
        "session_id": session.id,
    }