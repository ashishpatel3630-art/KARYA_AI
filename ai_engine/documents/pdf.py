from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass
class PDFPage:
    """Represents one extracted PDF page."""

    page_number: int
    content: str


class PDFParser:
    """Extract page-aware text from PDF documents."""

    def parse(self, file_path: str) -> list[PDFPage]:
        """
        Extract text from every page of a PDF.

        Args:
            file_path: Path to the PDF file.

        Returns:
            A list of PDFPage objects containing page numbers
            and extracted text.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {file_path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Expected a PDF file, got: {path.suffix}"
            )

        reader = PdfReader(str(path))

        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            text = page.extract_text()

            if not text:
                continue

            text = text.strip()

            if not text:
                continue

            pages.append(
                PDFPage(
                    page_number=page_number,
                    content=text,
                )
            )

        return pages