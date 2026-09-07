import json
from collections.abc import Iterator
from urllib import error, request

from .exceptions import (
    LLMConnectionError,
    LLMGenerationError,
    LLMModelNotFoundError,
    LLMTimeoutError,
)
from .schemas import LLMMessage


class OllamaClient:
    """Client for communicating with the local Ollama server."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        timeout: float = 120.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health_check(self) -> bool:
        """Check whether the local Ollama server is available."""

        try:
            req = request.Request(
                f"{self.base_url}/api/tags",
                method="GET",
            )

            with request.urlopen(req, timeout=10) as response:
                return response.status == 200

        except (error.URLError, TimeoutError):
            return False

    def list_models(self) -> list[dict]:
        """Return models available in the local Ollama runtime."""

        try:
            req = request.Request(
                f"{self.base_url}/api/tags",
                method="GET",
            )

            with request.urlopen(req, timeout=10) as response:
                result = json.loads(
                    response.read().decode("utf-8")
                )

        except TimeoutError as exc:
            raise LLMTimeoutError(
                "Ollama model listing timed out."
            ) from exc

        except error.URLError as exc:
            raise LLMConnectionError(
                "Could not connect to the local Ollama server."
            ) from exc

        except json.JSONDecodeError as exc:
            raise LLMGenerationError(
                "Invalid model list received from Ollama."
            ) from exc

        return result.get("models", [])

    def generate(
        self,
        messages: list[LLMMessage],
        model: str,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> str:
        """Generate a complete response using a local Ollama model."""

        payload = self._build_payload(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )

        data = json.dumps(payload).encode("utf-8")

        req = request.Request(
            f"{self.base_url}/api/chat",
            data=data,
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(
                req,
                timeout=self.timeout,
            ) as response:
                result = json.loads(
                    response.read().decode("utf-8")
                )

        except TimeoutError as exc:
            raise LLMTimeoutError(
                "Ollama generation timed out."
            ) from exc

        except error.HTTPError as exc:
            self._raise_http_error(exc, model)

        except error.URLError as exc:
            raise LLMConnectionError(
                "Could not connect to the local Ollama server."
            ) from exc

        except json.JSONDecodeError as exc:
            raise LLMGenerationError(
                "Invalid response received from Ollama."
            ) from exc

        content = result.get("message", {}).get("content")

        if not content:
            raise LLMGenerationError(
                "Ollama returned an empty response."
            )

        return content

    def generate_stream(
        self,
        messages: list[LLMMessage],
        model: str,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        """
        Stream response chunks from a local Ollama model.

        Yields only generated text chunks.

        Example:

            for chunk in client.generate_stream(...):
                print(chunk, end="", flush=True)
        """

        payload = self._build_payload(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        data = json.dumps(payload).encode("utf-8")

        req = request.Request(
            f"{self.base_url}/api/chat",
            data=data,
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            response = request.urlopen(
                req,
                timeout=self.timeout,
            )

        except TimeoutError as exc:
            raise LLMTimeoutError(
                "Ollama streaming generation timed out."
            ) from exc

        except error.HTTPError as exc:
            self._raise_http_error(exc, model)

        except error.URLError as exc:
            raise LLMConnectionError(
                "Could not connect to the local Ollama server."
            ) from exc

        try:
            for raw_line in response:
                line = raw_line.decode(
                    "utf-8",
                    errors="replace",
                ).strip()

                if not line:
                    continue

                try:
                    chunk = json.loads(line)

                except json.JSONDecodeError as exc:
                    raise LLMGenerationError(
                        "Invalid streaming response received from Ollama."
                    ) from exc

                if chunk.get("error"):
                    raise LLMGenerationError(
                        str(chunk["error"])
                    )

                message = chunk.get("message") or {}
                content = message.get("content")

                if content:
                    yield content

                if chunk.get("done"):
                    break

        except TimeoutError as exc:
            raise LLMTimeoutError(
                "Ollama streaming generation timed out."
            ) from exc

        except error.URLError as exc:
            raise LLMConnectionError(
                "Connection to Ollama was interrupted during streaming."
            ) from exc

        finally:
            response.close()

    def _build_payload(
        self,
        messages: list[LLMMessage],
        model: str,
        temperature: float,
        max_tokens: int | None,
        stream: bool,
    ) -> dict:
        """Build a request payload for Ollama."""

        if not model or not model.strip():
            raise ValueError(
                "Ollama model name cannot be empty."
            )

        if not messages:
            raise ValueError(
                "At least one LLM message is required."
            )

        payload = {
            "model": model,
            "messages": [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages
            ],
            "stream": stream,
            "options": {
                "temperature": temperature,
            },
        }

        if max_tokens is not None:
            if max_tokens <= 0:
                raise ValueError(
                    "max_tokens must be greater than zero."
                )

            payload["options"]["num_predict"] = max_tokens

        return payload

    def _raise_http_error(
        self,
        exc: error.HTTPError,
        model: str,
    ) -> None:
        """Convert Ollama HTTP errors into KARYA exceptions."""

        if exc.code == 404:
            raise LLMModelNotFoundError(
                f"Ollama model '{model}' was not found."
            ) from exc

        raise LLMGenerationError(
            f"Ollama returned HTTP {exc.code}."
        ) from exc