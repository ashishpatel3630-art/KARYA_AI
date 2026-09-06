from dataclasses import dataclass


@dataclass
class ParsedDocument:
    """Represents normalized document content for RAG."""

    file_name: str
    file_type: str
    content: str


class DocumentParser:
    """Normalize extracted document content for the RAG pipeline."""

    def parse(
        self,
        file_name: str,
        file_type: str,
        content: str,
    ) -> ParsedDocument:
        """
        Normalize document content before chunking.
        """

        normalized_content = content.strip()

        if not normalized_content:
            raise ValueError(
                f"Document contains no readable text: {file_name}"
            )

        return ParsedDocument(
            file_name=file_name,
            file_type=file_type.lower(),
            content=normalized_content,
        )