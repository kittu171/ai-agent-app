import ast
import operator

from langchain_core.tools import tool


# -----------------------------
# Safe Calculator
# -----------------------------

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_calculate(node):

    if isinstance(node, ast.Constant):

        if isinstance(node.value, (int, float)):
            return node.value

        raise ValueError("Only numbers are allowed.")

    if isinstance(node, ast.BinOp):

        left = _safe_calculate(node.left)
        right = _safe_calculate(node.right)

        operator_function = _ALLOWED_OPERATORS.get(
            type(node.op)
        )

        if operator_function is None:
            raise ValueError("Operator not allowed.")

        return operator_function(left, right)

    if isinstance(node, ast.UnaryOp):

        operand = _safe_calculate(node.operand)

        operator_function = _ALLOWED_OPERATORS.get(
            type(node.op)
        )

        if operator_function is None:
            raise ValueError("Operator not allowed.")

        return operator_function(operand)

    raise ValueError("Invalid mathematical expression.")


@tool
def calculator(expression: str) -> str:
    """
    Safely calculate a mathematical expression.
    """

    try:
        
        tree = ast.parse(
            expression,
            mode="eval"
        )

        result = _safe_calculate(tree.body)

        return str(result)

    except Exception as e:

        return f"CALCULATION_ERROR: {str(e)}"

# -----------------------------
# Knowledge Search Tool
# -----------------------------

@tool
def knowledge_search(question: str) -> str:
    """
    Search the local knowledge base for information about
    Generative AI, RAG, embeddings, LangGraph, and AI agents.
    """

    from knowledge_tool import search_knowledge

    return search_knowledge(question)