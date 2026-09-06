
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    """Runtime state maintained during an agent execution."""

    user_input: str

    plan: list[dict[str, Any]] = field(
        default_factory=list
    )

    current_step: int = 0

    tool_calls: list[dict[str, Any]] = field(
        default_factory=list
    )

    tool_results: list[dict[str, Any]] = field(
        default_factory=list
    )

    final_answer: str | None = None

    completed: bool = False

    error: str | None = None
