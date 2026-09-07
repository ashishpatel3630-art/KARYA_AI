from collections.abc import Iterator

from .client import OllamaClient
from .schemas import LLMRequest, LLMResponse


class LLMService:
    """Application-level service for KARYA's local LLM."""

    def __init__(
        self,
        client: OllamaClient | None = None,
        default_model: str = "llama3.2",
    ):
        self.client = client or OllamaClient()
        self.default_model = default_model

    def chat(self, request: LLMRequest) -> LLMResponse:
        """Generate a complete AI response for an LLM request."""

        model = request.model or self.default_model

        content = self.client.generate(
            messages=request.messages,
            model=model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return LLMResponse(
            content=content,
            model=model,
        )

    def stream(self, request: LLMRequest) -> Iterator[str]:
        """
        Stream an AI response for an LLM request.

        Yields generated text chunks from the local Ollama runtime.
        """

        model = request.model or self.default_model

        yield from self.client.generate_stream(
            messages=request.messages,
            model=model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )