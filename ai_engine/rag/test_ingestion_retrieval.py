from rag.embeddings import EmbeddingModel
from rag.retrieval import Retriever


def main():
    embedding_model = EmbeddingModel()
    retriever = Retriever()

    question = "What is the condition of Compressor C-101?"

    query_embedding = embedding_model.embed_text(question)

    results = retriever.search(
        query_embedding=query_embedding,
        top_k=3,
    )

    print("\nSEMANTIC RETRIEVAL TEST")
    print("=" * 60)

    print(f"QUESTION:")
    print(question)

    print("\nRESULTS:")

    for result in results:
        print("-" * 60)
        print(f"FILE: {result.file_name}")
        print(f"CHUNK: {result.chunk_id}")
        print(f"SIMILARITY: {result.similarity:.4f}")
        print(f"CONTENT:")
        print(result.content)

    print("=" * 60)


if __name__ == "__main__":
    main()
