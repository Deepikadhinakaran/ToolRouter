"""ToolRouter: scores every registered tool against a query and picks the
best-matching one.

score = capability_match + relevance + pattern_bonus
        - risk_penalty - cost_penalty - latency_penalty

Permission is deliberately NOT a hard gate here. The router picks the tool
that best fits the *query* -- e.g. a guest asking "find employee 105" should
still route to `database`, because that's genuinely the right tool for the
question. Whether the caller is *allowed* to use it is a separate concern,
enforced by the check_permission step downstream (app/security.py). Baking
permission into tool selection would silently reroute denied requests to a
fallback tool instead of surfacing a real "permission denied" -- which
defeats the point of having a guardrail step at all.
"""
import re

from app.registry import all_tools
from app.security import RISK_SCORE, has_permission

W_CAPABILITY = 2.0
W_RELEVANCE = 1.0
W_PATTERN = 3.0
W_RISK = 1.0
W_COST = 5.0        # cost is in $, small numbers -> scale up
W_LATENCY = 0.002   # latency is in ms -> scale down

_STEM_LEN = 6

# Words too generic to carry routing signal (question words, articles, etc).
# Filtering these out stops e.g. "the" in a query from spuriously matching
# "the" inside a tool's description and dragging in the wrong tool.
_STOPWORDS = {
    "what", "is", "are", "the", "a", "an", "of", "for", "to", "on", "in",
    "and", "how", "do", "does", "can", "i", "my", "please", "tell", "me",
    "about", "with", "this", "that", "it", "you", "get", "give", "show",
}


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z]+", text.lower()) if t not in _STOPWORDS}


def _stems(tokens: set[str]) -> set[str]:
    """Crude stemmer: first N chars of each token, so 'calculate' and
    'calculation' collapse to the same stem without a real NLP dependency."""
    return {t[:_STEM_LEN] if len(t) > _STEM_LEN else t for t in tokens}


def _overlap(a: set[str], b: set[str]) -> int:
    return len(_stems(a) & _stems(b))


def score_tool(query: str, tool_meta: dict, role: str) -> dict:
    query_tokens = _tokenize(query)
    capability_tokens = _tokenize(" ".join(tool_meta["capabilities"]))
    description_tokens = _tokenize(tool_meta["description"])

    capability_match = _overlap(query_tokens, capability_tokens)
    relevance = _overlap(query_tokens, description_tokens)

    pattern = tool_meta.get("pattern")
    pattern_hit = bool(pattern and re.search(pattern, query, re.IGNORECASE))

    risk_penalty = 1 - RISK_SCORE.get(tool_meta["risk"], 0.5)
    cost_penalty = tool_meta["cost"]
    latency_penalty = tool_meta["avg_latency_ms"]

    score = (
        W_CAPABILITY * capability_match
        + W_RELEVANCE * relevance
        + (W_PATTERN if pattern_hit else 0)
        - W_RISK * risk_penalty
        - W_COST * cost_penalty
        - W_LATENCY * latency_penalty
    )
    return {
        "tool": tool_meta["name"],
        "eligible": has_permission(role, tool_meta),
        "score": round(score, 4),
        "capability_match": capability_match,
        "relevance": relevance,
        "pattern_hit": pattern_hit,
    }


def route(query: str, role: str) -> dict:
    """Return the best-matching tool for this query, plus full scoring for
    transparency/debugging. `eligible` on each candidate reflects the
    caller's permission but does NOT affect which tool is selected -- that's
    enforced later by the permission-check step."""
    scored = [score_tool(query, meta, role) for meta in all_tools()]
    scored.sort(key=lambda s: s["score"], reverse=True)

    best = scored[0] if scored else None

    # Fallback: if the top pick has zero textual/pattern signal at all,
    # prefer the generic "search" tool instead of whatever won purely on
    # having the lowest cost/latency penalty.
    if (
        best
        and best["capability_match"] == 0
        and best["relevance"] == 0
        and not best["pattern_hit"]
        and best["tool"] != "search"
    ):
        search_entry = next((s for s in scored if s["tool"] == "search"), None)
        if search_entry:
            best = search_entry

    return {"selected": best["tool"] if best else None, "candidates": scored}
