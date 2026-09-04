from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.verification.service import verify_email


router = APIRouter(prefix="/verification", tags=["Email verification"])


class VerificationRequest(BaseModel):
	token: str = Field(min_length=20)


@router.post("/confirm")
def confirm_verification(data: VerificationRequest, db: Session = Depends(get_db)):
	verify_email(db, data.token)
	return {"message": "Email verified successfully"}
