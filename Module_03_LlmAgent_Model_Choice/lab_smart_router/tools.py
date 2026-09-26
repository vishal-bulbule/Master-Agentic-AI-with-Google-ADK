# Author: Vishal Bulbule
# Date: 2026-09-22

"""Shared `compute` tool used by both the Flash and the Pro agent.

The lab keeps the tool identical and varies only the model, so any difference
in the results comes from the model.

The expression is parsed with `ast` and only numbers and arithmetic operators
are evaluated. `eval` is avoided because even a character whitelist lets
through inputs like `9**9**9**9`, which would hang the process.
"""

import ast
import operator

_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_MAX_EXPONENT = 100


def _evaluate(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_evaluate(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPS:
        left, right = _evaluate(node.left), _evaluate(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > _MAX_EXPONENT:
            raise ValueError(f"exponent larger than {_MAX_EXPONENT}")
        return _BINARY_OPS[type(node.op)](left, right)
    raise ValueError("only numbers and + - * / % ** are allowed")


def compute(expression: str) -> dict:
    """Evaluates a basic arithmetic expression exactly.

    Args:
        expression: A math expression like "12 * (3 + 4)". Only numbers,
            parentheses, and the operators + - * / % ** are allowed.

    Returns:
        A dict with `status` "success" plus `expression` and `result`, or
        `status` "error" with an `error_message` for invalid input.
    """
    try:
        result = _evaluate(ast.parse(expression, mode="eval").body)
    except (SyntaxError, ValueError, ZeroDivisionError) as exc:
        return {"status": "error", "error_message": f"Could not evaluate: {exc}"}
    return {"status": "success", "expression": expression, "result": result}
