from __future__ import annotations

import base64
from pathlib import Path

import requests

from .schemas import VisionRequest, VisionResponse


class VisionClient:
    """
    Local Ollama client for multimodal vision models.

    Responsibilities:
        - Validate image files
        - Encode images
        - Send prompt + image to Ollama
        - Return structured VisionResponse
        - Never call external AI APIs
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        timeout: int = 120,
    ):
        if not base_url or not base_url.strip():
            raise ValueError("base_url cannot be empty.")

        if timeout <= 0:
            raise ValueError("timeout must be greater than zero.")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # ---------------------------------------------------------
    # HEALTH
    # ---------------------------------------------------------

    def health_check(self) -> bool:
        """
        Check whether the local Ollama server is reachable.
        """

        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10,
            )

            return response.status_code == 200

        except requests.RequestException:
            return False

    # ---------------------------------------------------------
    # MODEL CHECK
    # ---------------------------------------------------------

    def list_models(self) -> list[str]:
        """
        Return models currently available in local Ollama.
        """

        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            raise RuntimeError(
                "Could not connect to local Ollama server."
            ) from exc

        data = response.json()

        models = data.get("models", [])

        return [
            model.get("name", "")
            for model in models
            if model.get("name")
        ]

    def is_model_available(self, model: str) -> bool:
        """
        Check whether a specific model exists locally.
        """

        if not model or not model.strip():
            raise ValueError("model cannot be empty.")

        return model in self.list_models()

    # ---------------------------------------------------------
    # IMAGE VALIDATION
    # ---------------------------------------------------------

    def _validate_image(self, image_path: str) -> Path:
        """
        Validate and resolve a local image path.
        """

        if not image_path or not image_path.strip():
            raise ValueError("image_path cannot be empty.")

        path = Path(image_path).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(
                f"Image not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Image path is not a file: {path}"
            )

        supported_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".gif",
            ".bmp",
        }

        if path.suffix.lower() not in supported_extensions:
            raise ValueError(
                f"Unsupported image format: {path.suffix}"
            )

        return path

    # ---------------------------------------------------------
    # IMAGE ENCODING
    # ---------------------------------------------------------

    def _encode_image(self, image_path: str) -> str:
        """
        Convert a local image into base64.
        """

        path = self._validate_image(image_path)

        try:
            image_bytes = path.read_bytes()

        except OSError as exc:
            raise RuntimeError(
                f"Could not read image: {path}"
            ) from exc

        return base64.b64encode(image_bytes).decode("utf-8")

    # ---------------------------------------------------------
    # GENERATION
    # ---------------------------------------------------------

    def analyze(
        self,
        request: VisionRequest,
    ) -> VisionResponse:
        """
        Send an image + prompt to the local Ollama vision model.
        """

        if not isinstance(request, VisionRequest):
            raise TypeError(
                "request must be a VisionRequest."
            )

        if not request.prompt.strip():
            raise ValueError(
                "Vision prompt cannot be empty."
            )

        image_base64 = self._encode_image(
            request.image_path
        )

        payload = {
            "model": request.model,
            "messages": [
                {
                    "role": "user",
                    "content": request.prompt,
                    "images": [
                        image_base64
                    ],
                }
            ],
            "stream": False,
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()

        except requests.Timeout as exc:
            raise TimeoutError(
                "Vision model request timed out."
            ) from exc

        except requests.RequestException as exc:
            raise RuntimeError(
                "Vision model request failed."
            ) from exc

        try:
            data = response.json()

        except ValueError as exc:
            raise RuntimeError(
                "Ollama returned invalid JSON."
            ) from exc

        message = data.get("message", {})

        content = message.get("content", "")

        if not isinstance(content, str):
            content = str(content)

        return VisionResponse(
            model=request.model,
            prompt=request.prompt,
            content=content.strip(),
        )