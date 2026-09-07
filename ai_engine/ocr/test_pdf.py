from pathlib import Path

from PIL import Image

from ocr import OCRPDFPage, OCRPDFResult, PDFOCRService


TEST_PDF = Path("rag/test_ingestion_document.pdf")


def test_ocr_pdf_page():
    page = OCRPDFPage(
        page_number=1,
        text="Compressor C-101 is critical.",
    )

    assert page.page_number == 1
    assert not page.is_empty()


def test_ocr_pdf_result():
    result = OCRPDFResult(
        file_name="test.pdf",
        pages=[
            OCRPDFPage(
                page_number=1,
                text="Test content",
            )
        ],
    )

    assert result.page_count() == 1
    assert not result.is_empty()
    assert "[Page: 1]" in result.full_text()


def test_pdf_ocr_service():
    service = PDFOCRService()

    assert service.is_available()

    result = service.extract_text_from_pdf(
        str(TEST_PDF)
    )

    assert result.file_name == "test_ingestion_document.pdf"
    assert result.page_count() == 1
    assert not result.is_empty()

    text = result.full_text()

    assert "Compressor C-101" in text
    assert "Temperature" in text
    assert "Vibration" in text
    assert "Critical" in text
