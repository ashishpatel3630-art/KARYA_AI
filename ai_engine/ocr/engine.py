from pathlib import Path

import pytesseract
from PIL import Image


class OCREngine:
    """
    Local OCR engine for KARYA using Tesseract.

    No cloud API or external AI service is used.
    """

    def __init__(
        self,
        language: str = "eng",
        config: str = "--psm 6",
    ):
        if not language or not language.strip():
            raise ValueError(
                "OCR language cannot be empty."
            )

        self.language = language
        self.config = config

    def is_available(self) -> bool:
        """
        Check whether the local Tesseract executable
        is available.
        """

        try:
            pytesseract.get_tesseract_version()
            return True

        except (
            pytesseract.TesseractNotFoundError,
            FileNotFoundError,
            RuntimeError,
        ):
            return False

    def get_version(self) -> str:
        """
        Return the installed Tesseract version.
        """

        if not self.is_available():
            raise RuntimeError(
                "Tesseract OCR engine is not available."
            )

        version = pytesseract.get_tesseract_version()

        return str(version)

    def extract_text(
        self,
        image: Image.Image,
    ) -> str:
        """
        Extract text from a PIL image.
        """

        if not isinstance(image, Image.Image):
            raise TypeError(
                "image must be a PIL Image."
            )

        if not self.is_available():
            raise RuntimeError(
                "Tesseract OCR engine is not available."
            )

        try:
            text = pytesseract.image_to_string(
                image,
                lang=self.language,
                config=self.config,
            )

        except Exception as exc:
            raise RuntimeError(
                "OCR text extraction failed."
            ) from exc

        return text.strip()

    def extract_text_from_file(
        self,
        image_path: str,
    ) -> str:
        """
        Extract text directly from an image file.
        """

        if not image_path or not image_path.strip():
            raise ValueError(
                "Image path cannot be empty."
            )

        path = Path(
            image_path
        ).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(
                f"Image not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Path is not a file: {path}"
            )

        try:
            with Image.open(path) as image:
                return self.extract_text(
                    image
                )

        except FileNotFoundError:
            raise

        except Exception as exc:
            raise ValueError(
                f"Could not read image file: {path}"
            ) from exc