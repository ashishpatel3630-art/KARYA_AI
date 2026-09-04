from datetime import datetime, timezone

from sqlalchemy.orm import Session as DBSession

from app.auth.token_hash import hash_refresh_token
from app.models.session import Session


def create_session(
    db: DBSession,
    user_id: str,
    refresh_token: str,
    expires_at: datetime,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Session:

    session = Session(
        user_id=user_id,
        refresh_token_hash=hash_refresh_token(refresh_token),
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=expires_at,
        revoked=False,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session