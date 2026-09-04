import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.email_verification_token import EmailVerificationToken
from app.models.user import User


def _hash_token(token: str) -> str:
	return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_verification_token(db: Session, user: User) -> str:
	token = secrets.token_urlsafe(32)
	db.add(
		EmailVerificationToken(
			user_id=user.id,
			token_hash=_hash_token(token),
			expires_at=datetime.now(timezone.utc)
			+ timedelta(minutes=settings.EMAIL_VERIFICATION_TTL_MINUTES),
		)
	)
	db.commit()
	return token


def verify_email(db: Session, token: str) -> None:
	record = db.scalar(
		select(EmailVerificationToken).where(
			EmailVerificationToken.token_hash == _hash_token(token),
		)
	)
	if record is None or record.used_at is not None:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token")

	expires_at = record.expires_at
	if expires_at.tzinfo is None:
		expires_at = expires_at.replace(tzinfo=timezone.utc)
	if expires_at <= datetime.now(timezone.utc):
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token expired")

	user = db.scalar(select(User).where(User.id == record.user_id))
	if user is None or not user.is_active:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token")

	user.is_verified = True
	record.used_at = datetime.now(timezone.utc)
	db.commit()
