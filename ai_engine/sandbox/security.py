import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class SecurityCheckResult:
    """Result of sandbox code security validation."""

    allowed: bool
    reason: str = ""


class SandboxSecurity:
    """
    Static security validator for Python code.

    This validator is intentionally conservative.

    It rejects:
    - imports
    - dangerous builtins
    - filesystem access
    - subprocess execution
    - networking
    - dynamic code execution
    - dangerous Python attributes

    This is one layer of defense only.
    The actual execution must still happen inside the sandbox
    process with resource limits.
    """

    BLOCKED_IMPORTS = {
        "os",
        "sys",
        "subprocess",
        "socket",
        "shutil",
        "pathlib",
        "requests",
        "httpx",
        "urllib",
        "urllib3",
        "ftplib",
        "telnetlib",
        "ctypes",
        "multiprocessing",
        "threading",
        "asyncio",
        "signal",
        "resource",
        "pickle",
        "marshal",
        "importlib",
        "builtins",
    }

    BLOCKED_FUNCTIONS = {
        "eval",
        "exec",
        "compile",
        "__import__",
        "open",
        "input",
        "breakpoint",
        "globals",
        "locals",
        "vars",
        "getattr",
        "setattr",
        "delattr",
    }

    BLOCKED_ATTRIBUTES = {
        "__class__",
        "__bases__",
        "__base__",
        "__subclasses__",
        "__globals__",
        "__builtins__",
        "__code__",
        "__closure__",
        "__func__",
        "__self__",
        "__module__",
        "__dict__",
    }

    ALLOWED_IMPORTS = {
        "math",
        "statistics",
        "decimal",
        "fractions",
        "datetime",
        "json",
        "re",
        "random",
        "itertools",
        "functools",
        "collections",
    }

    def validate(self, code: str) -> SecurityCheckResult:
        """
        Validate Python source code before execution.
        """

        if not isinstance(code, str):
            return SecurityCheckResult(
                allowed=False,
                reason="Code must be a string.",
            )

        if not code.strip():
            return SecurityCheckResult(
                allowed=False,
                reason="Code cannot be empty.",
            )

        try:
            tree = ast.parse(code, mode="exec")
        except SyntaxError as exc:
            return SecurityCheckResult(
                allowed=False,
                reason=f"Invalid Python syntax: {exc.msg}.",
            )

        for node in ast.walk(tree):
            result = self._check_node(node)

            if not result.allowed:
                return result

        return SecurityCheckResult(
            allowed=True,
            reason="Code passed sandbox security validation.",
        )

    def is_allowed(self, code: str) -> bool:
        """Return True when code passes validation."""
        return self.validate(code).allowed

    def _check_node(self, node: ast.AST) -> SecurityCheckResult:
        """Validate one AST node."""

        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return self._check_import(node)

        if isinstance(node, ast.Call):
            return self._check_call(node)

        if isinstance(node, ast.Attribute):
            if node.attr in self.BLOCKED_ATTRIBUTES:
                return SecurityCheckResult(
                    allowed=False,
                    reason=f"Blocked attribute access: {node.attr}",
                )

        if isinstance(node, ast.Name):
            if node.id in self.BLOCKED_FUNCTIONS:
                return SecurityCheckResult(
                    allowed=False,
                    reason=f"Blocked name: {node.id}",
                )

        return SecurityCheckResult(allowed=True)

    def _check_import(
        self,
        node: ast.Import | ast.ImportFrom,
    ) -> SecurityCheckResult:
        """Validate import statements."""

        if isinstance(node, ast.Import):
            module_names = [alias.name for alias in node.names]
        else:
            module_names = [node.module or ""]

        for module_name in module_names:
            root_module = module_name.split(".")[0]

            if root_module in self.BLOCKED_IMPORTS:
                return SecurityCheckResult(
                    allowed=False,
                    reason=f"Blocked import: {module_name}",
                )

            if root_module not in self.ALLOWED_IMPORTS:
                return SecurityCheckResult(
                    allowed=False,
                    reason=f"Import not allowed: {module_name}",
                )

        return SecurityCheckResult(allowed=True)

    def _check_call(self, node: ast.Call) -> SecurityCheckResult:
        """Validate function calls."""

        if isinstance(node.func, ast.Name):
            function_name = node.func.id

            if function_name in self.BLOCKED_FUNCTIONS:
                return SecurityCheckResult(
                    allowed=False,
                    reason=f"Blocked function call: {function_name}",
                )

        if isinstance(node.func, ast.Attribute):
            if node.func.attr in self.BLOCKED_FUNCTIONS:
                return SecurityCheckResult(
                    allowed=False,
                    reason=f"Blocked method call: {node.func.attr}",
                )

        return SecurityCheckResult(allowed=True)