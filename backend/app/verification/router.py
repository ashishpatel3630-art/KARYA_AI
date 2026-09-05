from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.security.rate_limit import enforce_auth_rate_limit
from app.verification.service import create_verification_token, verify_email


router = APIRouter(prefix="/verification", tags=["Email verification"])


class VerificationRequest(BaseModel):
	token: str = Field(min_length=20)


@router.post("/confirm")
def confirm_verification(data: VerificationRequest, db: Session = Depends(get_db)):
	verify_email(db, data.token)
	return {"message": "Email verified successfully"}


@router.post("/resend", status_code=status.HTTP_202_ACCEPTED)
def resend_verification(
	request: Request,
	user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	enforce_auth_rate_limit(
		key=f"verification-resend:user:{user.id}",
		limit=settings.VERIFICATION_RESEND_RATE_LIMIT,
	)
	if not user.is_verified:
		create_verification_token(db, user)
	return {"message": "If verification is required, instructions have been sent."}
