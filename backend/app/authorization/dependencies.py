from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.models.user import User


def require_roles(*allowed_roles: str) -> Callable:
	def dependency(user: User = Depends(get_current_user)) -> User:
		if user.role.upper() not in {role.upper() for role in allowed_roles}:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="Insufficient permissions",
			)
		return user

	return dependency


ROLE_PERMISSIONS = {
	"USER": {
		"agents.execute",
		"tasks.read",
		"knowledge.read",
	},
	"STAFF": {
		"agents.execute",
		"tasks.read",
		"workflows.read",
		"workflows.execute",
		"analytics.read",
	},
	"ADMIN": {
		"users.read",
		"users.manage",
		"agents.execute",
		"workflows.execute",
		"analytics.read",
		"audit.read",
		"system.manage",
	},
}


def require_permission(permission: str) -> Callable:
	def dependency(user: User = Depends(get_current_user)) -> User:
		permissions = ROLE_PERMISSIONS.get(user.role.upper(), set())
		if permission not in permissions:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="Insufficient permissions",
			)
		return user

	return dependency
