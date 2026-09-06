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

        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        document_id,
                        file_name,
                        file_type,
                        chunk_id,
                        content,
                        1 - (embedding <=> %s::vector) AS similarity
                    FROM document_chunks
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (
                        query_embedding,
                        query_embedding,
                        top_k,
                    ),
                )

                rows = cursor.fetchall()

        return [
            RetrievedChunk(
                id=row[0],
                document_id=row[1],
                file_name=row[2],
                file_type=row[3],
                chunk_id=row[4],
                content=row[5],
                similarity=float(row[6]),
            )
            for row in rows
        ]