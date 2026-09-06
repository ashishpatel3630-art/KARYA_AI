
from llm.schemas import LLMMessage, LLMRequest
from llm.service import LLMService

from tools.registry import ToolRegistry, create_default_registry
from tools.schemas import ToolCall

from .state import AgentState


class AgentExecutor:
    """Executes structured agent steps using the LLM and real tools."""

    def __init__(
        self,
        llm_service: LLMService | None = None,
        tool_registry: ToolRegistry | None = None,
    ):
        self.llm_service = llm_service or LLMService()

        self.tool_registry = (
            tool_registry or create_default_registry()
        )

    def execute_step(
        self,
        state: AgentState,
        step: dict,
    ) -> str:
        """Execute one structured plan step."""

        if not isinstance(step, dict):
            raise ValueError(
                "Agent step must be a dictionary."
            )

        action = step.get("action")

        if not isinstance(action, str) or not action.strip():
            raise ValueError(
                "Agent step must contain a valid action."
            )

        tool_name = step.get("tool")
        arguments = step.get("arguments", {})

        # ---------------------------------------------------------
        # REAL TOOL EXECUTION
        # ---------------------------------------------------------

        if tool_name is not None:

            if not isinstance(tool_name, str):
                raise ValueError(
                    "Tool name must be a string or null."
                )

            if not isinstance(arguments, dict):
                raise ValueError(
                    "Tool arguments must be a dictionary."
                )

            return self.execute_tool(
                state=state,
                tool_name=tool_name,
                arguments=arguments,
            )

        # ---------------------------------------------------------
        # NORMAL LLM EXECUTION
        # ---------------------------------------------------------

        context = ""

        if state.tool_results:
            context = "\n\n".join(
                str(result)
                for result in state.tool_results
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
{context if context else "None"}

IMPORTANT RULES:

- Do not invent facts.
- Do not claim that you accessed an external system.
- Do not claim that you accessed sensors, databases,
  monitoring systems, files, or networks unless a real
  tool provided that information.
- Use only the verified information provided.
- If required information is unavailable, clearly say so.
- Return a concise result for this step.
""".strip()

        request = LLMRequest(
            messages=[
                LLMMessage(
                    role="system",
                    content=(
                        "You are a precise industrial AI "
                        "execution engine. "
                        "Never fabricate tool execution."
                    ),
                ),
                LLMMessage(
                    role="user",
                    content=prompt,
                ),
            ],
            temperature=0.1,
        )

        response = self.llm_service.chat(request)

        result = response.content.strip()

        if not result:
            raise ValueError(
                "Executor received an empty response from the LLM."
            )

        return result

    def execute_tool(
        self,
        state: AgentState,
        tool_name: str,
        arguments: dict,
    ) -> str:
        """Execute a real tool through the Tool Registry."""

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

        return str(result.output)

    def execute_current_step(
        self,
        state: AgentState,
    ) -> AgentState:
        """Execute the current step stored in AgentState."""

        if not state.plan:
            raise ValueError(
                "Cannot execute because the agent has no plan."
            )

        if state.current_step >= len(state.plan):
            state.completed = True
            return state

        step = state.plan[state.current_step]

        try:

            result = self.execute_step(
                state=state,
                step=step,
            )

            state.tool_results.append(
                {
                    "step": state.current_step + 1,
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

            if state.current_step >= len(state.plan):
                state.completed = True

        except Exception as exc:

            state.error = str(exc)
            state.completed = False

            raise

        return state

    def _get_tool_descriptions(self) -> str:
        """Return descriptions of all registered tools."""

        definitions = (
            self.tool_registry.get_definitions()
        )

        if not definitions:
            return "No tools available."

        descriptions = []

        for definition in definitions:
            descriptions.append(
                (
                    f"- {definition.name}: "
                    f"{definition.description}\n"
                    f"  Input schema: "
                    f"{definition.input_schema}"
                )
            )

        return "\n".join(descriptions)
