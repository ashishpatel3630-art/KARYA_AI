from rag.service import RAGService


def main():
    rag_service = RAGService()

    question = "What is the condition of Compressor C-101?"

    response = rag_service.answer(
        question=question,
        top_k=3,
    )

    print("\nFULL RAG + CITATION TEST")
    print("=" * 60)

    print("QUESTION:")
    print(question)

    print("\nANSWER:")
    print("-" * 60)
    print(response.answer)

    print("\nSOURCES:")
    print("-" * 60)

    for citation in response.citations:
        print(
            f"FILE: {citation.file_name}"
        )
        print(
            f"TYPE: {citation.file_type}"
        )
        print(
            f"CHUNK: {citation.chunk_id}"
        )
        print(
            f"SIMILARITY: {citation.similarity:.4f}"
        )
        print("-" * 60)

    print("=" * 60)


if __name__ == "__main__":
    main()