# ToolRouter — Intelligent Tool Selection Framework

A small FastAPI + LangGraph agent that scores every registered tool against
an incoming query (capability match, relevance, risk, cost, latency),
enforces role-based permissions, executes the winning tool, and logs an
audit trail — instead of just letting an LLM freely call whatever it wants.

## Architecture

```
User Query
    │
    ▼
FastAPI  (POST /chat)
    │
    ▼
LangGraph Agent
    │
 analyze_query → select_tool → check_permission → execute_tool → generate_response
    │                │                │                 │
    │                ▼                ▼                 ▼
    │           ToolRouter        Guardrails      Calculator / SQLite /
    │           (scoring)       (role-based)      Document Search (RAG) / Search
    │                                                     │
    ▼                                                     ▼
Audit Log  ◄──────────────────────────────────────  Tool Result
(logs/audit.log)                                          │
                                                            ▼
                                                     Final Answer
```

**Tool selection** (`app/router.py`) scores each tool as:

```
score = 2·capability_match + 1·relevance + 3·pattern_bonus
        − 1·risk_penalty − 5·cost_penalty − 0.002·latency_penalty
```

Permission is **not** baked into this score — the router always picks the
tool that best fits the *query*. Whether the caller is *allowed* to use it
is checked afterward (`app/security.py`) and is what actually blocks
execution. This means a guest asking a database question is correctly
routed to `database` and then **rejected** at the permission gate — a real,
demonstrable guardrail, not a silently-swapped fallback tool.

## Tools

| Tool | Purpose | Min role | Risk |
|---|---|---|---|
| `calculator` | Safe AST-based arithmetic (no `eval`) | guest | low |
| `document_search` | Keyword-retrieval RAG over `data/documents/` (upgrades to Chroma + OpenAI embeddings automatically if `OPENAI_API_KEY` is set) | employee | low |
| `database` | Read-only SQL against a seeded SQLite employee table (writes/DDL are rejected) | admin | high |
| `search` | Stub fallback for anything else | guest | low |

## Setup

```bash
python -m venv venv
source venv/bin/activate      # venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env          # OPENAI_API_KEY is optional — leave blank to run fully offline
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the Swagger UI.

## API

```
POST /chat
{ "query": "What is the leave policy?", "role": "employee" }

→ {
    "answer": "...",
    "tool": "document_search",
    "status": "success",
    "permission": { "granted": true, "reason": "ok" },
    "latency_ms": 2.4,
    "candidates": [ ...every tool's score, for transparency... ]
  }
```

`GET /tools` lists the full tool catalog. Roles are `guest < employee < admin`.

## Demo queries

```
1. "Calculate 125 * 48"            → calculator
2. "What is the leave policy?"     → document_search (RAG)
3. "Find employee 105" (as admin)  → database
4. "Find employee 105" (as guest)  → routed to database, but REJECTED (permission denied)
5. "Search for information about Python" → search (fallback)
```

## Evaluation

Run `python -m tests.evaluate` for a live scored run. Latest result:

```
Tool Selection Accuracy: 10/10 = 100.00%
Permission Compliance:   4/4  = 100.00%
Average Latency:         ~2 ms  (deterministic mode, no LLM call)
```

`pytest tests/ -v` runs 12 unit/integration tests covering routing,
permission enforcement, unsafe-input rejection, and the live API.

## What's deliberately out of scope (v1)

React frontend, real microservices, a full memory/session system,
Kubernetes, cloud deployment, multi-agent orchestration, a custom ML model.
These are the natural "day 2" extensions — see below.

## Next steps (not yet built)

- LangSmith tracing (`LANGCHAIN_TRACING_V2=true` in `.env` — LangChain/LangGraph
  pick it up automatically, no code change needed)
- Swap the keyword-overlap router for embedding-based semantic routing
- Streamlit demo UI
- Conversation memory across turns
- Human-in-the-loop approval step for `high` risk tools
