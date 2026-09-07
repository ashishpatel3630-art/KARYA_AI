"""
Execution strategy builder for KARYA AI.

The strategy builder converts a classified request into a concrete
ExecutionPlan that the OrchestratorExecutor can execute.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from orchestrator.classifier import (
    ClassificationResult,
    RequestType,
)
from orchestrator.schemas import (
    ExecutionPlan,
    ExecutionStep,
    OrchestrationRequest,
)


@dataclass
class StrategyConfig:
    """Default configuration for orchestration strategies."""

    default_top_k: int = 3
    default_similarity_threshold: float = 0.60

    def __post_init__(self) -> None:
        if self.default_top_k < 1:
            raise ValueError(
                "default_top_k must be at least 1."
            )

        if not 0.0 <= self.default_similarity_threshold <= 1.0:
            raise ValueError(
                "default_similarity_threshold must be between 0 and 1."
            )


class StrategyBuilder:
    """
    Converts request classifications into execution plans.
    """

    def __init__(
        self,
        config: StrategyConfig | None = None,
    ) -> None:
        self.config = config or StrategyConfig()

    def build(
        self,
        request: OrchestrationRequest,
        classification: ClassificationResult,
    ) -> ExecutionPlan:
        """Build an execution plan for a classified request."""

        if not isinstance(
            request,
            OrchestrationRequest,
        ):
            raise TypeError(
                "request must be an OrchestrationRequest."
            )

        if not isinstance(
            classification,
            ClassificationResult,
        ):
            raise TypeError(
                "classification must be a ClassificationResult."
            )

        request_type = classification.request_type

        if request_type == RequestType.TEXT:
            return self._build_text_strategy(request)

        if request_type == RequestType.RAG:
            return self._build_rag_strategy(request)

        if request_type == RequestType.CALCULATION:
            return self._build_calculation_strategy(request)

        if request_type == RequestType.PYTHON:
            return self._build_python_strategy(request)

        if request_type == RequestType.FILE:
            return self._build_file_strategy(request)

        if request_type == RequestType.OCR:
            return self._build_ocr_strategy(request)

        if request_type == RequestType.VISION:
            return self._build_vision_strategy(request)

        if request_type == RequestType.AGENT:
            return self._build_agent_strategy(request)

        raise ValueError(
            f"Unsupported request type: {request_type}"
        )

    def _build_text_strategy(
        self,
        request: OrchestrationRequest,
    ) -> ExecutionPlan:
        """Build a direct local LLM strategy."""

        plan = ExecutionPlan(
            request=request,
            strategy="direct",
            reasoning=(
                "The request is a general text task, so "
                "the local LLM can answer directly."
            ),
        )

        plan.add_step(
            ExecutionStep(
                step_id="step_1",
                action="generate_answer",
                description="Generate a direct answer using the local LLM.",
                component="llm",
                arguments={
                    "prompt": request.user_input,
                },
            )
        )

        return plan

    def _build_rag_strategy(
        self,
        request: OrchestrationRequest,
    ) -> ExecutionPlan:
        """Build a retrieval-augmented generation strategy."""

        plan = ExecutionPlan(
            request=request,
            strategy="rag",
            reasoning=(
                "The request requires knowledge retrieval "
                "from the local KARYA knowledge base."
            ),
        )

        plan.add_step(
            ExecutionStep(
                step_id="step_1",
                action="retrieve_context",
                description="Retrieve relevant local knowledge.",
                component="rag",
                arguments={
                    "question": request.user_input,
                    "top_k": self.config.default_top_k,
                    "similarity_threshold": (
                        self.config.default_similarity_threshold
                    ),
                },
            )
        )

        plan.add_step(
            ExecutionStep(
                step_id="step_2",
                action="generate_answer",
                description=(
                    "Generate an answer using the retrieved "
                    "knowledge and the local LLM."
                ),
                component="llm",
                depends_on=["step_1"],
                arguments={
                    "prompt": (
                        "Answer the user's request using the "
                        "verified retrieved context.\n\n"
                        f"User request: {request.user_input}"
                    ),
                },
            )
        )

        return plan

    def _build_calculation_strategy(
        self,
        request: OrchestrationRequest,
    ) -> ExecutionPlan:
        """Build a safe calculator-first strategy."""

        expression = self._extract_calculation_expression(
            request.user_input
        )

        plan = ExecutionPlan(
            request=request,
            strategy="calculation",
            reasoning=(
                "The request is computational, so the "
                "calculator tool should produce the verified "
                "numeric result before explanation."
            ),
        )

        plan.add_step(
            ExecutionStep(
                step_id="step_1",
                action="execute_tool",
                description="Evaluate the mathematical expression.",
                component="tool",
                tool_name="calculator",
                arguments={
                    "expression": expression,
                },
            )
        )

        plan.add_step(
            ExecutionStep(
                step_id="step_2",
                action="generate_answer",
                description=(
                    "Explain the verified calculation result "
                    "using the local LLM."
                ),
                component="llm",
                depends_on=["step_1"],
                arguments={
                    "prompt": (
                        "Give the final answer to the user's "
                        "calculation request. Use the verified "
                        "calculator result from the previous step. "
                        "Do not invent or change the numeric result.\n\n"
                        f"User request: {request.user_input}"
                    ),
                },
            )
        )

        return plan

    def _build_python_strategy(
        self,
        request: OrchestrationRequest,
    ) -> ExecutionPlan:
        """Build a sandboxed Python execution strategy."""

        code = self._extract_python_code(
            request.user_input
        )

        plan = ExecutionPlan(
            request=request,
            strategy="python",
            reasoning=(
                "The request requires Python execution, "
                "so execution is delegated to the sandboxed "
                "Python tool."
            ),
        )

        plan.add_step(
            ExecutionStep(
                step_id="step_1",
                action="execute_tool",
                description="Execute Python safely in the sandbox.",
                component="tool",
                tool_name="python",
                arguments={
                    "code": code,
                },
            )
        )

        return plan

    def _build_file_strategy(
        self,
        request: OrchestrationRequest,
    ) -> ExecutionPlan:
        """Build a local file-reading strategy."""

        file_path = self._extract_file_path(
            request.user_input
        )

        plan = ExecutionPlan(
            request=request,
            strategy="file",
            reasoning=(
                "The request requires reading a local document "
                "or file before generating an analysis."
            ),
        )

        plan.add_step(
            ExecutionStep(
                step_id="step_1",
                action="read_file",
                description="Read the requested local file.",
                component="file",
                arguments={
                    "file_path": file_path,
                },
            )
        )

        plan.add_step(
            ExecutionStep(
                step_id="step_2",
                action="generate_answer",
                description=(
                    "Analyze the file content using the local LLM."
                ),
                component="llm",
                depends_on=["step_1"],
                arguments={
                    "prompt": (
                        "Analyze the file content retrieved in "
                        "the previous step.\n\n"
                        f"User request: {request.user_input}"
                    ),
                },
            )
        )

        return plan

    def _build_ocr_strategy(
        self,
        request: OrchestrationRequest,
    ) -> ExecutionPlan:
        """Build an OCR strategy."""

        file_path = self._extract_file_path(
            request.user_input
        )

        plan = ExecutionPlan(
            request=request,
            strategy="ocr",
            reasoning=(
                "The request requires text extraction from "
                "a scanned or image-based document."
            ),
        )

        plan.add_step(
            ExecutionStep(
                step_id="step_1",
                action="extract_text",
                description="Extract text using the local OCR engine.",
                component="ocr",
                arguments={
                    "file_path": file_path,
                },
            )
        )

        plan.add_step(
            ExecutionStep(
                step_id="step_2",
                action="generate_answer",
                description="Analyze the OCR output.",
                component="llm",
                depends_on=["step_1"],
                arguments={
                    "prompt": (
                        "Analyze the OCR-extracted text and answer "
                        "the user's request.\n\n"
                        f"User request: {request.user_input}"
                    ),
                },
            )
        )

        return plan

    def _build_vision_strategy(
        self,
        request: OrchestrationRequest,
    ) -> ExecutionPlan:
        """Build an image-analysis strategy."""

        image_path = self._extract_image_path(
            request.user_input
        )

        plan = ExecutionPlan(
            request=request,
            strategy="vision",
            reasoning=(
                "The request requires local multimodal "
                "image analysis."
            ),
        )

        plan.add_step(
            ExecutionStep(
                step_id="step_1",
                action="analyze_image",
                description="Analyze the image using the local vision model.",
                component="vision",
                arguments={
                    "image_path": image_path,
                    "prompt": request.user_input,
                },
            )
        )

        return plan

    def _build_agent_strategy(
        self,
        request: OrchestrationRequest,
    ) -> ExecutionPlan:
        """Build a full agent strategy."""

        plan = ExecutionPlan(
            request=request,
            strategy="agent",
            reasoning=(
                "The request requires multiple capabilities "
                "or dynamic tool selection, so the KARYA agent "
                "will plan and execute the workflow."
            ),
        )

        plan.add_step(
            ExecutionStep(
                step_id="step_1",
                action="execute_agent",
                description=(
                    "Let the KARYA agent plan and execute "
                    "the multi-step task."
                ),
                component="agent",
            )
        )

        return plan

    @staticmethod
    def _extract_calculation_expression(
        user_input: str,
    ) -> str:
        """
        Extract the mathematical expression from natural language.

        Examples:

            Calculate 25 * 4 + 10
            → 25 * 4 + 10

            What is 100 / 5?
            → 100 / 5

            Solve (25 + 5) * 2
            → (25 + 5) * 2
        """

        text = user_input.strip()

        patterns = (
            r"(?:calculate|compute|evaluate|solve)\s+(.+)",
            r"(?:what\s+is)\s+(.+)",
        )

        expression: str | None = None

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if match:
                expression = match.group(1).strip()
                break

        if expression is None:
            expression = text

        expression = expression.rstrip("?.!")

        # Keep only the mathematical expression when there is
        # explanatory text surrounding it.
        expression = expression.strip()

        if not expression:
            raise ValueError(
                "Unable to extract a mathematical expression."
            )

        return expression

    @staticmethod
    def _extract_python_code(
        user_input: str,
    ) -> str:
        """Extract Python code from a natural-language request."""

        text = user_input.strip()

        match = re.search(
            r"```(?:python)?\s*(.*?)```",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        if match:
            return match.group(1).strip()

        prefixes = (
            "run python",
            "execute python",
            "run this python",
            "execute this python",
        )

        lowered = text.lower()

        for prefix in prefixes:
            if lowered.startswith(prefix):
                return text[len(prefix):].strip(
                    " :\n"
                )

        return text

    @staticmethod
    def _extract_file_path(
        user_input: str,
    ) -> str:
        """
        Extract a likely local file path.

        The planner intentionally performs only lightweight extraction.
        More sophisticated file discovery will be handled by the
        search/file subsystem.
        """

        quoted = re.findall(
            r"""["']([^"']+\.(?:pdf|docx|xlsx|pptx|txt|csv))["']""",
            user_input,
            flags=re.IGNORECASE,
        )

        if quoted:
            return quoted[0]

        path_match = re.search(
            r"([^\s\"']+\.(?:pdf|docx|xlsx|pptx|txt|csv))",
            user_input,
            flags=re.IGNORECASE,
        )

        if path_match:
            return path_match.group(1)

        return ""

    @staticmethod
    def _extract_image_path(
        user_input: str,
    ) -> str:
        """Extract a likely image path."""

        quoted = re.findall(
            r"""["']([^"']+\.(?:png|jpg|jpeg|webp|bmp))["']""",
            user_input,
            flags=re.IGNORECASE,
        )

        if quoted:
            return quoted[0]

        path_match = re.search(
            r"([^\s\"']+\.(?:png|jpg|jpeg|webp|bmp))",
            user_input,
            flags=re.IGNORECASE,
        )

        if path_match:
            return path_match.group(1)

        return ""