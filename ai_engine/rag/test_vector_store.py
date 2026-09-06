from rag.embeddings import EmbeddingModel
from rag.vector_store import VectorStore


embedding_model = EmbeddingModel()
vector_store = VectorStore()


text = """
Pump P-101 is operating under abnormal conditions.
The equipment temperature is 85 C.
The measured vibration is 7.2 mm/s.
The current equipment status is Critical.
Maintenance inspection is required immediately.
"""


embedding = embedding_model.embed_text(text)


vector_store.add_chunk(
    document_id="test-document-001",
    file_name="maintenance_report.pdf",
    file_type=".pdf",
    chunk_id=1,
    content=text.strip(),
    embedding=embedding,
)


print("Chunk stored successfully.")
print("Total chunks:", vector_store.count_chunks())
