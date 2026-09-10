"""Audit logging + lightweight in-process tracing.

Real LangSmith tracing is opt-in: set LANGCHAIN_TRACING_V2=true and
LANGCHAIN_API_KEY in .env and LangChain/LangGraph pick it up automatically —
no code change needed here. This module additionally writes a local audit
trail so the project is inspectable without any external dashboard.
"""
import json
import time
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "audit.log"


def log_event(event: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    event = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), **event}
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


class Trace:
    """Collects step timings for a single request, for the API response."""

    def __init__(self) -> None:
        self.steps: list[dict] = []
        self._start = time.perf_counter()

    def step(self, name: str, **details) -> None:
        self.steps.append({"step": name, "t_ms": round((time.perf_counter() - self._start) * 1000, 2), **details})

    def total_ms(self) -> float:
        return round((time.perf_counter() - self._start) * 1000, 2)
