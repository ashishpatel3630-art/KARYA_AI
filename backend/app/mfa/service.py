from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.mfa.totp import generate_secret, provisioning_uri, verify_code
from app.models.mfa import MFA
from app.models.user import User


def enroll_totp(db: Session, user: User) -> dict[str, str]:
	method = db.scalar(
		select(MFA).where(MFA.user_id == user.id, MFA.type == "totp")
	)
	secret = generate_secret()
	if method is None:
		method = MFA(user_id=user.id, type="totp", secret=secret, enabled=False)
		db.add(method)
	else:
		method.secret = secret
		method.enabled = False
	db.commit()
	return {"secret": secret, "otpauth_uri": provisioning_uri(secret, user.email)}


def enable_totp(db: Session, user: User, code: str) -> None:
	method = db.scalar(
		select(MFA).where(MFA.user_id == user.id, MFA.type == "totp")
	)
	if method is None or not verify_code(method.secret, code):
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid MFA code")
	method.enabled = True
	db.commit()


def verify_totp(db: Session, user: User, code: str) -> bool:
	method = db.scalar(
		select(MFA).where(
			MFA.user_id == user.id,
			MFA.type == "totp",
			MFA.enabled.is_(True),
		)
	)
	return method is not None and verify_code(method.secret, code)
