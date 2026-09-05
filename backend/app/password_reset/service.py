import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.auth.password import password_hasher
from app.core.config import settings
from app.models.password_reset_token import PasswordResetToken
from app.models.session import Session as UserSession
from app.models.user import User
from app.security.audit import record_security_event


def _hash_token(token: str) -> str:
	return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_password_reset_token(db: Session, user: User) -> str:
	token = secrets.token_urlsafe(32)
	db.execute(
		update(PasswordResetToken)
		.where(
			PasswordResetToken.user_id == user.id,
			PasswordResetToken.used_at.is_(None),
		)
		.values(used_at=datetime.now(timezone.utc))
	)
	db.add(
		PasswordResetToken(
			user_id=user.id,
			token_hash=_hash_token(token),
			expires_at=datetime.now(timezone.utc)
			+ timedelta(minutes=settings.PASSWORD_RESET_TTL_MINUTES),
		)
	)
	db.commit()
	return token


def reset_password(db: Session, token: str, new_password: str) -> None:
	record = db.scalar(
		select(PasswordResetToken).where(
			PasswordResetToken.token_hash == _hash_token(token),
		).with_for_update()
	)
	if record is None or record.used_at is not None:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")

	expires_at = record.expires_at
	if expires_at.tzinfo is None:
		expires_at = expires_at.replace(tzinfo=timezone.utc)
	if expires_at <= datetime.now(timezone.utc):
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token expired")

	user = db.scalar(select(User).where(User.id == record.user_id))
	if user is None or not user.is_active:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")

	user.password_hash = password_hasher.hash(new_password)
	record.used_at = datetime.now(timezone.utc)
	db.execute(
		update(UserSession)
		.where(UserSession.user_id == user.id, UserSession.revoked.is_(False))
		.values(revoked=True, revoked_at=datetime.now(timezone.utc))
	)
	record_security_event(db, "password_reset_completed", user_id=user.id)
	db.commit()


def find_user_by_email(db: Session, email: str) -> User | None:
	return db.scalar(select(User).where(User.email == email.lower()))
