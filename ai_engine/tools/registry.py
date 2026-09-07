from __future__ import annotations

from typing import Any

from tools.calculator import CalculatorTool
from tools.file_reader import FileReaderTool
from tools.python import PythonTool
from tools.rag import RAGTool
from tools.schemas import ToolCall, ToolDefinition, ToolResult
from tools.search import SearchTool


class ToolRegistry:
    """
    Central registry for KARYA tools.

    The registry is responsible for:
    - registering tools
    - looking up tools
    - exposing tool definitions to the planner
    - executing tool calls
    - handling tool execution errors safely
    """

    def __init__(self, register_defaults: bool = True) -> None:
        self._tools: dict[str, Any] = {}

        if register_defaults:
            self._register_default_tools()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def _register_default_tools(self) -> None:
        """
        Register KARYA's built-in tools.
        """

        self.register(CalculatorTool())
        self.register(FileReaderTool())
        self.register(SearchTool())
        self.register(PythonTool())

        # RAG is lazily initialized internally, so registering it does
        # not immediately load the embedding model or database resources.
        self.register(RAGTool())

    def register(self, tool: Any) -> None:
        """
        Register a tool instance.
        """

        if tool is None:
            raise ValueError("tool cannot be None.")

        name = getattr(tool, "name", None)

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Tool must have a valid non-empty name.")

        normalized_name = name.strip().lower()

        if normalized_name in self._tools:
            raise ValueError(
                f"Tool '{normalized_name}' is already registered."
            )

        self._tools[normalized_name] = tool

    def unregister(self, tool_name: str) -> None:
        """
        Remove a tool from the registry.
        """

        normalized_name = self._normalize_name(tool_name)

        if normalized_name not in self._tools:
            raise KeyError(
                f"Tool '{normalized_name}' is not registered."
            )

        del self._tools[normalized_name]

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, tool_name: str) -> Any:
        """
        Return a registered tool.
        """

        normalized_name = self._normalize_name(tool_name)

        try:
            return self._tools[normalized_name]
        except KeyError as exc:
            raise KeyError(
                f"Tool '{normalized_name}' is not registered."
            ) from exc

    def has(self, tool_name: str) -> bool:
        """
        Check whether a tool exists.
        """

        normalized_name = self._normalize_name(tool_name)
        return normalized_name in self._tools

    def exists(self, tool_name: str) -> bool:
        """
        Alias used by the AgentExecutor.
        """

        return self.has(tool_name)

    # ------------------------------------------------------------------
    # Tool definitions
    # ------------------------------------------------------------------

    def list_tools(self) -> list[str]:
        """
        Return registered tool names.
        """

        return sorted(self._tools.keys())

    def definitions(self) -> list[ToolDefinition]:
        """
        Return definitions for all registered tools.
        """

        definitions: list[ToolDefinition] = []

        for name in self.list_tools():
            tool = self._tools[name]

            definition_method = getattr(tool, "definition", None)

            if not callable(definition_method):
                continue

            definition = definition_method()

            if not isinstance(definition, ToolDefinition):
                raise TypeError(
                    f"Tool '{name}' returned an invalid ToolDefinition."
                )

            definitions.append(definition)

        return definitions

    def get_definitions(self) -> list[ToolDefinition]:
        """
        Compatibility alias used by the Agent Planner.

        The planner needs a list of all available tools and their schemas.
        """

        return self.definitions()

    def get_definition(self, tool_name: str) -> ToolDefinition:
        """
        Return the definition for one specific tool.
        """

        tool = self.get(tool_name)

        definition_method = getattr(tool, "definition", None)

        if not callable(definition_method):
            raise ValueError(
                f"Tool '{tool_name}' does not provide a definition."
            )

        definition = definition_method()

        if not isinstance(definition, ToolDefinition):
            raise TypeError(
                f"Tool '{tool_name}' returned an invalid ToolDefinition."
            )

        return definition

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        tool_call: ToolCall | str,
        arguments: dict[str, Any] | None = None,
    ) -> ToolResult:
        """
        Execute a tool call.

        Supports both:

            registry.execute(ToolCall(...))

        and:

            registry.execute("calculator", {"expression": "2 + 2"})
        """

        if isinstance(tool_call, ToolCall):
            tool_name = tool_call.tool_name
            tool_arguments = tool_call.arguments
        elif isinstance(tool_call, str):
            tool_name = tool_call
            tool_arguments = arguments or {}
        else:
            return ToolResult(
                tool_name="unknown",
                success=False,
                output=None,
                error=(
                    "tool_call must be a ToolCall or a tool name string."
                ),
            )

        try:
            tool = self.get(tool_name)
        except (KeyError, ValueError, TypeError) as exc:
            return ToolResult(
                tool_name=str(tool_name),
                success=False,
                output=None,
                error=str(exc),
            )

        if not isinstance(tool_arguments, dict):
            return ToolResult(
                tool_name=str(tool_name),
                success=False,
                output=None,
                error="Tool arguments must be a dictionary.",
            )

        try:
            execute_with_input = getattr(
                tool,
                "execute_with_input",
                None,
            )

            if callable(execute_with_input):
                return execute_with_input(tool_arguments)

            return self._execute_standard_tool(
                tool,
                str(tool_name),
                tool_arguments,
            )

        except Exception as exc:
            return ToolResult(
                tool_name=str(tool_name),
                success=False,
                output=None,
                error=f"Tool execution failed: {exc}",
            )

    def _execute_standard_tool(
        self,
        tool: Any,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """
        Execute tools that expose an execute(**kwargs) interface.
        """

        execute_method = getattr(tool, "execute", None)

        if not callable(execute_method):
            return ToolResult(
                tool_name=tool_name,
                success=False,
                output=None,
                error=(
                    f"Tool '{tool_name}' does not provide "
                    "an executable interface."
                ),
            )

        try:
            output = execute_method(**arguments)

            if isinstance(output, ToolResult):
                return output

            return ToolResult(
                tool_name=tool_name,
                success=True,
                output=output,
                error=None,
            )

        except Exception as exc:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                output=None,
                error=str(exc),
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_name(tool_name: str) -> str:
        if not isinstance(tool_name, str):
            raise TypeError("tool_name must be a string.")

        normalized_name = tool_name.strip().lower()

        if not normalized_name:
            raise ValueError("tool_name cannot be empty.")

        return normalized_name


def create_default_registry() -> ToolRegistry:
    """
    Create a registry containing all standard KARYA tools.
    """

    return ToolRegistry(register_defaults=True)