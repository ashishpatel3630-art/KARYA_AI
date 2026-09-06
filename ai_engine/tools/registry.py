
from typing import Any

from .calculator import CalculatorTool
from .file_reader import FileReaderTool
from .schemas import ToolCall, ToolDefinition, ToolResult
from .search import SearchTool


class ToolRegistry:
    """Central registry for all tools available to KARYA."""

    def __init__(self):
        self._tools: dict[str, Any] = {}

    def register(self, tool: Any) -> None:
        """Register a tool using its name."""

        if not hasattr(tool, "name"):
            raise ValueError(
                "Tool must define a 'name' attribute."
            )

        if not hasattr(tool, "description"):
            raise ValueError(
                "Tool must define a 'description' attribute."
            )

        if not hasattr(tool, "execute"):
            raise ValueError(
                "Tool must define an 'execute' method."
            )

        tool_name = tool.name

        if tool_name in self._tools:
            raise ValueError(
                f"Tool '{tool_name}' is already registered."
            )

        self._tools[tool_name] = tool

    def get(self, tool_name: str) -> Any | None:
        """Return a registered tool by name."""

        return self._tools.get(tool_name)

    def exists(self, tool_name: str) -> bool:
        """Check whether a tool is registered."""

        return tool_name in self._tools

    def list_tools(self) -> list[str]:
        """Return names of all registered tools."""

        return list(self._tools.keys())

    def get_definitions(self) -> list[ToolDefinition]:
        """Return standardized definitions for all tools."""

        definitions = []

        for tool in self._tools.values():
            input_schema = getattr(
                tool,
                "input_schema",
                {},
            )

            definitions.append(
                ToolDefinition(
                    name=tool.name,
                    description=tool.description,
                    input_schema=input_schema,
                )
            )

        return definitions

    def execute(
        self,
        tool_call: ToolCall,
    ) -> ToolResult:
        """Execute a tool call through the registry."""

        tool = self.get(tool_call.tool_name)

        if tool is None:
            return ToolResult(
                tool_name=tool_call.tool_name,
                success=False,
                output=None,
                error=(
                    f"Tool '{tool_call.tool_name}' "
                    f"is not registered."
                ),
            )

        try:
            output = tool.execute(
                **tool_call.arguments
            )

            return ToolResult(
                tool_name=tool_call.tool_name,
                success=True,
                output=output,
            )

        except Exception as exc:
            return ToolResult(
                tool_name=tool_call.tool_name,
                success=False,
                output=None,
                error=str(exc),
            )


def create_default_registry() -> ToolRegistry:
    """Create a registry containing KARYA's default tools."""

    registry = ToolRegistry()

    registry.register(
        CalculatorTool()
    )

    registry.register(
        FileReaderTool()
    )

    registry.register(
        SearchTool()
    )

    return registry
