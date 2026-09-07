"""
KARYA AI orchestration executor.

Executes an ExecutionPlan by dispatching each step
to the appropriate KARYA subsystem.
"""

from __future__ import annotations

from typing import Any

from agents.agent import KaryaAgent
from llm.schemas import LLMMessage, LLMRequest
from llm.service import LLMService
from ocr.service import OCRService
from orchestrator.schemas import (
    ExecutionPlan,
    ExecutionStep,
    OrchestrationResult,
    OrchestrationRequest,
    StepResult,
)
from tools.registry import ToolRegistry, create_default_registry
from tools.schemas import ToolCall
from vision.service import VisionService


class OrchestratorExecutor:
    """
    Executes KARYA orchestration plans.

    Supported components:

    - llm
    - rag
    - tool
    - agent
    - ocr
    - vision
    - file
    """

    def __init__(
        self,
        llm_service: LLMService | None = None,
        tool_registry: ToolRegistry | None = None,
        agent: KaryaAgent | None = None,
        ocr_service: OCRService | None = None,
        vision_service: VisionService | None = None,
    ) -> None:
        self.llm_service = (
            llm_service
            or LLMService()
        )

        self.tool_registry = (
            tool_registry
            or create_default_registry()
        )

        self.agent = (
            agent
            or KaryaAgent()
        )

        self.ocr_service = (
            ocr_service
            or OCRService()
        )

        self.vision_service = (
            vision_service
            or VisionService()
        )

    def execute(
        self,
        plan: ExecutionPlan,
    ) -> OrchestrationResult:
        """
        Execute all steps in an orchestration plan.
        """

        if not isinstance(
            plan,
            ExecutionPlan,
        ):
            raise TypeError(
                "plan must be an ExecutionPlan."
            )

        validation_errors = plan.validate()

        if validation_errors:
            return OrchestrationResult(
                success=False,
                answer="",
                plan=plan,
                step_results=[],
                error=(
                    "Invalid execution plan: "
                    + "; ".join(validation_errors)
                ),
            )

        step_results: list[StepResult] = []

        completed_outputs: dict[str, Any] = {}

        for step in plan.steps:
            dependency_error = self._check_dependencies(
                step,
                completed_outputs,
            )

            if dependency_error:
                result = StepResult(
                    step_id=step.step_id,
                    success=False,
                    output=None,
                    error=dependency_error,
                )

                step_results.append(result)

                return OrchestrationResult(
                    success=False,
                    answer="",
                    plan=plan,
                    step_results=step_results,
                    error=dependency_error,
                )

            try:
                output = self._execute_step(
                    plan.request,
                    step,
                    completed_outputs,
                )

                result = StepResult(
                    step_id=step.step_id,
                    success=True,
                    output=output,
                    error=None,
                )

                step_results.append(result)

                completed_outputs[
                    step.step_id
                ] = output

            except Exception as exc:
                result = StepResult(
                    step_id=step.step_id,
                    success=False,
                    output=None,
                    error=str(exc),
                )

                step_results.append(result)

                return OrchestrationResult(
                    success=False,
                    answer="",
                    plan=plan,
                    step_results=step_results,
                    error=(
                        f"Step '{step.step_id}' failed: "
                        f"{exc}"
                    ),
                )

        return OrchestrationResult(
            success=True,
            answer="",
            plan=plan,
            step_results=step_results,
            error=None,
        )

    def _execute_step(
        self,
        request: OrchestrationRequest,
        step: ExecutionStep,
        completed_outputs: dict[str, Any],
    ) -> Any:
        """
        Dispatch one execution step.
        """

        component = step.component.strip().lower()

        arguments = self._resolve_arguments(
            step.arguments,
            completed_outputs,
        )

        if component == "llm":
            return self._execute_llm(
                request,
                step,
                arguments,
                completed_outputs,
            )

        if component == "rag":
            return self._execute_rag(
                step,
                arguments,
            )

        if component == "tool":
            return self._execute_tool(
                step,
                arguments,
            )

        if component == "agent":
            return self._execute_agent(
                request,
                step,
                arguments,
            )

        if component == "ocr":
            return self._execute_ocr(
                step,
                arguments,
            )

        if component == "vision":
            return self._execute_vision(
                step,
                arguments,
            )

        if component == "file":
            return self._execute_file(
                step,
                arguments,
            )

        raise ValueError(
            f"Unsupported orchestration component: "
            f"{step.component}"
        )

    def _execute_llm(
        self,
        request: OrchestrationRequest,
        step: ExecutionStep,
        arguments: dict[str, Any],
        completed_outputs: dict[str, Any],
    ) -> str:
        """
        Execute a local LLM step.

        IMPORTANT:
        LLMService.chat() expects an LLMRequest,
        not a raw string.
        """

        prompt = arguments.get("prompt")

        if prompt is None:
            prompt = step.description

        if not isinstance(prompt, str):
            prompt = str(prompt)

        prompt = prompt.strip()

        if not prompt:
            raise ValueError(
                "LLM prompt cannot be empty."
            )

        previous_context = self._build_previous_context(
            step,
            completed_outputs,
        )

        if previous_context:
            prompt = (
                f"{prompt}\n\n"
                "Verified outputs from previous "
                "orchestration steps:\n"
                f"{previous_context}"
            )

        messages = [
            LLMMessage(
                role="user",
                content=prompt,
            )
        ]

        llm_request = LLMRequest(
            messages=messages,
            model=arguments.get("model"),
            temperature=float(
                arguments.get(
                    "temperature",
                    0.2,
                )
            ),
            max_tokens=int(
                arguments.get(
                    "max_tokens",
                    1024,
                )
            ),
        )

        response = self.llm_service.chat(
            llm_request
        )

        return self._extract_llm_text(
            response
        )

    def _execute_rag(
        self,
        step: ExecutionStep,
        arguments: dict[str, Any],
    ) -> Any:
        """
        Execute the RAG tool.
        """

        tool_name = (
            step.tool_name
            or "rag"
        )

        if not self.tool_registry.exists(
            tool_name
        ):
            raise ValueError(
                f"Tool '{tool_name}' is not registered."
            )

        tool_call = ToolCall(
            tool_name=tool_name,
            arguments=arguments,
        )

        result = self.tool_registry.execute(
            tool_call
        )

        if not result.success:
            raise ValueError(
                result.error
                or f"Tool '{tool_name}' failed."
            )

        return result.output

    def _execute_tool(
        self,
        step: ExecutionStep,
        arguments: dict[str, Any],
    ) -> Any:
        """
        Execute a registered tool.
        """

        if not step.tool_name:
            raise ValueError(
                "Tool execution step requires "
                "tool_name."
            )

        tool_name = step.tool_name

        if not self.tool_registry.exists(
            tool_name
        ):
            raise ValueError(
                f"Tool '{tool_name}' is not registered."
            )

        tool_call = ToolCall(
            tool_name=tool_name,
            arguments=arguments,
        )

        result = self.tool_registry.execute(
            tool_call
        )

        if not result.success:
            raise ValueError(
                result.error
                or f"Tool '{tool_name}' failed."
            )

        return result.output

    def _execute_agent(
        self,
        request: OrchestrationRequest,
        step: ExecutionStep,
        arguments: dict[str, Any],
    ) -> str:
        """
        Execute the KARYA agent.
        """

        user_input = arguments.get(
            "user_input"
        )

        if user_input is None:
            user_input = request.user_input

        if not isinstance(
            user_input,
            str,
        ):
            user_input = str(user_input)

        user_input = user_input.strip()

        if not user_input:
            raise ValueError(
                "Agent input cannot be empty."
            )

        return self.agent.ask(
            user_input
        )

    def _execute_ocr(
        self,
        step: ExecutionStep,
        arguments: dict[str, Any],
    ) -> str:
        """
        Execute OCR against a file.
        """

        file_path = arguments.get(
            "file_path"
        )

        if not file_path:
            raise ValueError(
                "OCR step requires 'file_path'."
            )

        result = self.ocr_service.extract_text(
            file_path
        )

        return self._extract_service_output(
            result
        )

    def _execute_vision(
        self,
        step: ExecutionStep,
        arguments: dict[str, Any],
    ) -> str:
        """
        Execute local vision analysis.
        """

        image_path = arguments.get(
            "image_path"
        )

        if not image_path:
            raise ValueError(
                "Vision step requires 'image_path'."
            )

        prompt = arguments.get(
            "prompt"
        )

        if prompt is None:
            prompt = step.description

        result = self.vision_service.analyze(
            image_path=image_path,
            prompt=prompt,
        )

        return self._extract_service_output(
            result
        )

    def _execute_file(
        self,
        step: ExecutionStep,
        arguments: dict[str, Any],
    ) -> Any:
        """
        Execute the file_reader tool.
        """

        tool_name = (
            step.tool_name
            or "file_reader"
        )

        if not self.tool_registry.exists(
            tool_name
        ):
            raise ValueError(
                f"Tool '{tool_name}' is not registered."
            )

        tool_call = ToolCall(
            tool_name=tool_name,
            arguments=arguments,
        )

        result = self.tool_registry.execute(
            tool_call
        )

        if not result.success:
            raise ValueError(
                result.error
                or f"Tool '{tool_name}' failed."
            )

        return result.output

    def _check_dependencies(
        self,
        step: ExecutionStep,
        completed_outputs: dict[str, Any],
    ) -> str | None:
        """
        Ensure all dependencies completed successfully.
        """

        for dependency in step.depends_on:
            if dependency not in completed_outputs:
                return (
                    f"Step '{step.step_id}' depends on "
                    f"'{dependency}', but that step has "
                    "not completed."
                )

        return None

    def _resolve_arguments(
        self,
        value: Any,
        completed_outputs: dict[str, Any],
    ) -> Any:
        """
        Resolve $step_id references recursively.

        Example:

            {
                "value": "$step_1"
            }

        becomes:

            {
                "value": 110
            }
        """

        if isinstance(value, dict):
            return {
                key: self._resolve_arguments(
                    item,
                    completed_outputs,
                )
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [
                self._resolve_arguments(
                    item,
                    completed_outputs,
                )
                for item in value
            ]

        if isinstance(value, tuple):
            return tuple(
                self._resolve_arguments(
                    item,
                    completed_outputs,
                )
                for item in value
            )

        if isinstance(value, str):
            if value.startswith("$"):
                reference = value[1:]

                if reference in completed_outputs:
                    return completed_outputs[
                        reference
                    ]

            return value

        return value

    def _build_previous_context(
        self,
        step: ExecutionStep,
        completed_outputs: dict[str, Any],
    ) -> str:
        """
        Build context from declared dependencies.
        """

        sections: list[str] = []

        for dependency in step.depends_on:
            if dependency not in completed_outputs:
                continue

            output = completed_outputs[
                dependency
            ]

            sections.append(
                f"[{dependency}]\n{output}"
            )

        return "\n\n".join(
            sections
        )

    @staticmethod
    def _extract_llm_text(
        response: Any,
    ) -> str:
        """
        Normalize an LLMResponse into text.
        """

        if response is None:
            raise ValueError(
                "LLM returned no response."
            )

        content = getattr(
            response,
            "content",
            None,
        )

        if content is None:
            if isinstance(
                response,
                str,
            ):
                content = response
            else:
                raise ValueError(
                    "LLM response does not contain "
                    "text content."
                )

        content = str(
            content
        ).strip()

        if not content:
            raise ValueError(
                "LLM returned empty content."
            )

        return content

    @staticmethod
    def _extract_service_output(
        result: Any,
    ) -> str:
        """
        Normalize service outputs into text.
        """

        if result is None:
            raise ValueError(
                "Service returned no output."
            )

        if isinstance(
            result,
            str,
        ):
            output = result.strip()

            if not output:
                raise ValueError(
                    "Service returned empty output."
                )

            return output

        for attribute in (
            "text",
            "content",
            "answer",
            "output",
        ):
            value = getattr(
                result,
                attribute,
                None,
            )

            if value is not None:
                output = str(
                    value
                ).strip()

                if output:
                    return output

        output = str(
            result
        ).strip()

        if not output:
            raise ValueError(
                "Service returned empty output."
            )

        return output


__all__ = [
    "OrchestratorExecutor",
]