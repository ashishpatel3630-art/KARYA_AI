from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from rag.service import RAGService
from tools.permissions import PermissionLevel, PermissionManager
from tools.schemas import ToolDefinition, ToolResult


@dataclass
class RAGTool:
    """
    KARYA RAG tool.

    The RAGService is initialized lazily.

    This is important because creating the ToolRegistry should
    not immediately load the embedding model. The embedding
    model is only initialized when the RAG tool is actually used.

    Flow:

        Agent
          ↓
        ToolRegistry
          ↓
        RAGTool
          ↓
        RAGService
          ↓
        EmbeddingModel
          ↓
        PostgreSQL + pgvector
          ↓
        Local LLM
          ↓
        Grounded answer + citations
    """

    rag_service: RAGService | None = None
    permissions: PermissionManager | None = None

    name: str = "rag"

    description: str = (
        "Search KARYA's local industrial knowledge base and "
        "answer questions using grounded document evidence "
        "with source citations."
    )

    _initialized: bool = field(
        default=False,
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        """
        Configure lightweight dependencies only.

        IMPORTANT:
        RAGService is NOT created here.

        This prevents the embedding model from loading when
        ToolRegistry is merely created.
        """

        if self.permissions is None:
            self.permissions = PermissionManager()

        if self.rag_service is not None:
            self._initialized = True

    def _get_rag_service(self) -> RAGService:
        """
        Lazily create and return the RAGService.

        The service and embedding model are initialized only
        when the RAG tool is actually executed.
        """

        if self.rag_service is None:
            self.rag_service = RAGService()

        self._initialized = True

        return self.rag_service

    def definition(self) -> ToolDefinition:
        """Return the tool definition."""

        return ToolDefinition(
            name=self.name,
            description=self.description,
            input_schema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": (
                            "Question to answer using the local "
                            "KARYA knowledge base."
                        ),
                    },
                    "top_k": {
                        "type": "integer",
                        "description": (
                            "Maximum number of document chunks "
                            "to retrieve."
                        ),
                        "minimum": 1,
                        "maximum": 10,
                        "default": 3,
                    },
                    "similarity_threshold": {
                        "type": "number",
                        "description": (
                            "Minimum semantic similarity required "
                            "for retrieved document chunks."
                        ),
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.60,
                    },
                },
                "required": ["question"],
                "additionalProperties": False,
            },
        )

    def execute(
        self,
        question: str,
        top_k: int = 3,
        similarity_threshold: float = 0.60,
    ) -> ToolResult:
        """Execute a RAG query."""

        if not isinstance(question, str):
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Question must be a string.",
            )

        question = question.strip()

        if not question:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Question cannot be empty.",
            )

        if not isinstance(top_k, int) or isinstance(top_k, bool):
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="top_k must be an integer.",
            )

        if top_k <= 0:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="top_k must be greater than zero.",
            )

        if top_k > 10:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="top_k cannot be greater than 10.",
            )

        if not isinstance(
            similarity_threshold,
            (int, float),
        ) or isinstance(similarity_threshold, bool):
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="similarity_threshold must be a number.",
            )

        similarity_threshold = float(similarity_threshold)

        if not 0.0 <= similarity_threshold <= 1.0:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error=(
                    "similarity_threshold must be between "
                    "0.0 and 1.0."
                ),
            )

        if self.permissions is None:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Permission manager is not configured.",
            )

        permission_result = self.permissions.check(
            PermissionLevel.READ
        )

        if not permission_result.allowed:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error=permission_result.reason,
            )

        try:
            rag_service = self._get_rag_service()

            response = rag_service.answer(
                question=question,
                top_k=top_k,
                similarity_threshold=similarity_threshold,
            )

        except Exception as exc:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error=f"RAG execution failed: {exc}",
            )

        output = self._format_response(response)

        return ToolResult(
            tool_name=self.name,
            success=True,
            output=output,
            error=None,
        )

    def execute_with_input(
        self,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """
        Execute the RAG tool using registry-style arguments.
        """

        if not isinstance(arguments, dict):
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Tool arguments must be a dictionary.",
            )

        question = arguments.get("question")

        if question is None:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Missing required argument: question.",
            )

        top_k = arguments.get(
            "top_k",
            3,
        )

        similarity_threshold = arguments.get(
            "similarity_threshold",
            0.60,
        )

        return self.execute(
            question=question,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
        )

    @property
    def is_initialized(self) -> bool:
        """
        Return whether RAGService has been initialized.
        """

        return self._initialized

    @staticmethod
    def _format_response(response: Any) -> str:
        """
        Convert RAGResponse into agent-readable text.

        The answer remains the primary result.

        Citation metadata is also included explicitly so the
        agent can preserve evidence during later reasoning.
        """

        if response is None:
            return "RAG returned no response."

        answer = str(
            getattr(
                response,
                "answer",
                "",
            )
        ).strip()

        if not answer:
            answer = "RAG returned an empty answer."

        citations = getattr(
            response,
            "citations",
            [],
        )

        if not citations:
            return answer

        citation_lines: list[str] = []

        for citation in citations:
            file_name = getattr(
                citation,
                "file_name",
                "Unknown",
            )

            page_number = getattr(
                citation,
                "page_number",
                None,
            )

            chunk_id = getattr(
                citation,
                "chunk_id",
                "Unknown",
            )

            similarity = getattr(
                citation,
                "similarity",
                None,
            )

            page_text = (
                str(page_number)
                if page_number is not None
                else "Unknown"
            )

            if similarity is None:
                citation_lines.append(
                    f"[Source: {file_name}, "
                    f"Page {page_text}, "
                    f"Chunk {chunk_id}]"
                )
            else:
                citation_lines.append(
                    f"[Source: {file_name}, "
                    f"Page {page_text}, "
                    f"Chunk {chunk_id}, "
                    f"Similarity {float(similarity):.4f}]"
                )

        return (
            f"{answer}\n\n"
            "Retrieved Sources:\n"
            + "\n".join(citation_lines)
        )


__all__ = ["RAGTool"]