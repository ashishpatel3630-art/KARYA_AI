from dataclasses import dataclass, field
from typing import Any


@dataclass
class Citation:
    """
    Source reference used to support an AI answer.

    Citation metadata is kept separate from the generated
    natural-language answer.
    """

    file_name: str
    file_type: str
    page_number: int | None
    chunk_id: int
    similarity: float
    document_id: str = ""
    source_text: str = ""
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if (
            not isinstance(self.file_name, str)
            or not self.file_name.strip()
        ):
            raise ValueError(
                "Citation file_name cannot be empty."
            )

        if (
            not isinstance(self.file_type, str)
            or not self.file_type.strip()
        ):
            raise ValueError(
                "Citation file_type cannot be empty."
            )

        if self.page_number is not None:
            if (
                not isinstance(self.page_number, int)
                or isinstance(self.page_number, bool)
                or self.page_number <= 0
            ):
                raise ValueError(
                    "Citation page_number must be a positive integer."
                )

        if (
            not isinstance(self.chunk_id, int)
            or isinstance(self.chunk_id, bool)
            or self.chunk_id <= 0
        ):
            raise ValueError(
                "Citation chunk_id must be a positive integer."
            )

        if not isinstance(
            self.similarity,
            (int, float),
        ) or isinstance(
            self.similarity,
            bool,
        ):
            raise ValueError(
                "Citation similarity must be numeric."
            )

        self.similarity = float(
            self.similarity
        )

        if not 0.0 <= self.similarity <= 1.0:
            raise ValueError(
                "Citation similarity must be between 0.0 and 1.0."
            )

        if not isinstance(
            self.document_id,
            str,
        ):
            raise ValueError(
                "Citation document_id must be a string."
            )

        if not isinstance(
            self.source_text,
            str,
        ):
            raise ValueError(
                "Citation source_text must be a string."
            )

        if self.metadata is None:
            self.metadata = {}

    @property
    def key(self) -> tuple[str, int | None, int]:
        """
        Stable user-facing citation identity.

        We intentionally deduplicate by:

            file name
            page
            chunk

        rather than document UUID.

        This prevents duplicate uploaded copies of the same
        document from appearing as separate sources in the UI.
        """

        return (
            self.file_name.strip().lower(),
            self.page_number,
            self.chunk_id,
        )

    def user_facing_label(
        self,
        index: int,
    ) -> str:
        """
        Return a concise source label.

        UUIDs and similarity scores are intentionally hidden
        from the normal user-facing label.
        """

        page = (
            str(self.page_number)
            if self.page_number is not None
            else "Unknown"
        )

        return (
            f"[{index}] "
            f"{self.file_name} · Page {page}"
        )


def deduplicate_citations(
    citations: list[Citation],
) -> list[Citation]:
    """
    Return unique citations ordered by relevance.

    If the same file/page/chunk appears multiple times,
    keep the result with the highest similarity score.
    """

    unique: dict[
        tuple[str, int | None, int],
        Citation,
    ] = {}

    for citation in citations:
        if not isinstance(
            citation,
            Citation,
        ):
            continue

        existing = unique.get(
            citation.key
        )

        if (
            existing is None
            or citation.similarity > existing.similarity
        ):
            unique[citation.key] = citation

    return sorted(
        unique.values(),
        key=lambda citation: (
            -citation.similarity,
            citation.file_name.lower(),
            citation.page_number or 0,
            citation.chunk_id,
        ),
    )


@dataclass
class RAGResponse:
    """
    Complete RAG response.

    answer:
        Only the clean natural-language answer.

    citations:
        Structured evidence returned separately.
    """

    answer: str
    citations: list[Citation]

    def __post_init__(self) -> None:
        if self.answer is None:
            self.answer = ""

        if self.citations is None:
            self.citations = []

        self.citations = deduplicate_citations(
            self.citations
        )