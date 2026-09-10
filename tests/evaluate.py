"""Standalone router evaluation — run with `python -m tests.evaluate`.

Prints tool-selection accuracy plus permission-compliance and average
latency, so results can be pasted straight into a resume/README.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agent import run_agent  # noqa: E402

EVAL_CASES = [
    ("What is 25 * 10?", "employee", "calculator"),
    ("Calculate 90 divided by 3", "employee", "calculator"),
    ("What's 12 + 8?", "employee", "calculator"),
    ("What is the leave policy?", "employee", "document_search"),
    ("How many sick leave days do I get?", "employee", "document_search"),
    ("What are the working hours?", "employee", "document_search"),
    ("Find employee 102", "admin", "database"),
    ("List all employees", "admin", "database"),
    ("Search Python news", "employee", "search"),
    ("Tell me about the latest AI trends", "employee", "search"),
]

PERMISSION_CASES = [
    ("Find employee 102", "guest", False),
    ("Find employee 102", "admin", True),
    ("What is the leave policy?", "guest", False),
    ("What is the leave policy?", "employee", True),
]


def main() -> None:
    correct = 0
    latencies = []
    print(f"{'Query':<40} {'Expected':<16} {'Got':<16} {'OK'}")
    for query, role, expected in EVAL_CASES:
        t0 = time.perf_counter()
        result = run_agent(query, role)
        latencies.append((time.perf_counter() - t0) * 1000)
        got = result["selected_tool"]
        ok = got == expected
        correct += ok
        print(f"{query:<40} {expected:<16} {str(got):<16} {'✓' if ok else '✗'}")

    accuracy = correct / len(EVAL_CASES) * 100
    print(f"\nTool Selection Accuracy: {correct}/{len(EVAL_CASES)} = {accuracy:.2f}%")
    print(f"Average Latency: {sum(latencies) / len(latencies):.2f} ms")

    perm_correct = 0
    for query, role, expect_granted in PERMISSION_CASES:
        result = run_agent(query, role)
        granted = result["permission"]["granted"]
        perm_correct += granted == expect_granted
    perm_accuracy = perm_correct / len(PERMISSION_CASES) * 100
    print(f"Permission Compliance: {perm_correct}/{len(PERMISSION_CASES)} = {perm_accuracy:.2f}%")


if __name__ == "__main__":
    main()
