"""
Schemas for the KARYA AI orchestration layer.

This module defines the data structures used to move a request
through classification, planning, execution, and final response.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class OrchestrationRequest:
    """User request entering the KARYA orchestration layer."""

    user_input: str
    conversation_id: str | None = None
    user_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.user_input, str):
            raise TypeError("user_input must be a string.")

        self.user_input = self.user_input.strip()

        if not self.user_input:
            raise ValueError("user_input cannot be empty.")

        if self.metadata is None:
            self.metadata = {}


@dataclass
class ExecutionStep:
    """One step inside an orchestration execution plan."""

    step_id: str
    action: str
    description: str
    component: str
    tool_name: str | None = None
    arguments: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    required: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.step_id = self.step_id.strip()
        self.action = self.action.strip()
        self.description = self.description.strip()
        self.component = self.component.strip()

        if not self.step_id:
            raise ValueError("step_id cannot be empty.")

        if not self.action:
            raise ValueError("action cannot be empty.")

        if not self.component:
            raise ValueError("component cannot be empty.")

        if self.tool_name is not None:
            self.tool_name = self.tool_name.strip()

        if self.arguments is None:
            self.arguments = {}

        if self.depends_on is None:
            self.depends_on = []

        if self.metadata is None:
            self.metadata = {}


@dataclass
class ExecutionPlan:
    """Complete plan generated for an orchestration request."""

    request: OrchestrationRequest
    steps: list[ExecutionStep] = field(default_factory=list)
    strategy: str = "direct"
    reasoning: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(
            self.request,
            OrchestrationRequest,
        ):
            raise TypeError(
                "request must be an OrchestrationRequest."
            )

        if self.steps is None:
            self.steps = []

        if self.metadata is None:
            self.metadata = {}

    def add_step(
        self,
        step: ExecutionStep,
    ) -> None:
        """Add a step to the execution plan."""

        if not isinstance(
            step,
            ExecutionStep,
        ):
            raise TypeError(
                "step must be an ExecutionStep."
            )

        if any(
            existing.step_id == step.step_id
            for existing in self.steps
        ):
            raise ValueError(
                f"Duplicate step_id: {step.step_id}"
            )

        self.steps.append(step)

    def get_step(
        self,
        step_id: str,
    ) -> ExecutionStep | None:
        """Return a step by ID."""

        for step in self.steps:
            if step.step_id == step_id:
                return step

        return None

    def validate(self) -> list[str]:
        """
        Validate the execution plan.

        Returns:
            A list of validation errors.

            An empty list means the plan is valid.
        """

        errors: list[str] = []

        if not self.steps:
            errors.append(
                "Execution plan contains no steps."
            )
            return errors

        step_ids = {
            step.step_id
            for step in self.steps
        }

        for step in self.steps:
            if not step.step_id:
                errors.append(
                    "Execution step has an empty step_id."
                )

            for dependency in step.depends_on:
                if dependency not in step_ids:
                    errors.append(
                        f"Step '{step.step_id}' depends on "
                        f"unknown step '{dependency}'."
                    )

            if step.step_id in step.depends_on:
                errors.append(
                    f"Step '{step.step_id}' cannot depend "
                    f"on itself."
                )

        # Detect dependency cycles using DFS.
        graph = {
            step.step_id: list(step.depends_on)
            for step in self.steps
        }

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(step_id: str) -> bool:
            if step_id in visiting:
                return True

            if step_id in visited:
                return False

            visiting.add(step_id)

            for dependency in graph.get(
                step_id,
                [],
            ):
                if dependency in graph:
                    if visit(dependency):
                        return True

            visiting.remove(step_id)
            visited.add(step_id)

            return False

        for step_id in graph:
            if visit(step_id):
                errors.append(
                    "Execution plan contains a dependency cycle."
                )
                break

        return errors


@dataclass
class StepResult:
    """Result produced by one executed orchestration step."""

    step_id: str
    success: bool
    output: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


@dataclass
class OrchestrationResult:
    """Final result returned by the KARYA orchestrator."""

    success: bool
    answer: str
    plan: ExecutionPlan | None = None
    step_results: list[StepResult] = field(
        default_factory=list
    )
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.answer is None:
            self.answer = ""

        if self.step_results is None:
            self.step_results = []

        if self.metadata is None:
            self.metadata = {}

    @property
    def completed_steps(self) -> list[StepResult]:
        """Return successfully completed steps."""

        return [
            result
            for result in self.step_results
            if result.success
        ]

    @property
    def failed_steps(self) -> list[StepResult]:
        """Return failed steps."""

        return [
            result
            for result in self.step_results
            if not result.success
        ]