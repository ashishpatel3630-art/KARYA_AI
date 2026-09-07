"""
Main orchestration entry point for KARYA AI.

The KARYAOrchestrator coordinates:

    User Request
        ↓
    Classification
        ↓
    Strategy
        ↓
    Execution Plan
        ↓
    Execution
        ↓
    Final Result
"""

from __future__ import annotations

from orchestrator.classifier import (
    ClassificationResult,
    RequestClassifier,
)
from orchestrator.executor import OrchestratorExecutor
from orchestrator.schemas import (
    ExecutionPlan,
    OrchestrationRequest,
    OrchestrationResult,
)
from orchestrator.strategy import StrategyBuilder
from rag.schemas import deduplicate_citations


class KARYAOrchestrator:
    """
    Main entry point for the KARYA AI engine.

    This class does not implement individual AI capabilities itself.
    Instead, it coordinates the specialized subsystems already built
    inside ai_engine.
    """

    def __init__(
        self,
        classifier: RequestClassifier | None = None,
        strategy_builder: StrategyBuilder | None = None,
        executor: OrchestratorExecutor | None = None,
    ) -> None:
        self.classifier = (
            classifier
            or RequestClassifier()
        )

        self.strategy_builder = (
            strategy_builder
            or StrategyBuilder()
        )

        self.executor = (
            executor
            or OrchestratorExecutor()
        )

    def classify(
        self,
        user_input: str,
    ) -> ClassificationResult:
        """
        Classify a user request.
        """

        return self.classifier.classify(
            user_input
        )

    def build_plan(
        self,
        request: OrchestrationRequest,
        classification: ClassificationResult | None = None,
    ) -> ExecutionPlan:
        """
        Build an execution plan for a request.
        """

        if not isinstance(
            request,
            OrchestrationRequest,
        ):
            raise TypeError(
                "request must be an OrchestrationRequest."
            )

        if classification is None:
            classification = self.classify(
                request.user_input
            )

        if not isinstance(
            classification,
            ClassificationResult,
        ):
            raise TypeError(
                "classification must be a ClassificationResult."
            )

        plan = self.strategy_builder.build(
            request,
            classification,
        )

        if not isinstance(
            plan,
            ExecutionPlan,
        ):
            raise TypeError(
                "StrategyBuilder must return an ExecutionPlan."
            )

        return plan

    def execute_plan(
        self,
        plan: ExecutionPlan,
    ) -> OrchestrationResult:
        """
        Execute an existing plan.
        """

        return self.executor.execute(
            plan
        )

    def orchestrate(
        self,
        user_input: str,
        conversation_id: str | None = None,
        user_id: str | None = None,
        metadata: dict | None = None,
    ) -> OrchestrationResult:
        """
        Run the complete KARYA orchestration pipeline.

        Flow:

            input
              ↓
            request
              ↓
            classification
              ↓
            strategy
              ↓
            execution
              ↓
            final result
        """

        if not isinstance(
            user_input,
            str,
        ):
            raise TypeError(
                "user_input must be a string."
            )

        user_input = user_input.strip()

        if not user_input:
            raise ValueError(
                "user_input cannot be empty."
            )

        request = OrchestrationRequest(
            user_input=user_input,
            conversation_id=conversation_id,
            user_id=user_id,
            metadata=metadata or {},
        )

        classification = self.classify(
            user_input
        )

        plan = self.build_plan(
            request,
            classification,
        )

        result = self.execute_plan(
            plan
        )

        result.metadata.update(
            {
                "request_type": (
                    classification.request_type.value
                ),
                "classification_confidence": (
                    classification.confidence
                ),
                "classification_reasons": (
                    classification.reasons
                ),
                "requires_multiple_components": (
                    classification.requires_multiple_components
                ),
            }
        )

        return self._finalize_result(
            result
        )

    def _finalize_result(
        self,
        result: OrchestrationResult,
    ) -> OrchestrationResult:
        """
        Build the final user-facing answer.

        For a single-step execution, the step output is normally
        already the final answer.

        For multi-step workflows, combine successful outputs so
        the caller can inspect the complete execution trace.
        """

        if not result.success:
            return result

        successful_steps = [
            step
            for step in result.step_results
            if step.success
        ]

        if not successful_steps:
            result.success = False
            result.error = (
                "Orchestration completed without "
                "a successful execution step."
            )
            return result

        if len(successful_steps) == 1:
            output = successful_steps[0].output

            if output is not None:
                result.answer = str(
                    output
                ).strip()

        else:
            result.answer = self._combine_outputs(
                successful_steps
            )

        citations = deduplicate_citations(result.citations)
        if citations:
            sources = "\n".join(
                citation.user_facing_label(index)
                for index, citation in enumerate(citations, start=1)
            )
            result.answer = f"{result.answer}\n\nSources:\n{sources}"

        return result

    @staticmethod
    def _combine_outputs(
        successful_steps: list,
    ) -> str:
        """
        Combine multiple step outputs into a readable result.
        """

        sections: list[str] = []

        for step in successful_steps:
            if step.output is None:
                continue

            output = str(
                step.output
            ).strip()

            if not output:
                continue

            sections.append(
                f"[{step.step_id}]\n{output}"
            )

        return "\n\n".join(
            sections
        )


# Convenient alias for application code.

KaryaOrchestrator = KARYAOrchestrator


def create_orchestrator() -> KARYAOrchestrator:
    """
    Create a default KARYA orchestrator instance.
    """

    return KARYAOrchestrator()
