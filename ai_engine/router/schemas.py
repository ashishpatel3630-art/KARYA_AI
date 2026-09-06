from dataclasses import dataclass
from typing import Optional


@dataclass
class RouteResult:
    """Result produced by KARYA's model router."""

    task_type: str
    selected_model: Optional[str]
    model_type: str
    requires_vision: bool
    requires_tools: bool
    reason: str
