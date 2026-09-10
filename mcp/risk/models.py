from dataclasses import dataclass
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskAction(str, Enum):
    ALLOW = "allow"
    AUDIT_ALLOW = "audit_allow"
    REQUIRE_APPROVAL = "require_approval"
    BLOCK = "block"


@dataclass(frozen=True)
class RiskContext:
    tool_name: str
    role: str
    work_id: str
    task_id: str
    arguments: dict


@dataclass(frozen=True)
class RiskDecision:
    level: RiskLevel
    action: RiskAction
    score: int
    reasons: tuple[str, ...]