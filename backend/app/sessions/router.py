from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.session import Session as UserSession
from app.models.user import User


router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("")
def list_sessions(
	user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	sessions = db.scalars(
		select(UserSession)
		.where(UserSession.user_id == user.id)
		.order_by(UserSession.created_at.desc())
	).all()
	return [
		{
			"id": session.id,
			"ip_address": session.ip_address,
			"user_agent": session.user_agent,
			"created_at": session.created_at,
			"expires_at": session.expires_at,
			"revoked": session.revoked,
		}
		for session in sessions
	]


@router.delete("/{session_id}")
def revoke_session(
	session_id: str,
	user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	session = db.scalar(
		select(UserSession).where(
			UserSession.id == session_id,
			UserSession.user_id == user.id,
		)
	)
	if session is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
	session.revoked = True
	session.revoked_at = datetime.now(timezone.utc)
	db.commit()
	return {"message": "Session revoked"}


@router.delete("")
def revoke_all_sessions(
	user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	result = db.execute(
		update(UserSession)
		.where(UserSession.user_id == user.id, UserSession.revoked.is_(False))
		.values(revoked=True, revoked_at=datetime.now(timezone.utc))
	)
	db.commit()
	return {"message": "Sessions revoked", "count": result.rowcount}
