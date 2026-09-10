"""Access control + guardrails.

Role hierarchy: guest < employee < admin. A tool declares a `min_role` in its
TOOL_META; a caller may use it if their role rank >= the tool's rank.
"""

ROLE_RANK = {"guest": 0, "employee": 1, "admin": 2}

# Risk score used by the router's scoring function (higher risk = lower score
# contribution unless the caller's role comfortably clears the bar).
RISK_SCORE = {"low": 1.0, "medium": 0.6, "high": 0.3}


def is_valid_role(role: str) -> bool:
    return role in ROLE_RANK


def has_permission(role: str, tool_meta: dict) -> bool:
    if not is_valid_role(role):
        return False
    return ROLE_RANK[role] >= ROLE_RANK.get(tool_meta.get("min_role", "admin"), 2)


def check_permission(role: str, tool_meta: dict) -> dict:
    if not is_valid_role(role):
        return {"granted": False, "reason": f"Unknown role '{role}'."}
    if has_permission(role, tool_meta):
        return {"granted": True, "reason": "ok"}
    return {
        "granted": False,
        "reason": f"Role '{role}' lacks permission for tool "
                  f"'{tool_meta['name']}' (requires '{tool_meta['min_role']}').",
    }
