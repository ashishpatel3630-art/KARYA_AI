from dataclasses import dataclass, field
from typing import Any

from rag.schemas import Citation


@dataclass
class AgentState:
    """
    Runtime state maintained during one KARYA agent execution.

    The state contains:

    - Original user request
    - Generated execution plan
    - Current execution position
    - Tool calls
    - Verified tool results
    - Final synthesized answer
    - Completion status
    - Error information
    """

    # =============================================================
    # USER REQUEST
    # =============================================================

    user_input: str

    # =============================================================
    # EXECUTION PLAN
    # =============================================================

    plan: list[dict[str, Any]] = field(
        default_factory=list
    )

    # Zero-based index of the step currently being executed.
    current_step: int = 0

    # =============================================================
    # TOOL EXECUTION HISTORY
    # =============================================================

    tool_calls: list[dict[str, Any]] = field(
        default_factory=list
    )

    # Results that have actually been produced by tools
    # or verified execution steps.
    tool_results: list[dict[str, Any]] = field(
        default_factory=list
    )

    citations: list[Citation] = field(
        default_factory=list
    )

    # =============================================================
    # FINAL OUTPUT
    # =============================================================

    final_answer: str | None = None

    # =============================================================
    # EXECUTION STATUS
    # =============================================================

    completed: bool = False

    # Error message when execution fails.
    error: str | None = None

    # =============================================================
    # HELPERS
    # =============================================================

    def has_plan(self) -> bool:
        """Return True when the agent has an execution plan."""

        return bool(self.plan)

    def has_results(self) -> bool:
        """Return True when execution produced results."""

        return bool(self.tool_results)

    def has_error(self) -> bool:
        """Return True when the agent has an execution error."""

        return self.error is not None

    def remaining_steps(self) -> int:
        """Return the number of plan steps that remain."""

        if self.current_step >= len(self.plan):
            return 0

        return len(self.plan) - self.current_step

    def current_plan_step(
        self,
    ) -> dict[str, Any] | None:
        """
        Return the current plan step.

        Returns None when execution has reached the end.
        """

        if (
            self.current_step < 0
            or self.current_step >= len(self.plan)
        ):
            return None

        return self.plan[self.current_step]

    def reset_execution(self) -> None:
        """
        Reset execution-specific state while preserving
        the original user request and plan.
        """

        self.current_step = 0
        self.tool_calls.clear()
        self.tool_results.clear()
        self.citations.clear()
        self.final_answer = None
        self.completed = False
        self.error = None