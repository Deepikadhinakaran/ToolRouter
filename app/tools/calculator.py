"""Calculator tool — evaluates arithmetic expressions safely (no eval())."""
import ast
import operator
import re

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_node(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants are allowed")
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


def safe_eval(expression: str) -> float:
    tree = ast.parse(expression, mode="eval")
    return _eval_node(tree.body)


TOOL_META = {
    "name": "calculator",
    "description": "Evaluate a mathematical expression, e.g. '25 * 18'.",
    "capabilities": ["math", "arithmetic", "calculation", "number"],
    "min_role": "guest",
    "risk": "low",
    "cost": 0.0,
    "avg_latency_ms": 5,
    # Catches numeric expressions the keyword matcher would miss, e.g.
    # "What is 25 * 10?" has no word stemming to "calculat...".
    "pattern": r"\d+\s*[\+\-*/xX%^]\s*\d+|\d+\s*(plus|minus|times|divided by|multiplied by)\s*\d+",
}


_EXPR_PATTERN = re.compile(r"[-+]?\d[\d\s+\-*/().%^]*\d|[-+]?\d")


def _extract_expression(text: str) -> str:
    """Pull the arithmetic-looking substring out of a natural-language
    query, e.g. 'Calculate 500 / 25' -> '500 / 25'."""
    text = text.replace("x", "*").replace("X", "*")
    match = _EXPR_PATTERN.search(text)
    return match.group(0).strip() if match else text


def run(query: str, expression: str | None = None) -> dict:
    expr = expression or _extract_expression(query)
    try:
        result = safe_eval(expr)
        return {"status": "success", "result": str(result)}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "result": f"Invalid expression: {exc}"}
