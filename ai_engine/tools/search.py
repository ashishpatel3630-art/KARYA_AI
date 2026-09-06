
from rag.embeddings import EmbeddingModel
from rag.retrieval import Retriever


class SearchTool:
    """Semantic search tool for KARYA's local RAG system."""

    name = "search"

    description = (
        "Searches KARYA's local knowledge base using "
        "semantic similarity and returns the most relevant "
        "document chunks with source information."
    )

    input_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "Question or information to search "
                    "for in the local knowledge base."
                ),
            },
            "top_k": {
                "type": "integer",
                "description": (
                    "Maximum number of relevant chunks "
                    "to return."
                ),
                "default": 5,
            },
        },
        "required": ["query"],
    }

    def __init__(
        self,
        embedding_model: EmbeddingModel | None = None,
        retriever: Retriever | None = None,
    ):
        self.embedding_model = (
            embedding_model or EmbeddingModel()
        )

        self.retriever = (
            retriever or Retriever()
        )

    def execute(
        self,
        query: str,
        top_k: int = 5,
    ) -> str:
        """Search the local RAG knowledge base."""

        if not query or not query.strip():
            raise ValueError(
                "Search query cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        if top_k > 20:
            raise ValueError(
                "top_k cannot be greater than 20."
            )

        query = query.strip()

        # Generate a local embedding for the query.
        query_embedding = (
            self.embedding_model.embed_text(query)
        )

        # Search PostgreSQL + pgvector.
        results = self.retriever.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )

        if not results:
            return (
                "No relevant information was found "
                "in the local knowledge base."
            )

        output = []

        for result in results:
            source = (
                f"File: {result.file_name}"
            )

            if result.page_number is not None:
                source += (
                    f" | Page: {result.page_number}"
                )

            source += (
                f" | Chunk: {result.chunk_id}"
                f" | Similarity: "
                f"{result.similarity:.4f}"
            )

            output.append(
                f"{source}\n"
                f"{result.content}"
            )

        return "\n\n".join(output)
