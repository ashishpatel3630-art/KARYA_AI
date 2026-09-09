from dataclasses import dataclass

import psycopg


@dataclass
class RetrievedChunk:
    """Represents a chunk retrieved from the vector store."""

    id: int
    document_id: str
    file_name: str
    file_type: str
    chunk_id: int
    page_number: int | None
    content: str
    similarity: float


class Retriever:
    """Retrieve semantically similar document chunks."""

    def __init__(
        self,
        database_url: str = "dbname=karya_ai",
    ):
        self.database_url = database_url

    def _get_connection(self):
        """Create a PostgreSQL connection."""
        return psycopg.connect(self.database_url)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[RetrievedChunk]:
        """Search for the most similar document chunks."""

        if len(query_embedding) != 384:
            raise ValueError(
                f"Expected a 384-dimensional query embedding, "
                f"got {len(query_embedding)}."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        document_filter = ""

        # IMPORTANT:
        # The SQL placeholders appear in this order:
        #
        #   1. query_embedding
        #   2. document_ids (if supplied)
        #   3. query_embedding
        #   4. top_k
        #
        # Therefore the parameters MUST follow exactly
        # the same order.

        parameters: list[object] = [
            query_embedding,
        ]

        if document_ids is not None:
            if not document_ids:
                return []

            document_filter = (
                "WHERE document_id = ANY(%s::text[])"
            )

            parameters.append(document_ids)

        parameters.extend(
            [
                query_embedding,
                top_k,
            ]
        )

        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        id,
                        document_id,
                        file_name,
                        file_type,
                        chunk_id,
                        page_number,
                        content,
                        1 - (embedding <=> %s::vector) AS similarity
                    FROM document_chunks
                    {document_filter}
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    parameters,
                )

                rows = cursor.fetchall()

        return [
            RetrievedChunk(
                id=row[0],
                document_id=row[1],
                file_name=row[2],
                file_type=row[3],
                chunk_id=row[4],
                page_number=row[5],
                content=row[6],
                similarity=float(row[7]),
            )
            for row in rows
        ]