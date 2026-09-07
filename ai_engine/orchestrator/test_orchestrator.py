"""
Tests for the KARYA AI orchestration layer.
"""

from __future__ import annotations

import unittest

from orchestrator.classifier import RequestType
from orchestrator.orchestrator import (
    KARYAOrchestrator,
    KaryaOrchestrator,
    create_orchestrator,
)
from orchestrator.schemas import (
    OrchestrationRequest,
)


class TestKARYAOrchestrator(unittest.TestCase):
    """Test the main KARYA orchestration pipeline."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.orchestrator = KARYAOrchestrator()

    def test_calculator_orchestration(self) -> None:
        """Calculator request should execute successfully."""

        result = self.orchestrator.orchestrate(
            "Calculate 25 * 4 + 10"
        )

        self.assertTrue(
            result.success,
            result.error,
        )

        self.assertIsNone(
            result.error
        )

        self.assertEqual(
            result.metadata["request_type"],
            RequestType.CALCULATION.value,
        )

        self.assertEqual(
            len(result.step_results),
            2,
        )

        self.assertTrue(
            result.step_results[0].success
        )

        self.assertEqual(
            result.step_results[0].output,
            110,
        )

        self.assertTrue(
            result.step_results[1].success
        )

        self.assertTrue(
            result.answer
        )

    def test_classification(self) -> None:
        """Requests should be classified correctly."""

        result = self.orchestrator.classify(
            "Search the maintenance documents for Compressor C-101"
        )

        self.assertEqual(
            result.request_type,
            RequestType.RAG,
        )

        self.assertGreater(
            result.confidence,
            0.5,
        )

    def test_build_rag_plan(self) -> None:
        """RAG requests should produce a RAG execution plan."""

        request = OrchestrationRequest(
            user_input=(
                "Search the maintenance documents "
                "for Compressor C-101"
            )
        )

        classification = self.orchestrator.classify(
            request.user_input
        )

        plan = self.orchestrator.build_plan(
            request,
            classification,
        )

        self.assertEqual(
            plan.strategy,
            "rag",
        )

        self.assertGreaterEqual(
            len(plan.steps),
            2,
        )

        self.assertEqual(
            plan.steps[0].component,
            "rag",
        )

        self.assertEqual(
            plan.steps[0].action,
            "retrieve_context",
        )

        self.assertEqual(
            plan.steps[1].component,
            "llm",
        )

        self.assertEqual(
            plan.steps[1].action,
            "generate_answer",
        )

        self.assertEqual(
            plan.steps[1].depends_on,
            ["step_1"],
        )

    def test_plan_validation(self) -> None:
        """Generated plans should pass validation."""

        request = OrchestrationRequest(
            user_input="Calculate 10 + 20"
        )

        classification = self.orchestrator.classify(
            request.user_input
        )

        plan = self.orchestrator.build_plan(
            request,
            classification,
        )

        errors = plan.validate()

        self.assertEqual(
            errors,
            [],
        )

    def test_alias_class(self) -> None:
        """KaryaOrchestrator should be the public alias."""

        self.assertIs(
            KARYAOrchestrator,
            KaryaOrchestrator,
        )

    def test_factory(self) -> None:
        """Factory should return a working orchestrator."""

        orchestrator = create_orchestrator()

        self.assertIsInstance(
            orchestrator,
            KARYAOrchestrator,
        )

    def test_empty_input(self) -> None:
        """Empty input should be rejected."""

        with self.assertRaises(ValueError):
            self.orchestrator.orchestrate("")

    def test_whitespace_input(self) -> None:
        """Whitespace-only input should be rejected."""

        with self.assertRaises(ValueError):
            self.orchestrator.orchestrate(
                "     "
            )

    def test_invalid_input_type(self) -> None:
        """Non-string input should be rejected."""

        with self.assertRaises(TypeError):
            self.orchestrator.orchestrate(
                123  # type: ignore[arg-type]
            )

    def test_request_building(self) -> None:
        """Metadata and IDs should be preserved."""

        request = OrchestrationRequest(
            user_input="Calculate 5 + 5",
            conversation_id="conversation-001",
            user_id="user-001",
            metadata={
                "source": "test",
            },
        )

        classification = self.orchestrator.classify(
            request.user_input
        )

        plan = self.orchestrator.build_plan(
            request,
            classification,
        )

        self.assertEqual(
            plan.request.conversation_id,
            "conversation-001",
        )

        self.assertEqual(
            plan.request.user_id,
            "user-001",
        )

        self.assertEqual(
            plan.request.metadata["source"],
            "test",
        )


if __name__ == "__main__":
    unittest.main()