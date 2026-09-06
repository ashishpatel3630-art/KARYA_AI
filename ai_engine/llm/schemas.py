from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMMessage:
    role: str
    content: str


@dataclass
class LLMRequest:
    messages: list[LLMMessage]
    model: Optional[str] = None
    temperature: float = 0.2
    max_tokens: Optional[int] = None


@dataclass
class LLMResponse:
    content: str
    model: str
