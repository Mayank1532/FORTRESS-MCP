"""Safe deterministic calculator tool."""

import ast
from collections.abc import Mapping

Numeric = int | float


class CalculatorTool:
    """Evaluate a deliberately restricted arithmetic expression."""

    name = "calculator_read"

    def execute(self, arguments: Mapping[str, object]) -> object:
        """Validate and evaluate an arithmetic expression."""
        expression = arguments.get("expression")

        if not isinstance(expression, str):
            raise ValueError("expression must be a string")

        if len(expression) > 200:
            raise ValueError("expression is too long")

        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as exc:
            raise ValueError("invalid arithmetic expression") from exc

        return self._evaluate(tree.body)

    def _evaluate(self, node: ast.AST) -> Numeric:
        """Evaluate only explicitly approved arithmetic AST nodes."""

        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                raise ValueError("boolean values are not allowed")

            if isinstance(node.value, (int, float)):
                return node.value

            raise ValueError("only numeric constants are allowed")

        if isinstance(node, ast.UnaryOp):
            value = self._evaluate(node.operand)

            if isinstance(node.op, ast.USub):
                result = -value
            elif isinstance(node.op, ast.UAdd):
                result = +value
            else:
                raise ValueError("unsupported unary operator")

            self._validate_result(result)
            return result

        if isinstance(node, ast.BinOp):
            left = self._evaluate(node.left)
            right = self._evaluate(node.right)

            if isinstance(node.op, ast.Add):
                result = left + right
            elif isinstance(node.op, ast.Sub):
                result = left - right
            elif isinstance(node.op, ast.Mult):
                result = left * right
            elif isinstance(node.op, ast.Div):
                if right == 0:
                    raise ValueError("division by zero is not allowed")
                result = left / right
            elif isinstance(node.op, ast.Mod):
                if right == 0:
                    raise ValueError("modulo by zero is not allowed")
                result = left % right
            elif isinstance(node.op, ast.Pow):
                if abs(right) > 10:
                    raise ValueError("exponent is too large")
                result = left**right
            else:
                raise ValueError("unsupported binary operator")

            self._validate_result(result)
            return result

        raise ValueError("unsupported calculator expression")

    @staticmethod
    def _validate_result(result: Numeric) -> None:
        """Prevent unreasonably large calculator results."""
        if abs(result) > 1e12:
            raise ValueError("result is too large")
