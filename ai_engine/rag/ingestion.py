from dataclasses import dataclass
from pathlib import Path

from documents.docx import DOCXParser
from documents.pdf import PDFPage, PDFParser
from documents.pptx import PPTXParser
from documents.xlsx import XLSXParser


@dataclass
class IngestedPage:
    """Represents a document section with optional location metadata."""

    page_number: int | None
    content: str


@dataclass
class IngestedDocument:
    """Represents a document after ingestion."""

    file_name: str
    file_path: str
    file_type: str
    content: str
    pages: list[IngestedPage]


class DocumentIngestion:
    """Ingest documents into the KARYA RAG pipeline."""

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".xlsx",
        ".pptx",
    }

    def __init__(self):
        self.parsers = {
            ".pdf": PDFParser(),
            ".docx": DOCXParser(),
            ".xlsx": XLSXParser(),
            ".pptx": PPTXParser(),
        }

    def ingest(self, file_path: str) -> IngestedDocument:
        """
        Ingest a supported document.

        Args:
            file_path: Path to the document.

        Returns:
            IngestedDocument containing extracted text and
            document location metadata.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {file_path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Path is not a file: {file_path}"
            )

        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported document type: {extension}"
            )

        parser = self.parsers[extension]

        if extension == ".pdf":
            pdf_pages: list[PDFPage] = parser.parse(
                str(path)
            )

            content_test = "".join(
                page.text for page in pdf_pages if page.text
            )

            if not content_test.strip():
                from ocr.pdf import PDFOCRService
                ocr_service = PDFOCRService()
                
                if ocr_service.is_available():
                    ocr_result = ocr_service.extract_text_from_pdf(str(path))
                    pdf_pages = [
                        PDFPage(
                            page_number=page.page_number,
                            text=page.text
                        )
                        for page in ocr_result.pages
                    ]

            pages = [
                IngestedPage(
                    page_number=page.page_number,
                    content=page.text,
                )
                for page in pdf_pages
            ]

            content = "\n\n".join(
                page.content
                for page in pages
                if page.content
            )

        else:
            content = parser.parse(str(path))

            pages = [
                IngestedPage(
                    page_number=None,
                    content=content,
                )
            ]

        if not content.strip():
            raise ValueError("Extracted document content is empty.")

        return IngestedDocument(
            file_name=path.name,
            file_path=str(path),
            file_type=extension,
            content=content,
            pages=pages,
        )