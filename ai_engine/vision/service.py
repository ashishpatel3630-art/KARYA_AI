from pathlib import Path

from .client import VisionClient
from .schemas import VisionRequest, VisionResponse


class VisionService:
    """
    High-level local vision service.

    Responsibilities:
    - Validate image paths.
    - Check local Ollama availability.
    - Check whether the requested vision model exists.
    - Send vision requests through VisionClient.
    """

    SUPPORTED_IMAGE_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".gif",
        ".bmp",
    }

    def __init__(
        self,
        client: VisionClient | None = None,
        default_model: str = "llama3.2-vision",
    ):
        if not default_model or not default_model.strip():
            raise ValueError("default_model cannot be empty.")

        self.client = client or VisionClient()
        self.default_model = default_model

    def is_available(self) -> bool:
        """Return True when the local Ollama server is reachable."""
        return self.client.health_check()

    def list_models(self) -> list[str]:
        """Return models currently available in local Ollama."""
        return self.client.list_models()

    def model_available(self, model: str | None = None) -> bool:
        """Check whether a specific local model is installed."""
        selected_model = model or self.default_model

        if not selected_model or not selected_model.strip():
            raise ValueError("Model name cannot be empty.")

        return self.client.is_model_available(selected_model)

    def validate_image(self, image_path: str) -> Path:
        """
        Validate and resolve an image path.
        """
        if not image_path or not image_path.strip():
            raise ValueError("Image path cannot be empty.")

        path = Path(image_path).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")

        if path.suffix.lower() not in self.SUPPORTED_IMAGE_EXTENSIONS:
            supported = ", ".join(sorted(self.SUPPORTED_IMAGE_EXTENSIONS))
            raise ValueError(
                f"Unsupported image format: {path.suffix}. "
                f"Supported formats: {supported}"
            )

        return path

    def analyze(
        self,
        prompt: str,
        image_path: str,
        model: str | None = None,
    ) -> VisionResponse:
        """
        Analyze an image using a locally hosted vision model.
        """

        if not prompt or not prompt.strip():
            raise ValueError("Vision prompt cannot be empty.")

        path = self.validate_image(image_path)

        selected_model = model or self.default_model

        if not self.is_available():
            raise RuntimeError(
                "Local Ollama server is unavailable. "
                "Start Ollama before running vision inference."
            )

        if not self.model_available(selected_model):
            raise RuntimeError(
                f"Vision model '{selected_model}' is not installed "
                "in the local Ollama runtime."
            )

        request = VisionRequest(
            prompt=prompt.strip(),
            image_path=str(path),
            model=selected_model,
        )

        return self.client.analyze(request)

    def analyze_industrial_image(
        self,
        image_path: str,
        model: str | None = None,
    ) -> VisionResponse:
        """
        Analyze an industrial image using KARYA's standard inspection prompt.
        """

        prompt = """
You are KARYA, a sovereign industrial AI inspection assistant.

Analyze the provided industrial image carefully.

Identify, where visible:

1. Equipment or asset type
2. Visible equipment identifiers
3. Physical condition
4. Warning signs or abnormal conditions
5. Leaks, corrosion, cracks, deformation, smoke, overheating,
   damaged components, or other visible anomalies
6. Safety concerns
7. Possible maintenance concerns
8. Recommended next inspection or maintenance action

Do not invent information that cannot be visually verified.

Clearly separate:
- Observed evidence
- Possible interpretation
- Recommended action

If something is not visible or cannot be determined from the image,
state that explicitly.
""".strip()

        return self.analyze(
            prompt=prompt,
            image_path=image_path,
            model=model,
        )