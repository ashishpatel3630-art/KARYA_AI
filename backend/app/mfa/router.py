from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.mfa.service import enable_totp, enroll_totp, verify_totp
from app.models.user import User


router = APIRouter(prefix="/mfa", tags=["MFA"])


class MFACode(BaseModel):
	code: str = Field(pattern=r"^\d{6}$")


@router.post("/totp/enroll")
def enroll(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	return enroll_totp(db, user)


@router.post("/totp/enable")
def enable(data: MFACode, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	enable_totp(db, user, data.code)
	return {"message": "MFA enabled"}


@router.post("/totp/verify")
def verify(data: MFACode, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	if not verify_totp(db, user, data.code):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code")
	return {"message": "MFA verified"}
