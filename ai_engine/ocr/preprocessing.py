from PIL import Image, ImageFilter, ImageOps


class ImagePreprocessor:
    """
    Local image preprocessing pipeline for KARYA OCR.

    Responsibilities:
    - Convert images to grayscale.
    - Improve contrast.
    - Reduce noise.
    - Sharpen text.
    - Prepare images for OCR.
    """

    def __init__(
        self,
        grayscale: bool = True,
        autocontrast: bool = True,
        denoise: bool = True,
        sharpen: bool = True,
    ):
        self.grayscale = grayscale
        self.autocontrast = autocontrast
        self.denoise = denoise
        self.sharpen = sharpen

    def process(self, image: Image.Image) -> Image.Image:
        """
        Apply the configured preprocessing pipeline.
        """

        if not isinstance(image, Image.Image):
            raise TypeError(
                "image must be a PIL Image."
            )

        processed = image.copy()

        if self.grayscale:
            processed = ImageOps.grayscale(
                processed
            )

        if self.autocontrast:
            processed = ImageOps.autocontrast(
                processed
            )

        if self.denoise:
            processed = processed.filter(
                ImageFilter.MedianFilter(
                    size=3
                )
            )

        if self.sharpen:
            processed = processed.filter(
                ImageFilter.SHARPEN
            )

        return processed

    def load_and_process(
        self,
        image_path: str,
    ) -> Image.Image:
        """
        Load an image from disk and preprocess it.
        """

        if not image_path or not image_path.strip():
            raise ValueError(
                "Image path cannot be empty."
            )

        try:
            image = Image.open(
                image_path
            )

        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            ) from exc

        except Exception as exc:
            raise ValueError(
                f"Could not open image: {image_path}"
            ) from exc

        return self.process(image)