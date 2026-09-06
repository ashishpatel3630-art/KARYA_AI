from rag.ingestion import DocumentIngestion


ingestion = DocumentIngestion()

document = ingestion.ingest(
    "test_document.pdf"
)

print("FILE NAME:")
print(document.file_name)

print("\nFILE TYPE:")
print(document.file_type)

print("\nEXTRACTED CONTENT:")
print(document.content)
