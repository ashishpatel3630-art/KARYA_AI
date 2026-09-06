
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolDefinition:
    """Describes a tool available to the KARYA agent."""

    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass
class ToolCall:
    """Represents a request from the agent to execute a tool."""

    tool_name: str
    arguments: dict[str, Any]


@dataclass
class ToolResult:
    """Represents the result returned after tool execution."""

    tool_name: str
    success: bool
    output: Any
    error: str | None = None

