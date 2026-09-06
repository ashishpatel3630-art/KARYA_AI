from dataclasses import dataclass


@dataclass
class DocumentChunk:
    """Represents a chunk of a document."""

    chunk_id: int
    content: str
    page_number: int | None = None


class DocumentChunker:
    """Split documents into clean overlapping text chunks."""

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
        """Find a natural boundary for the end of a chunk."""

        if end >= len(text):
            return len(text)

        search_start = start + (self.chunk_size // 2)

        # Prefer paragraph/newline boundaries.
        newline_position = text.rfind(
            "\n",
            search_start,
            end,
        )

        if newline_position > start:
            return newline_position

        # Prefer sentence boundaries.
        sentence_positions = [
            text.rfind(". ", search_start, end),
            text.rfind("! ", search_start, end),
            text.rfind("? ", search_start, end),
        ]

        valid_positions = [
            position
            for position in sentence_positions
            if position > start
        ]

        if valid_positions:
            return max(valid_positions) + 1

        # Finally prefer whitespace.
        space_position = text.rfind(
            " ",
            search_start,
            end,
        )

        if space_position > start:
            return space_position

        return end

    def _move_to_next_word(
        self,
        text: str,
        position: int,
    ) -> int:
        """Move forward until the beginning of the next word."""

        if position >= len(text):
            return len(text)

        # If we are already at whitespace, skip it.
        while (
            position < len(text)
            and text[position].isspace()
        ):
            position += 1

        # If position is inside a word, move to its end.
        while (
            position < len(text)
            and not text[position].isspace()
        ):
            position += 1

        # Skip whitespace before the next word.
        while (
            position < len(text)
            and text[position].isspace()
        ):
            position += 1

        return position

    def chunk(
        self,
        content: str,
        page_number: int | None = None,
    ) -> list[DocumentChunk]:
        """Split content into clean overlapping chunks."""

        text = content.strip()

        if not text:
            raise ValueError(
                "Cannot chunk empty document content."
            )

        chunks = []

        start = 0
        chunk_id = 1
        text_length = len(text)

        while start < text_length:

            target_end = min(
                start + self.chunk_size,
                text_length,
            )

            end = self._find_split_position(
                text,
                start,
                target_end,
            )

            # Ensure the chunk ends cleanly.
            if end < text_length:
                while (
                    end < text_length
                    and not text[end].isspace()
                ):
                    end += 1

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        content=chunk_text,
                        page_number=page_number,
                    )
                )

                chunk_id += 1

            if end >= text_length:
                break

            # Calculate desired overlap.
            overlap_start = max(
                start + 1,
                end - self.chunk_overlap,
            )

            # IMPORTANT:
            # Never allow the next chunk to start
            # in the middle of a word.
            next_start = self._move_to_next_word(
                text,
                overlap_start,
            )

            # Safety protection.
            if next_start <= start:
                next_start = end

            if next_start >= text_length:
                break

            start = next_start

        return chunks