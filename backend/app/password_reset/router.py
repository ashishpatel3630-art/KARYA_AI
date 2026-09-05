from pydantic import BaseModel, EmailStr, Field
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.password_reset.service import (
	create_password_reset_token,
	find_user_by_email,
	reset_password,
)
from app.security.rate_limit import enforce_auth_rate_limit


router = APIRouter(prefix="/password-reset", tags=["Password reset"])


class PasswordResetRequest(BaseModel):
	email: EmailStr


class PasswordResetConfirm(BaseModel):
	token: str = Field(min_length=20)
	new_password: str = Field(min_length=8)


@router.post("/request", status_code=status.HTTP_202_ACCEPTED)
def request_reset(
	data: PasswordResetRequest,
	request: Request,
	db: Session = Depends(get_db),
):
	enforce_auth_rate_limit(
		key=f"password-reset:ip:{request.client.host if request.client else 'unknown'}",
		limit=settings.PASSWORD_RESET_RATE_LIMIT,
	)
	user = find_user_by_email(db, data.email)
	token = create_password_reset_token(db, user) if user and user.is_active else None
	response = {"message": "If the account exists, a reset link has been issued."}
	if token is not None:
		response["reset_token"] = token
	return response


@router.post("/confirm")
def confirm_reset(data: PasswordResetConfirm, db: Session = Depends(get_db)):
	reset_password(db, data.token, data.new_password)
	return {"message": "Password reset successfully"}
