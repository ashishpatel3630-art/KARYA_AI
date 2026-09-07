
from __future__ import annotations

import re
from typing import Any

from llm.schemas import LLMMessage, LLMRequest
from llm.service import LLMService
from tools.registry import ToolRegistry, create_default_registry
from tools.schemas import ToolCall

from .state import AgentState


class AgentExecutor:
    """
    Executes structured agent plans using real local tools
    and the local LLM.

    Responsibilities:
    1. Execute deterministic tools.
    2. Maintain verified execution results.
    3. Resolve dependencies between steps.
    4. Resolve $step_N placeholders.
    5. Prevent fabricated tool results.
    6. Execute normal LLM reasoning steps.
    7. Record tool calls and execution results.
    8. Keep all execution local.
    """

    PREVIOUS_RESULT_TOKEN = "$PREVIOUS_RESULT"

    # Correct pattern for:
    # $step_1
    # $step_2
    # $step_10
    STEP_RESULT_PATTERN = re.compile(
        r"\$step_(\d+)",
        re.IGNORECASE,
    )

    def __init__(
        self,
        llm_service: LLMService | None = None,
        tool_registry: ToolRegistry | None = None,
    ) -> None:
        self.llm_service = (
            llm_service or LLMService()
        )

        self.tool_registry = (
            tool_registry or create_default_registry()
        )

    # =============================================================
    # STEP EXECUTION
    # =============================================================

    def execute_step(
        self,
        state: AgentState,
        step: dict[str, Any],
    ) -> str:
        """
        Execute one agent step.

        Tool steps are executed through ToolRegistry.

        Non-tool steps are executed by the local LLM using
        the actual prompt supplied by the planner.
        """

        if not isinstance(step, dict):
            raise ValueError(
                "Agent step must be a dictionary."
            )

        action = step.get("action")

        if not isinstance(action, str):
            raise ValueError(
                "Agent step must contain a valid action."
            )

        action = action.strip()

        if not action:
            raise ValueError(
                "Agent step action cannot be empty."
            )

        tool_name = step.get("tool")

        arguments = step.get(
            "arguments",
            {},
        )

        if arguments is None:
            arguments = {}

        if not isinstance(arguments, dict):
            raise ValueError(
                "Agent step arguments must be a dictionary."
            )

        # ---------------------------------------------------------
        # TOOL EXECUTION
        # ---------------------------------------------------------

        if tool_name is not None:
            if not isinstance(tool_name, str):
                raise ValueError(
                    "Tool name must be a string or null."
                )

            tool_name = tool_name.strip()

            if not tool_name:
                raise ValueError(
                    "Tool name cannot be empty."
                )

            if not self.tool_registry.exists(
                tool_name
            ):
                raise ValueError(
                    f"Tool '{tool_name}' is not registered."
                )

            resolved_arguments = (
                self._resolve_tool_arguments(
                    state=state,
                    tool_name=tool_name,
                    arguments=arguments,
                )
            )

            return self.execute_tool(
                state=state,
                tool_name=tool_name,
                arguments=resolved_arguments,
            )

        # ---------------------------------------------------------
        # LLM EXECUTION
        # ---------------------------------------------------------

        resolved_arguments = (
            self._resolve_arguments(
                state=state,
                value=arguments,
            )
        )

        if not isinstance(
            resolved_arguments,
            dict,
        ):
            raise ValueError(
                "Resolved LLM arguments must be a dictionary."
            )

        prompt = resolved_arguments.get(
            "prompt"
        )

        if prompt is not None:
            if not isinstance(
                prompt,
                str,
            ):
                raise ValueError(
                    "LLM step prompt must be a string."
                )

            return self._execute_llm_step(
                state=state,
                prompt=prompt,
                action=action,
            )

        return self._execute_llm_step(
            state=state,
            prompt=action,
            action=action,
        )

    # =============================================================
    # TOOL EXECUTION
    # =============================================================

    def execute_tool(
        self,
        state: AgentState,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> str:
        """
        Execute a registered tool and record the result.
        """

        tool_call = ToolCall(
            tool_name=tool_name,
            arguments=arguments,
        )

        result = self.tool_registry.execute(
            tool_call
        )

        tool_record = {
            "tool": tool_name,
            "arguments": arguments,
            "success": result.success,
            "output": result.output,
            "error": result.error,
        }

        state.tool_calls.append(
            tool_record
        )

        if not result.success:
            raise ValueError(
                f"Tool '{tool_name}' failed: "
                f"{result.error}"
            )

        if result.output is None:
            raise ValueError(
                f"Tool '{tool_name}' returned no output."
            )

        output = str(
            result.output
        ).strip()

        if not output:
            raise ValueError(
                f"Tool '{tool_name}' returned empty output."
            )

        return output

    # =============================================================
    # LLM STEP
    # =============================================================

    def _execute_llm_step(
        self,
        state: AgentState,
        prompt: str,
        action: str | None = None,
    ) -> str:
        """
        Execute a non-tool step using the local LLM.

        The supplied prompt has already been resolved.

        The LLM is explicitly instructed to use only verified
        execution results and never fabricate missing information.
        """

        if not isinstance(
            prompt,
            str,
        ):
            raise ValueError(
                "LLM prompt must be a string."
            )

        prompt = prompt.strip()

        if not prompt:
            raise ValueError(
                "LLM prompt cannot be empty."
            )

        verified_results = (
            self._get_verified_results_text(
                state
            )
        )

        execution_context = (
            "KARYA VERIFIED EXECUTION CONTEXT\n\n"
            "The following information was produced by real "
            "local tools or previous local execution steps.\n\n"
            "VERIFIED RESULTS:\n\n"
            f"{verified_results}\n\n"
            "IMPORTANT:\n"
            "The VERIFIED RESULTS section is evidence only.\n"
            "Do not assume information that is not present there."
        )

        system_prompt = """
You are a precise execution component of KARYA,
a sovereign industrial AI system.

Your job is to execute the requested reasoning step
using ONLY the information supplied in the user prompt
and verified execution context.

STRICT SAFETY RULES:

- Never invent facts.
- Never invent measurements.
- Never invent thresholds.
- Never invent limits.
- Never invent calculations.
- Never invent tool execution.
- Never claim access to external systems.
- Never claim access to sensors.
- Never claim access to databases unless a real tool
  provided that information.
- Never claim access to files unless a real tool
  provided that information.
- Never claim network access.
- Never use outside knowledge when the task explicitly
  requires document-grounded information.
- If required information is missing, explicitly say so.
- Preserve exact units.
- Preserve exact values.
- If a value is unavailable, return the required
  unavailable marker when the user prompt specifies one.
- Keep the response concise and directly related
  to the requested execution step.
""".strip()

        full_prompt = (
            f"{execution_context}\n\n"
            "EXECUTION STEP:\n\n"
            f"{action or 'Execute the requested task.'}\n\n"
            "TASK PROMPT:\n\n"
            f"{prompt}"
        )

        request = LLMRequest(
            messages=[
                LLMMessage(
                    role="system",
                    content=system_prompt,
                ),
                LLMMessage(
                    role="user",
                    content=full_prompt,
                ),
            ],
            temperature=0.1,
        )

        response = self.llm_service.chat(
            request
        )

        result = response.content.strip()

        if not result:
            raise ValueError(
                "Executor received an empty response "
                "from the local LLM."
            )

        return result

    # =============================================================
    # CURRENT STEP
    # =============================================================

    def execute_current_step(
        self,
        state: AgentState,
    ) -> AgentState:
        """
        Execute the current plan step and update state.
        """

        if not state.plan:
            raise ValueError(
                "Cannot execute because the agent "
                "has no plan."
            )

        if state.current_step < 0:
            raise ValueError(
                "Agent current_step cannot be negative."
            )

        if state.current_step >= len(
            state.plan
        ):
            state.completed = True
            return state

        step_index = state.current_step

        step = state.plan[
            step_index
        ]

        if not isinstance(
            step,
            dict,
        ):
            raise ValueError(
                f"Plan step {step_index + 1} is invalid."
            )

        step_id = step.get(
            "step_id",
            f"step_{step_index + 1}",
        )

        try:
            result = self.execute_step(
                state=state,
                step=step,
            )

            state.tool_results.append(
                {
                    "step": step_index + 1,
                    "step_id": step_id,
                    "action": step.get(
                        "action"
                    ),
                    "tool": step.get(
                        "tool"
                    ),
                    "arguments": step.get(
                        "arguments",
                        {},
                    ),
                    "result": result,
                }
            )

            state.current_step += 1

            if (
                state.current_step
                >= len(state.plan)
            ):
                state.completed = True

            return state

        except Exception as exc:
            state.error = str(exc)
            state.completed = False
            raise

    # =============================================================
    # ARGUMENT RESOLUTION
    # =============================================================

    def _resolve_tool_arguments(
        self,
        state: AgentState,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Resolve dynamic arguments before tool execution.

        Supported dependencies:

            $PREVIOUS_RESULT
            $step_1
            $step_2
            $step_3

        References can appear anywhere inside strings.
        """

        resolved = self._resolve_arguments(
            state=state,
            value=arguments,
        )

        if not isinstance(
            resolved,
            dict,
        ):
            raise ValueError(
                "Resolved tool arguments must be a dictionary."
            )

        # Calculator requires numeric substitution.
        if tool_name == "calculator":
            resolved = self._resolve_calculator_arguments(
                state=state,
                arguments=resolved,
            )

        return resolved

    # =============================================================
    # GENERIC ARGUMENT RESOLUTION
    # =============================================================

    def _resolve_arguments(
        self,
        state: AgentState,
        value: Any,
    ) -> Any:
        """
        Recursively resolve execution references.

        Supports:

            $PREVIOUS_RESULT
            $step_1
            $step_2
            $step_3

        References can appear anywhere inside a string.

        Example:

            "DOCUMENT:\\n$step_1"

        becomes:

            "DOCUMENT:\\n[actual step 1 result]"
        """

        # ---------------------------------------------------------
        # DICTIONARY
        # ---------------------------------------------------------

        if isinstance(
            value,
            dict,
        ):
            return {
                key: self._resolve_arguments(
                    state=state,
                    value=item,
                )
                for key, item in value.items()
            }

        # ---------------------------------------------------------
        # LIST
        # ---------------------------------------------------------

        if isinstance(
            value,
            list,
        ):
            return [
                self._resolve_arguments(
                    state=state,
                    value=item,
                )
                for item in value
            ]

        # ---------------------------------------------------------
        # TUPLE
        # ---------------------------------------------------------

        if isinstance(
            value,
            tuple,
        ):
            return tuple(
                self._resolve_arguments(
                    state=state,
                    value=item,
                )
                for item in value
            )

        # ---------------------------------------------------------
        # NON-STRING
        # ---------------------------------------------------------

        if not isinstance(
            value,
            str,
        ):
            return value

        resolved = value

        # ---------------------------------------------------------
        # $PREVIOUS_RESULT
        # ---------------------------------------------------------

        if (
            self.PREVIOUS_RESULT_TOKEN
            in resolved
        ):
            previous_result = (
                self._get_previous_result(
                    state
                )
            )

            resolved = resolved.replace(
                self.PREVIOUS_RESULT_TOKEN,
                previous_result,
            )

        # ---------------------------------------------------------
        # $step_N
        # ---------------------------------------------------------

        matches = list(
            self.STEP_RESULT_PATTERN.finditer(
                resolved
            )
        )

        # Replace from right to left so string indexes
        # remain valid while replacing multiple references.
        for match in reversed(
            matches
        ):
            step_number = int(
                match.group(1)
            )

            step_result = (
                self._get_step_result(
                    state=state,
                    step_number=step_number,
                )
            )

            start, end = match.span()

            resolved = (
                resolved[:start]
                + step_result
                + resolved[end:]
            )

        return resolved

    # =============================================================
    # CALCULATOR ARGUMENT RESOLUTION
    # =============================================================

    def _resolve_calculator_arguments(
        self,
        state: AgentState,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Convert calculator dependency references into
        numeric values where required.

        Example:

            "$step_2 - 80"

        where step 2 contains:

            "92 C"

        becomes:

            "92 - 80"
        """

        resolved = dict(
            arguments
        )

        expression = resolved.get(
            "expression"
        )

        if not isinstance(
            expression,
            str,
        ):
            return resolved

        def replace_step(
            match: re.Match[str],
        ) -> str:
            step_number = int(
                match.group(1)
            )

            result = (
                self._get_step_result(
                    state=state,
                    step_number=step_number,
                )
            )

            return self._extract_numeric_value(
                result
            )

        expression = self.STEP_RESULT_PATTERN.sub(
            replace_step,
            expression,
        )

        if (
            self.PREVIOUS_RESULT_TOKEN
            in expression
        ):
            previous_result = (
                self._get_previous_result(
                    state
                )
            )

            expression = expression.replace(
                self.PREVIOUS_RESULT_TOKEN,
                self._extract_numeric_value(
                    previous_result
                ),
            )

        resolved[
            "expression"
        ] = expression

        return resolved

    # =============================================================
    # PREVIOUS RESULT
    # =============================================================

    def _get_previous_result(
        self,
        state: AgentState,
    ) -> str:
        """
        Return the most recent verified execution result.
        """

        if not state.tool_results:
            raise ValueError(
                "$PREVIOUS_RESULT requires a previous "
                "execution result."
            )

        previous = state.tool_results[-1]

        if not isinstance(
            previous,
            dict,
        ):
            raise ValueError(
                "Previous execution result is invalid."
            )

        result = previous.get(
            "result"
        )

        if result is None:
            raise ValueError(
                "Previous execution result is unavailable."
            )

        result_text = str(
            result
        ).strip()

        if not result_text:
            raise ValueError(
                "Previous execution result is empty."
            )

        return result_text

    # =============================================================
    # STEP RESULT
    # =============================================================

    def _get_step_result(
        self,
        state: AgentState,
        step_number: int,
    ) -> str:
        """
        Return the verified result of a specific
        previously executed step.

        Example:

            $step_1

        resolves to the result produced by step 1.
        """

        if step_number <= 0:
            raise ValueError(
                f"Invalid step reference: "
                f"$step_{step_number}"
            )

        for record in state.tool_results:

            if not isinstance(
                record,
                dict,
            ):
                continue

            record_step = record.get(
                "step"
            )

            record_step_id = record.get(
                "step_id"
            )

            if (
                record_step == step_number
                or record_step_id
                == f"step_{step_number}"
            ):
                result = record.get(
                    "result"
                )

                if result is None:
                    raise ValueError(
                        f"Result for step {step_number} "
                        "is unavailable."
                    )

                result_text = str(
                    result
                ).strip()

                if not result_text:
                    raise ValueError(
                        f"Result for step {step_number} "
                        "is empty."
                    )

                return result_text

        raise ValueError(
            f"Step result '$step_{step_number}' "
            "is not available yet."
        )

    # =============================================================
    # VERIFIED RESULTS
    # =============================================================

    def _get_verified_results_text(
        self,
        state: AgentState,
    ) -> str:
        """
        Format all previously executed results
        into clearly separated execution context.
        """

        if not state.tool_results:
            return (
                "No previous verified execution "
                "results are available."
            )

        sections: list[str] = []

        for record in state.tool_results:

            if not isinstance(
                record,
                dict,
            ):
                continue

            step = record.get(
                "step",
                "?",
            )

            step_id = record.get(
                "step_id",
                f"step_{step}",
            )

            result = record.get(
                "result"
            )

            if result is None:
                continue

            result_text = str(
                result
            ).strip()

            if not result_text:
                continue

            sections.append(
                f"STEP {step} ({step_id}) RESULT:\n"
                f"{result_text}"
            )

        if not sections:
            return (
                "No valid verified execution "
                "results are available."
            )

        return "\n\n".join(
            sections
        )

    # =============================================================
    # NUMERIC EXTRACTION
    # =============================================================

    def _extract_numeric_value(
        self,
        result: str,
    ) -> str:
        """
        Extract a numeric value from a verified result.

        Examples:

            92 C
            87.5 °C
            18 bar
            42.2 %
            1500 RPM
            12.5 V
            10 A
            55 kW
            3.2 mm/s

        If multiple numbers are present, the first numeric
        value is returned.

        This method is intended for deterministic
        calculator dependencies, not general NLP.
        """

        if not isinstance(
            result,
            str,
        ):
            result = str(
                result
            )

        # Correct numeric regex.
        matches = re.findall(
            r"[-+]?(?:\d+(?:\.\d+)?|\.\d+)",
            result,
        )

        if not matches:
            raise ValueError(
                "Could not extract a numeric value "
                "from the previous result."
            )

        return matches[0]
