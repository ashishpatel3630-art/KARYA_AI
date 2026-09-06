from datetime import datetime, timezone
import hashlib
import secrets
from datetime import timedelta

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
    MFAChallengeResponse,
    InvitationRequest,
    RegisterRequest,
    RefreshRequest,
    TokenResponse,
)
from app.auth.token_hash import hash_refresh_token
from app.auth.service import authenticate_user
from app.auth.tokens import (
    create_access_token,
    create_mfa_challenge,
    create_refresh_token,
)
from app.core.config import settings
from app.core.database import get_db
from app.models.session import Session as SessionModel
from app.models.mfa import MFA
from app.models.role_invitation import RoleInvitation
from app.models.user import User
from app.security.brute_force import (
    clear_failed_logins,
    is_login_blocked,
    record_failed_login,
)
from app.security.audit import record_security_event
from app.security.rate_limit import enforce_auth_rate_limit
from app.sessions.service import create_session
from app.verification.service import create_verification_token
from app.authorization.dependencies import require_roles


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def _hash_invitation_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _normalize_invited_role(role: str) -> str:
    normalized = role.strip().upper()
    if normalized == "MANAGER":
        normalized = "STAFF"
    if normalized not in {"STAFF", "ADMIN"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only manager or admin invitations are supported")
    return normalized


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    enforce_auth_rate_limit(
        key=f"register:ip:{request.client.host if request.client else 'unknown'}",
        limit=settings.AUTH_REGISTER_RATE_LIMIT,
    )
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

    # Public registration never grants elevated roles. Invitation-based role
    # assignment can be added without trusting a client-controlled role.
    registration_secret = data.secret_key or secrets.token_urlsafe(32)
    requested_role = data.role.strip().upper()
    if requested_role == "MANAGER":
        requested_role = "STAFF"
    invitation = None
    if requested_role in {"STAFF", "ADMIN"} or data.invitation_token:
        if not data.invitation_token:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="A valid role invitation is required")
        invitation = db.scalar(
            select(RoleInvitation)
            .where(RoleInvitation.token_hash == _hash_invitation_token(data.invitation_token))
            .with_for_update()
        )
        now = datetime.now(timezone.utc)
        if invitation is None or invitation.used_at is not None or invitation.revoked_at is not None or invitation.expires_at <= now:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired role invitation")
        if invitation.email and invitation.email != email:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invitation email does not match")
        requested_role = invitation.role

    user = User(
        name=data.name.strip(),
        email=email,
        password_hash=hashed_password,
        secret_key_hash=password_hasher.hash(registration_secret),
        role=requested_role if invitation else "USER",
    )

    if invitation:
        invitation.used_at = datetime.now(timezone.utc)

    db.add(user)
    record_security_event(db, "user_registered", metadata={"email": email})
    db.commit()
    db.refresh(user)
    create_verification_token(db, user)

    return {
        "message": "User registered successfully",
        "user_id": str(user.id),
        "email": user.email,
        "role": user.role,
    }


@router.post("/invitations", status_code=status.HTTP_201_CREATED)
def create_invitation(
    data: InvitationRequest,
    user: User = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    token = secrets.token_urlsafe(32)
    invitation = RoleInvitation(
        token_hash=_hash_invitation_token(token),
        role=_normalize_invited_role(data.role),
        email=data.email.lower() if data.email else None,
        created_by=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=data.expires_in_hours),
    )
    db.add(invitation)
    db.commit()
    return {"invitation_token": token, "role": invitation.role, "expires_at": invitation.expires_at}


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=TokenResponse | MFAChallengeResponse,
)
def login(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    email = data.email.lower()
    ip_address = request.client.host if request.client else "unknown"

    enforce_auth_rate_limit(
        key=f"login:ip:{ip_address}",
        limit=settings.AUTH_LOGIN_IP_RATE_LIMIT,
    )
    enforce_auth_rate_limit(
        key=f"login:account:{email}",
        limit=settings.AUTH_LOGIN_ACCOUNT_RATE_LIMIT,
    )

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

    enabled_mfa = db.scalar(
        select(MFA).where(
            MFA.user_id == user.id,
            MFA.type == "totp",
            MFA.enabled.is_(True),
        )
    )
    if enabled_mfa is not None:
        return MFAChallengeResponse(
            challenge_token=create_mfa_challenge(user.id),
        )

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
    request: Request,
    db: Session = Depends(get_db),
):
    enforce_auth_rate_limit(
        key=f"refresh:ip:{request.client.host if request.client else 'unknown'}",
        limit=settings.AUTH_REFRESH_RATE_LIMIT,
    )
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
        absolute_expires_at=session.absolute_expires_at,
        revoked=False,
        last_used_at=datetime.now(timezone.utc),
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
    request: Request,
    db: Session = Depends(get_db),
):
    enforce_auth_rate_limit(
        key=f"logout:ip:{request.client.host if request.client else 'unknown'}",
        limit=settings.AUTH_LOGOUT_RATE_LIMIT,
    )
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