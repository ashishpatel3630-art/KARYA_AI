from pathlib import Path

from reportlab.pdfgen import canvas

from rag.ingestion_service import RAGIngestionService


TEST_PDF = Path("rag/test_ingestion_document.pdf")


def create_test_pdf():
    pdf = canvas.Canvas(str(TEST_PDF))

    pdf.drawString(
        100,
        750,
        "KARYA AI Industrial Maintenance Report",
    )

    pdf.drawString(
        100,
        720,
        "Equipment: Compressor C-101",
    )

    pdf.drawString(
        100,
        690,
        "Temperature: 92 C",
    )

    pdf.drawString(
        100,
        660,
        "Vibration: 8.5 mm/s",
    )

    pdf.drawString(
        100,
        630,
        "Status: Critical",
    )

    pdf.drawString(
        100,
        600,
        "Immediate maintenance inspection is required.",
    )

    pdf.save()


def main():
    create_test_pdf()

    service = RAGIngestionService()

    result = service.ingest_document(
        str(TEST_PDF)
    )

    print("\nDOCUMENT INGESTION RESULT")
    print("=" * 60)

    print(f"Document ID: {result['document_id']}")
    print(f"File Name: {result['file_name']}")
    print(f"File Type: {result['file_type']}")
    print(f"Chunks Created: {result['chunks_created']}")

    print("=" * 60)


if __name__ == "__main__":
    main()
