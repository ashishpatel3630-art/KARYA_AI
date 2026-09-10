from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterator

from .client import OllamaClient
from .schemas import LLMMessage


@dataclass(frozen=True)
class LLMConfig:
    """
    Runtime configuration for KARYA local LLM inference.
    """

    model: str = "llama3.2"
    temperature: float = 0.2
    max_tokens: int = 2048


class LLMService:
    """
    High-level LLM abstraction.

    Agent code should communicate with this service,
    not directly with Ollama HTTP APIs.
    """

    def __init__(
        self,
        client: OllamaClient | None = None,
        config: LLMConfig | None = None,
    ):
        self.client = client or OllamaClient()
        self.config = config or LLMConfig()

    def health(self) -> bool:
        return self.client.health_check()

    def models(self) -> list[dict]:
        return self.client.list_models()

    def generate(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:

        selected_model = model or self.config.model

        selected_temperature = (
            self.config.temperature
            if temperature is None
            else temperature
        )

        selected_max_tokens = (
            self.config.max_tokens
            if max_tokens is None
            else max_tokens
        )

        return self.client.generate(
            messages=messages,
            model=selected_model,
            temperature=selected_temperature,
            max_tokens=selected_max_tokens,
        )

    def stream(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> Iterator[str]:

        selected_model = model or self.config.model

        selected_temperature = (
            self.config.temperature
            if temperature is None
            else temperature
        )

        selected_max_tokens = (
            self.config.max_tokens
            if max_tokens is None
            else max_tokens
        )

        yield from self.client.generate_stream(
            messages=messages,
            model=selected_model,
            temperature=selected_temperature,
            max_tokens=selected_max_tokens,
        )