from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sandbox.executor import SandboxExecutor
from tools.permissions import (
    PermissionManager,
    PermissionLevel,
)
from tools.schemas import (
    ToolDefinition,
    ToolResult,
)


@dataclass
class PythonTool:
    """
    Safe Python execution tool for KARYA.

    Python code is never executed directly by this tool.
    All code is passed through the SandboxExecutor.
    """

    sandbox: SandboxExecutor | None = None
    permissions: PermissionManager | None = None

    name: str = "python"
    description: str = (
        "Execute safe Python code inside the KARYA sandbox. "
        "The code is security-validated and resource-limited "
        "before execution."
    )

    def __post_init__(self) -> None:
        if self.sandbox is None:
            self.sandbox = SandboxExecutor()

        if self.permissions is None:
            self.permissions = PermissionManager()

    def definition(self) -> ToolDefinition:
        """
        Return the tool definition used by the Tool Registry / Agent.
        """

        return ToolDefinition(
            name=self.name,
            description=self.description,
            input_schema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": (
                            "Python code to execute safely "
                            "inside the sandbox."
                        ),
                    }
                },
                "required": ["code"],
                "additionalProperties": False,
            },
        )

    def execute(
        self,
        code: str,
    ) -> ToolResult:
        """
        Execute Python code through the sandbox.

        Permission flow:
            PythonTool
                ↓
            EXECUTE permission
                ↓
            SandboxExecutor
                ↓
            Security validation
                ↓
            Resource-limited execution
        """

        if not isinstance(code, str):
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Python code must be a string.",
            )

        code = code.strip()

        if not code:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Python code cannot be empty.",
            )

        # ---------------------------------------------------------
        # Permission check
        # ---------------------------------------------------------

        if self.permissions is None:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Permission manager is not configured.",
            )

        permission_result = self.permissions.check(
            PermissionLevel.EXECUTE
        )

        if not permission_result.allowed:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error=permission_result.reason,
            )

        # ---------------------------------------------------------
        # Sandbox execution
        # ---------------------------------------------------------

        if self.sandbox is None:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Sandbox executor is not configured.",
            )

        try:
            result = self.sandbox.execute(code)

        except Exception as exc:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error=f"Sandbox execution failed: {exc}",
            )

        # ---------------------------------------------------------
        # Convert SandboxResult → ToolResult
        # ---------------------------------------------------------

        if result.success:
            return ToolResult(
                tool_name=self.name,
                success=True,
                output=result.output,
                error=None,
            )

        error_message = result.error or "Python execution failed."

        if result.timed_out:
            error_message = (
                "Python execution timed out. "
                f"{error_message}"
            )

        return ToolResult(
            tool_name=self.name,
            success=False,
            output=result.output,
            error=error_message,
        )

    def validate(
        self,
        code: str,
    ) -> tuple[bool, str | None]:
        """
        Validate Python code without executing it.

        Returns:
            (True, None) when valid.
            (False, error_message) when invalid.
        """

        if not isinstance(code, str):
            return False, "Python code must be a string."

        code = code.strip()

        if not code:
            return False, "Python code cannot be empty."

        if self.permissions is None:
            return False, "Permission manager is not configured."

        permission_result = self.permissions.check(
            PermissionLevel.EXECUTE
        )

        if not permission_result.allowed:
            return False, permission_result.reason

        if self.sandbox is None:
            return False, "Sandbox executor is not configured."

        try:
            security_result = self.sandbox.validate(code)
        except Exception as exc:
            return False, f"Sandbox validation failed: {exc}"

        if not security_result.allowed:
            return False, security_result.reason

        return True, None

    def execute_with_input(
        self,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """
        Execute the tool using ToolRegistry-style arguments.

        Expected format:

            {
                "code": "print(2 + 2)"
            }
        """

        if not isinstance(arguments, dict):
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Tool arguments must be a dictionary.",
            )

        code = arguments.get("code")

        if code is None:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Missing required argument: code.",
            )

        if not isinstance(code, str):
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="The 'code' argument must be a string.",
            )

        return self.execute(code)
