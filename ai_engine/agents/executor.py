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
    4. Prevent fabricated tool results.
    5. Execute normal LLM reasoning steps when no tool is required.
    6. Record every tool call in AgentState.
    """

    PREVIOUS_RESULT_TOKEN = "$PREVIOUS_RESULT"

    def __init__(
        self,
        llm_service: LLMService | None = None,
        tool_registry: ToolRegistry | None = None,
    ):
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
        only verified information already present in state.
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

        return self._execute_llm_step(
            state=state,
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
        action: str,
    ) -> str:
        """
        Execute a non-tool step using the local LLM.

        The LLM receives only verified results.
        """

        verified_results = (
            self._get_verified_results_text(
                state
            )
        )

        prompt = f"""
You are the execution component of KARYA,
a sovereign industrial AI system.

Execute the following task step.

USER REQUEST:
{state.user_input}

CURRENT STEP:
{action}

VERIFIED PREVIOUS RESULTS:
{verified_results}

STRICT RULES:

- Use only verified information provided above.
- Do not invent facts.
- Do not fabricate tool execution.
- Do not claim access to external systems.
- Do not claim access to sensors.
- Do not claim access to databases unless a real tool
  provided that information.
- Do not claim access to files unless a real tool
  provided that information.
- Do not claim network access.
- If required information is unavailable,
  clearly state that it is unavailable.
- Keep the result concise.
""".strip()

        request = LLMRequest(
            messages=[
                LLMMessage(
                    role="system",
                    content=(
                        "You are a precise industrial AI "
                        "execution engine. "
                        "Never fabricate information."
                    ),
                ),
                LLMMessage(
                    role="user",
                    content=prompt,
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

        step = state.plan[
            state.current_step
        ]

        try:
            result = self.execute_step(
                state=state,
                step=step,
            )

            state.tool_results.append(
                {
                    "step": (
                        state.current_step + 1
                    ),
                    "action": step["action"],
                    "tool": step.get("tool"),
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

        Supported dependency:

            $PREVIOUS_RESULT

        Example:

            {
                "expression":
                    "$PREVIOUS_RESULT - 80"
            }

        The previous verified result is resolved before
        execution.
        """

        resolved_arguments = dict(
            arguments
        )

        for key, value in list(
            resolved_arguments.items()
        ):

            if not isinstance(value, str):
                continue

            if (
                self.PREVIOUS_RESULT_TOKEN
                not in value
            ):
                continue

            previous_result = (
                self._get_previous_result(
                    state
                )
            )

            replacement = (
                self._resolve_previous_result_value(
                    previous_result=previous_result,
                    tool_name=tool_name,
                    argument_name=key,
                )
            )

            resolved_arguments[key] = (
                value.replace(
                    self.PREVIOUS_RESULT_TOKEN,
                    replacement,
                )
            )

        return resolved_arguments

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
    # PREVIOUS RESULT RESOLUTION
    # =============================================================

    def _resolve_previous_result_value(
        self,
        previous_result: str,
        tool_name: str,
        argument_name: str,
    ) -> str:
        """
        Convert a previous result into a value suitable
        for the consuming tool.

        Calculator dependencies require a numeric value.

        Other tools receive the complete verified result.
        """

        if tool_name == "calculator":

            return self._extract_numeric_value(
                previous_result
            )

        return previous_result

    # =============================================================
    # NUMERIC EXTRACTION
    # =============================================================

    def _extract_numeric_value(
        self,
        result: str,
    ) -> str:
        """
        Extract a numeric value from a verified result.

        Supports common industrial measurements:

            92 C
            87.5 °C
            18 bar
            42.2 %
            1500 RPM
            12.5 V
            10 A
            55 kW
            3.2 mm/s

        The first valid measurement value is returned.
        """

        if not result or not result.strip():
            raise ValueError(
                "Cannot extract a numeric value "
                "from an empty result."
            )

        text = result.strip()

        # ---------------------------------------------------------
        # NUMBER + INDUSTRIAL UNIT
        # ---------------------------------------------------------

        unit_pattern = (
            r"(-?\d+(?:\.\d+)?)"
            r"\s*"
            r"(?:"
            r"°\s*C|"
            r"°C|"
            r"C|"
            r"bar|"
            r"kPa|"
            r"MPa|"
            r"psi|"
            r"%|"
            r"rpm|"
            r"V|"
            r"kV|"
            r"A|"
            r"kA|"
            r"W|"
            r"kW|"
            r"MW|"
            r"Hz|"
            r"mm/s|"
            r"m/s|"
            r"L/min|"
            r"m3/h|"
            r"kg|"
            r"kg/h|"
            r"ton|"
            r"tons|"
            r"Pa"
            r")"
            r"\b"
        )

        match = re.search(
            unit_pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            return match.group(1)

        # ---------------------------------------------------------
        # LABEL + NUMBER
        # ---------------------------------------------------------

        label_pattern = (
            r"(?:value|reading|measurement|"
            r"result|level|pressure|temperature|"
            r"flow|speed|rpm|vibration|voltage|"
            r"current|power|load)"
            r"\s*"
            r"(?:is|:|=|-)?"
            r"\s*"
            r"(-?\d+(?:\.\d+)?)"
        )

        match = re.search(
            label_pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            return match.group(1)

        # ---------------------------------------------------------
        # FALLBACK NUMERIC VALUE
        # ---------------------------------------------------------

        numbers = re.findall(
            r"-?\d+(?:\.\d+)?",
            text,
        )

        if len(numbers) == 1:
            return numbers[0]

        if not numbers:
            raise ValueError(
                "Could not extract a numeric value "
                "from the previous result."
            )

        raise ValueError(
            "Previous result contains multiple numeric "
            "values and cannot be safely resolved "
            "without additional context."
        )

    # =============================================================
    # VERIFIED RESULTS
    # =============================================================

    def _get_verified_results_text(
        self,
        state: AgentState,
    ) -> str:
        """
        Format verified execution results for LLM steps.
        """

        if not state.tool_results:
            return "None"

        results = []

        for item in state.tool_results:

            step_number = item.get(
                "step",
                "?",
            )

            action = item.get(
                "action",
                "",
            )

            tool = item.get(
                "tool"
            )

            result = item.get(
                "result"
            )

            results.append(
                (
                    f"Step {step_number}\n"
                    f"Action: {action}\n"
                    f"Tool: {tool}\n"
                    f"Verified result: {result}"
                )
            )

        return "\n\n".join(
            results
        )