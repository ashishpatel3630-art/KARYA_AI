from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.refresh import get_session_from_refresh_token
from app.auth.token_hash import hash_refresh_token
from app.auth.tokens import create_refresh_token
from app.core.database import Base
from app.models.session import Session


def make_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    return engine, TestingSessionLocal


def create_test_session(
    db,
    user_id,
    refresh_token,
    jti,
    token_family,
):
    session = Session(
        user_id=user_id,
        refresh_token_hash=hash_refresh_token(refresh_token),
        jti=jti,
        token_family=token_family,
        parent_jti=None,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        revoked=False,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def test_rejects_jti_mismatch():
    engine, SessionLocal = make_db()
    db = SessionLocal()

    try:
        user_id = "test-user-jti"

        token, jti, token_family, _ = create_refresh_token(
            user_id=user_id,
        )

        create_test_session(
            db=db,
            user_id=user_id,
            refresh_token=token,
            jti=jti,
            token_family=token_family,
        )

        mismatched_payload = {
            "sub": user_id,
            "type": "refresh",
            "jti": "different-jti",
            "token_family": token_family,
        }

        with patch(
            "app.auth.refresh.decode_token",
            return_value=mismatched_payload,
        ):
            with pytest.raises(HTTPException) as exc:
                get_session_from_refresh_token(
                    db=db,
                    refresh_token=token,
                )

        assert exc.value.status_code == 401
        assert exc.value.detail == (
            "Refresh token session mismatch"
        )

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_rejects_token_family_mismatch():
    engine, SessionLocal = make_db()
    db = SessionLocal()

    try:
        user_id = "test-user-family"

        token, jti, token_family, _ = create_refresh_token(
            user_id=user_id,
        )

        create_test_session(
            db=db,
            user_id=user_id,
            refresh_token=token,
            jti=jti,
            token_family=token_family,
        )

        mismatched_payload = {
            "sub": user_id,
            "type": "refresh",
            "jti": jti,
            "token_family": "different-family",
        }

        with patch(
            "app.auth.refresh.decode_token",
            return_value=mismatched_payload,
        ):
            with pytest.raises(HTTPException) as exc:
                get_session_from_refresh_token(
                    db=db,
                    refresh_token=token,
                )

        assert exc.value.status_code == 401
        assert exc.value.detail == (
            "Refresh token family mismatch"
        )

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)