class LLMError(Exception):
    """Base exception for all KARYA LLM errors."""


class LLMConnectionError(LLMError):
    """Raised when the local LLM runtime cannot be reached."""


class LLMGenerationError(LLMError):
    """Raised when the LLM fails during generation."""


class LLMTimeoutError(LLMError):
    """Raised when LLM generation exceeds the allowed timeout."""


class LLMModelNotFoundError(LLMError):
    """Raised when the requested model is unavailable."""
