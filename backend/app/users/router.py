from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.authorization.dependencies import require_roles
from app.core.database import get_db
from app.models.user import User


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
def current_profile(user: User = Depends(get_current_user)):
	return {
		"id": user.id,
		"email": user.email,
		"role": user.role,
		"is_active": user.is_active,
		"is_verified": user.is_verified,
	}


@router.get("/admin-check")
def admin_check(user: User = Depends(require_roles("ADMIN"))):
	return {"message": "Admin access granted", "user_id": user.id}
