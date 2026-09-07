from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class PermissionLevel(str, Enum):
    """Permission levels available to KARYA tools."""

    READ = "read"
    CALCULATE = "calculate"
    EXECUTE = "execute"
    WRITE = "write"
    ADMIN = "admin"


@dataclass(frozen=True)
class PermissionResult:
    """Result of a permission check."""

    allowed: bool
    reason: str

    def is_allowed(self) -> bool:
        return self.allowed


class PermissionManager:
    """
    Central permission manager for KARYA tools.

    KARYA follows a deny-by-default approach:
    a tool must have an explicitly granted permission
    before the operation is allowed.
    """

    DEFAULT_PERMISSIONS = frozenset(
        {
            PermissionLevel.READ,
            PermissionLevel.CALCULATE,
        }
    )

    def __init__(
        self,
        permissions: Iterable[
            PermissionLevel | str
        ] | None = None,
    ):
        if permissions is None:
            permissions = self.DEFAULT_PERMISSIONS

        self._permissions: set[
            PermissionLevel
        ] = set()

        for permission in permissions:
            self.grant(permission)

    def grant(
        self,
        permission: PermissionLevel | str,
    ) -> None:
        """Grant a permission."""

        normalized = self._normalize(permission)

        self._permissions.add(normalized)

    def revoke(
        self,
        permission: PermissionLevel | str,
    ) -> None:
        """Revoke a permission."""

        normalized = self._normalize(permission)

        self._permissions.discard(normalized)

    def has_permission(
        self,
        permission: PermissionLevel | str,
    ) -> bool:
        """Check whether a permission exists."""

        normalized = self._normalize(permission)

        return normalized in self._permissions

    def check(
        self,
        permission: PermissionLevel | str,
    ) -> PermissionResult:
        """Return a detailed permission result."""

        normalized = self._normalize(permission)

        if normalized in self._permissions:
            return PermissionResult(
                allowed=True,
                reason=(
                    f"Permission granted: "
                    f"{normalized.value}"
                ),
            )

        return PermissionResult(
            allowed=False,
            reason=(
                f"Permission denied: "
                f"{normalized.value}"
            ),
        )

    def require(
        self,
        permission: PermissionLevel | str,
    ) -> None:
        """Raise PermissionError when permission is denied."""

        result = self.check(permission)

        if not result.allowed:
            raise PermissionError(
                result.reason
            )

    def list_permissions(self) -> list[str]:
        """Return all currently granted permissions."""

        return sorted(
            permission.value
            for permission in self._permissions
        )

    def clear(self) -> None:
        """Remove all permissions."""

        self._permissions.clear()

    def grant_all(self) -> None:
        """Grant every available permission."""

        self._permissions = set(
            PermissionLevel
        )

    def _normalize(
        self,
        permission: PermissionLevel | str,
    ) -> PermissionLevel:
        """Normalize a permission value."""

        if isinstance(
            permission,
            PermissionLevel,
        ):
            return permission

        if not isinstance(permission, str):
            raise TypeError(
                "permission must be a "
                "PermissionLevel or string."
            )

        value = permission.strip().lower()

        if not value:
            raise ValueError(
                "permission cannot be empty."
            )

        try:
            return PermissionLevel(value)

        except ValueError as exc:
            allowed = ", ".join(
                permission.value
                for permission in PermissionLevel
            )

            raise ValueError(
                f"Unknown permission '{permission}'. "
                f"Allowed permissions: {allowed}"
            ) from exc


TOOL_PERMISSIONS: dict[
    str,
    PermissionLevel,
] = {
    "calculator": PermissionLevel.CALCULATE,
    "file_reader": PermissionLevel.READ,
    "search": PermissionLevel.READ,
    "python": PermissionLevel.EXECUTE,
    "rag": PermissionLevel.READ,
}


def required_permission(
    tool_name: str,
) -> PermissionLevel:
    """Return the permission required by a tool."""

    if not isinstance(tool_name, str):
        raise TypeError(
            "tool_name must be a string."
        )

    normalized_name = (
        tool_name.strip().lower()
    )

    if not normalized_name:
        raise ValueError(
            "tool_name cannot be empty."
        )

    try:
        return TOOL_PERMISSIONS[
            normalized_name
        ]

    except KeyError as exc:
        raise ValueError(
            f"No permission policy configured "
            f"for tool '{tool_name}'."
        ) from exc


def check_tool_permission(
    manager: PermissionManager,
    tool_name: str,
) -> PermissionResult:
    """Check whether a tool has the required permission."""

    if not isinstance(
        manager,
        PermissionManager,
    ):
        raise TypeError(
            "manager must be a PermissionManager."
        )

    permission = required_permission(
        tool_name
    )

    return manager.check(permission)


def require_tool_permission(
    manager: PermissionManager,
    tool_name: str,
) -> None:
    """Require the permission needed by a tool."""

    if not isinstance(
        manager,
        PermissionManager,
    ):
        raise TypeError(
            "manager must be a PermissionManager."
        )

    permission = required_permission(
        tool_name
    )

    manager.require(permission)