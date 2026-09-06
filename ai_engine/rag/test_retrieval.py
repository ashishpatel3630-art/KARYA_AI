from rag.embeddings import EmbeddingModel
from rag.retrieval import Retriever


embedding_model = EmbeddingModel()
retriever = Retriever()


query = "What is the condition of Pump P-101?"

query_embedding = embedding_model.embed_text(query)

results = retriever.search(
    query_embedding=query_embedding,
    top_k=3,
)


print("QUERY:")
print(query)

print("\nRESULTS:")
print("=" * 60)

for result in results:
    print(f"ID: {result.id}")
    print(f"FILE: {result.file_name}")
    print(f"CHUNK: {result.chunk_id}")
    print(f"SIMILARITY: {result.similarity:.4f}")
    print(f"CONTENT: {result.content}")
    print("=" * 60)
