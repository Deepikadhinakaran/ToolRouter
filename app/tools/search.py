"""Generic/web search tool — stubbed so the project has no external search
API dependency. Swap the body of run() for a real search API later."""

TOOL_META = {
    "name": "search",
    "description": "General-purpose fallback search for anything not covered by other tools.",
    "capabilities": ["general", "fallback", "web"],
    "min_role": "guest",
    "risk": "low",
    "cost": 0.0,
    "avg_latency_ms": 50,
}


def run(query: str) -> dict:
    return {
        "status": "success",
        "result": f"(mock) Top result for '{query}': no external search API is wired up yet.",
    }
