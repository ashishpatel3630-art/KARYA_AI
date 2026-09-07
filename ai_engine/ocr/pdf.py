from dataclasses import dataclass
from pathlib import Path

from pdf2image import convert_from_path

from .engine import OCREngine
from .preprocessing import ImagePreprocessor


@dataclass(frozen=True)
class OCRPDFPage:
    """OCR result for one PDF page."""

    page_number: int
    text: str

    def is_empty(self) -> bool:
        return not self.text.strip()


@dataclass(frozen=True)
class OCRPDFResult:
    """Complete OCR result for a PDF."""

    file_name: str
    pages: list[OCRPDFPage]

    def is_empty(self) -> bool:
        return not self.pages or all(
            page.is_empty()
            for page in self.pages
        )

    def page_count(self) -> int:
        return len(self.pages)

    def full_text(self) -> str:
        sections: list[str] = []

        for page in self.pages:
            sections.append(
                f"[Page: {page.page_number}]"
            )
            sections.append(page.text)

        return "\n\n".join(sections)


class PDFOCRService:
    """
    Local OCR service for scanned PDFs.

    Pipeline:

        PDF
         ↓
        Poppler
         ↓
        PDF pages → images
         ↓
        Image preprocessing
         ↓
        Tesseract OCR
         ↓
        OCRPDFResult
    """

    def __init__(
        self,
        engine: OCREngine | None = None,
        preprocessor: ImagePreprocessor | None = None,
        dpi: int = 200,
    ):
        if dpi <= 0:
            raise ValueError(
                "dpi must be greater than zero."
            )

        self.engine = engine or OCREngine()

        self.preprocessor = (
            preprocessor
            or ImagePreprocessor()
        )

        self.dpi = dpi

    def is_available(self) -> bool:
        """Check whether the OCR engine is available."""

        return self.engine.is_available()

    def extract_text_from_pdf(
        self,
        pdf_path: str,
        preprocess: bool = True,
    ) -> OCRPDFResult:
        """Extract OCR text from every page of a scanned PDF."""

        if not pdf_path or not pdf_path.strip():
            raise ValueError(
                "PDF path cannot be empty."
            )

        path = (
            Path(pdf_path)
            .expanduser()
            .resolve()
        )

        if not path.exists():
            raise FileNotFoundError(
                f"PDF not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Path is not a file: {path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                "PDF OCR requires a .pdf file."
            )

        if not self.is_available():
            raise RuntimeError(
                "Tesseract OCR engine is not available."
            )

        try:
            images = convert_from_path(
                str(path),
                dpi=self.dpi,
            )

        except Exception as exc:
            raise RuntimeError(
                f"Could not convert PDF to images: {path.name}"
            ) from exc

        pages: list[OCRPDFPage] = []

        for page_number, image in enumerate(
            images,
            start=1,
        ):
            if preprocess:
                image = self.preprocessor.process(
                    image
                )

            text = self.engine.extract_text(
                image
            )

            pages.append(
                OCRPDFPage(
                    page_number=page_number,
                    text=text,
                )
            )

        return OCRPDFResult(
            file_name=path.name,
            pages=pages,
        )
