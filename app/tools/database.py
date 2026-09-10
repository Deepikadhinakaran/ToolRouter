"""SQLite tool — read-only, validated queries against a small seeded DB."""
import re
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "database.db"

_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|attach|pragma|create|replace)\b", re.IGNORECASE
)


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            role TEXT NOT NULL
        )"""
    )
    count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO employees (id, name, department, role) VALUES (?, ?, ?, ?)",
            [
                (101, "Ananya Rao", "Engineering", "Backend Developer"),
                (102, "Vikram Sen", "Engineering", "ML Engineer"),
                (103, "Priya Nair", "HR", "HR Manager"),
                (104, "Rahul Iyer", "Sales", "Account Executive"),
                (105, "Sneha Kumar", "Engineering", "DevOps Engineer"),
            ],
        )
        conn.commit()
    conn.close()


TOOL_META = {
    "name": "database",
    "description": "Run a read-only SQL SELECT against the employee records database.",
    "capabilities": ["records", "employee", "employees", "structured-data", "sql", "staff"],
    "min_role": "admin",
    "risk": "high",
    "cost": 0.001,
    "avg_latency_ms": 15,
    "pattern": r"\bemployee[s]?\b.{0,15}\b\d{2,}\b|\bid\s*\d{2,}\b|\bstaff\b",
}


def run(query: str, sql: str | None = None) -> dict:
    init_db()

    statement = sql
    if statement is None:
        # naive fallback: extract an employee id if present, else list all
        match = re.search(r"\b(\d{3})\b", query)
        if match:
            statement = f"SELECT * FROM employees WHERE id = {match.group(1)}"
        else:
            statement = "SELECT * FROM employees"

    if not statement.strip().lower().startswith("select"):
        return {"status": "rejected", "result": "Only SELECT statements are permitted."}
    if _FORBIDDEN.search(statement):
        return {"status": "rejected", "result": "Query contains a forbidden keyword."}

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute(statement)
        rows = cursor.fetchall()
        conn.close()
        return {"status": "success", "result": rows}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "result": f"Query failed: {exc}"}
