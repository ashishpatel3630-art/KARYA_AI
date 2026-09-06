from rag.ingestion import DocumentIngestion


ingestion = DocumentIngestion()

document = ingestion.ingest(
    "rag/test_ingestion_document.pdf"
)

print("FILE NAME:")
print(document.file_name)

print("\nFILE TYPE:")
print(document.file_type)

print("\nEXTRACTED CONTENT:")
print(document.content)
