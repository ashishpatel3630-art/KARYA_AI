from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EXECUTED = "executed"


@dataclass(frozen=True)
class ApprovalRequest:
    approval_id: str

    # Original requester
    user_id: str

    # Role required to approve this action
    approver_role: str

    # Actual approver identity
    approved_by_id: str | None

    work_id: str
    task_id: str

    server: str
    tool: str

    # Exact arguments captured when approval was requested
    arguments: dict[str, Any]

    risk_score: int
    risk_level: str

    # Approval lifecycle
    status: ApprovalStatus = ApprovalStatus.PENDING

    # Approval expiry
    expires_at: datetime | None = None

    # Lifecycle timestamps
    created_at: datetime | None = None
    approved_at: datetime | None = None
    rejected_at: datetime | None = None
    executed_at: datetime | None = None