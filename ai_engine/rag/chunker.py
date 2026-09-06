from dataclasses import dataclass


@dataclass
class DocumentChunk:
    """Represents a chunk of a document."""

    chunk_id: int
    content: str


class DocumentChunker:
    """Split documents into overlapping text chunks."""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ):
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative."
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _find_split_position(
        self,
        text: str,
        start: int,
        end: int,
    ) -> int:
        """Find a natural position to split the text."""

        if end >= len(text):
            return len(text)

        search_start = start + (self.chunk_size // 2)

        newline_position = text.rfind(
            "\n",
            search_start,
            end,
        )

        if newline_position > start:
            return newline_position

        sentence_position = text.rfind(
            ". ",
            search_start,
            end,
        )

        if sentence_position > start:
            return sentence_position + 1

        space_position = text.rfind(
            " ",
            search_start,
            end,
        )

        if space_position > start:
            return space_position

        return end

    def chunk(self, content: str) -> list[DocumentChunk]:
        """Split document content into overlapping chunks."""

        text = content.strip()

        if not text:
            raise ValueError(
                "Cannot chunk empty document content."
            )

        chunks = []

        start = 0
        chunk_id = 1

        while start < len(text):
            target_end = min(
                start + self.chunk_size,
                len(text),
            )

            end = self._find_split_position(
                text,
                start,
                target_end,
            )

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        content=chunk_text,
                    )
                )

                chunk_id += 1

            if end >= len(text):
                break

            next_start = end - self.chunk_overlap

            if next_start <= start:
                next_start = end

            start = next_start

        return chunks