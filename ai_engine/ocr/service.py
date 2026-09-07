from dataclasses import dataclass

from PIL import Image

from .engine import OCREngine
from .preprocessing import ImagePreprocessor


@dataclass(frozen=True)
class OCRResult:
    """
    Structured OCR result returned by KARYA.
    """

    text: str
    language: str
    engine: str
    processed: bool

    def is_empty(self) -> bool:
        return not self.text.strip()

    def character_count(self) -> int:
        return len(self.text)

    def word_count(self) -> int:
        return len(self.text.split())


class OCRService:
    """
    High-level OCR service for KARYA.

    Pipeline:

        Image
          ↓
        Preprocessing
          ↓
        Tesseract
          ↓
        OCRResult
    """

    def __init__(
        self,
        engine: OCREngine | None = None,
        preprocessor: ImagePreprocessor | None = None,
    ):
        self.engine = engine or OCREngine()

        self.preprocessor = (
            preprocessor
            or ImagePreprocessor()
        )

    def is_available(self) -> bool:
        """
        Check whether the OCR engine is available.
        """

        return self.engine.is_available()

    def extract_text(
        self,
        image: Image.Image,
        preprocess: bool = True,
    ) -> OCRResult:
        """
        Extract text from a PIL image.
        """

        if not isinstance(image, Image.Image):
            raise TypeError(
                "image must be a PIL Image."
            )

        if not self.is_available():
            raise RuntimeError(
                "OCR engine is not available."
            )

        processed_image = image

        if preprocess:
            processed_image = (
                self.preprocessor.process(
                    image
                )
            )

        text = self.engine.extract_text(
            processed_image
        )

        return OCRResult(
            text=text,
            language=self.engine.language,
            engine="tesseract",
            processed=preprocess,
        )

    def extract_text_from_file(
        self,
        image_path: str,
        preprocess: bool = True,
    ) -> OCRResult:
        """
        Extract text from an image file.
        """

        if not image_path or not image_path.strip():
            raise ValueError(
                "Image path cannot be empty."
            )

        image = (
            self.preprocessor.load_and_process(
                image_path
            )
            if preprocess
            else self._load_image(image_path)
        )

        text = self.engine.extract_text(
            image
        )

        return OCRResult(
            text=text,
            language=self.engine.language,
            engine="tesseract",
            processed=preprocess,
        )

    def _load_image(
        self,
        image_path: str,
    ) -> Image.Image:
        """
        Load an image without preprocessing.
        """

        try:
            image = Image.open(
                image_path
            )

            return image.copy()

        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            ) from exc

        except Exception as exc:
            raise ValueError(
                f"Could not open image: {image_path}"
            ) from exc