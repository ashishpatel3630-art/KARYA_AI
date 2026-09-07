
import json
import re
from typing import Any

from llm.schemas import LLMMessage, LLMRequest
from llm.service import LLMService

from tools.registry import ToolRegistry, create_default_registry

from .state import AgentState


class AgentPlanner:
    """
    Creates structured execution plans for the KARYA agent.

    The planner follows a deterministic-first architecture:

    1. Detect deterministic operations locally.
    2. Build explicit tool plans when possible.
    3. Fall back to the local LLM for complex requests.
    4. Validate every LLM-generated plan before execution.

    The planner never executes tools.
    """

    MAX_PLAN_STEPS = 6

    SUPPORTED_FILE_EXTENSIONS = (
        "pdf",
        "docx",
        "xlsx",
        "pptx",
    )

    CALCULATION_KEYWORDS = (
        "calculate",
        "compute",
        "solve",
    )

    SEARCH_KEYWORDS = (
        "search",
        "find",
        "look up",
    )

    MULTI_STEP_CALCULATION_KEYWORDS = (
        "calculate",
        "compute",
        "solve",
        "how much",
        "difference",
        "exceeds",
        "above",
        "over",
        "greater than",
        "less than",
        "below",
        "under",
        "subtract",
        "minus",
    )

    MEASUREMENT_TYPES = (
        "temperature",
        "temp",
        "pressure",
        "level",
        "flow",
        "flow rate",
        "speed",
        "rpm",
        "vibration",
        "voltage",
        "current",
        "power",
        "load",
        "humidity",
        "frequency",
        "density",
        "viscosity",
        "capacity",
        "volume",
        "weight",
        "mass",
    )

    def __init__(
        self,
        llm_service: LLMService | None = None,
        tool_registry: ToolRegistry | None = None,
    ):
        self.llm_service = llm_service or LLMService()
        self.tool_registry = (
            tool_registry or create_default_registry()
        )

    # =============================================================
    # PUBLIC API
    # =============================================================

    def create_plan(
        self,
        state: AgentState,
    ) -> list[dict[str, Any]]:
        """
        Create a validated execution plan for the user request.
        """

        user_input = state.user_input.strip()

        if not user_input:
            raise ValueError(
                "Cannot create a plan for empty user input."
            )

        # ---------------------------------------------------------
        # 1. MULTI-STEP TOOL WORKFLOW
        # ---------------------------------------------------------

        multi_step_plan = self._detect_multi_step_request(
            user_input
        )

        if multi_step_plan is not None:
            return multi_step_plan

        # ---------------------------------------------------------
        # 2. SIMPLE CALCULATION
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # 3. LOCAL FILE READING
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # 4. KNOWLEDGE BASE SEARCH
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # 5. LOCAL LLM PLANNING
        # ---------------------------------------------------------

        return self._create_llm_plan(
            user_input
        )

    def plan_task(
        self,
        state: AgentState,
    ) -> AgentState:
        """
        Create a plan and store it in AgentState.
        """

        plan = self.create_plan(state)

        state.plan = plan
        state.current_step = 0
        state.completed = False
        state.error = None

        return state

    # =============================================================
    # MULTI-STEP PLANNING
    # =============================================================

    def _detect_multi_step_request(
        self,
        user_input: str,
    ) -> list[dict[str, Any]] | None:
        """
        Detect requests that require:

            Search → Extract verified value → Calculate

        Example:

            Find Pump P-201 temperature and calculate
            how much it exceeds 75 C.

        Example:

            Find Compressor C-101 pressure and calculate
            the difference from 20 bar.
        """

        text = user_input.strip()

        if not text:
            return None

        if not self.tool_registry.exists("search"):
            return None

        if not self.tool_registry.exists("calculator"):
            return None

        lower_text = text.lower()

        # ---------------------------------------------------------
        # CHECK CALCULATION INTENT
        # ---------------------------------------------------------

        if not any(
            keyword in lower_text
            for keyword in self.MULTI_STEP_CALCULATION_KEYWORDS
        ):
            return None

        # ---------------------------------------------------------
        # DETECT MEASUREMENT TYPE
        # ---------------------------------------------------------

        measurement_type = self._detect_measurement_type(
            lower_text
        )

        if measurement_type is None:
            return None

        # ---------------------------------------------------------
        # DETECT COMPARISON OPERATOR
        # ---------------------------------------------------------

        comparison = self._detect_comparison(
            lower_text
        )

        if comparison is None:
            return None

        operator_name = comparison["operator"]
        threshold = comparison["threshold"]

        # ---------------------------------------------------------
        # EXTRACT SEARCH SUBJECT
        # ---------------------------------------------------------

        search_query = self._extract_multi_step_subject(
            text=text,
            measurement_type=measurement_type,
        )

        if search_query is None:
            return None

        # ---------------------------------------------------------
        # CREATE SEARCH STEP
        # ---------------------------------------------------------

        search_step = {
            "action": (
                "Search the knowledge base for "
                f"{search_query}"
            ),
            "tool": "search",
            "arguments": {
                "query": search_query,
            },
        }

        # ---------------------------------------------------------
        # CREATE CALCULATION STEP
        # ---------------------------------------------------------

        calculation_expression = (
            self._build_calculation_expression(
                operator_name=operator_name,
                threshold=threshold,
            )
        )

        calculation_action = (
            f"Calculate the {measurement_type} "
            f"relative to {threshold} "
            f"using the verified value from "
            f"the previous search result"
        )

        calculation_step = {
            "action": calculation_action,
            "tool": "calculator",
            "arguments": {
                "expression": calculation_expression,
            },
        }

        return [
            search_step,
            calculation_step,
        ]

    def _detect_measurement_type(
        self,
        text: str,
    ) -> str | None:
        """
        Detect the measurement/value involved
        in a multi-step calculation.
        """

        measurements = sorted(
            self.MEASUREMENT_TYPES,
            key=len,
            reverse=True,
        )

        for measurement in measurements:
            pattern = rf"\b{re.escape(measurement)}\b"

            if re.search(
                pattern,
                text,
                re.IGNORECASE,
            ):
                return measurement

        return None

    def _detect_comparison(
        self,
        text: str,
    ) -> dict[str, str] | None:
        """
        Detect comparison language and threshold.

        Examples:

            exceeds 80
            above 80
            over 80
            greater than 80
            difference from 80
            below 50
            less than 50
        """

        patterns = [
            (
                r"(?:exceeds|above|over|greater than)"
                r"\s+"
                r"(-?\d+(?:\.\d+)?)",
                "subtract",
            ),
            (
                r"(?:less than|below|under)"
                r"\s+"
                r"(-?\d+(?:\.\d+)?)",
                "subtract_reverse",
            ),
            (
                r"(?:difference from|difference of)"
                r"\s+"
                r"(-?\d+(?:\.\d+)?)",
                "absolute_difference",
            ),
        ]

        for pattern, operator_name in patterns:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:
                return {
                    "operator": operator_name,
                    "threshold": match.group(1),
                }

        return None

    def _build_calculation_expression(
        self,
        operator_name: str,
        threshold: str,
    ) -> str:
        """
        Build a calculator expression using
        the verified previous result.

        The executor resolves:

            $PREVIOUS_RESULT

        before the calculator runs.
        """

        if operator_name == "subtract":
            return (
                f"$PREVIOUS_RESULT - {threshold}"
            )

        if operator_name == "subtract_reverse":
            return (
                f"{threshold} - $PREVIOUS_RESULT"
            )

        if operator_name == "absolute_difference":
            return (
                f"abs($PREVIOUS_RESULT - {threshold})"
            )

        raise ValueError(
            f"Unsupported comparison operator: "
            f"{operator_name}"
        )

    def _extract_multi_step_subject(
        self,
        text: str,
        measurement_type: str,
    ) -> str | None:
        """
        Extract the entity/equipment that should
        be searched.
        """

        measurement = re.escape(
            measurement_type
        )

        # ---------------------------------------------------------
        # PATTERN 1
        # "temperature of Pump P-201"
        # ---------------------------------------------------------

        match = re.search(
            rf"\b{measurement}\b"
            r"\s+of\s+"
            r"(.+?)"
            r"(?:\s+and\b|"
            r"\s+then\b|"
            r"\s+calculate\b|"
            r"\s+that\b|"
            r"\s+which\b|$)",
            text,
            re.IGNORECASE,
        )

        if match:
            subject = match.group(1).strip()

            subject = self._clean_search_subject(
                subject
            )

            if subject:
                return (
                    f"{subject} "
                    f"{measurement_type}"
                )

        # ---------------------------------------------------------
        # PATTERN 2
        # "Pump P-201 temperature"
        # "Compressor C-101 pressure"
        # ---------------------------------------------------------

        equipment_pattern = (
            r"\b("
            r"[A-Za-z]+"
            r"(?:\s+[A-Za-z]+){0,2}"
            r"\s+"
            r"[A-Z]?"
            r"-?\d+"
            r"(?:[A-Za-z0-9\-]*)"
            r")\s+"
            rf"{measurement}\b"
        )

        match = re.search(
            equipment_pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            subject = match.group(1).strip()

            return (
                f"{subject} "
                f"{measurement_type}"
            )

        # ---------------------------------------------------------
        # PATTERN 3
        # "Find Pump P-201 temperature"
        # ---------------------------------------------------------

        match = re.search(
            r"(?:search|find|look\s+up)"
            r"\s+"
            r"(?:for\s+)?"
            r"(.+?)"
            rf"\s+{measurement}\b",
            text,
            re.IGNORECASE,
        )

        if match:
            subject = match.group(1).strip()

            subject = self._clean_search_subject(
                subject
            )

            if subject:
                return (
                    f"{subject} "
                    f"{measurement_type}"
                )

        return None

    def _clean_search_subject(
        self,
        subject: str,
    ) -> str:
        """Clean unnecessary words from a search subject."""

        cleaned = subject.strip()

        cleaned = re.sub(
            r"^(?:the|a|an)\s+",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s+(?:and|then)$",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        return cleaned.strip()

    # =============================================================
    # SIMPLE CALCULATION
    # =============================================================

    def _detect_calculation(
        self,
        user_input: str,
    ) -> str | None:
        """
        Detect a direct mathematical calculation.

        Example:

            Calculate 1200 + 3500
        """

        text = user_input.strip()

        pattern = (
            r"(?:calculate|compute|solve)"
            r"\s+(.+)"
        )

        calculation_match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if calculation_match is None:
            return None

        expression = (
            calculation_match.group(1)
            .strip()
            .rstrip("?")
        )

        if not expression:
            return None

        if not self._is_safe_calculation_expression(
            expression
        ):
            return None

        return expression

    def _is_safe_calculation_expression(
        self,
        expression: str,
    ) -> bool:
        """
        Validate a basic mathematical expression.

        Actual execution security is enforced by
        CalculatorTool's AST validation.
        """

        return bool(
            re.fullmatch(
                r"[0-9\s+\-*/().%^]+",
                expression,
            )
        )

    # =============================================================
    # FILE DETECTION
    # =============================================================

    def _detect_file_request(
        self,
        user_input: str,
    ) -> str | None:
        """
        Detect a request to read a local document.

        Supports:

            Read /path/report.pdf
            Open /path/report.pdf
            Analyze /path/report.pdf
            Inspect /path/report.pdf
            Read file /path/report.pdf
            Open the file /path/report.pdf

        The important rule is that words such as
        "file" and "the file" are command prefixes,
        not part of the actual path.
        """

        text = user_input.strip()

        if not text:
            return None

        extensions = "|".join(
            self.SUPPORTED_FILE_EXTENSIONS
        )

        # ---------------------------------------------------------
        # READ / OPEN / ANALYZE / INSPECT + FILE PATH
        # ---------------------------------------------------------
        #
        # Examples:
        #
        #   Read rag/report.pdf
        #   Read file rag/report.pdf
        #   Read the file rag/report.pdf
        #   Open rag/report.pdf
        #   Analyze /tmp/report.pdf
        #
        # ---------------------------------------------------------

        file_pattern = (
            r"^(?:read|open|analyze|inspect)"
            r"\s+"
            r"(?:the\s+)?"
            r"(?:file\s+)?"
            rf"(.+\.({extensions}))$"
        )

        file_match = re.search(
            file_pattern,
            text,
            re.IGNORECASE,
        )

        if file_match:
            file_path = (
                file_match.group(1)
                .strip()
                .strip("\"'")
            )

            if file_path:
                return file_path

        return None

    # =============================================================
    # SEARCH DETECTION
    # =============================================================

    def _detect_search_request(
        self,
        user_input: str,
    ) -> str | None:
        """
        Detect a direct knowledge-base search request.

        Supports:

            Search compressor C-101
            Find compressor C-101
            Look up compressor C-101
        """

        pattern = (
            r"(?:search|find|look\s+up)"
            r"\s+"
            r"(?:for\s+)?(.+)"
        )

        search_match = re.search(
            pattern,
            user_input,
            re.IGNORECASE,
        )

        if search_match is None:
            return None

        query = (
            search_match.group(1)
            .strip()
            .rstrip("?")
        )

        if not query:
            return None

        return query

    # =============================================================
    # LLM PLANNER
    # =============================================================

    def _create_llm_plan(
        self,
        user_input: str,
    ) -> list[dict[str, Any]]:
        """
        Use the local LLM for requests that cannot
        be deterministically planned.
        """

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

STRICT RULES:

1. Create only steps that are actually necessary.

2. Prefer the shortest valid plan.

3. Use one step whenever one step is sufficient.

4. Maximum {self.MAX_PLAN_STEPS} steps.

5. Do not create artificial reasoning steps.

6. Never create steps such as:
   - parse the request
   - understand the request
   - think about the problem
   - split the problem
   - return the answer
   unless an actual registered tool is required.

7. If a registered tool can directly perform
   the requested operation, use that tool.

8. For mathematical calculations, use calculator.

9. For local document reading, use file_reader.

10. For knowledge-base searches, use search.

11. If multiple real operations are required,
    create them in the correct execution order.

12. A later step may depend on the verified result
    of an earlier step.

13. Only use tools listed under AVAILABLE TOOLS.

14. Never invent a tool.

15. Never execute a tool.

16. Never provide the final answer.

17. Tool arguments must be valid JSON objects.

18. If a calculation depends on a previous tool result,
    use:

    "$PREVIOUS_RESULT"

    inside the calculator expression.

Example:

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

        response = self.llm_service.chat(
            request
        )

        raw_content = response.content.strip()

        data = self._parse_json(
            raw_content
        )

        return self._validate_plan(
            data
        )

    # =============================================================
    # PLAN VALIDATION
    # =============================================================

    def _validate_plan(
        self,
        data: Any,
    ) -> list[dict[str, Any]]:
        """
        Validate and normalize an LLM-generated plan.
        """

        if not isinstance(data, dict):
            raise ValueError(
                "Planner response must be a JSON object."
            )

        steps = data.get("steps")

        if not isinstance(steps, list):
            raise ValueError(
                "Planner response must contain "
                "a 'steps' list."
            )

        if not steps:
            raise ValueError(
                "Planner returned an empty execution plan."
            )

        if len(steps) > self.MAX_PLAN_STEPS:
            raise ValueError(
                "Planner returned more than "
                f"{self.MAX_PLAN_STEPS} steps."
            )

        available_tools = set(
            self.tool_registry.list_tools()
        )

        cleaned_steps = []

        for index, step in enumerate(
            steps,
            start=1,
        ):
            if not isinstance(step, dict):
                raise ValueError(
                    f"Plan step {index} must be an object."
                )

            action = step.get("action")
            tool = step.get("tool")
            arguments = step.get("arguments")

            # -----------------------------------------------------
            # ACTION
            # -----------------------------------------------------

            if not isinstance(
                action,
                str,
            ):
                raise ValueError(
                    f"Plan step {index} must contain "
                    "a valid 'action'."
                )

            action = action.strip()

            if not action:
                raise ValueError(
                    f"Plan step {index} action "
                    "cannot be empty."
                )

            # -----------------------------------------------------
            # TOOL
            # -----------------------------------------------------

            if tool is not None:
                if not isinstance(
                    tool,
                    str,
                ):
                    raise ValueError(
                        f"Plan step {index} tool "
                        "must be a string or null."
                    )

                tool = tool.strip()

                if not tool:
                    raise ValueError(
                        f"Plan step {index} tool "
                        "cannot be empty."
                    )

                if tool not in available_tools:
                    raise ValueError(
                        f"Planner requested unknown tool: "
                        f"{tool}"
                    )

                # -------------------------------------------------
                # ARGUMENTS
                # -------------------------------------------------

                if not isinstance(
                    arguments,
                    dict,
                ):
                    raise ValueError(
                        f"Plan step {index} tool arguments "
                        "must be an object."
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

    # =============================================================
    # TOOL DESCRIPTIONS
    # =============================================================

    def _get_tool_descriptions(
        self,
    ) -> str:
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

        return "\n".join(
            descriptions
        )

    # =============================================================
    # JSON PARSING
    # =============================================================

    def _parse_json(
        self,
        content: str,
    ) -> dict:
        """
        Parse JSON returned by the local LLM.

        Supports normal JSON and markdown code fences.
        """

        if not content or not content.strip():
            raise ValueError(
                "Planner returned an empty response."
            )

        content = content.strip()

        # ---------------------------------------------------------
        # NORMAL JSON
        # ---------------------------------------------------------

        try:
            return json.loads(
                content
            )
        except json.JSONDecodeError:
            pass

        # ---------------------------------------------------------
        # MARKDOWN CODE FENCE
        # ---------------------------------------------------------

        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            content,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned,
        )

        cleaned = cleaned.strip()

        try:
            return json.loads(
                cleaned
            )
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Planner returned invalid JSON."
            ) from exc
