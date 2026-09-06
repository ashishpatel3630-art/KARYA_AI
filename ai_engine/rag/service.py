from llm.schemas import LLMMessage, LLMRequest
from llm.service import LLMService

from .embeddings import EmbeddingModel
from .retrieval import Retriever


class RAGService:
    """Application-level service for KARYA Retrieval-Augmented Generation."""

    def __init__(
        self,
        embedding_model: EmbeddingModel | None = None,
        retriever: Retriever | None = None,
        llm_service: LLMService | None = None,
    ):
        self.embedding_model = embedding_model or EmbeddingModel()
        self.retriever = retriever or Retriever()
        self.llm_service = llm_service or LLMService()

    def answer(
        self,
        question: str,
        top_k: int = 3,
    ) -> str:
        """Answer a question using retrieved local knowledge."""

        if not question or not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        query_embedding = self.embedding_model.embed_text(
            question
        )

        results = self.retriever.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )

        if not results:
            return (
                "I could not find relevant information "
                "in the local knowledge base."
            )

        context_parts = []

        for result in results:
            context_parts.append(
                f"Source: {result.file_name}\n"
                f"Content:\n{result.content}"
            )

        context = "\n\n---\n\n".join(context_parts)

        prompt = f"""
You are KARYA, a sovereign industrial AI assistant.

Answer the user's question using ONLY the provided
local knowledge-base context.

If the context does not contain enough information,
say that the information is not available in the
provided knowledge base.

Do not invent facts.

LOCAL KNOWLEDGE-BASE CONTEXT:
{context}

USER QUESTION:
{question}
""".strip()

        request = LLMRequest(
            messages=[
                LLMMessage(
                    role="system",
                    content=(
                        "You are a precise industrial AI "
                        "assistant. Use only supplied context."
                    ),
                ),
                LLMMessage(
                    role="user",
                    content=prompt,
                ),
            ],
            temperature=0.1,
        )

        response = self.llm_service.chat(request)

        return response.content