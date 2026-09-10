from datetime import datetime, timezone
from typing import Any


def audit_log(
    *,
    user_id: str,
    action: str,
    details: dict[str, Any] | None = None,
) -> None:
    """
    Record an MCP security/audit event.

    This is the central audit entry point used by the
    MCP gateway, authorization layer, and security policies.
    """

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "action": action,
        "details": details or {},
    }

    print(
        "[KARYA AUDIT]",
        event,
    )