from rag.embeddings import EmbeddingModel


embedding_model = EmbeddingModel()


text = """
Pump P-101 is operating under abnormal conditions.
The equipment temperature is 85 C.
The measured vibration is 7.2 mm/s.
The current equipment status is Critical.
"""


embedding = embedding_model.embed_text(text)


print("MODEL:")
print(embedding_model.model_name)

print("\nVECTOR DIMENSION:")
print(len(embedding))

print("\nFIRST 10 VALUES:")
print(embedding[:10])
