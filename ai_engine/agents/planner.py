
import json
import re

from llm.schemas import LLMMessage, LLMRequest
from llm.service import LLMService

from tools.registry import ToolRegistry, create_default_registry

from .state import AgentState


class AgentPlanner:
    """Creates structured execution plans using the local LLM."""

    def __init__(
        self,
        llm_service: LLMService | None = None,
        tool_registry: ToolRegistry | None = None,
    ):
        self.llm_service = llm_service or LLMService()

        self.tool_registry = (
            tool_registry or create_default_registry()
        )

    def create_plan(
        self,
        state: AgentState,
    ) -> list[dict]:
        """Create a structured execution plan."""

        user_input = state.user_input.strip()

        if not user_input:
            raise ValueError(
                "Cannot create a plan for empty user input."
            )

        # Fast deterministic path for simple calculations.
        calculator_expression = self._detect_calculation(
            user_input
        )

        if calculator_expression is not None:
            return [
                {
                    "action": (
                        f"Calculate {calculator_expression}"
                    ),
                    "tool": "calculator",
                    "arguments": {
                        "expression": calculator_expression
                    },
                }
            ]

        # Fast deterministic path for local file reading.
        file_path = self._detect_file_request(
            user_input
        )

        if file_path is not None:
            return [
                {
                    "action": f"Read file {file_path}",
                    "tool": "file_reader",
                    "arguments": {
                        "file_path": file_path
                    },
                }
            ]

        # Fast deterministic path for knowledge-base search.
        search_query = self._detect_search_request(
            user_input
        )

        if search_query is not None:
            return [
                {
                    "action": (
                        "Search the knowledge base for "
                        f"{search_query}"
                    ),
                    "tool": "search",
                    "arguments": {
                        "query": search_query
                    },
                }
            ]

        tool_descriptions = (
            self._get_tool_descriptions()
        )

        prompt = f"""
You are the planning component of KARYA,
a sovereign industrial AI system.

Create the shortest correct execution plan
for the user's request.

USER REQUEST:
{user_input}

AVAILABLE TOOLS:
{tool_descriptions}

Return ONLY valid JSON.

Required structure:

{{
    "steps": [
        {{
            "action": "clear description of the action",
            "tool": null,
            "arguments": {{}}
        }}
    ]
}}

Rules:

- Create only the steps that are actually necessary.
- Prefer the shortest valid plan.
- Use 1 step whenever one step is sufficient.
- Maximum 6 steps.
- Do not create artificial reasoning steps.
- Do not create steps such as:
  - parse the request
  - understand the request
  - think about the problem
  - split the problem
  - return the answer
  unless an actual tool or external operation requires them.
- If a registered tool can directly perform the requested operation,
  use that tool.
- For mathematical calculations, use the calculator tool directly.
- For local document reading, use the file_reader tool.
- For knowledge-base searches, use the search tool.
- Only use tools listed under AVAILABLE TOOLS.
- Do not invent tools.
- Do not execute tools.
- Do not provide the final answer.

For a simple calculation:

User:
Calculate 1200 + 3500

Return:

{{
    "steps": [
        {{
            "action": "Calculate 1200 + 3500",
            "tool": "calculator",
            "arguments": {{
                "expression": "1200 + 3500"
            }}
        }}
    ]
}}
""".strip()

        request = LLMRequest(
            messages=[
                LLMMessage(
                    role="system",
                    content=(
                        "You are a precise task planning engine. "
                        "Create the minimum necessary steps. "
                        "Return only valid JSON."
                    ),
                ),
                LLMMessage(
                    role="user",
                    content=prompt,
                ),
            ],
            temperature=0.0,
        )

        response = self.llm_service.chat(request)

        raw_content = response.content.strip()

        data = self._parse_json(raw_content)

        if not isinstance(data, dict):
            raise ValueError(
                "Planner response must be a JSON object."
            )

        steps = data.get("steps")

        if not isinstance(steps, list):
            raise ValueError(
                "Planner response must contain a 'steps' list."
            )

        if not steps:
            raise ValueError(
                "Planner returned an empty execution plan."
            )

        if len(steps) > 6:
            raise ValueError(
                "Planner returned more than 6 steps."
            )

        cleaned_steps = []

        available_tools = set(
            self.tool_registry.list_tools()
        )

        for step in steps:

            if not isinstance(step, dict):
                raise ValueError(
                    "Every plan step must be an object."
                )

            action = step.get("action")
            tool = step.get("tool")
            arguments = step.get("arguments")

            if not isinstance(action, str):
                raise ValueError(
                    "Every plan step must contain "
                    "a valid 'action'."
                )

            action = action.strip()

            if not action:
                raise ValueError(
                    "Plan action cannot be empty."
                )

            if tool is not None:

                if not isinstance(tool, str):
                    raise ValueError(
                        "Plan tool must be a string or null."
                    )

                if tool not in available_tools:
                    raise ValueError(
                        f"Planner requested unknown tool: {tool}"
                    )

                if not isinstance(arguments, dict):
                    raise ValueError(
                        "Tool arguments must be an object."
                    )

            else:
                arguments = {}

            cleaned_steps.append(
                {
                    "action": action,
                    "tool": tool,
                    "arguments": arguments,
                }
            )

        return cleaned_steps

    def plan_task(
        self,
        state: AgentState,
    ) -> AgentState:
        """Create a plan and store it in agent state."""

        plan = self.create_plan(state)

        state.plan = plan
        state.current_step = 0
        state.completed = False
        state.error = None

        return state

    def _detect_calculation(
        self,
        user_input: str,
    ) -> str | None:
        """Detect a simple mathematical expression."""

        text = user_input.strip()

        patterns = [
            r"^(?:calculate|compute|solve)\s+(.+?)\s*[.?]?$",
            r"^what\s+is\s+(.+?)\s*[.?]?$",
            r"^how\s+much\s+is\s+(.+?)\s*[.?]?$",
        ]

        expression = None

        for pattern in patterns:
            match = re.match(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if match:
                expression = match.group(1).strip()
                break

        if expression is None:
            return None

        if not self._is_safe_calculation_expression(
            expression
        ):
            return None

        if not self.tool_registry.exists(
            "calculator"
        ):
            return None

        return expression

    def _is_safe_calculation_expression(
        self,
        expression: str,
    ) -> bool:
        """Check whether text looks like a simple calculation."""

        if not expression:
            return False

        allowed_characters = re.fullmatch(
            r"[0-9+\-*/%().\s]+",
            expression,
        )

        if not allowed_characters:
            return False

        operators = "+-*/%"

        return any(
            operator in expression
            for operator in operators
        )

    def _detect_file_request(
        self,
        user_input: str,
    ) -> str | None:
        """Detect a request to read a local supported file."""

        if not self.tool_registry.exists(
            "file_reader"
        ):
            return None

        text = user_input.strip()

        file_match = re.search(
            r"([^\s\"']+\.(?:pdf|docx|xlsx|pptx))",
            text,
            flags=re.IGNORECASE,
        )

        if not file_match:
            return None

        file_path = file_match.group(1)

        read_keywords = [
            "read",
            "open",
            "analyze",
            "analyse",
            "review",
            "inspect",
            "extract",
            "summarize",
            "summarise",
        ]

        text_without_path = text.replace(
            file_path,
            "",
        ).lower()

        if not any(
            keyword in text_without_path
            for keyword in read_keywords
        ):
            return None

        return file_path

    def _detect_search_request(
        self,
        user_input: str,
    ) -> str | None:
        """Detect a request to search the local knowledge base."""

        if not self.tool_registry.exists(
            "search"
        ):
            return None

        text = user_input.strip()

        if not text:
            return None

        search_keywords = [
            "search",
            "find information",
            "find details",
            "look for",
            "look up",
            "lookup",
            "search for",
            "search the knowledge base",
            "find in documents",
            "according to the documents",
            "according to the report",
            "what does the document say",
            "retrieve",
        ]

        lower_text = text.lower()

        if not any(
            keyword in lower_text
            for keyword in search_keywords
        ):
            return None

        return text

    def _get_tool_descriptions(self) -> str:
        """Return descriptions of registered tools."""

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

    def _parse_json(
        self,
        raw_content: str,
    ) -> dict:
        """Parse JSON returned by the planner."""

        try:
            return json.loads(raw_content)

        except json.JSONDecodeError:

            start = raw_content.find("{")
            end = raw_content.rfind("}")

            if start == -1 or end == -1:
                raise ValueError(
                    "Planner returned invalid JSON."
                )

            try:
                return json.loads(
                    raw_content[start:end + 1]
                )

            except json.JSONDecodeError as exc:
                raise ValueError(
                    "Planner returned invalid JSON."
                ) from exc