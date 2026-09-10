"""Central registry mapping tool name -> metadata + executable function.

Adding a new tool later means: write app/tools/<name>.py with TOOL_META + run(),
then register it here. Nothing else in the framework needs to change.
"""
from app.tools import calculator, database, rag, search

REGISTRY = {
    calculator.TOOL_META["name"]: {"meta": calculator.TOOL_META, "run": calculator.run},
    database.TOOL_META["name"]: {"meta": database.TOOL_META, "run": database.run},
    rag.TOOL_META["name"]: {"meta": rag.TOOL_META, "run": rag.run},
    search.TOOL_META["name"]: {"meta": search.TOOL_META, "run": search.run},
}


def all_tools() -> list[dict]:
    return [entry["meta"] for entry in REGISTRY.values()]


def get_tool(name: str) -> dict | None:
    return REGISTRY.get(name)
