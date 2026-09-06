
import ast
import operator


class CalculatorTool:
    """Safe local calculator tool for KARYA agents."""

    name = "calculator"

    description = (
        "Performs basic mathematical calculations "
        "using numbers and arithmetic operators."
    )

    input_schema = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to calculate.",
            }
        },
        "required": ["expression"],
    }

    ALLOWED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def execute(self, expression: str) -> float:
        """Evaluate a mathematical expression safely."""

        if not expression or not expression.strip():
            raise ValueError(
                "Calculator expression cannot be empty."
            )

        expression = expression.strip()

        try:
            tree = ast.parse(
                expression,
                mode="eval",
            )

        except SyntaxError as exc:
            raise ValueError(
                "Invalid mathematical expression."
            ) from exc

        return self._evaluate(tree.body)

    def _evaluate(self, node: ast.AST) -> float:
        """Recursively evaluate a safe AST expression."""

        if isinstance(node, ast.Constant):

            if isinstance(node.value, bool):
                raise ValueError(
                    "Boolean values are not allowed."
                )

            if isinstance(node.value, (int, float)):
                return node.value

            raise ValueError(
                "Only numeric values are allowed."
            )

        if isinstance(node, ast.BinOp):

            operator_function = self.ALLOWED_OPERATORS.get(
                type(node.op)
            )

            if operator_function is None:
                raise ValueError(
                    "Unsupported mathematical operator."
                )

            left = self._evaluate(node.left)
            right = self._evaluate(node.right)

            try:
                return operator_function(
                    left,
                    right,
                )

            except ZeroDivisionError as exc:
                raise ValueError(
                    "Division by zero is not allowed."
                ) from exc

        if isinstance(node, ast.UnaryOp):

            operator_function = self.ALLOWED_OPERATORS.get(
                type(node.op)
            )

            if operator_function is None:
                raise ValueError(
                    "Unsupported unary operator."
                )

            operand = self._evaluate(
                node.operand
            )

            return operator_function(
                operand
            )

        raise ValueError(
            "Unsupported expression."
        )