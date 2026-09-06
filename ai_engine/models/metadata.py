from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelMetadata:
    """Metadata describing a local AI model."""

    name: str
    provider: str
    model_type: str
    description: str = ""
    context_window: Optional[int] = None
    supports_tools: bool = False
    supports_vision: bool = False
    supports_streaming: bool = True
