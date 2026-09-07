"""
Request classifier for the KARYA AI orchestration layer.

The classifier determines which KARYA components are likely required
for a user request.

This version is deterministic so that routing remains predictable,
auditable, and easy to test.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RequestType(str, Enum):
    """High-level categories of requests handled by KARYA."""

    TEXT = "text"
    RAG = "rag"
    CALCULATION = "calculation"
    PYTHON = "python"
    FILE = "file"
    OCR = "ocr"
    VISION = "vision"
    AGENT = "agent"


@dataclass(frozen=True)
class ClassificationResult:
    """Result returned by the request classifier."""

    request_type: RequestType
    confidence: float
    reasons: tuple[str, ...]
    requires_multiple_components: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.request_type, RequestType):
            raise TypeError("request_type must be a RequestType.")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1.")

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple.")

        if not all(isinstance(reason, str) for reason in self.reasons):
            raise TypeError("Every reason must be a string.")

        if not isinstance(self.requires_multiple_components, bool):
            raise TypeError(
                "requires_multiple_components must be a boolean."
            )


class RequestClassifier:
    """
    Deterministic request classifier.

    Priority for specialized requests:

    1. Vision
    2. OCR
    3. Python
    4. File
    5. Calculation
    6. RAG
    7. Agent / multi-component
    8. Text
    """

    VISION_KEYWORDS = (
        "image",
        "photo",
        "picture",
        "drawing",
        "diagram",
        "visual",
        "camera",
        "scan image",
        "engineering drawing",
        "engineering image",
        "p&id",
        "pid",
    )

    OCR_KEYWORDS = (
        "ocr",
        "scanned pdf",
        "scanned document",
        "scan document",
        "scan pdf",
        "handwritten",
        "handwriting",
        "extract text from scan",
        "read scanned",
    )

    PYTHON_KEYWORDS = (
        "run python",
        "execute python",
        "python code",
        "python script",
        "execute this code",
        "run this code",
    )

    FILE_KEYWORDS = (
        "read file",
        "read the file",
        "open file",
        "open the file",
        "read pdf",
        "read the pdf",
        "open pdf",
        "open the pdf",
        "analyze pdf",
        "analyze the pdf",
        "summarize pdf",
        "summarize the pdf",
        "read document",
        "read the document",
        "open document",
        "open the document",
        "analyze document",
        "analyze the document",
        "summarize document",
        "summarize the document",
        "document content",
        "file content",
    )

    RAG_KEYWORDS = (
        "search documents",
        "search the documents",
        "search document",
        "search the document",
        "search maintenance documents",
        "search the maintenance documents",
        "search maintenance reports",
        "search the maintenance reports",
        "search knowledge base",
        "search the knowledge base",
        "knowledge base",
        "according to the documents",
        "according to the report",
        "according to our documents",
        "according to maintenance records",
        "find in documents",
        "find in the documents",
        "find in maintenance documents",
        "find in the maintenance documents",
        "look up in documents",
        "look up in the documents",
        "retrieve information",
        "retrieve from documents",
        "retrieve from the documents",
        "maintenance report",
        "maintenance reports",
        "maintenance document",
        "maintenance documents",
        "equipment history",
        "historical records",
        "company documents",
        "company knowledge",
        "internal documents",
        "internal knowledge",
    )

    CALCULATION_KEYWORDS = (
        "calculate",
        "calculation",
        "compute",
        "equation",
        "solve",
        "multiply",
        "divide",
        "subtract",
        "add",
        "percentage",
        "percent",
        "average",
        "mean",
        "sum",
        "difference",
        "ratio",
        "convert",
    )

    AGENT_KEYWORDS = (
        "and then",
        "after that",
        "then calculate",
        "then analyze",
        "then prepare",
        "then generate",
        "and calculate",
        "and analyze",
        "and prepare",
        "and generate",
        "create a report",
        "prepare a report",
        "prepare an approval",
        "prepare approval",
        "generate an approval",
        "generate approval",
        "perform the entire",
        "complete the workflow",
        "end to end",
        "end-to-end",
        "workflow",
        "multiple steps",
        "step by step",
    )

    def classify(self, user_input: str) -> ClassificationResult:
        """
        Classify a user request.
        """

        if not isinstance(user_input, str):
            raise TypeError("user_input must be a string.")

        text = user_input.strip().lower()

        if not text:
            raise ValueError("user_input cannot be empty.")

        matches = self._get_matches(text)

        component_types = [
            request_type
            for request_type, keywords in matches.items()
            if keywords
        ]

        if len(component_types) > 1:
            return self._classify_multi_component(
                matches,
                component_types,
            )

        if component_types:
            request_type = component_types[0]
            keywords = matches[request_type]

            return ClassificationResult(
                request_type=request_type,
                confidence=self._confidence_for(
                    request_type,
                    len(keywords),
                ),
                reasons=(
                    f"Matched keywords: {', '.join(keywords)}",
                ),
                requires_multiple_components=False,
            )

        return ClassificationResult(
            request_type=RequestType.TEXT,
            confidence=0.85,
            reasons=(
                "No specialized component keywords detected.",
                "Defaulting to normal local LLM reasoning.",
            ),
            requires_multiple_components=False,
        )

    def classify_components(
        self,
        user_input: str,
    ) -> list[RequestType]:
        """Return all specialized components detected."""

        if not isinstance(user_input, str):
            raise TypeError("user_input must be a string.")

        text = user_input.strip().lower()

        if not text:
            raise ValueError("user_input cannot be empty.")

        matches = self._get_matches(text)

        return [
            request_type
            for request_type, keywords in matches.items()
            if keywords
        ]

    def _get_matches(
        self,
        text: str,
    ) -> dict[RequestType, list[str]]:
        """Return all keyword matches."""

        return {
            RequestType.VISION: self._find_matches(
                text,
                self.VISION_KEYWORDS,
            ),
            RequestType.OCR: self._find_matches(
                text,
                self.OCR_KEYWORDS,
            ),
            RequestType.PYTHON: self._find_matches(
                text,
                self.PYTHON_KEYWORDS,
            ),
            RequestType.FILE: self._find_matches(
                text,
                self.FILE_KEYWORDS,
            ),
            RequestType.CALCULATION: self._find_matches(
                text,
                self.CALCULATION_KEYWORDS,
            ),
            RequestType.RAG: self._find_matches(
                text,
                self.RAG_KEYWORDS,
            ),
            RequestType.AGENT: self._find_matches(
                text,
                self.AGENT_KEYWORDS,
            ),
        }

    def _classify_multi_component(
        self,
        matches: dict[RequestType, list[str]],
        component_types: list[RequestType],
    ) -> ClassificationResult:
        """Classify requests requiring multiple components."""

        if RequestType.AGENT in component_types:
            return ClassificationResult(
                request_type=RequestType.AGENT,
                confidence=0.95,
                reasons=tuple(self._build_multi_reasons(matches)),
                requires_multiple_components=True,
            )

        if (
            RequestType.OCR in component_types
            and RequestType.VISION in component_types
        ):
            return ClassificationResult(
                request_type=RequestType.VISION,
                confidence=0.92,
                reasons=tuple(self._build_multi_reasons(matches)),
                requires_multiple_components=True,
            )

        if (
            RequestType.RAG in component_types
            and RequestType.CALCULATION in component_types
        ):
            return ClassificationResult(
                request_type=RequestType.AGENT,
                confidence=0.94,
                reasons=tuple(self._build_multi_reasons(matches)),
                requires_multiple_components=True,
            )

        if (
            RequestType.FILE in component_types
            and RequestType.CALCULATION in component_types
        ):
            return ClassificationResult(
                request_type=RequestType.AGENT,
                confidence=0.93,
                reasons=tuple(self._build_multi_reasons(matches)),
                requires_multiple_components=True,
            )

        if (
            RequestType.PYTHON in component_types
            and len(component_types) > 1
        ):
            return ClassificationResult(
                request_type=RequestType.AGENT,
                confidence=0.93,
                reasons=tuple(self._build_multi_reasons(matches)),
                requires_multiple_components=True,
            )

        priority = [
            RequestType.VISION,
            RequestType.OCR,
            RequestType.PYTHON,
            RequestType.RAG,
            RequestType.FILE,
            RequestType.CALCULATION,
        ]

        selected_type = next(
            request_type
            for request_type in priority
            if request_type in component_types
        )

        return ClassificationResult(
            request_type=selected_type,
            confidence=0.88,
            reasons=tuple(self._build_multi_reasons(matches)),
            requires_multiple_components=True,
        )

    @staticmethod
    def _find_matches(
        text: str,
        keywords: tuple[str, ...],
    ) -> list[str]:
        """Find keyword matches in normalized text."""

        return [
            keyword
            for keyword in keywords
            if keyword in text
        ]

    @staticmethod
    def _confidence_for(
        request_type: RequestType,
        match_count: int,
    ) -> float:
        """Calculate deterministic classification confidence."""

        base_confidence = {
            RequestType.VISION: 0.94,
            RequestType.OCR: 0.94,
            RequestType.PYTHON: 0.95,
            RequestType.FILE: 0.91,
            RequestType.CALCULATION: 0.90,
            RequestType.RAG: 0.91,
            RequestType.AGENT: 0.93,
        }.get(request_type, 0.85)

        bonus = min(
            max(match_count - 1, 0) * 0.02,
            0.05,
        )

        return min(
            base_confidence + bonus,
            0.99,
        )

    @staticmethod
    def _build_multi_reasons(
        matches: dict[RequestType, list[str]],
    ) -> list[str]:
        """Build human-readable classification reasons."""

        reasons: list[str] = []

        for request_type, keywords in matches.items():
            if keywords:
                reasons.append(
                    f"{request_type.value}: "
                    f"{', '.join(keywords)}"
                )

        return reasons