from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class PDFPage:
    """Extracted text from one PDF page."""

    page_number: int
    text: str


class PDFParser:
    """
    PDF parser for KARYA.

    This parser is responsible only for extracting text from
    text-based PDFs.

    OCR for scanned/image-based PDFs is handled separately by
    the KARYA OCR subsystem.
    """

    supported_extensions = {".pdf"}

    def parse(
        self,
        file_path: str | Path,
    ) -> list[PDFPage]:
        """
        Extract text from every page of a PDF.

        Args:
            file_path: Path to the PDF file.

        Returns:
            A list of PDFPage objects.

        Raises:
            FileNotFoundError:
                When the PDF does not exist.
            ValueError:
                When the file is not a PDF.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"PDF path is not a file: {path}"
            )

        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(
                f"Unsupported file type: {path.suffix}"
            )

        reader = PdfReader(str(path))

        pages: list[PDFPage] = []

        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            pages.append(
                PDFPage(
                    page_number=index,
                    text=text.strip(),
                )
            )

        return pages

    def extract_text(
        self,
        file_path: str | Path,
    ) -> str:
        """
        Extract all text from a PDF as one string.
        """

        pages = self.parse(file_path)

        return "\n\n".join(
            page.text
            for page in pages
            if page.text
        )

    def page_count(
        self,
        file_path: str | Path,
    ) -> int:
        """
        Return the number of pages in a PDF.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {path}"
            )

        reader = PdfReader(str(path))

        return len(reader.pages)