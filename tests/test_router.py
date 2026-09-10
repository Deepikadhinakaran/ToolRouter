import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from app.main import app
from app.router import route
from app.security import check_permission, has_permission
from app.tools import calculator, database, rag, search

client = TestClient(app)

CASES = [
    ("What is 25 * 18?", "employee", "calculator"),
    ("What is the leave policy?", "employee", "document_search"),
    ("Find employee 105", "admin", "database"),
    ("Search for information about Python", "employee", "search"),
]


def test_routing_accuracy():
    correct = 0
    for query, role, expected in CASES:
        result = route(query, role)
        if result["selected"] == expected:
            correct += 1
    accuracy = correct / len(CASES)
    assert accuracy >= 0.75, f"Routing accuracy too low: {accuracy:.0%}"


def test_calculator_tool():
    out = calculator.run("", expression="12 * 5")
    assert out["status"] == "success"
    assert out["result"] == "60"


def test_calculator_rejects_unsafe_input():
    out = calculator.run("", expression="__import__('os').system('echo hi')")
    assert out["status"] == "error"


def test_database_blocks_write_queries():
    out = database.run("", sql="DROP TABLE employees")
    assert out["status"] == "rejected"


def test_database_read_query():
    out = database.run("Find employee 101")
    assert out["status"] == "success"
    assert len(out["result"]) == 1


def test_rag_keyword_fallback_finds_leave_policy():
    out = rag.run("What is the leave policy?")
    assert out["status"] == "success"
    assert any("leave_policy" in hit["source"] for hit in out["result"])


def test_search_stub():
    out = search.run("anything")
    assert out["status"] == "success"


def test_permission_guest_blocked_from_database():
    assert has_permission("guest", database.TOOL_META) is False
    result = check_permission("guest", database.TOOL_META)
    assert result["granted"] is False


def test_permission_admin_allowed_everywhere():
    for meta in (calculator.TOOL_META, database.TOOL_META, rag.TOOL_META, search.TOOL_META):
        assert has_permission("admin", meta) is True


def test_api_calculator_flow():
    resp = client.post("/chat", json={"query": "Calculate 500 / 25", "role": "employee"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["tool"] == "calculator"
    assert body["answer"] == "20.0"


def test_api_guest_blocked_from_database():
    resp = client.post("/chat", json={"query": "Find employee 105", "role": "guest"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "rejected"


def test_api_list_tools():
    resp = client.get("/tools")
    assert resp.status_code == 200
    names = [t["name"] for t in resp.json()["tools"]]
    assert set(names) == {"calculator", "database", "document_search", "search"}
