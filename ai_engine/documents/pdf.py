from pathlib import Path

from pypdf import PdfReader


class PDFParser:
    """Extract text from PDF documents."""

    def parse(self, file_path: str) -> str:
        """
        Extract text from all pages of a PDF.

        Args:
            file_path: Path to the PDF file.

        Returns:
            Extracted text as a single string.
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

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text.strip())

        return "\n\n".join(pages)
