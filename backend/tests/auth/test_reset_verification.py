from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.auth.password import password_hasher, verify_password
from app.models.email_verification_token import EmailVerificationToken
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.password_reset.service import create_password_reset_token, reset_password
from app.verification.service import create_verification_token, verify_email


def test_password_reset_is_one_time_and_revokes_sessions(db_session):
    user = User(email="reset@example.com", password_hash=password_hasher.hash("OldPass123!"))
    db_session.add(user)
    db_session.commit()

    token = create_password_reset_token(db_session, user)
    reset_password(db_session, token, "NewPass123!")

    db_session.refresh(user)
    assert verify_password("NewPass123!", user.password_hash)
    with pytest.raises(HTTPException):
        reset_password(db_session, token, "AnotherPass123!")


def test_verification_token_is_single_use(db_session):
    user = User(email="verify@example.com", password_hash=password_hasher.hash("Pass123!"))
    db_session.add(user)
    db_session.commit()

    token = create_verification_token(db_session, user)
    verify_email(db_session, token)

    db_session.refresh(user)
    assert user.is_verified is True
    with pytest.raises(HTTPException):
        verify_email(db_session, token)


def test_expired_tokens_are_rejected(db_session):
    user = User(email="expired@example.com", password_hash=password_hasher.hash("Pass123!"))
    db_session.add(user)
    db_session.commit()

    reset_token = create_password_reset_token(db_session, user)
    reset_record = db_session.query(PasswordResetToken).one()
    reset_record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()
    with pytest.raises(HTTPException):
        reset_password(db_session, reset_token, "NewPass123!")

    verification_token = create_verification_token(db_session, user)
    verification_record = db_session.query(EmailVerificationToken).one()
    verification_record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()
    with pytest.raises(HTTPException):
        verify_email(db_session, verification_token)