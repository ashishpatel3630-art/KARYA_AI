import sys
from functools import lru_cache
from pathlib import Path

from app.core.config import settings


AI_ENGINE_ROOT = Path(__file__).resolve().parents[2] / "ai_engine"
if str(AI_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ENGINE_ROOT))


@lru_cache(maxsize=1)
def _services():
    from llm.client import OllamaClient
    from llm.service import LLMService
    from rag.embeddings import EmbeddingModel
    from rag.ingestion_service import RAGIngestionService
    from rag.retrieval import Retriever
    from rag.service import RAGService
    from rag.vector_store import VectorStore

    embedding_model = EmbeddingModel(settings.EMBEDDING_MODEL)
    vector_database_url = settings.VECTOR_DATABASE_URL
    return (
        RAGIngestionService(
            embedding_model=embedding_model,
            vector_store=VectorStore(vector_database_url),
        ),
        RAGService(
            embedding_model=embedding_model,
            retriever=Retriever(vector_database_url),
            llm_service=LLMService(
                client=OllamaClient(settings.OLLAMA_BASE_URL),
                default_model=settings.OLLAMA_MODEL,
            ),
        ),
    )


def ingest_document(file_path: str, document_id: str) -> dict:
    ingestion_service, _ = _services()
    return ingestion_service.ingest_document(file_path, document_id=document_id)


def answer_question(question: str, document_ids: list[str]):
    _, rag_service = _services()
    return rag_service.answer(question=question, document_ids=document_ids)