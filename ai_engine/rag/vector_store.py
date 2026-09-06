import psycopg


class VectorStore:
    """PostgreSQL + pgvector storage for KARYA RAG."""

    def __init__(
        self,
        database_url: str = "dbname=karya_ai",
    ):
        self.database_url = database_url

    def _get_connection(self):
        """Create a PostgreSQL connection."""
        return psycopg.connect(self.database_url)

    def add_chunk(
        self,
        document_id: str,
        file_name: str,
        file_type: str,
        chunk_id: int,
        content: str,
        embedding: list[float],
    ) -> None:
        """Store one document chunk and its embedding."""

        if len(embedding) != 384:
            raise ValueError(
                f"Expected a 384-dimensional embedding, "
                f"got {len(embedding)}."
            )

        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO document_chunks (
                        document_id,
                        file_name,
                        file_type,
                        chunk_id,
                        content,
                        embedding
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        document_id,
                        file_name,
                        file_type,
                        chunk_id,
                        content,
                        embedding,
                    ),
                )

            connection.commit()

    def add_chunks(
        self,
        chunks: list[dict],
    ) -> None:
        """Store multiple document chunks."""

        if not chunks:
            raise ValueError(
                "Cannot store an empty chunk list."
            )

        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                for chunk in chunks:
                    embedding = chunk["embedding"]

                    if len(embedding) != 384:
                        raise ValueError(
                            "Every embedding must have "
                            "384 dimensions."
                        )

                    cursor.execute(
                        """
                        INSERT INTO document_chunks (
                            document_id,
                            file_name,
                            file_type,
                            chunk_id,
                            content,
                            embedding
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (
                            chunk["document_id"],
                            chunk["file_name"],
                            chunk["file_type"],
                            chunk["chunk_id"],
                            chunk["content"],
                            embedding,
                        ),
                    )

            connection.commit()

    def count_chunks(self) -> int:
        """Return the total number of stored chunks."""

        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM document_chunks"
                )

                result = cursor.fetchone()

        return result[0]
