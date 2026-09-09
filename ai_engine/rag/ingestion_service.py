from pathlib import Path
from uuid import uuid4

from .chunker import DocumentChunker
from .embeddings import EmbeddingModel
from .ingestion import DocumentIngestion
from .parser import DocumentParser
from .vector_store import VectorStore


class RAGIngestionService:
    """Complete document ingestion pipeline for KARYA RAG."""

    def __init__(
        self,
        ingestion: DocumentIngestion | None = None,
        parser: DocumentParser | None = None,
        chunker: DocumentChunker | None = None,
        embedding_model: EmbeddingModel | None = None,
        vector_store: VectorStore | None = None,
    ):
        self.ingestion = ingestion or DocumentIngestion()
        self.parser = parser or DocumentParser()
        self.chunker = chunker or DocumentChunker()
        self.embedding_model = embedding_model or EmbeddingModel()
        self.vector_store = vector_store or VectorStore()

    def ingest_document(self, file_path: str, document_id: str | None = None) -> dict:
        """Run the complete document-to-vector ingestion pipeline."""

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {file_path}"
            )

        document = self.ingestion.ingest(
            str(path)
        )

        parsed_document = self.parser.parse(
            file_name=document.file_name,
            file_type=document.file_type,
            content=document.content,
        )

        all_chunks = []

        # PDF documents contain page-aware metadata.
        if document.file_type == ".pdf" and document.pages:

            for page in document.pages:

                page_parsed = self.parser.parse(
                    file_name=document.file_name,
                    file_type=document.file_type,
                    content=page.content,
                )

                page_chunks = self.chunker.chunk(
                    page_parsed.content,
                    page_number=page.page_number,
                )

                all_chunks.extend(page_chunks)

        else:
            # Non-PDF documents currently use the complete
            # extracted content as one logical section.
            all_chunks = self.chunker.chunk(
                parsed_document.content
            )

        # Re-number chunks globally.
        for chunk_id, chunk in enumerate(
            all_chunks,
            start=1,
        ):
            chunk.chunk_id = chunk_id

        embeddings = self.embedding_model.embed_documents(
            [chunk.content for chunk in all_chunks]
        )

        document_id = document_id or str(uuid4())

        records = []

        for chunk, embedding in zip(
            all_chunks,
            embeddings,
        ):
            records.append(
                {
                    "document_id": document_id,
                    "file_name": parsed_document.file_name,
                    "file_type": parsed_document.file_type,
                    "chunk_id": chunk.chunk_id,
                    "page_number": chunk.page_number,
                    "content": chunk.content,
                    "embedding": embedding,
                }
            )

        self.vector_store.add_chunks(records)

        return {
            "document_id": document_id,
            "file_name": parsed_document.file_name,
            "file_type": parsed_document.file_type,
            "chunks_created": len(all_chunks),
        }