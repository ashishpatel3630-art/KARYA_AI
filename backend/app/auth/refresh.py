from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.auth.token_hash import hash_refresh_token
from app.core.config import settings
from app.auth.tokens import decode_token
from app.models.session import Session as UserSession
from app.security.audit import record_security_event


def get_session_from_refresh_token(
    db: Session,
    refresh_token: str,
) -> UserSession:

    # ---------------------------------------------------------
    # 1. Decode JWT
    # ---------------------------------------------------------

    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # ---------------------------------------------------------
    # 2. Verify token type
    # ---------------------------------------------------------

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    # ---------------------------------------------------------
    # 3. Extract required claims
    # ---------------------------------------------------------

    user_id = payload.get("sub")
    jti = payload.get("jti")
    token_family = payload.get("token_family")

    if not user_id or not jti or not token_family:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # ---------------------------------------------------------
    # 4. Hash the presented refresh token
    # ---------------------------------------------------------

    token_hash = hash_refresh_token(refresh_token)

    # ---------------------------------------------------------
    # 5. Lock and locate the session
    # ---------------------------------------------------------

    result = db.execute(
        select(UserSession)
        .where(
            UserSession.user_id == user_id,
            UserSession.refresh_token_hash == token_hash,
        )
        .with_for_update()
    )

    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session not found",
        )

    # ---------------------------------------------------------
    # 6. Verify JWT jti against database session
    # ---------------------------------------------------------

    if session.jti != jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token session mismatch",
        )

    # ---------------------------------------------------------
    # 7. Verify JWT token family against session
    # ---------------------------------------------------------

    if session.token_family != token_family:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token family mismatch",
        )

    # ---------------------------------------------------------
    # 8. Detect refresh-token reuse
    # ---------------------------------------------------------

    if session.revoked:

        # Revoke every active session in the token family.
        db.execute(
            update(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.token_family == session.token_family,
                UserSession.revoked.is_(False),
            )
            .values(
                revoked=True,
                revoked_at=datetime.now(timezone.utc),
            )
        )

        # Record the security incident.
        record_security_event(
            db,
            "refresh_token_reuse_detected",
            user_id=user_id,
            ip_address=session.ip_address,
            user_agent=session.user_agent,
            metadata={
                "token_family": session.token_family,
                "jti": session.jti,
            },
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token reuse detected",
        )

    # ---------------------------------------------------------
    # 9. Verify session expiration
    # ---------------------------------------------------------

    expires_at = session.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session expired",
        )

    now = datetime.now(timezone.utc)
    absolute_expires_at = session.absolute_expires_at
    if absolute_expires_at is not None:
        if absolute_expires_at.tzinfo is None:
            absolute_expires_at = absolute_expires_at.replace(
                tzinfo=timezone.utc
            )
        if absolute_expires_at <= now:
            session.revoked = True
            session.revoked_at = now
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh session expired",
            )

    last_used_at = session.last_used_at or session.created_at
    if last_used_at.tzinfo is None:
        last_used_at = last_used_at.replace(tzinfo=timezone.utc)
    idle_deadline = last_used_at + timedelta(
        days=settings.SESSION_IDLE_TIMEOUT_DAYS
    )
    if idle_deadline <= now:
        session.revoked = True
        session.revoked_at = now
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session expired",
        )

    # ---------------------------------------------------------
    # 10. Update last-used timestamp
    # ---------------------------------------------------------

    session.last_used_at = now

    return session