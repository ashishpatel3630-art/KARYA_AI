from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from sentence_transformers import SentenceTransformer


@dataclass(frozen=True)
class EmbeddingConfig:
    """
    Configuration for KARYA's local embedding engine.
    """

    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    device: str | None = None
    batch_size: int = 32
    normalize_embeddings: bool = True


class EmbeddingError(RuntimeError):
    """Base exception for embedding failures."""


class EmbeddingModel:
    """
    Production-oriented local embedding service.

    Responsibilities:
    - Load one local embedding model.
    - Generate single embeddings.
    - Generate batch embeddings.
    - Expose embedding dimension.
    """

    def __init__(
        self,
        config: EmbeddingConfig | None = None,
    ):
        self.config = config or EmbeddingConfig()

        if self.config.batch_size <= 0:
            raise ValueError(
                "Embedding batch_size must be greater than zero."
            )

        try:
            self.model = SentenceTransformer(
                self.config.model_name,
                device=self.config.device,
            )
        except Exception as exc:
            raise EmbeddingError(
                "Failed to load embedding model "
                f"'{self.config.model_name}'."
            ) from exc

    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding for a single text.
        """

        self._validate_text(text)

        try:
            embedding = self.model.encode(
                text,
                normalize_embeddings=(
                    self.config.normalize_embeddings
                ),
                convert_to_numpy=True,
                show_progress_bar=False,
            )
        except Exception as exc:
            raise EmbeddingError(
                "Failed to generate text embedding."
            ) from exc

        return embedding.tolist()

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple document chunks.
        """

        if not texts:
            raise ValueError(
                "Cannot generate embeddings for an empty list."
            )

        for text in texts:
            self._validate_text(text)

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=self.config.batch_size,
                normalize_embeddings=(
                    self.config.normalize_embeddings
                ),
                convert_to_numpy=True,
                show_progress_bar=False,
            )
        except Exception as exc:
            raise EmbeddingError(
                "Failed to generate document embeddings."
            ) from exc

        return embeddings.tolist()

    def dimension(self) -> int:
        """
        Return the embedding vector dimension.
        """

        dimension = (
            self.model.get_sentence_embedding_dimension()
        )

        if dimension is None:
            raise EmbeddingError(
                "Embedding model did not expose a vector dimension."
            )

        return int(dimension)

    @staticmethod
    def _validate_text(text: str) -> None:
        if not isinstance(text, str):
            raise TypeError(
                "Embedding input must be a string."
            )

        if not text.strip():
            raise ValueError(
                "Embedding input cannot be empty."
            )


@lru_cache(maxsize=4)
def get_embedding_model(
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
) -> EmbeddingModel:
    """
    Return a cached embedding service.

    This prevents unnecessary repeated model loading.
    """

    return EmbeddingModel(
        EmbeddingConfig(
            model_name=model_name,
        )
    )