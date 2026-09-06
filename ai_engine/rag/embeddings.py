from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """Generate local embeddings for KARYA RAG."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.model_name = model_name

        self.model = SentenceTransformer(
            model_name
        )

    def embed_text(self, text: str) -> list[float]:
        """Generate an embedding vector for a single text."""

        if not text or not text.strip():
            raise ValueError(
                "Cannot generate embedding for empty text."
            )

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate embeddings for multiple text chunks."""

        if not texts:
            raise ValueError(
                "Cannot generate embeddings for empty document list."
            )

        for text in texts:
            if not text or not text.strip():
                raise ValueError(
                    "Document list contains empty text."
                )

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    def dimension(self) -> int:
        """Return the embedding vector dimension."""

        return self.model.get_sentence_embedding_dimension()