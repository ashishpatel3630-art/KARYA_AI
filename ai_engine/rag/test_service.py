from rag.service import RAGService


rag_service = RAGService()


question = "What is the condition of Pump P-101?"


answer = rag_service.answer(
    question=question,
    top_k=3,
)


print("QUESTION:")
print(question)

print("\nANSWER:")
print("=" * 60)
print(answer)
print("=" * 60)
