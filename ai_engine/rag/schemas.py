from dataclasses import dataclass


@dataclass
class Citation:
    """Source reference used to support an AI answer."""

    file_name: str
    file_type: str
    page_number: int | None
    chunk_id: int
    similarity: float


@dataclass
class RAGResponse:
    """Complete RAG response with source citations."""

    answer: str
    citations: list[Citation]