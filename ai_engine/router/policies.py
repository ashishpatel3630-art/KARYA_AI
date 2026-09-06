from dataclasses import dataclass


@dataclass
class RoutingPolicy:
    """Defines which model capability is required for a task."""

    task_type: str
    model_type: str
    requires_vision: bool = False
    requires_tools: bool = False


TEXT_POLICY = RoutingPolicy(
    task_type="text",
    model_type="text",
)

VISION_POLICY = RoutingPolicy(
    task_type="vision",
    model_type="vision",
    requires_vision=True,
)

TOOL_POLICY = RoutingPolicy(
    task_type="tool",
    model_type="text",
    requires_tools=True,
)
