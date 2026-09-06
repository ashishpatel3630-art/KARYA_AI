from dataclasses import dataclass
from pathlib import Path

from documents.docx import DOCXParser
from documents.pdf import PDFParser
from documents.pptx import PPTXParser
from documents.xlsx import XLSXParser


@dataclass
class IngestedDocument:
    """Represents a document after ingestion."""

    file_name: str
    file_path: str
    file_type: str
    content: str


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
            IngestedDocument containing extracted text.
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

        content = parser.parse(str(path))

        return IngestedDocument(
            file_name=path.name,
            file_path=str(path),
            file_type=extension,
            content=content,
        )