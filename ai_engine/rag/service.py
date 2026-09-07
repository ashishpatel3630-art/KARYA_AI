from llm.schemas import LLMMessage, LLMRequest
from llm.service import LLMService

from .embeddings import EmbeddingModel
from .retrieval import Retriever
from .schemas import Citation, RAGResponse


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
        similarity_threshold: float = 0.60,
    ) -> RAGResponse:
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        if not 0.0 <= similarity_threshold <= 1.0:
            raise ValueError(
                "similarity_threshold must be between 0.0 and 1.0."
            )

        query_embedding = self.embedding_model.embed_text(question)

        results = self.retriever.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )

        results = [
            result
            for result in results
            if result.similarity >= similarity_threshold
        ]

        if not results:
            return RAGResponse(
                answer=(
                    "I could not find sufficiently relevant "
                    "information in the local knowledge base."
                ),
                citations=[],
            )

        context_parts = []

        for result in results:
            page_info = (
                f"Page: {result.page_number}"
                if result.page_number is not None
                else "Page: Unknown"
            )

            context_parts.append(
                f"Source File: {result.file_name}\n"
                f"{page_info}\n"
                f"Source Chunk: {result.chunk_id}\n"
                f"Content:\n{result.content}"
            )

        context = "\n\n---\n\n".join(context_parts)

        prompt = f"""
You are KARYA, a sovereign industrial AI assistant.

Answer the user's question using ONLY the provided
local knowledge-base context.

IMPORTANT CITATION RULE:

Whenever you use information from a source, cite that
source directly in the answer using this format:

[Source: filename, Page X, Chunk Y]

If the page is marked as "Unknown", use:

[Source: filename, Page Unknown, Chunk Y]

For example:

The equipment is currently in a critical condition.
[Source: maintenance_report.pdf, Page 1, Chunk 2]

Use the exact file name, page number, and chunk number
provided in the context.

If multiple sources support different statements,
cite each statement with its corresponding source.

Do not create or invent source names, page numbers,
or chunk numbers.

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
                        "assistant. Use only supplied context "
                        "and always provide source citations."
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

        citations = [
            Citation(
                file_name=result.file_name,
                file_type=result.file_type,
                page_number=result.page_number,
                chunk_id=result.chunk_id,
                similarity=result.similarity,
                document_id=result.document_id,
                source_text=result.content,
            )
            for result in results
        ]

        return RAGResponse(
            answer=response.content,
            citations=citations,
        )