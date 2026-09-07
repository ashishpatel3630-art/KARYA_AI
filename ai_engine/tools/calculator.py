from __future__ import annotations

import ast
import operator
from dataclasses import dataclass
from typing import Any

from tools.schemas import ToolDefinition, ToolResult


@dataclass
class CalculatorTool:
    """
    Safe mathematical calculator for KARYA.

    Expressions are parsed using Python's AST instead of eval().
    Only explicitly allowed mathematical operations are supported.
    """

    name: str = "calculator"

    description: str = (
        "Perform safe mathematical calculations using numbers, "
        "arithmetic operators, comparisons, and parentheses."
    )

    _binary_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    _unary_operators = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def definition(self) -> ToolDefinition:
        """
        Return the tool definition used by the registry and agent.
        """

        return ToolDefinition(
            name=self.name,
            description=self.description,
            input_schema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "A mathematical expression such as "
                            "'25 * 4 + 10' or '(100 - 20) / 4'."
                        ),
                    }
                },
                "required": ["expression"],
                "additionalProperties": False,
            },
        )

    def execute(
        self,
        expression: str,
    ) -> ToolResult:
        """
        Evaluate a mathematical expression safely.
        """

        if not isinstance(expression, str):
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Expression must be a string.",
            )

        expression = expression.strip()

        if not expression:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Expression cannot be empty.",
            )

        try:
            tree = ast.parse(
                expression,
                mode="eval",
            )

        except SyntaxError as exc:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error=f"Invalid mathematical expression: {exc}",
            )

        self._validate_ast(tree.body)

        try:
            result = self._evaluate(tree.body)

        except ZeroDivisionError:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Division by zero is not allowed.",
            )

        except (ValueError, TypeError, OverflowError) as exc:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error=str(exc),
            )

        except Exception as exc:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error=f"Calculation failed: {exc}",
            )

        return ToolResult(
            tool_name=self.name,
            success=True,
            output=result,
            error=None,
        )

    def execute_with_input(
        self,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """
        Execute using ToolRegistry-style arguments.

        Expected:

            {
                "expression": "25 * 4"
            }
        """

        if not isinstance(arguments, dict):
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Tool arguments must be a dictionary.",
            )

        expression = arguments.get("expression")

        if expression is None:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output=None,
                error="Missing required argument: expression.",
            )

        return self.execute(expression)

    def validate(
        self,
        expression: str,
    ) -> tuple[bool, str | None]:
        """
        Validate an expression without executing it.
        """

        if not isinstance(expression, str):
            return False, "Expression must be a string."

        expression = expression.strip()

        if not expression:
            return False, "Expression cannot be empty."

        try:
            tree = ast.parse(
                expression,
                mode="eval",
            )
            self._validate_ast(tree.body)

        except (SyntaxError, ValueError, TypeError) as exc:
            return False, str(exc)

        return True, None

    def _validate_ast(
        self,
        node: ast.AST,
    ) -> None:
        """
        Validate that the AST contains only safe calculator nodes.
        """

        allowed_nodes = (
            ast.Expression,
            ast.Constant,
            ast.BinOp,
            ast.UnaryOp,
            ast.Add,
            ast.Sub,
            ast.Mult,
            ast.Div,
            ast.FloorDiv,
            ast.Mod,
            ast.Pow,
            ast.UAdd,
            ast.USub,
        )

        if not isinstance(node, allowed_nodes):
            raise ValueError(
                f"Unsupported calculator operation: "
                f"{type(node).__name__}"
            )

        if isinstance(node, ast.Constant):
            if not isinstance(
                node.value,
                (int, float),
            ) or isinstance(node.value, bool):
                raise ValueError(
                    "Only numeric values are allowed."
                )

            return

        if isinstance(node, ast.BinOp):
            if type(node.op) not in self._binary_operators:
                raise ValueError(
                    f"Unsupported binary operator: "
                    f"{type(node.op).__name__}"
                )

            self._validate_ast(node.left)
            self._validate_ast(node.right)
            return

        if isinstance(node, ast.UnaryOp):
            if type(node.op) not in self._unary_operators:
                raise ValueError(
                    f"Unsupported unary operator: "
                    f"{type(node.op).__name__}"
                )

            self._validate_ast(node.operand)
            return

    def _evaluate(
        self,
        node: ast.AST,
    ) -> int | float:
        """
        Recursively evaluate a validated AST.
        """

        self._validate_ast(node)

        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.BinOp):
            operation = self._binary_operators[type(node.op)]

            left = self._evaluate(node.left)
            right = self._evaluate(node.right)

            # Prevent extremely large exponentiation.
            if isinstance(node.op, ast.Pow):
                if abs(right) > 100:
                    raise ValueError(
                        "Exponent is too large."
                    )

                if abs(left) > 1_000_000:
                    raise ValueError(
                        "Base is too large for exponentiation."
                    )

            return operation(left, right)

        if isinstance(node, ast.UnaryOp):
            operation = self._unary_operators[type(node.op)]

            operand = self._evaluate(node.operand)

            return operation(operand)

        raise ValueError(
            f"Unsupported AST node: {type(node).__name__}"
        )