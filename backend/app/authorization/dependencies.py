from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.models.user import User


def require_roles(*allowed_roles: str) -> Callable:
	def dependency(user: User = Depends(get_current_user)) -> User:
		if user.role not in allowed_roles:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="Insufficient permissions",
			)
		return user

	return dependency
