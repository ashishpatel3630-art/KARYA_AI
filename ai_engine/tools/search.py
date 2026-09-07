from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tools.schemas import ToolDefinition, ToolResult


@dataclass
class SearchTool:
    """
    Local search tool for KARYA.

    This tool intentionally performs only local filesystem
    search. It does not make external network requests.

    This is important for KARYA's sovereign / air-gapped design.
    """

    name: str = "search"

    description: str = (
        "Search local files and directories by filename. "
        "No external network access is performed."
    )

    def definition(self) -> ToolDefinition:
        """Return the tool definition."""

        return ToolDefinition(
            name=self.name,
            description=self.description,
            input_schema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": (
                            "Directory to search."
                        ),
                    },
                    "query": {
                        "type": "string",
                        "description": (
                            "Text to search for in filenames."
                        ),
                    },
                    "max_results": {
                        "type": "integer",
                        "description": (
                            "Maximum number of results."
                        ),
                        "minimum": 1,
                        "maximum": 100,
                    },
                },
                "required": [
                    "directory",
                    "query",
                ],
                "additionalProperties": False,
            },
        )

    def execute(
        self,
        directory: str,
        query: str,
        max_results: int = 20,
    ) -> ToolResult:
        """Search a local directory."""

        if not isinstance(directory, str):
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="directory must be a string.",
            )

        if not isinstance(query, str):
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="query must be a string.",
            )

        directory = directory.strip()
        query = query.strip()

        if not directory:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="directory cannot be empty.",
            )

        if not query:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="query cannot be empty.",
            )

        if not isinstance(max_results, int):
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="max_results must be an integer.",
            )

        if max_results < 1:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="max_results must be at least 1.",
            )

        if max_results > 100:
            max_results = 100

        root = __import__("pathlib").Path(directory)

        if not root.exists():
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error=f"Directory not found: {root}",
            )

        if not root.is_dir():
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error=f"Path is not a directory: {root}",
            )

        query_lower = query.lower()

        results: list[str] = []

        try:
            for path in root.rglob("*"):
                if not path.is_file():
                    continue

                if query_lower in path.name.lower():
                    results.append(str(path))

                if len(results) >= max_results:
                    break

        except PermissionError as exc:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error=f"Permission denied while searching: {exc}",
            )

        return ToolResult(
            tool_name=self.name,
            success=True,
            output=results,
            error=None,
        )

    def execute_with_input(
        self,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """Execute using ToolRegistry-style arguments."""

        if not isinstance(arguments, dict):
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Tool arguments must be a dictionary.",
            )

        directory = arguments.get("directory")
        query = arguments.get("query")
        max_results = arguments.get(
            "max_results",
            20,
        )

        if directory is None:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Missing required argument: directory.",
            )

        if query is None:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Missing required argument: query.",
            )

        return self.execute(
            directory=directory,
            query=query,
            max_results=max_results,
        )