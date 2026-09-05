import hashlib
import secrets
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.mfa.totp import generate_secret, provisioning_uri, verify_code
from app.models.mfa import MFA
from app.models.mfa_recovery_code import MFARecoveryCode
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


def enable_totp(db: Session, user: User, code: str) -> list[str]:
	method = db.scalar(
		select(MFA).where(MFA.user_id == user.id, MFA.type == "totp")
	)
	if method is None or not verify_code(method.secret, code):
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid MFA code")
	method.enabled = True
	recovery_codes = [secrets.token_urlsafe(8) for _ in range(10)]
	db.execute(delete(MFARecoveryCode).where(MFARecoveryCode.user_id == user.id))
	for recovery_code in recovery_codes:
		db.add(
			MFARecoveryCode(
				user_id=user.id,
				code_hash=hashlib.sha256(recovery_code.encode()).hexdigest(),
			)
		)
	db.commit()
	return recovery_codes


def verify_totp(db: Session, user: User, code: str) -> bool:
	method = db.scalar(
		select(MFA).where(
			MFA.user_id == user.id,
			MFA.type == "totp",
			MFA.enabled.is_(True),
		)
	)
	return method is not None and verify_code(method.secret, code)


def verify_recovery_code(db: Session, user: User, code: str) -> bool:
	record = db.scalar(
		select(MFARecoveryCode)
		.where(
			MFARecoveryCode.user_id == user.id,
			MFARecoveryCode.code_hash == hashlib.sha256(code.encode()).hexdigest(),
			MFARecoveryCode.used_at.is_(None),
		)
		.with_for_update()
	)
	if record is None:
		return False
	record.used_at = datetime.now(timezone.utc)
	db.commit()
	return True
