
from __future__ import annotations

import json
import re
from typing import Any

from llm.schemas import LLMMessage, LLMRequest
from llm.service import LLMService

from agents.state import AgentState
from tools.registry import ToolRegistry, create_default_registry


class AgentPlanner:
    """
    KARYA Agent Planner.

    Deterministic-first planning architecture.

    The planner NEVER executes tools.

    Priority:

    1. Explicit industrial document workflow
    2. Search + calculation workflow
    3. Simple calculation
    4. File reading
    5. Search
    6. Local LLM fallback

    The industrial workflow is intentionally deterministic so the
    local LLM cannot invent files, datasets, thresholds, Python code,
    or knowledge-base paths.

    Important grounding rule:

    The planner must distinguish between:

        FACT
        - explicitly present in the source document

        INFERENCE
        - something the model believes based on a fact

    KARYA must NOT present an inference as a verified industrial fact.

    Example:

        Document:
            Vibration: 8.5 mm/s

        Allowed:
            "The measured vibration is 8.5 mm/s."

        Not allowed unless explicitly stated:
            "The vibration is high."
            "The vibration is excessive."
            "The vibration is unsafe."
            "The vibration is above the safe limit."

    If the source does not contain a threshold, the planner must
    force the model to state that numeric comparison is unavailable.
    """

    def __init__(
        self,
        llm_service: LLMService | None = None,
        tool_registry: ToolRegistry | None = None,
    ) -> None:
        self.llm_service = llm_service or LLMService()
        self.tool_registry = (
            tool_registry or create_default_registry()
        )
    def plan_task(
        self,
        state: AgentState,
    ) -> list[dict[str, Any]]:
        """
        Create and attach a plan to AgentState.

        The planner only plans.

        It does not execute tools.
        """

        if not isinstance(
            state,
            AgentState,
        ):
            raise TypeError(
                "state must be an AgentState instance."
            )

        user_input = state.user_input.strip()

        if not user_input:
            state.error = (
                "Cannot create a plan for empty user input."
            )
            state.plan = []
            return []


        plan = self._detect_industrial_document_workflow(
            user_input
        )

        if not plan:
            plan = self._detect_multi_step_request(
                user_input
            )

        if not plan:
            plan = self._detect_calculation(
                user_input
            )

        if not plan:
            plan = self._detect_file_request(
                user_input
            )

        if not plan:
            plan = self._detect_search_request(
                user_input
            )

        if not plan:
            plan = self._create_llm_plan(
                user_input
            )

        errors = self._validate_plan(
            plan
        )

        if errors:
            state.error = (
                "Planner returned invalid plan: "
                + "; ".join(errors)
            )
            state.plan = []
            return []

        state.plan = plan
        state.current_step = 0
        state.error = None

        return plan


    def create_plan(
        self,
        state: AgentState,
    ) -> list[dict[str, Any]]:
        return self.plan_task(
            state
        )



    def _detect_industrial_document_workflow(
        self,
        user_input: str,
    ) -> list[dict[str, Any]] | None:
        """
        Detect requests such as:

        Read the maintenance report, calculate the vibration risk,
        compare it with the safe limit, and prepare a recommendation.

        This workflow intentionally uses only:

        - the explicitly supplied file
        - verified document content
        - local LLM reasoning
        - no invented CSV files
        - no invented knowledge-base paths
        - no invented thresholds
        """

        text = user_input.lower()

        has_document = any(
            keyword in text
            for keyword in (
                ".pdf",
                ".docx",
                ".xlsx",
                ".pptx",
                "maintenance report",
                "report",
                "document",
            )
        )

        has_measurement = any(
            keyword in text
            for keyword in (
                "vibration",
                "temperature",
                "pressure",
                "flow",
                "speed",
                "current",
                "voltage",
                "risk",
                "measurement",
            )
        )

        has_calculation = any(
            keyword in text
            for keyword in (
                "calculate",
                "calculation",
                "compute",
                "evaluate",
                "ratio",
                "risk",
            )
        )

        has_comparison = any(
            keyword in text
            for keyword in (
                "compare",
                "comparison",
                "safe limit",
                "threshold",
                "limit",
                "maximum",
                "minimum",
            )
        )

        has_recommendation = (
            self._has_recommendation_intent(
                text
            )
        )

        if not (
            has_document
            and has_measurement
            and has_calculation
            and (
                has_comparison
                or has_recommendation
            )
        ):
            return None

        file_path = self._extract_file_path(
            user_input
        )

        if not file_path:
            return None

        measurement_type = (
            self._detect_measurement_type(
                text
            )
        )

        plan: list[dict[str, Any]] = []

        # --------------------------------------------------------------
        # STEP 1
        # --------------------------------------------------------------

        plan.append(
            {
                "step_id": "step_1",
                "action": "use_tool",
                "description": (
                    "Read the supplied industrial document."
                ),
                "tool": "file_reader",
                "arguments": {
                    "file_path": file_path,
                },
                "depends_on": [],
                "required": True,
            }
        )


        plan.append(
            {
                "step_id": "step_2",
                "action": "llm",
                "description": (
                    f"Extract the verified "
                    f"{measurement_type} measurement "
                    "from the document."
                ),
                "tool": None,
                "arguments": {
                    "prompt": (
                        "You are a strict industrial document "
                        "extraction system.\n\n"

                        f"Extract the {measurement_type} "
                        "measurement from the document below.\n\n"

                        "GROUNDING RULES:\n"
                        "- Use ONLY the supplied document.\n"
                        "- Never invent a value.\n"
                        "- Never estimate a value.\n"
                        "- Never convert a value unless necessary "
                        "to preserve the exact documented value.\n"
                        "- Do not describe the measurement as high, "
                        "low, excessive, unsafe, abnormal, or safe "
                        "unless those words are explicitly stated "
                        "in the document.\n\n"

                        "OUTPUT RULE:\n"
                        "Return ONLY the verified measurement "
                        "and unit.\n"
                        "If the document does not contain the "
                        "measurement, return "
                        "MEASUREMENT_NOT_FOUND.\n\n"

                        "DOCUMENT:\n"
                        "$step_1"
                    ),
                },
                "depends_on": [
                    "step_1"
                ],
                "required": True,
            }
        )


        plan.append(
            {
                "step_id": "step_3",
                "action": "llm",
                "description": (
                    "Extract the explicitly documented safe limit. "
                    "Never invent or assume a threshold."
                ),
                "tool": None,
                "arguments": {
                    "prompt": (
                        "You are a strict industrial document "
                        "extraction system.\n\n"

                        f"Find the explicitly documented safe "
                        f"limit, threshold, maximum, minimum, "
                        f"alarm limit, trip limit, or acceptable "
                        f"range for {measurement_type} in the "
                        "document below.\n\n"

                        "GROUNDING RULES:\n"
                        "- Use ONLY the supplied document.\n"
                        "- Do not use outside knowledge.\n"
                        "- Do not use general engineering standards.\n"
                        "- Do not use remembered industry limits.\n"
                        "- Do not infer a threshold from the equipment "
                        "status.\n"
                        "- Do not infer a threshold from words such "
                        "as Critical, Warning, Normal, High, or Low.\n"
                        "- A measurement is NOT a safe limit.\n"
                        "- A status is NOT a safe limit.\n\n"

                        "OUTPUT RULE:\n"
                        "Return ONLY the explicitly documented "
                        "limit and unit.\n"
                        "If no explicit limit is documented, return "
                        "LIMIT_NOT_FOUND.\n\n"

                        "DOCUMENT:\n"
                        "$step_1"
                    ),
                },
                "depends_on": [
                    "step_1"
                ],
                "required": True,
            }
        )


        plan.append(
            {
                "step_id": "step_4",
                "action": "llm",
                "description": (
                    "Compare the verified measurement with "
                    "the verified safe limit."
                ),
                "tool": None,
                "arguments": {
                    "prompt": (
                        "Compare ONLY the following verified "
                        "measurement and explicitly documented "
                        "safe limit.\n\n"

                        "MEASUREMENT:\n"
                        "$step_2\n\n"

                        "SAFE LIMIT:\n"
                        "$step_3\n\n"

                        "STRICT RULES:\n"
                        "- Do not invent missing values.\n"
                        "- Do not use outside knowledge.\n"
                        "- Do not use general engineering standards.\n"
                        "- Do not infer a threshold.\n"
                        "- Do not infer whether a value is high "
                        "or low without a documented limit.\n"
                        "- If SAFE LIMIT is LIMIT_NOT_FOUND, return "
                        "COMPARISON_NOT_POSSIBLE.\n"
                        "- If MEASUREMENT is MEASUREMENT_NOT_FOUND, "
                        "return COMPARISON_NOT_POSSIBLE.\n"
                        "- If both values exist, state whether the "
                        "measurement is within, equal to, or above "
                        "the explicitly documented limit.\n\n"

                        "OUTPUT RULE:\n"
                        "Return a concise factual comparison only."
                    ),
                },
                "depends_on": [
                    "step_2",
                    "step_3",
                ],
                "required": True,
            }
        )

        # --------------------------------------------------------------
        # STEP 5
        # --------------------------------------------------------------
        # Final recommendation.
        #
        # This is the critical safety/grounding fix.
        #
        # The LLM is explicitly forbidden from converting a raw
        # measurement into a qualitative judgment.
        #
        # Example:
        #
        #   "Vibration: 8.5 mm/s"
        #
        # MUST NOT become:
        #
        #   "8.5 mm/s indicates high vibration."
        #
        # unless the source explicitly says that.
        # --------------------------------------------------------------

        if has_recommendation:
            plan.append(
                {
                    "step_id": "step_5",
                    "action": "llm",
                    "description": (
                        "Prepare a strictly grounded industrial "
                        "maintenance recommendation."
                    ),
                    "tool": None,
                    "arguments": {
                        "prompt": (
                            "You are KARYA, a sovereign industrial "
                            "AI assistant.\n\n"

                            "Prepare a concise industrial maintenance "
                            "recommendation using ONLY the verified "
                            "information below.\n\n"

                            "DOCUMENT:\n"
                            "$step_1\n\n"

                            "VERIFIED MEASUREMENT:\n"
                            "$step_2\n\n"

                            "VERIFIED SAFE LIMIT:\n"
                            "$step_3\n\n"

                            "VERIFIED COMPARISON:\n"
                            "$step_4\n\n"

                            "==================================================\n"
                            "STRICT GROUNDING RULES\n"
                            "==================================================\n\n"

                            "1. SOURCE-ONLY REASONING\n"
                            "- Use ONLY information explicitly present "
                            "in the supplied document and verified "
                            "results.\n"
                            "- Do not use outside knowledge.\n"
                            "- Do not use general engineering standards.\n"
                            "- Do not use remembered industry limits.\n"
                            "- Do not invent missing facts.\n\n"

                            "2. MEASUREMENTS\n"
                            "- Preserve the exact documented measurement.\n"
                            "- Never call a measurement high, low, excessive, "
                            "unsafe, abnormal, dangerous, or safe unless "
                            "the document explicitly uses that description "
                            "or an explicitly documented threshold supports "
                            "the statement.\n\n"

                            "3. THRESHOLDS\n"
                            "- Never invent a safe limit.\n"
                            "- Never assume a standard threshold.\n"
                            "- Never infer a threshold from equipment status.\n"
                            "- If SAFE LIMIT is LIMIT_NOT_FOUND, explicitly "
                            "state that the document does not provide a "
                            "safe limit and numeric comparison is unavailable.\n\n"

                            "4. STATUS\n"
                            "- If the document says the equipment status is "
                            "Critical, you may report that the equipment "
                            "status is Critical.\n"
                            "- Do NOT reinterpret Critical as proof that a "
                            "specific measurement is excessive unless the "
                            "document explicitly makes that connection.\n\n"

                            "5. RECOMMENDATION\n"
                            "- Base the recommendation on explicit "
                            "maintenance instructions in the document.\n"
                            "- If the document explicitly says immediate "
                            "maintenance inspection is required, report "
                            "that recommendation.\n"
                            "- Do not create additional repair instructions "
                            "unless they are explicitly supported by the "
                            "document.\n\n"

                            "6. COMPARISON\n"
                            "- If COMPARISON_NOT_POSSIBLE is returned, do "
                            "not claim the measurement is above or below "
                            "a limit.\n"
                            "- If a documented limit exists, use only that "
                            "limit for comparison.\n\n"

                            "==================================================\n"
                            "OUTPUT FORMAT\n"
                            "==================================================\n\n"

                            "Return a concise answer with these sections "
                            "when applicable:\n\n"

                            "Finding:\n"
                            "State the verified equipment status and "
                            "documented measurement.\n\n"

                            "Comparison:\n"
                            "State the documented comparison, or state "
                            "that numeric comparison is unavailable "
                            "because no safe limit is documented.\n\n"

                            "Recommendation:\n"
                            "State only the maintenance action explicitly "
                            "supported by the document.\n\n"

                            "IMPORTANT:\n"
                            "If the document says:\n"
                            "\"Vibration: 8.5 mm/s\"\n"
                            "and does NOT say that 8.5 mm/s is high, "
                            "excessive, unsafe, or above a limit, you "
                            "MUST NOT use those descriptions.\n\n"

                            "The exact value 8.5 mm/s is a measurement, "
                            "not a qualitative judgment."
                        ),
                    },
                    "depends_on": [
                        "step_1",
                        "step_2",
                        "step_3",
                        "step_4",
                    ],
                    "required": True,
                }
            )

        return plan

    # ------------------------------------------------------------------
    # SEARCH + CALCULATION
    # ------------------------------------------------------------------

    def _detect_multi_step_request(
        self,
        user_input: str,
    ) -> list[dict[str, Any]] | None:

        text = user_input.lower()

        has_search = any(
            keyword in text
            for keyword in (
                "search",
                "find",
                "look up",
                "retrieve",
                "maintenance documents",
                "knowledge base",
            )
        )

        has_calculation = any(
            keyword in text
            for keyword in (
                "calculate",
                "compute",
                "evaluate",
            )
        )

        if not (
            has_search
            and has_calculation
        ):
            return None

        subject = self._extract_search_subject(
            user_input
        )

        return [
            {
                "step_id": "step_1",
                "action": "use_tool",
                "description": (
                    "Search the local knowledge base."
                ),
                "tool": "search",
                "arguments": {
                    "directory": ".",
                    "query": subject,
                },
                "depends_on": [],
                "required": True,
            },
            {
                "step_id": "step_2",
                "action": "use_tool",
                "description": (
                    "Calculate the requested difference."
                ),
                "tool": "calculator",
                "arguments": {
                    "expression": "0",
                },
                "depends_on": [
                    "step_1"
                ],
                "required": True,
            },
        ]

    # ------------------------------------------------------------------
    # SIMPLE CALCULATION
    # ------------------------------------------------------------------

    def _detect_calculation(
        self,
        user_input: str,
    ) -> list[dict[str, Any]] | None:

        expression = (
            self._extract_calculation_expression(
                user_input
            )
        )

        if not expression:
            return None

        return [
            {
                "step_id": "step_1",
                "action": "use_tool",
                "description": (
                    "Calculate the requested expression."
                ),
                "tool": "calculator",
                "arguments": {
                    "expression": expression,
                },
                "depends_on": [],
                "required": True,
            }
        ]

    def _extract_calculation_expression(
        self,
        user_input: str,
    ) -> str | None:

        text = user_input.strip()

        patterns = [
            r"(?:calculate|compute|evaluate|solve)\s+"
            r"(?:the\s+)?(.+?)(?:[?.!]|$)",

            r"what\s+is\s+(.+?)(?:[?.!]|$)",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if not match:
                continue

            expression = match.group(
                1
            ).strip()

            expression = re.sub(
                r"\b(?:please|for me|and explain|explain)\b.*$",
                "",
                expression,
                flags=re.IGNORECASE,
            ).strip()

            if expression:
                return expression

        return None

    # ------------------------------------------------------------------
    # FILE REQUEST
    # ------------------------------------------------------------------

    def _detect_file_request(
        self,
        user_input: str,
    ) -> list[dict[str, Any]] | None:

        file_path = self._extract_file_path(
            user_input
        )

        if not file_path:
            return None

        return [
            {
                "step_id": "step_1",
                "action": "use_tool",
                "description": (
                    "Read the requested local file."
                ),
                "tool": "file_reader",
                "arguments": {
                    "file_path": file_path,
                },
                "depends_on": [],
                "required": True,
            }
        ]

    def _extract_file_path(
        self,
        user_input: str,
    ) -> str | None:
        """
        Extract an explicit local document path.

        Supported extensions:

            pdf
            docx
            xlsx
            pptx
            txt
            csv
        """

        explicit_path = re.search(
            r"(?P<path>"
            r"(?:\.{0,2}/|/)?"
            r"[\w./\\-]+"
            r"\."
            r"(?:pdf|docx|xlsx|pptx|txt|csv)"
            r")",
            user_input,
            re.IGNORECASE,
        )

        if explicit_path:
            return explicit_path.group(
                "path"
            )

        return None

    # ------------------------------------------------------------------
    # SEARCH REQUEST
    # ------------------------------------------------------------------

    def _detect_search_request(
        self,
        user_input: str,
    ) -> list[dict[str, Any]] | None:

        text = user_input.lower()

        if not any(
            keyword in text
            for keyword in (
                "search",
                "find",
                "retrieve",
                "look up",
            )
        ):
            return None

        subject = self._extract_search_subject(
            user_input
        )

        return [
            {
                "step_id": "step_1",
                "action": "use_tool",
                "description": (
                    "Search the local knowledge base."
                ),
                "tool": "search",
                "arguments": {
                    "directory": ".",
                    "directory": ".",
                    "query": subject,
                },
                "depends_on": [],
                "required": True,
            }
        ]

    def _extract_search_subject(
        self,
        user_input: str,
    ) -> str:

        text = user_input.strip()

        patterns = [
            r"(?:search|find|retrieve|look up)\s+"
            r"(?:for\s+)?(.+?)(?:[?.!]|$)",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:
                subject = match.group(
                    1
                ).strip()

                subject = re.sub(
                    r"\b(?:and\s+calculate.*)$",
                    "",
                    subject,
                    flags=re.IGNORECASE,
                ).strip()

                if subject:
                    return subject

        return text

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _detect_measurement_type(
        self,
        text: str,
    ) -> str:

        measurement_keywords = (
            ("vibration", "vibration"),
            ("temperature", "temperature"),
            ("pressure", "pressure"),
            ("flow", "flow"),
            ("speed", "speed"),
            ("current", "current"),
            ("voltage", "voltage"),
        )

        for keyword, value in measurement_keywords:
            if keyword in text:
                return value

        return "measurement"

    def _has_recommendation_intent(
        self,
        text: str,
    ) -> bool:

        return any(
            keyword in text
            for keyword in (
                "recommendation",
                "recommend",
                "what should",
                "what do you recommend",
                "action",
                "next step",
                "maintenance action",
            )
        )

    # ------------------------------------------------------------------
    # LOCAL LLM FALLBACK
    # ------------------------------------------------------------------

    def _create_llm_plan(
        self,
        user_input: str,
    ) -> list[dict[str, Any]]:
        """
        Ask the local LLM for a plan only when deterministic
        planning cannot identify the task.

        The LLM must return JSON only.
        """

        prompt = f"""
You are the KARYA Agent Planner.

Create a safe execution plan for this user request:

{user_input}

Available tools:

- calculator
- file_reader
- search
- rag
- python

Return ONLY valid JSON.

Required format:

{{
  "steps": [
    {{
      "step_id": "step_1",
      "action": "use_tool",
      "description": "short description",
      "tool": "calculator",
      "arguments": {{}},
      "depends_on": [],
      "required": true
    }}
  ]
}}

Rules:

- Never invent a file path.
- Never invent a dataset.
- Never invent a knowledge-base path.
- Never create fake data.
- Use python only when genuinely necessary.
- Use calculator for arithmetic.
- Use file_reader for explicit local files.
- Use rag for knowledge-base retrieval.
- Keep the plan minimal.
"""

        try:
            request = LLMRequest(
                messages=[
                    LLMMessage(
                        role="system",
                        content=(
                            "Return valid JSON only."
                        ),
                    ),
                    LLMMessage(
                        role="user",
                        content=prompt,
                    ),
                ],
                temperature=0.0,
                max_tokens=1200,
            )

            response = self.llm_service.chat(
                request
            )

            raw = getattr(
                response,
                "content",
                response,
            )

            if not isinstance(
                raw,
                str,
            ):
                raw = str(raw)

            return self._parse_llm_plan(
                raw
            )

        except Exception:
            return []

    def _parse_llm_plan(
        self,
        raw: str,
    ) -> list[dict[str, Any]]:

        text = raw.strip()

        # Remove markdown fences if the model added them.

        text = re.sub(
            r"^```json\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"^```\s*",
            "",
            text,
        )

        text = re.sub(
            r"\s*```$",
            "",
            text,
        )

        try:
            payload = json.loads(
                text
            )

        except json.JSONDecodeError:
            return []

        if not isinstance(
            payload,
            dict,
        ):
            return []

        steps = payload.get(
            "steps"
        )

        if not isinstance(
            steps,
            list,
        ):
            return []

        normalized: list[
            dict[str, Any]
        ] = []

        for index, step in enumerate(
            steps,
            start=1,
        ):
            if not isinstance(
                step,
                dict,
            ):
                continue

            normalized.append(
                {
                    "step_id": str(
                        step.get(
                            "step_id"
                        )
                        or f"step_{index}"
                    ),
                    "action": str(
                        step.get(
                            "action"
                        )
                        or "use_tool"
                    ),
                    "description": str(
                        step.get(
                            "description"
                        )
                        or ""
                    ),
                    "tool": step.get(
                        "tool"
                    ),
                    "arguments": (
                        step.get(
                            "arguments"
                        )
                        if isinstance(
                            step.get(
                                "arguments"
                            ),
                            dict,
                        )
                        else {}
                    ),
                    "depends_on": (
                        step.get(
                            "depends_on"
                        )
                        if isinstance(
                            step.get(
                                "depends_on"
                            ),
                            list,
                        )
                        else []
                    ),
                    "required": bool(
                        step.get(
                            "required",
                            True,
                        )
                    ),
                }
            )

        return normalized

    # ------------------------------------------------------------------
    # PLAN VALIDATION
    # ------------------------------------------------------------------

    def _validate_plan(
        self,
        plan: list[dict[str, Any]],
    ) -> list[str]:

        errors: list[str] = []

        if not isinstance(
            plan,
            list,
        ):
            return [
                "Plan must be a list."
            ]

        if not plan:
            return [
                "Plan is empty."
            ]

        step_ids: set[str] = set()

        # First pass:
        # Validate basic step structure and collect IDs.

        for step in plan:

            if not isinstance(
                step,
                dict,
            ):
                errors.append(
                    "Each plan step must be a dictionary."
                )
                continue

            step_id = step.get(
                "step_id"
            )

            if not step_id:
                errors.append(
                    "Plan step is missing step_id."
                )
                continue

            step_id = str(
                step_id
            )

            if step_id in step_ids:
                errors.append(
                    f"Duplicate step_id: {step_id}"
                )

            step_ids.add(
                step_id
            )

            if not step.get(
                "action"
            ):
                errors.append(
                    f"{step_id}: missing action."
                )

            tool = step.get(
                "tool"
            )

            if tool:
                if not self.tool_registry.has(
                    str(tool)
                ):
                    errors.append(
                        f"{step_id}: unknown tool '{tool}'."
                    )

            arguments = step.get(
                "arguments"
            )

            if (
                arguments is not None
                and not isinstance(
                    arguments,
                    dict,
                )
            ):
                errors.append(
                    f"{step_id}: arguments must be a dictionary."
                )

            dependencies = step.get(
                "depends_on",
                [],
            )

            if not isinstance(
                dependencies,
                list,
            ):
                errors.append(
                    f"{step_id}: depends_on must be a list."
                )
                continue

            for dependency in dependencies:

                if dependency == step_id:
                    errors.append(
                        f"{step_id}: cannot depend on itself."
                    )

        # Second pass:
        # Validate dependency references.

        for step in plan:

            if not isinstance(
                step,
                dict,
            ):
                continue

            step_id = str(
                step.get(
                    "step_id"
                )
            )

            for dependency in step.get(
                "depends_on",
                [],
            ):

                if dependency not in step_ids:
                    errors.append(
                        f"{step_id}: unknown dependency "
                        f"'{dependency}'."
                    )

        # Third pass:
        # Detect dependency cycles.

        graph = {
            str(
                step["step_id"]
            ): [
                str(dep)
                for dep in step.get(
                    "depends_on",
                    [],
                )
            ]
            for step in plan
            if (
                isinstance(
                    step,
                    dict,
                )
                and step.get(
                    "step_id"
                )
            )
        }

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(
            node: str,
        ) -> None:

            if node in visiting:
                errors.append(
                    f"Dependency cycle detected at '{node}'."
                )
                return

            if node in visited:
                return

            visiting.add(
                node
            )

            for dependency in graph.get(
                node,
                [],
            ):
                if dependency in graph:
                    visit(
                        dependency
                    )

            visiting.remove(
                node
            )

            visited.add(
                node
            )

        for node in graph:
            visit(
                node
            )

        return list(
            dict.fromkeys(
                errors
            )
        )
