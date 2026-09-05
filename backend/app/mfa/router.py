import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.password import verify_password
from app.auth.tokens import (
	create_access_token,
	create_refresh_token,
	decode_mfa_challenge,
)
from app.core.database import get_db
from app.core.config import settings
from app.mfa.service import (
	enable_totp,
	enroll_totp,
	verify_recovery_code,
	verify_totp,
)
from app.models.mfa import MFA
from app.models.session import Session as UserSession
from app.models.user import User
from app.security.audit import record_security_event
from app.security.rate_limit import enforce_auth_rate_limit
from app.sessions.service import create_session


router = APIRouter(prefix="/mfa", tags=["MFA"])


class MFACode(BaseModel):
	code: str = Field(pattern=r"^\d{6}$")


class MFAChallenge(BaseModel):
	challenge_token: str = Field(min_length=20)
	code: str = Field(min_length=6, max_length=16)


class MFADisableRequest(BaseModel):
	password: str = Field(min_length=1)


@router.post("/totp/enroll")
def enroll(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	return enroll_totp(db, user)


@router.post("/totp/enable")
def enable(data: MFACode, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	recovery_codes = enable_totp(db, user, data.code)
	record_security_event(db, "mfa_enabled", user_id=user.id)
	return {"message": "MFA enabled", "recovery_codes": recovery_codes}


@router.post("/totp/verify")
def verify(data: MFACode, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	if not verify_totp(db, user, data.code):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code")
	return {"message": "MFA verified"}


@router.post("/totp/challenge")
def complete_challenge(
	data: MFAChallenge,
	request: Request,
	db: Session = Depends(get_db),
):
	enforce_auth_rate_limit(
		key=f"mfa:ip:{request.client.host if request.client else 'unknown'}",
		limit=settings.MFA_RATE_LIMIT_PER_MINUTE,
	)
	try:
		payload = decode_mfa_challenge(data.challenge_token)
	except (jwt.PyJWTError, ValueError):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid MFA challenge",
		)

	user = db.scalar(
		select(User).where(
			User.id == payload["sub"],
			User.is_active.is_(True),
		)
	)
	if user is None or not (
		verify_totp(db, user, data.code)
		if len(data.code) == 6 and data.code.isdigit()
		else verify_recovery_code(db, user, data.code)
	):
		record_security_event(db, "mfa_login_failed", user_id=user.id if user else None)
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid MFA code",
		)

	access_token = create_access_token(user.id)
	refresh_token, jti, token_family, expires_at = create_refresh_token(user.id)
	create_session(
		db=db,
		user_id=user.id,
		refresh_token=refresh_token,
		expires_at=expires_at,
		ip_address=request.client.host if request.client else None,
		user_agent=request.headers.get("user-agent"),
		jti=jti,
		token_family=token_family,
	)
	record_security_event(db, "mfa_login_success", user_id=user.id)
	return {
		"access_token": access_token,
		"refresh_token": refresh_token,
		"token_type": "bearer",
	}


@router.post("/totp/disable")
def disable(
	data: MFADisableRequest,
	user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	if not verify_password(data.password, user.password_hash):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Reauthentication required",
		)
	method = db.scalar(
		select(MFA).where(MFA.user_id == user.id, MFA.type == "totp")
	)
	if method is not None:
		method.enabled = False
		record_security_event(db, "mfa_disabled", user_id=user.id)
		db.commit()
	return {"message": "MFA disabled"}
