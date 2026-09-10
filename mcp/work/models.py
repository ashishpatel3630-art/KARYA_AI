from dataclasses import dataclass, field
from typing import Set


@dataclass
class WorkPolicy:
    work_id: str
    allowed_tools: Set[str] = field(default_factory=set)
    denied_tools: Set[str] = field(default_factory=set)

    def is_tool_allowed(self, tool_name: str) -> bool:
        if tool_name in self.denied_tools:
            return False

        return tool_name in self.allowed_tools