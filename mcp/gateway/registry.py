from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class ToolDefinition:
    name: str
    server: str
    description: str
    handler: Callable[..., Any]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(
        self,
        *,
        name: str,
        server: str,
        description: str,
        handler: Callable[..., Any],
    ) -> None:

        key = f"{server}.{name}"

        if key in self._tools:
            raise ValueError(f"Tool already registered: {key}")

        self._tools[key] = ToolDefinition(
            name=name,
            server=server,
            description=description,
            handler=handler,
        )

    def get(self, server: str, tool: str) -> ToolDefinition | None:
        return self._tools.get(f"{server}.{tool}")

    def list_tools(self) -> list[dict]:
        return [
            {
                "name": item.name,
                "server": item.server,
                "description": item.description,
            }
            for item in self._tools.values()
        ]


registry = ToolRegistry()